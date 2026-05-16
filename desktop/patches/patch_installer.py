#!/usr/bin/env python3
"""
Patch: installer.ts — Broaden API key detection for existing Hermes installations.

When a user already has Hermes installed, they may have API keys configured
for providers not in the original 3-key check (OpenRouter, Anthropic, OpenAI).
This patch:
  1. Adds a cross-provider auth.json credential pool scan
  2. Expands the .env API key pattern to cover 13 common providers
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from patch_utils import FilePatcher, PatchError

OVERLAY_ROOT = Path(__file__).resolve().parent.parent.parent
DESKTOP_DIR = OVERLAY_ROOT / "hermes-desktop"


def patch_installer_ts():
    """installer.ts: Broaden API key detection in checkInstallStatus()."""
    target = DESKTOP_DIR / "src" / "main" / "installer.ts"
    patcher = FilePatcher(target)

    # 1. Add cross-provider auth.json credential pool check
    #    Insert after the existing hasHermesAuthCredential check block
    patcher.insert_after(
        anchor="/* ignore */",
        insertion=(
            "  }\n"
            "\n"
            "  // [GENUI-OVERLAY] Check if ANY provider has credentials in auth.json\n"
            "  // The gateway resolves provider routing dynamically, so cross-provider\n"
            "  // credentials from a previous install are still valid.\n"
            "  if (!hasApiKey) {\n"
            "    try {\n"
            '      if (existsSync(HERMES_AUTH_FILE)) {\n'
            '        const auth = JSON.parse(readFileSync(HERMES_AUTH_FILE, "utf-8")) as {\n'
            "          credential_pool?: Record<string, unknown[]>;\n"
            "        };\n"
            "        const pool = auth.credential_pool;\n"
            '        if (pool && typeof pool === "object") {\n'
            "          for (const entries of Object.values(pool)) {\n"
            "            if (Array.isArray(entries) && entries.length > 0) {\n"
            "              hasApiKey = true;\n"
            "              break;\n"
            "            }\n"
            "          }\n"
            "        }\n"
            "      }\n"
            "    } catch {\n"
            "      /* ignore */\n"
            "    }\n"
        ),
        name="Cross-provider auth.json credential check",
        marker="[GENUI-OVERLAY] Check if ANY provider has credentials",
    )

    # 2. Expand the .env API key pattern to cover all common providers
    patcher.replace_text(
        target="/^(OPENROUTER_API_KEY|ANTHROPIC_API_KEY|OPENAI_API_KEY)=(.+)$/,",
        replacement=(
            "// [GENUI-OVERLAY] Expanded to cover all common provider API keys\n"
            "          /^(OPENROUTER_API_KEY|ANTHROPIC_API_KEY|OPENAI_API_KEY|GEMINI_API_KEY|GOOGLE_API_KEY|DEEPSEEK_API_KEY|GROQ_API_KEY|TOGETHER_API_KEY|FIREWORKS_API_KEY|CEREBRAS_API_KEY|MISTRAL_API_KEY|HF_TOKEN|PERPLEXITY_API_KEY)=(.+)$/,"
        ),
        name="Expand .env API key pattern",
        marker="[GENUI-OVERLAY] Expanded to cover all common provider API keys",
    )

    changed = patcher.write()
    print(patcher.report())
    return changed


def apply():
    results = []
    for fn, label in [
        (patch_installer_ts, "installer.ts"),
    ]:
        try:
            r = fn()
            results.append((label, r, None))
        except PatchError as e:
            print(f"  ✗ {label} FAILED: {e}", file=sys.stderr)
            results.append((label, False, str(e)))

    # Summary
    for label, success, err in results:
        if err:
            print(f"  ✗ {label}: {err}")
        elif success:
            print(f"  ✓ {label}")
        else:
            print(f"  ⏭ {label} (already applied)")

    return all(r[2] is None for r in results)


if __name__ == "__main__":
    success = apply()
    sys.exit(0)
