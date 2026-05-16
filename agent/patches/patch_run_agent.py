#!/usr/bin/env python3
"""
Patch: run_agent.py

Adds:
  1. Import of GENUI_GUIDANCE from agent.prompt_builder
  2. Conditional injection of GENUI_GUIDANCE when platform_key == "desktop"

Anchors:
  - Import block for prompt_builder (stable — always imports multiple names)
  - COMPUTER_USE_GUIDANCE injection block (stable pattern for capability injection)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from patch_utils import FilePatcher, PatchError

OVERLAY_ROOT = Path(__file__).resolve().parent.parent.parent
AGENT_DIR = OVERLAY_ROOT / "hermes-agent"
TARGET = AGENT_DIR / "run_agent.py"

GENUI_INJECTION = '''
        # [GENUI-OVERLAY] GenUI (Generative UI) — inject widget rendering
        # guidance when the platform supports interactive widgets (desktop app).
        if platform_key == "desktop":
            stable_parts.append(GENUI_GUIDANCE)
'''


def apply():
    try:
        patcher = FilePatcher(TARGET)

        # 1. Add GENUI_GUIDANCE to the prompt_builder import
        patcher.append_to_imports(
            module="agent.prompt_builder",
            names=["GENUI_GUIDANCE"],
            name="Import GENUI_GUIDANCE",
            marker="GENUI_GUIDANCE",
        )

        # 2. Inject GENUI_GUIDANCE after PLATFORM_HINTS block (which is right
        #    after platform_key is defined — the old anchor was before the
        #    variable existed, causing it to never execute).
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
