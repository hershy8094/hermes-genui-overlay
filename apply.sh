#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# apply.sh — Apply the GenUI overlay to hermes-agent and hermes-desktop
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENT_DIR="$SCRIPT_DIR/../hermes-agent"
DESKTOP_DIR="$SCRIPT_DIR/../hermes-desktop"

# ── Validation ──

if [ ! -d "$AGENT_DIR" ]; then
    echo "ERROR: hermes-agent not found at $AGENT_DIR"
    echo "Expected directory layout:"
    echo "  parent/"
    echo "  ├── hermes-agent/"
    echo "  ├── hermes-desktop/"
    echo "  └── hermes-genui-overlay/  ← you are here"
    exit 1
fi

if [ ! -d "$DESKTOP_DIR" ]; then
    echo "ERROR: hermes-desktop not found at $DESKTOP_DIR"
    exit 1
fi

echo "═══════════════════════════════════════════"
echo "  Applying GenUI Overlay"
echo "═══════════════════════════════════════════"
echo ""

# ── 1. Symlink plugin (idempotent) ──

PLUGIN_DIR="$HOME/.hermes/plugins"
PLUGIN_TARGET="$PLUGIN_DIR/genui"

mkdir -p "$PLUGIN_DIR"
if [ -L "$PLUGIN_TARGET" ]; then
    echo "✓ Plugin symlink already exists"
elif [ -d "$PLUGIN_TARGET" ]; then
    echo "⚠ Plugin directory exists (not a symlink) — skipping"
else
    ln -sf "$SCRIPT_DIR/agent/plugin" "$PLUGIN_TARGET"
    echo "✓ Plugin symlinked: $PLUGIN_TARGET → agent/plugin/"
fi

# ── 2. Copy standalone frontend files ──

echo ""
echo "── Standalone files ──"

# GenUI types
mkdir -p "$DESKTOP_DIR/src/shared"
cp "$SCRIPT_DIR/desktop/components/genui-types.ts" \
   "$DESKTOP_DIR/src/shared/genui-types.ts" 2>/dev/null && \
   echo "✓ Copied genui-types.ts" || echo "⏭ genui-types.ts (source missing)"

# GenUI components
mkdir -p "$DESKTOP_DIR/src/renderer/src/components/genui/widgets"
if [ -d "$SCRIPT_DIR/desktop/components/genui" ]; then
    cp -r "$SCRIPT_DIR/desktop/components/genui/"* \
       "$DESKTOP_DIR/src/renderer/src/components/genui/" 2>/dev/null && \
       echo "✓ Copied genui/ components" || echo "⏭ genui/ (already up to date)"
else
    echo "⏭ genui/ components (source missing — will be created during implementation)"
fi

# GenUI CSS
if [ -f "$SCRIPT_DIR/desktop/styles/genui.css" ]; then
    cp "$SCRIPT_DIR/desktop/styles/genui.css" \
       "$DESKTOP_DIR/src/renderer/src/assets/genui.css" 2>/dev/null && \
       echo "✓ Copied genui.css" || echo "⏭ genui.css (already up to date)"
    # Inject CSS import into main.css if not already present
    MAIN_CSS="$DESKTOP_DIR/src/renderer/src/assets/main.css"
    if [ -f "$MAIN_CSS" ] && ! grep -q "genui.css" "$MAIN_CSS"; then
        # @import must precede all other statements — prepend, don't append
        sed -i '' '1s/^/@import ".\/genui.css";  \/* [GENUI-OVERLAY] *\/\'$'\n/' "$MAIN_CSS"
        echo "✓ Injected genui.css import into main.css"
    fi
else
    echo "⏸ genui.css — not yet created"
fi

# ── 3. Copy genui_protocol.py into agent gateway ──

echo ""
echo "── Protocol module ──"
cp "$SCRIPT_DIR/agent/plugin/genui_protocol.py" \
   "$AGENT_DIR/gateway/platforms/genui_protocol.py" 2>/dev/null && \
   echo "✓ Copied genui_protocol.py to gateway/platforms/" || \
   echo "✗ Failed to copy genui_protocol.py"

# ── 4. Apply backend patches ──

echo ""
echo "── Backend patches ──"

PYTHON="${PYTHON:-python3}"
for patch in "$SCRIPT_DIR/agent/patches"/patch_*.py; do
    [ -f "$patch" ] || continue
    echo "  Applying $(basename "$patch")..."
    $PYTHON "$patch" || echo "  ⚠ Patch had issues (see above)"
done

# ── 5. Apply frontend patches ──

echo ""
echo "── Frontend patches ──"

for patch in "$SCRIPT_DIR/desktop/patches"/patch_*.py; do
    [ -f "$patch" ] || continue
    echo "  Applying $(basename "$patch")..."
    $PYTHON "$patch" || echo "  ⚠ Patch had issues (see above)"
done

echo ""
echo "═══════════════════════════════════════════"
echo "  Done!"
echo "═══════════════════════════════════════════"
