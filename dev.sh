#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# dev.sh — One-shot development launcher for GenUI
# ═══════════════════════════════════════════════════════════════════
#
# This script:
#   1. Installs hermes-agent from source (symlinks into ~/.hermes/)
#   2. Applies the GenUI overlay patches to both repos
#   3. Starts hermes-desktop in dev mode
#
# Usage:
#   ./dev.sh              — full setup + apply + launch
#   ./dev.sh --no-install — skip agent install, just apply + launch
#   ./dev.sh --install    — only install agent from source (no launch)
#   ./dev.sh --apply      — only apply overlay patches (no launch)
#
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENT_DIR="$SCRIPT_DIR/../hermes-agent"
DESKTOP_DIR="$SCRIPT_DIR/../hermes-desktop"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

# ── Parse flags ──

DO_INSTALL=true
DO_APPLY=true
DO_LAUNCH=true
for arg in "$@"; do
    case "$arg" in
        --no-install) DO_INSTALL=false ;;
        --install)    DO_APPLY=false; DO_LAUNCH=false ;;
        --apply)      DO_INSTALL=false; DO_LAUNCH=false ;;
        --help|-h)
            echo "Usage: ./dev.sh [--no-install] [--install] [--apply]"
            echo ""
            echo "  (no flags)    Full setup: install agent + apply overlay + launch desktop"
            echo "  --no-install  Skip agent install, just apply overlay + launch"
            echo "  --install     Only install agent from source (no launch)"
            echo "  --apply       Only apply overlay patches (no launch)"
            exit 0
            ;;
    esac
done

# ── Validation ──

if [ ! -d "$AGENT_DIR" ]; then
    echo -e "${RED}ERROR:${NC} hermes-agent not found at $AGENT_DIR"
    echo "Expected layout: parent/ ├── hermes-agent/ ├── hermes-desktop/ └── hermes-genui-overlay/"
    exit 1
fi

if [ ! -d "$DESKTOP_DIR" ]; then
    echo -e "${RED}ERROR:${NC} hermes-desktop not found at $DESKTOP_DIR"
    exit 1
fi

echo ""
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo -e "${CYAN}  GenUI Development Launcher${NC}"
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo ""

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
            echo -e "${GREEN}✓${NC} Symlink already correct: ~/.hermes/hermes-agent → $AGENT_DIR"
        else
            echo -e "${YELLOW}⚠${NC} Symlink points to $CURRENT_TARGET, updating..."
            rm "$AGENT_LINK"
            ln -sf "$AGENT_DIR" "$AGENT_LINK"
            echo -e "${GREEN}✓${NC} Updated symlink: ~/.hermes/hermes-agent → $AGENT_DIR"
        fi
    elif [ -d "$AGENT_LINK" ]; then
        echo -e "${YELLOW}⚠${NC} ~/.hermes/hermes-agent is a real directory (from official install)"
        echo -e "${YELLOW}⚠${NC} Backing up to ~/.hermes/hermes-agent.official"
        mv "$AGENT_LINK" "${AGENT_LINK}.official"
        ln -sf "$AGENT_DIR" "$AGENT_LINK"
        echo -e "${GREEN}✓${NC} Symlinked: ~/.hermes/hermes-agent → $AGENT_DIR"
    else
        ln -sf "$AGENT_DIR" "$AGENT_LINK"
        echo -e "${GREEN}✓${NC} Symlinked: ~/.hermes/hermes-agent → $AGENT_DIR"
    fi

    # Run setup-hermes.sh if venv doesn't exist yet
    if [ ! -f "$AGENT_DIR/venv/bin/python" ]; then
        echo ""
        echo -e "${CYAN}→${NC} Running setup-hermes.sh (first time — this takes a few minutes)..."
        echo ""
        cd "$AGENT_DIR"
        # Run non-interactively by piping 'n' to skip the setup wizard prompt
        echo "n" | bash setup-hermes.sh
        echo ""
        echo -e "${GREEN}✓${NC} Agent installed from source"
    else
        echo -e "${GREEN}✓${NC} Agent venv already exists at $AGENT_DIR/venv/"
    fi

    # Symlink .env to ~/.hermes/.env if it exists in the repo but not in HERMES_HOME
    if [ -f "$AGENT_DIR/.env" ] && [ ! -f "$HERMES_HOME/.env" ]; then
        ln -sf "$AGENT_DIR/.env" "$HERMES_HOME/.env"
        echo -e "${GREEN}✓${NC} Symlinked .env → ~/.hermes/.env"
    elif [ -f "$HERMES_HOME/.env" ]; then
        echo -e "${GREEN}✓${NC} ~/.hermes/.env already exists"
    else
        echo -e "${YELLOW}⚠${NC} No .env found — you'll need to configure API keys"
        echo "    Copy $AGENT_DIR/.env.example to $AGENT_DIR/.env and add your keys"
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
# Step 3: Install desktop npm deps + launch
# ══════════════════════════════════════════════════════════════════

if [ "$DO_LAUNCH" = true ]; then
    echo -e "${CYAN}── Step 3: Launch hermes-desktop ──${NC}"
    echo ""

    cd "$DESKTOP_DIR"

    # Install npm deps if needed
    if [ ! -d "node_modules" ]; then
        echo -e "${CYAN}→${NC} Installing npm dependencies..."
        npm install
        echo ""
    fi

    echo -e "${GREEN}✓${NC} Starting hermes-desktop dev server..."
    echo ""
    exec npm run dev
fi

echo ""
echo -e "${GREEN}Done!${NC}"
