#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# install.sh — Build and install Hermes Desktop with GenUI overlay
# ═══════════════════════════════════════════════════════════════════
#
# Production install script that:
#   1. Installs hermes-agent from source (symlinks into ~/.hermes/)
#   2. Applies the GenUI overlay patches to both repos
#   3. Stops any stale gateway from a previous installation
#   4. Builds the Electron app as a native .app bundle
#   5. Copies to /Applications (macOS)
#
# Handles pre-existing Hermes installations gracefully:
#   - Preserves existing ~/.hermes/.env, config.yaml, auth.json
#   - Backs up the old hermes-agent directory if it's not a symlink
#   - Kills stale gateway processes started from a different path
#
# Usage:
#   ./install.sh              — full install + build
#   ./install.sh --apply      — only apply overlay patches (no build)
#   ./install.sh --build      — only build desktop (skip agent install)
#   ./install.sh --no-build   — install agent + apply, skip build
#
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENT_DIR="$SCRIPT_DIR/hermes-agent"
DESKTOP_DIR="$SCRIPT_DIR/hermes-desktop"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

# ── Parse flags ──

DO_INSTALL=true
DO_APPLY=true
DO_BUILD=true
for arg in "$@"; do
    case "$arg" in
        --apply)    DO_INSTALL=false; DO_BUILD=false ;;
        --build)    DO_INSTALL=false; DO_APPLY=false ;;
        --no-build) DO_BUILD=false ;;
        --help|-h)
            echo "Usage: ./install.sh [--apply] [--build] [--no-build]"
            echo ""
            echo "  (no flags)    Full install: agent + overlay + build + install"
            echo "  --apply       Only apply overlay patches (no build)"
            echo "  --build       Only build desktop app (skip agent install)"
            echo "  --no-build    Install agent + apply overlay, skip building"
            exit 0
            ;;
    esac
done

# ── Validation ──

if [ ! -d "$AGENT_DIR" ]; then
    echo -e "${RED}ERROR:${NC} hermes-agent not found at $AGENT_DIR"
    echo "Run ./setup.sh first to clone dependency repos."
    exit 1
fi

if [ ! -d "$DESKTOP_DIR" ]; then
    echo -e "${RED}ERROR:${NC} hermes-desktop not found at $DESKTOP_DIR"
    echo "Run ./setup.sh first to clone dependency repos."
    exit 1
fi

echo ""
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo -e "${CYAN}  GenUI — Production Install${NC}"
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo ""

# ══════════════════════════════════════════════════════════════════
# Step 0: Detect and handle pre-existing Hermes installation
# ══════════════════════════════════════════════════════════════════

