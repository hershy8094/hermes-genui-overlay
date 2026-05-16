#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# pull-and-patch.sh — Pull upstream updates + re-apply overlay
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENT_DIR="$SCRIPT_DIR/hermes-agent"
DESKTOP_DIR="$SCRIPT_DIR/hermes-desktop"

echo "═══════════════════════════════════════════"
echo "  Pull & Patch — GenUI Overlay"
echo "═══════════════════════════════════════════"

# ── 1. Revert overlay changes ──

echo ""
echo "Step 1: Reverting overlay..."
"$SCRIPT_DIR/revert.sh"

# ── 2. Pull upstream ──

echo ""
echo "Step 2: Pulling upstream..."

echo "  hermes-agent:"
cd "$AGENT_DIR"
git pull --ff-only 2>&1 | sed 's/^/    /' || {
    echo "    ⚠ Fast-forward failed. You may need to resolve manually."
    echo "    Try: cd $AGENT_DIR && git pull"
}

echo "  hermes-desktop:"
cd "$DESKTOP_DIR"
git pull --ff-only 2>&1 | sed 's/^/    /' || {
    echo "    ⚠ Fast-forward failed. You may need to resolve manually."
    echo "    Try: cd $DESKTOP_DIR && git pull"
}

# ── 3. Re-apply overlay ──

echo ""
echo "Step 3: Re-applying overlay..."
"$SCRIPT_DIR/apply.sh"

echo ""
echo "═══════════════════════════════════════════"
echo "  Pull & Patch complete!"
echo "═══════════════════════════════════════════"
