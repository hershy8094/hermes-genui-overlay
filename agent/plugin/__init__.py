"""
GenUI Plugin — Entry Point

Registers hooks for GenUI system prompt injection, output transformation,
and template management tools.

This plugin is loaded via the hermes plugin system. It registers:
- `pre_llm_call`: Injects GenUI context + template list when platform is 'desktop'
- `transform_llm_output`: Intercepts agent responses containing ```genui blocks
- Template tools: template_manage, template_list, template_view
"""

from __future__ import annotations

import json
import logging

logger = logging.getLogger(__name__)


def _on_pre_llm_call(**kwargs) -> dict | None:
    """Pre-LLM hook: inject GenUI context and available templates for desktop."""
    platform = kwargs.get("platform", "")
    if platform.lower().strip() != "desktop":
        return None

    # Inject available template names as context so the agent knows what's reusable
    try:
        from .template_store import template_list
        templates_json = template_list()
        templates_data = json.loads(templates_json)
        if templates_data.get("count", 0) > 0:
            names = [t["name"] for t in templates_data["templates"]]
            context = (
                f"[GenUI templates available: {', '.join(names)}. "
                f"Use template_view(name) to load one.]"
            )
            return {"inject_context": context}
    except Exception:
        logger.debug("Failed to inject template context", exc_info=True)

    return None


def _on_transform_llm_output(**kwargs) -> str | None:
    """Transform hook: post-process agent output containing GenUI blocks."""
    response_text = kwargs.get("response_text", "")
    platform = kwargs.get("platform", "")

    if platform.lower().strip() != "desktop":
        return None

    if "```genui" not in response_text:
        return None

    # Currently pass-through — future validation/enrichment goes here
    return None


def register(ctx) -> None:
    """Register GenUI plugin hooks and template tools."""
    ctx.register_hook("pre_llm_call", _on_pre_llm_call)
    ctx.register_hook("transform_llm_output", _on_transform_llm_output)

    # Register template management tools
    try:
        from .template_store import (
            template_manage,
            template_list,
            template_view,
            TEMPLATE_MANAGE_SCHEMA,
            TEMPLATE_LIST_SCHEMA,
            TEMPLATE_VIEW_SCHEMA,
        )
        ctx.register_tool("template_manage", template_manage, TEMPLATE_MANAGE_SCHEMA)
        ctx.register_tool("template_list", template_list, TEMPLATE_LIST_SCHEMA)
        ctx.register_tool("template_view", template_view, TEMPLATE_VIEW_SCHEMA)
        logger.info("GenUI template tools registered")
    except Exception:
        logger.warning("Failed to register template tools", exc_info=True)

    logger.info("GenUI overlay plugin registered (v2 — composable blocks)")
