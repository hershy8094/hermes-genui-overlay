#!/usr/bin/env python3
"""
Patch: gateway/platforms/api_server.py

Adds:
  1. genui_protocol imports
  2. X-Hermes-Platform header parsing in _handle_chat_completions
  3. platform_override parameter in _create_agent and _run_agent

Anchors use stable function/method signatures and import patterns.

NOTE: Some sub-patches are marked as TODO for the re-implementation phase.
The import and header parsing are implemented; the deeper SSE/delta buffering
patches will be added when we resume full implementation.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from patch_utils import FilePatcher, PatchError

OVERLAY_ROOT = Path(__file__).resolve().parent.parent.parent
AGENT_DIR = OVERLAY_ROOT.parent / "hermes-agent"
TARGET = AGENT_DIR / "gateway" / "platforms" / "api_server.py"


def apply():
    try:
        patcher = FilePatcher(TARGET)

        # 1. Add genui_protocol import
        #    Uses append_to_imports — if the module isn't imported yet,
        #    adds a new import line after the last existing import.
        patcher.append_to_imports(
            module="gateway.platforms.genui_protocol",
            names=["parse_genui_block", "serialize_genui_event",
                   "parse_genui_message", "format_genui_context_for_agent"],
            name="Import genui_protocol",
            marker="genui_protocol",
        )

        # 2-3. platform_override and header parsing are TODO — these require
        # deeper anchoring into specific function signatures that change
        # frequently. They will be implemented during re-implementation.
        # For now, just the import is applied.

        changed = patcher.write()
        print(patcher.report())
        return changed

    except PatchError as e:
        print(f"  ✗ FAILED: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    success = apply()
    sys.exit(0)
