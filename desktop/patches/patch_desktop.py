#!/usr/bin/env python3
"""
Desktop Patches — Placeholder

These patches modify the hermes-desktop frontend files to add GenUI support.
Each patch targets a specific file and uses marker-based insertion to survive
upstream changes.

Patches to implement:
  1. hermes.ts    — Add X-Hermes-Platform header + onGenUIRender callback
  2. sse-parser.ts — Add hermes.genui.render event handling
  3. index.ts     — Add chat-genui-render IPC channel
  4. preload/index.ts + index.d.ts — Add onGenUIRender bridge
  5. Chat.tsx     — Widget state management + rendering
  6. main.css     — GenUI widget styles (append)

These will be implemented during the re-implementation phase.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from patch_utils import FilePatcher, PatchError

OVERLAY_ROOT = Path(__file__).resolve().parent.parent.parent
DESKTOP_DIR = OVERLAY_ROOT.parent / "hermes-desktop"


def patch_hermes_ts():
    """Add X-Hermes-Platform header to outbound API requests."""
    target = DESKTOP_DIR / "src" / "main" / "hermes.ts"
    try:
        patcher = FilePatcher(target)

        # Add X-Hermes-Platform header to the headers object
        # Anchor: existing headers in the fetch/request call
        patcher.insert_after(
            anchor='"Content-Type": "application/json"',
            insertion='      "X-Hermes-Platform": "desktop",  // [GENUI-OVERLAY]',
            name="Add X-Hermes-Platform header",
            marker="X-Hermes-Platform",
        )

        changed = patcher.write()
        print(patcher.report())
        return changed
    except PatchError as e:
        print(f"  ✗ hermes.ts FAILED: {e}", file=sys.stderr)
        return False


def patch_sse_parser():
    """Add hermes.genui.render event to SSE parser."""
    # Placeholder — will be implemented during re-implementation phase
    print("  ⏸ sse-parser.ts — not yet implemented")
    return True


def patch_main_index():
    """Add chat-genui-render IPC channel."""
    # Placeholder — will be implemented during re-implementation phase
    print("  ⏸ index.ts — not yet implemented")
    return True


def patch_preload():
    """Add onGenUIRender bridge to preload."""
    # Placeholder — will be implemented during re-implementation phase
    print("  ⏸ preload/index.ts — not yet implemented")
    return True


def patch_chat():
    """Add widget state management to Chat.tsx."""
    # Placeholder — will be implemented during re-implementation phase
    print("  ⏸ Chat.tsx — not yet implemented")
    return True


def patch_css():
    """Append GenUI styles to main.css."""
    target = DESKTOP_DIR / "src" / "renderer" / "src" / "assets" / "main.css"
    styles_file = OVERLAY_ROOT / "desktop" / "styles" / "genui.css"

    if not styles_file.exists():
        print("  ⏸ main.css — genui.css not yet created")
        return True

    try:
        patcher = FilePatcher(target)
        css_content = styles_file.read_text(encoding="utf-8")
        patcher.append_to_file(
            content=f"\n/* ═══ [GENUI-OVERLAY] GenUI Widget Styles ═══ */\n{css_content}",
            name="Append GenUI CSS",
            marker="[GENUI-OVERLAY]",
        )
        changed = patcher.write()
        print(patcher.report())
        return changed
    except PatchError as e:
        print(f"  ✗ main.css FAILED: {e}", file=sys.stderr)
        return False


def apply_all():
    """Apply all desktop patches."""
    results = [
        patch_hermes_ts(),
        patch_sse_parser(),
        patch_main_index(),
        patch_preload(),
        patch_chat(),
        patch_css(),
    ]
    return all(results)


if __name__ == "__main__":
    success = apply_all()
    sys.exit(0)
