#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# revert.sh — Revert the GenUI overlay, restoring upstream state
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENT_DIR="$SCRIPT_DIR/hermes-agent"
DESKTOP_DIR="$SCRIPT_DIR/hermes-desktop"

echo "═══════════════════════════════════════════"
echo "  Reverting GenUI Overlay"
echo "═══════════════════════════════════════════"
echo ""

# ── 1. Revert agent patched files ──

echo "── Backend (git checkout) ──"
cd "$AGENT_DIR"
git checkout -- agent/prompt_builder.py 2>/dev/null && echo "✓ prompt_builder.py" || echo "⏭ prompt_builder.py (clean)"
git checkout -- agent/system_prompt.py 2>/dev/null && echo "✓ system_prompt.py" || echo "⏭ system_prompt.py (clean)"
git checkout -- run_agent.py 2>/dev/null && echo "✓ run_agent.py" || echo "⏭ run_agent.py (clean)"
git checkout -- gateway/platforms/api_server.py 2>/dev/null && echo "✓ api_server.py" || echo "⏭ api_server.py (clean)"

# Remove copied protocol module
rm -f gateway/platforms/genui_protocol.py && echo "✓ Removed genui_protocol.py" || true

# ── 2. Revert desktop patched files ──

echo ""
echo "── Frontend (git checkout) ──"
cd "$DESKTOP_DIR"
git checkout -- src/main/hermes.ts 2>/dev/null && echo "✓ hermes.ts" || echo "⏭ hermes.ts (clean)"
git checkout -- src/main/sse-parser.ts 2>/dev/null && echo "✓ sse-parser.ts" || echo "⏭ sse-parser.ts (clean)"
git checkout -- src/main/index.ts 2>/dev/null && echo "✓ index.ts" || echo "⏭ index.ts (clean)"
git checkout -- src/preload/index.ts 2>/dev/null && echo "✓ preload/index.ts" || echo "⏭ preload/index.ts (clean)"
git checkout -- src/preload/index.d.ts 2>/dev/null && echo "✓ preload/index.d.ts" || echo "⏭ preload/index.d.ts (clean)"
git checkout -- src/renderer/src/screens/Chat/Chat.tsx 2>/dev/null && echo "✓ Chat.tsx" || echo "⏭ Chat.tsx (clean)"
git checkout -- src/renderer/src/assets/main.css 2>/dev/null && echo "✓ main.css" || echo "⏭ main.css (clean)"
git checkout -- src/main/installer.ts 2>/dev/null && echo "✓ installer.ts" || echo "⏭ installer.ts (clean)"

# Remove standalone files (not tracked by upstream)
echo ""
echo "── Standalone files ──"
rm -rf src/renderer/src/components/genui && echo "✓ Removed genui/ components" || true
rm -f src/shared/genui-types.ts && echo "✓ Removed genui-types.ts" || true
rm -f src/renderer/src/assets/genui.css && echo "✓ Removed genui.css" || true
rm -f src/renderer/src/assets/genui-blocks.css && echo "✓ Removed genui-blocks.css" || true
git checkout -- package-lock.json 2>/dev/null && echo "✓ Restored package-lock.json" || echo "⏭ package-lock.json (clean)"

# Clean build artifacts
rm -rf dist && echo "✓ Cleaned dist/" || true

# ── 3. Remove plugin symlink ──

echo ""
echo "── Plugin symlink ──"
PLUGIN_TARGET="$HOME/.hermes/plugins/genui"
if [ -L "$PLUGIN_TARGET" ]; then
    rm "$PLUGIN_TARGET"
    echo "✓ Removed plugin symlink"
else
    echo "⏭ No symlink found"
fi

echo ""
echo "═══════════════════════════════════════════"
echo "  Reverted — upstream state restored"
echo "═══════════════════════════════════════════"