if [ -d "$HERMES_HOME" ]; then
    echo -e "${CYAN}── Pre-existing Hermes installation detected ──${NC}"
    echo ""

    # --- Kill stale gateway ---
    PID_FILE="$HERMES_HOME/gateway.pid"
    if [ -f "$PID_FILE" ]; then
        # Read PID from the JSON file
        GATEWAY_PID=$(python3 -c "
import json, sys
try:
    with open('$PID_FILE') as f:
        d = json.load(f)
    pid = d.get('pid')
    argv = d.get('argv', [])
    # Check if the gateway was started from a different path
    if argv and '$AGENT_DIR' not in ' '.join(str(a) for a in argv):
        print(pid or '')
    else:
        print('')
except Exception:
    print('')
" 2>/dev/null)

        if [ -n "$GATEWAY_PID" ]; then
            # Verify the process is actually running
            if kill -0 "$GATEWAY_PID" 2>/dev/null; then
                echo -e "${YELLOW}⚠${NC}  Stopping stale gateway (PID $GATEWAY_PID) from previous install..."
                kill "$GATEWAY_PID" 2>/dev/null || true
                sleep 1
                # Force kill if still running
                kill -0 "$GATEWAY_PID" 2>/dev/null && kill -9 "$GATEWAY_PID" 2>/dev/null || true
                echo -e "${GREEN}✓${NC}  Stopped old gateway"
            fi
        else
            # Gateway is from our repo, still check if it's healthy
            CURRENT_PID=$(python3 -c "import json; print(json.load(open('$PID_FILE')).get('pid',''))" 2>/dev/null || echo "")
            if [ -n "$CURRENT_PID" ] && kill -0 "$CURRENT_PID" 2>/dev/null; then
                echo -e "${GREEN}✓${NC}  Existing gateway (PID $CURRENT_PID) is running from this repo"
            fi
        fi
    fi

    # --- Preserve existing configs ---
    if [ -f "$HERMES_HOME/.env" ]; then
        echo -e "${GREEN}✓${NC}  Preserving existing ~/.hermes/.env"
    fi
    if [ -f "$HERMES_HOME/config.yaml" ]; then
        echo -e "${GREEN}✓${NC}  Preserving existing ~/.hermes/config.yaml"
    fi
    if [ -f "$HERMES_HOME/auth.json" ]; then
        echo -e "${GREEN}✓${NC}  Preserving existing ~/.hermes/auth.json"
    fi
    echo ""
fi

# ══════════════════════════════════════════════════════════════════
# Step 1: Install hermes-agent from source
# ══════════════════════════════════════════════════════════════════

if [ "$DO_INSTALL" = true ]; then
    echo -e "${CYAN}── Step 1: Install hermes-agent from source ──${NC}"
    echo ""

    # Create ~/.hermes if needed
    mkdir -p "$HERMES_HOME"

    # Symlink ~/.hermes/hermes-agent → our dev repo
    AGENT_LINK="$HERMES_HOME/hermes-agent"
    if [ -L "$AGENT_LINK" ]; then
        CURRENT_TARGET="$(readlink "$AGENT_LINK")"
        if [ "$CURRENT_TARGET" = "$AGENT_DIR" ]; then
            echo -e "${GREEN}✓${NC}  Symlink already correct: ~/.hermes/hermes-agent → $AGENT_DIR"
        else
            echo -e "${YELLOW}⚠${NC}  Symlink points to $CURRENT_TARGET, updating..."
            rm "$AGENT_LINK"
            ln -sf "$AGENT_DIR" "$AGENT_LINK"
            echo -e "${GREEN}✓${NC}  Updated symlink: ~/.hermes/hermes-agent → $AGENT_DIR"
        fi
    elif [ -d "$AGENT_LINK" ]; then
        echo -e "${YELLOW}⚠${NC}  ~/.hermes/hermes-agent is a real directory (from official install)"
        echo -e "${YELLOW}⚠${NC}  Backing up to ~/.hermes/hermes-agent.official"
        mv "$AGENT_LINK" "${AGENT_LINK}.official"
        ln -sf "$AGENT_DIR" "$AGENT_LINK"
        echo -e "${GREEN}✓${NC}  Symlinked: ~/.hermes/hermes-agent → $AGENT_DIR"
    else
        ln -sf "$AGENT_DIR" "$AGENT_LINK"
        echo -e "${GREEN}✓${NC}  Symlinked: ~/.hermes/hermes-agent → $AGENT_DIR"
    fi

    # Run setup-hermes.sh if venv doesn't exist yet
    if [ ! -f "$AGENT_DIR/venv/bin/python" ]; then
        echo ""
        echo -e "${CYAN}→${NC}  Running setup-hermes.sh (first time — this takes a few minutes)..."
        echo ""
        cd "$AGENT_DIR"
        # Run non-interactively by piping 'n' to skip the setup wizard prompt
        echo "n" | bash setup-hermes.sh
        echo ""
        echo -e "${GREEN}✓${NC}  Agent installed from source"
    else
        echo -e "${GREEN}✓${NC}  Agent venv already exists at $AGENT_DIR/venv/"
    fi

    # Handle .env — NEVER overwrite existing user config
    if [ -f "$HERMES_HOME/.env" ]; then
        # Check if the existing .env is a symlink to our repo's bare template
        if [ -L "$HERMES_HOME/.env" ]; then
            LINK_TARGET="$(readlink "$HERMES_HOME/.env")"
            # If it points to our repo .env (which has all keys commented out),
            # check if the user has any real API keys in it
            HAS_REAL_KEY=$(grep -cE '^[^#]*(OPENROUTER_API_KEY|ANTHROPIC_API_KEY|OPENAI_API_KEY|GEMINI_API_KEY|GOOGLE_API_KEY)=.+' "$HERMES_HOME/.env" 2>/dev/null || echo "0")
            if [ "$HAS_REAL_KEY" = "0" ]; then
                echo -e "${YELLOW}⚠${NC}  ~/.hermes/.env exists but has no API keys configured"
                echo -e "    ${CYAN}→${NC}  The app will prompt you to set up your API key on first launch"
            else
                echo -e "${GREEN}✓${NC}  ~/.hermes/.env has API keys configured"
            fi
        else
            echo -e "${GREEN}✓${NC}  ~/.hermes/.env exists (preserved from previous install)"
        fi
    elif [ -f "$AGENT_DIR/.env" ]; then
        ln -sf "$AGENT_DIR/.env" "$HERMES_HOME/.env"
        echo -e "${GREEN}✓${NC}  Symlinked .env → ~/.hermes/.env"
    else
        echo -e "${YELLOW}⚠${NC}  No .env found — the app will prompt you to configure API keys"
    fi

    echo ""
fi

# ══════════════════════════════════════════════════════════════════
# Step 2: Apply the GenUI overlay
# ══════════════════════════════════════════════════════════════════

if [ "$DO_APPLY" = true ]; then
    echo -e "${CYAN}── Step 2: Apply GenUI overlay ──${NC}"
    echo ""
    cd "$SCRIPT_DIR"
    bash apply.sh
    echo ""
fi

# ══════════════════════════════════════════════════════════════════
# Step 3: Build and install the desktop app
# ══════════════════════════════════════════════════════════════════

if [ "$DO_BUILD" = true ]; then
    echo -e "${CYAN}── Step 3: Build Hermes Desktop ──${NC}"
    echo ""

    cd "$DESKTOP_DIR"

    # Install npm deps if needed
    if [ ! -d "node_modules" ]; then
        echo -e "${CYAN}→${NC}  Installing npm dependencies..."
        npm install
        echo ""
    fi

    echo -e "${CYAN}→${NC}  Building production app (this may take a minute)..."
    echo ""

    # Build without notarization (requires Apple Developer credentials)
    # and without publishing to GitHub releases
    CSC_IDENTITY_AUTO_DISCOVERY=false npx electron-builder --mac --config.mac.notarize=null --publish=never 2>&1 | tail -20

    echo ""

    # Find the built .app
    APP_PATH=$(find "$DESKTOP_DIR/dist" -maxdepth 2 -name "*.app" -type d 2>/dev/null | head -1)

    if [ -z "$APP_PATH" ]; then
        echo -e "${RED}ERROR:${NC} Build failed — no .app found in dist/"
        echo "Check the build output above for errors."
        exit 1
    fi

    APP_NAME=$(basename "$APP_PATH")
    echo -e "${GREEN}✓${NC}  Built: $APP_NAME"
    echo ""

    # Install to /Applications
    INSTALL_TARGET="/Applications/$APP_NAME"
    if [ -d "$INSTALL_TARGET" ]; then
        echo -e "${YELLOW}⚠${NC}  $APP_NAME already exists in /Applications — replacing..."
        rm -rf "$INSTALL_TARGET"
    fi

    cp -R "$APP_PATH" "/Applications/"
    echo -e "${GREEN}✓${NC}  Installed to /Applications/$APP_NAME"

    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════${NC}"
    echo -e "${CYAN}  Installation Complete! 🎉${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════${NC}"
    echo ""
    echo -e "  Launch ${BOLD}$APP_NAME${NC} from your Applications folder"
    echo -e "  or run: ${CYAN}open '/Applications/$APP_NAME'${NC}"
    echo ""
    echo -e "  ${YELLOW}Note:${NC} macOS may show a warning on first launch since the"
    echo -e "  app is not code-signed. Right-click → Open to bypass."
    echo ""
else
    echo ""
    echo -e "${GREEN}Done!${NC}"
fi
