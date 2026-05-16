"""
GenUI Protocol — Backend Type Definitions & Parsing

Defines the structured payload format for ``hermes.genui.render`` SSE events
and utilities for extracting GenUI blocks from the agent's streamed output.

v2: Adds GenUINode for composable component trees, multi-page support,
and template references.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Optional, List


class TrackingLevel(str, Enum):
    """4-tier tracking: what the frontend does when a field/action changes."""
    IGNORED = "ignored"    # Pure UI — never leaves widget
    CONTEXT = "context"    # Silent background context
    EXPLICIT = "explicit"  # Attached to next outbound message
    REPLY = "reply"        # Triggers immediate agent reply


@dataclass
class GenUIStateField:
    """Declares agent interest in a specific state field."""
    key: str
    tracking: TrackingLevel
    label: Optional[str] = None


@dataclass
class GenUIAction:
    """A clickable action within a widget."""
    id: str
    label: str
    style: str = "primary"  # "primary", "secondary", "danger", "ghost"
    tracking: TrackingLevel = TrackingLevel.IGNORED
    value: Any = None


@dataclass
class GenUINode:
    """A single node in the composable component tree.

    Nodes can be layout containers (Stack, Grid, Card, PageView), content
    elements (Text, Badge, Image, Stat), interactive controls (Button, Input,
    Select), or data displays (DataTable, List). They nest via `children`.
    """
    type: str
    key: Optional[str] = None
    props: Optional[dict] = field(default_factory=dict)
    children: Optional[List["GenUINode"]] = None
    bind: Optional[str] = None
    tracking: Optional[TrackingLevel] = None
    navigate: Optional[str] = None
    style: Optional[dict] = None


@dataclass
class GenUIRenderPayload:
    """Payload for a hermes.genui.render SSE event.

    v1 (legacy): Uses widget_type to look up a hardcoded React component.
    v2 (composable): Uses children[] to define a recursive component tree.
    Both paths coexist — the frontend branches on whether children is set.
    """
    widget_id: str
    widget_type: str
    initial_state: dict = field(default_factory=dict)
    tracked_fields: list[GenUIStateField] = field(default_factory=list)
    actions: list[GenUIAction] = field(default_factory=list)
    meta: Optional[dict] = None
    # v2 fields
    children: Optional[List[GenUINode]] = None
    template_id: Optional[str] = None
    initial_page: Optional[str] = None


# ---------------------------------------------------------------------------
# Regex for detecting ```genui ... ``` blocks in streamed text
# ---------------------------------------------------------------------------

_GENUI_BLOCK_RE = re.compile(
    r"```genui\s*\n(.*?)```",
    re.DOTALL,
)


def parse_genui_block(text: str) -> tuple[Optional[GenUIRenderPayload], str]:
    """Extract a ```genui``` block from streamed text.

    Returns ``(parsed_payload, remaining_text_with_block_removed)``.
    Returns ``(None, original_text)`` if no complete block is found.
    """
    match = _GENUI_BLOCK_RE.search(text)
    if not match:
        return None, text

    raw_json = match.group(1).strip()
    try:
        data = json.loads(raw_json)
    except (json.JSONDecodeError, ValueError):
        # Malformed JSON — strip the block but return None payload
        cleaned = text[: match.start()] + text[match.end() :]
        return None, cleaned

    # Parse tracked_fields
    tracked_fields = []
    for tf in data.get("trackedFields", []):
        tracked_fields.append(GenUIStateField(
            key=tf["key"],
            tracking=TrackingLevel(tf.get("tracking", "ignored")),
            label=tf.get("label"),
        ))

    # Parse actions
    actions = []
    for act in data.get("actions", []):
        actions.append(GenUIAction(
            id=act["id"],
            label=act["label"],
            style=act.get("style", "primary"),
            tracking=TrackingLevel(act.get("tracking", "ignored")),
            value=act.get("value"),
        ))

    # Parse v2 children tree (recursive)
    children = _parse_children(data.get("children")) if data.get("children") else None

    payload = GenUIRenderPayload(
        widget_id=data.get("widgetId", ""),
        widget_type=data.get("widgetType", ""),
        initial_state=data.get("initialState", {}),
        tracked_fields=tracked_fields,
        actions=actions,
        meta=data.get("meta"),
        children=children,
        template_id=data.get("templateId"),
        initial_page=data.get("initialPage"),
    )

    cleaned = text[: match.start()] + text[match.end() :]
    return payload, cleaned


def _parse_children(raw_children: list) -> List[GenUINode]:
    """Recursively parse a children array from JSON into GenUINode objects."""
    nodes = []
    for item in raw_children:
        if not isinstance(item, dict) or "type" not in item:
            continue
        node = GenUINode(
            type=item["type"],
            key=item.get("key"),
            props=item.get("props", {}),
            children=_parse_children(item["children"]) if item.get("children") else None,
            bind=item.get("bind"),
            tracking=TrackingLevel(item["tracking"]) if item.get("tracking") else None,
            navigate=item.get("navigate"),
            style=item.get("style"),
        )
        nodes.append(node)
    return nodes


def _serialize_children(nodes: List[GenUINode]) -> list:
    """Recursively serialize GenUINode objects to JSON-ready dicts."""
    result = []
    for node in nodes:
        d: dict[str, Any] = {"type": node.type}
        if node.key:
            d["key"] = node.key
        if node.props:
            d["props"] = node.props
        if node.children:
            d["children"] = _serialize_children(node.children)
        if node.bind:
            d["bind"] = node.bind
        if node.tracking:
            d["tracking"] = node.tracking.value
        if node.navigate:
            d["navigate"] = node.navigate
        if node.style:
            d["style"] = node.style
        result.append(d)
    return result


def serialize_genui_event(payload: GenUIRenderPayload) -> str:
    """Serialize a GenUIRenderPayload to JSON for SSE data line.

    Converts Python snake_case to camelCase for the wire format.
    """
    data = {
        "widgetId": payload.widget_id,
        "widgetType": payload.widget_type,
        "initialState": payload.initial_state,
        "trackedFields": [
            {
                "key": tf.key,
                "tracking": tf.tracking.value,
                **({"label": tf.label} if tf.label else {}),
            }
            for tf in payload.tracked_fields
        ],
        "actions": [
            {
                "id": act.id,
                "label": act.label,
                "style": act.style,
                "tracking": act.tracking.value,
                **({"value": act.value} if act.value is not None else {}),
            }
            for act in payload.actions
        ],
    }
    if payload.meta:
        data["meta"] = payload.meta
    if payload.children:
        data["children"] = _serialize_children(payload.children)
    if payload.template_id:
        data["templateId"] = payload.template_id
    if payload.initial_page:
        data["initialPage"] = payload.initial_page
    return json.dumps(data, separators=(",", ":"))


# ---------------------------------------------------------------------------
# GenUI context message parsing (incoming from frontend)
# ---------------------------------------------------------------------------

_GENUI_PREFIX_RE = re.compile(
    r"^\[genui:(reply|explicit|context)\]\s*(.+?)(?:\n|$)",
    re.DOTALL,
)


def parse_genui_message(text: str) -> tuple[Optional[str], Optional[dict], str]:
    """Parse a ``[genui:*]`` prefixed message from the frontend.

    Returns ``(tier, parsed_json, remaining_user_text)``.
    Returns ``(None, None, original_text)`` if no prefix is found.

    *tier* is one of ``"reply"``, ``"explicit"``, ``"context"``.
    """
    match = _GENUI_PREFIX_RE.match(text)
    if not match:
        return None, None, text

    tier = match.group(1)
    json_str = match.group(2).strip()
    remaining = text[match.end():].strip()

    try:
        data = json.loads(json_str)
    except (json.JSONDecodeError, ValueError):
        return tier, None, remaining

    return tier, data, remaining


def format_genui_context_for_agent(
    tier: str,
    data: dict,
    user_text: str = "",
) -> str:
    """Transform a parsed GenUI message into agent-readable text.

    This is injected into the conversation so the agent can reason about
    widget interactions.
    """
    if tier == "reply":
        trigger = data.get("trigger", {})
        parts = [
            "The user interacted with a UI widget:",
            f"- Widget: {trigger.get('widgetType', 'unknown')} (id: {trigger.get('widgetId', '?')})",
        ]
        if trigger.get("actionId"):
            parts.append(f"- Action: {trigger['actionId']}")
        if trigger.get("field"):
            parts.append(f"- Field changed: {trigger['field']}")
        parts.append(f"- Current state: {json.dumps(trigger.get('state', {}), indent=2)}")

        bg = data.get("backgroundContext", {})
        if bg:
            parts.append(f"- Background context: {json.dumps(bg, indent=2)}")

        explicit = data.get("explicitUpdates", [])
        if explicit:
            parts.append(f"- Pending explicit updates: {json.dumps(explicit, indent=2)}")

        parts.append("")
        parts.append("Please respond based on this interaction.")
        return "\n".join(parts)

    elif tier == "explicit":
        formatted = json.dumps(data, indent=2)
        prefix = f"[Widget state updates attached by the user's interface]\n{formatted}\n\n"
        return prefix + user_text if user_text else prefix.rstrip()

    elif tier == "context":
        formatted = json.dumps(data, indent=2)
        prefix = f"[Background widget context]\n{formatted}\n\n"
        return prefix + user_text if user_text else prefix.rstrip()

    return user_text or ""
