"""
GenUI Plugin — Entry Point

Registers hooks for GenUI output transformation, template management tools,
and composable block skills (supplementary docs via skill_view).

The full block reference lives in the system prompt as static text
(prefix-cacheable). This plugin provides:
- `transform_llm_output`: Intercepts agent responses containing ```genui blocks
- Template tools: template_manage, template_list, template_view
- Skills: genui:blocks, genui:patterns, genui:tracking (supplementary on-demand docs)

NOTE: No dynamic content is injected into the system prompt or pre_llm_call.
This preserves the KV cache prefix hash for optimal token caching.
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

SKILLS_DIR = Path(__file__).parent / "skills"


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
    """Register GenUI plugin hooks, template tools, and block skills."""
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

    # Register composable block skills (supplementary docs via skill_view)
    try:
        skills = {
            "blocks": "GenUI block reference — expanded docs with JSON examples and prop tables",
            "patterns": "GenUI composition patterns — wizards, forms, dashboards with copy-paste examples",
            "tracking": "GenUI tracking model — binding rules, common mistakes, detailed examples",
        }
        for name, description in skills.items():
            skill_path = SKILLS_DIR / name / "SKILL.md"
            if skill_path.exists():
                ctx.register_skill(name, skill_path, description=description)
                logger.debug("Registered GenUI skill: genui:%s", name)
            else:
                logger.warning("GenUI skill file missing: %s", skill_path)
        logger.info("GenUI skills registered (%d)", len(skills))
    except Exception:
        logger.warning("Failed to register GenUI skills", exc_info=True)

    logger.info("GenUI overlay plugin registered (v2 — static prompt + on-demand skills)")
