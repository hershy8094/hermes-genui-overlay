"""
GenUI Plugin — Entry Point

Registers hooks for GenUI system prompt injection and output transformation.

This plugin is loaded via the hermes plugin system. It registers:
- `pre_llm_call`: Injects GenUI context when the platform is 'desktop'
  (supplements the marker-based system prompt patches)
- `transform_llm_output`: Intercepts agent responses containing ```genui
  blocks for any post-processing needs

The heavy lifting (system prompt injection, SSE buffering, header parsing)
is done by the marker-based patches in ../patches/. This plugin provides
the hook-based parts that don't require patching core files.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def _on_pre_llm_call(**kwargs) -> dict | None:
    """Pre-LLM hook: inject GenUI context for desktop platform.

    Note: The system prompt injection is handled by the marker-based patches
    (which inject GENUI_GUIDANCE into _build_system_prompt_parts). This hook
    exists as a fallback/supplement — it can inject context into the user
    message for cases where the system prompt patch didn't apply cleanly.
    """
    platform = kwargs.get("platform", "")
    if platform.lower().strip() != "desktop":
        return None

    # The pre_llm_call hook injects into user messages, not system prompt.
    # We use it only for supplementary context, not core GenUI guidance.
    # The core guidance is injected via the system prompt patches.
    return None


def _on_transform_llm_output(**kwargs) -> str | None:
    """Transform hook: post-process agent output containing GenUI blocks.

    Currently a no-op pass-through. This hook exists as an extension point
    for future needs like:
    - Validating GenUI JSON schemas before they reach the frontend
    - Injecting default tracking levels
    - Logging widget usage metrics
    """
    response_text = kwargs.get("response_text", "")
    platform = kwargs.get("platform", "")

    # Only process for desktop platform
    if platform.lower().strip() != "desktop":
        return None

    # Check if response contains a genui block
    if "```genui" not in response_text:
        return None

    # Currently pass-through — future validation/enrichment goes here
    return None


def register(ctx) -> None:
    """Register GenUI plugin hooks. Called by the hermes plugin loader."""
    ctx.register_hook("pre_llm_call", _on_pre_llm_call)
    ctx.register_hook("transform_llm_output", _on_transform_llm_output)
    logger.info("GenUI overlay plugin registered")
