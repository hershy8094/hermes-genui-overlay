#!/usr/bin/env python3
"""
Patch: agent/system_prompt.py

Adds:
  1. Import of GENUI_GUIDANCE from agent.prompt_builder
  2. Conditional injection of GENUI_GUIDANCE when platform_key == "desktop"

The system prompt module was refactored from run_agent.py in upstream.
The injection point is after PLATFORM_HINTS[platform_key] is appended
to stable_parts — this places GenUI guidance in the "stable" tier
(prefix-cacheable, static across all turns in a session).

Anchors:
  - Import block for prompt_builder (stable — always imports multiple names)
  - PLATFORM_HINTS[platform_key] append (stable pattern for platform guidance)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from patch_utils import FilePatcher, PatchError

OVERLAY_ROOT = Path(__file__).resolve().parent.parent.parent
AGENT_DIR = OVERLAY_ROOT / "hermes-agent"
TARGET = AGENT_DIR / "agent" / "system_prompt.py"

GENUI_INJECTION = '''
        # [GENUI-OVERLAY] GenUI (Generative UI) — inject widget rendering
        # guidance when the platform supports interactive widgets (desktop app).
        if platform_key == "desktop":
            from agent.prompt_builder import GENUI_GUIDANCE
            stable_parts.append(GENUI_GUIDANCE)
'''


def apply():
    try:
        patcher = FilePatcher(TARGET)

        # Inject GENUI_GUIDANCE after PLATFORM_HINTS block.
        # Uses a lazy import inside the conditional to avoid adding
        # GENUI_GUIDANCE to the module-level import (which would fail
        # if the patch_prompt_builder hasn't run yet).
        patcher.insert_after(
            anchor="stable_parts.append(PLATFORM_HINTS[platform_key])",
            insertion=GENUI_INJECTION,
            name="Inject GENUI_GUIDANCE for desktop platform",
            marker="[GENUI-OVERLAY]",
        )

        changed = patcher.write()
        print(patcher.report())
        return changed

    except PatchError as e:
        print(f"  ✗ FAILED: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    success = apply()
    sys.exit(0)
