#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# setup.sh — Clone dependency repos into the workspace
# ═══════════════════════════════════════════════════════════════════
#
# This script clones hermes-agent and hermes-desktop into the overlay
# workspace if they're not already present.
#
# Usage:
#   ./setup.sh              — clone both repos
#   ./setup.sh --force      — re-clone (delete existing and start fresh)
#
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

AGENT_REPO="https://github.com/NousResearch/hermes-agent"
DESKTOP_REPO="https://github.com/fathah/hermes-desktop"

AGENT_DIR="$SCRIPT_DIR/hermes-agent"
DESKTOP_DIR="$SCRIPT_DIR/hermes-desktop"

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

FORCE=false
for arg in "$@"; do
    case "$arg" in
        --force) FORCE=true ;;
        --help|-h)
            echo "Usage: ./setup.sh [--force]"
            echo ""
            echo "  (no flags)  Clone repos if not present"
            echo "  --force     Delete and re-clone both repos"
            exit 0
            ;;
    esac
done

echo ""
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}  GenUI Overlay — Setup${NC}"
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo ""

# ── Clone hermes-agent ──

if [ "$FORCE" = true ] && [ -d "$AGENT_DIR" ]; then
    echo -e "${YELLOW}→${NC} Removing existing hermes-agent..."
    rm -rf "$AGENT_DIR"
fi

if [ -d "$AGENT_DIR" ]; then
    echo -e "${GREEN}✓${NC} hermes-agent already present"
else
    echo -e "${YELLOW}→${NC} Cloning hermes-agent..."
    git clone "$AGENT_REPO" "$AGENT_DIR"
    echo -e "${GREEN}✓${NC} hermes-agent cloned"
fi

# ── Clone hermes-desktop ──

if [ "$FORCE" = true ] && [ -d "$DESKTOP_DIR" ]; then
    echo -e "${YELLOW}→${NC} Removing existing hermes-desktop..."
    rm -rf "$DESKTOP_DIR"
fi

if [ -d "$DESKTOP_DIR" ]; then
    echo -e "${GREEN}✓${NC} hermes-desktop already present"
else
    echo -e "${YELLOW}→${NC} Cloning hermes-desktop..."
    git clone "$DESKTOP_REPO" "$DESKTOP_DIR"
    echo -e "${GREEN}✓${NC} hermes-desktop cloned"
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}  Setup complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo ""
echo "Next steps:"
echo "  ./dev.sh        — install agent + apply overlay + launch desktop"
echo "  ./apply.sh      — apply overlay patches only"
echo ""
