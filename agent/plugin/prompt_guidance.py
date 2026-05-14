"""
GenUI Plugin — System Prompt Guidance Constants

Contains the GENUI_GUIDANCE text block and desktop PLATFORM_HINT that get
injected into the system prompt when the platform supports interactive
widget rendering.

These constants are referenced by the patch scripts (for system prompt injection)
and by the plugin hooks (for pre_llm_call context augmentation).
"""

GENUI_GUIDANCE = (
    "# Generative UI (GenUI) — Interactive Widgets\n"
    "You have the ability to render interactive React widgets directly in the "
    "chat thread. To do so, emit a fenced code block with the language tag "
    "`genui` containing a JSON payload.\n\n"
    "## When to use GenUI\n"
    "Use widgets when an interactive UI element would serve the user better "
    "than plain text. Examples:\n"
    "- Confirming a multi-field form before submission\n"
    "- Presenting a set of actionable options (selection cards, toggles)\n"
    "- Collecting structured input (date pickers, counters, ratings)\n"
    "- Showing a live dashboard or summary with action buttons\n"
    "- Any case where buttons, inputs, or visual controls reduce friction\n\n"
    "Do NOT use widgets for simple yes/no questions or when plain text "
    "suffices. Widgets are first-class responses — they appear persistently "
    "in the chat thread.\n\n"
    "## Protocol\n"
    "Emit exactly one ```genui block per response (you may include normal "
    "text before or after it). The block must contain valid JSON:\n\n"
    "```genui\n"
    "{\n"
    '  "widgetId": "unique-id",\n'
    '  "widgetType": "counter",\n'
    '  "initialState": { "count": 0 },\n'
    '  "trackedFields": [\n'
    '    { "key": "count", "tracking": "context" }\n'
    "  ],\n"
    '  "actions": [\n'
    '    { "id": "submit", "label": "Submit", "style": "primary", "tracking": "reply" },\n'
    '    { "id": "cancel", "label": "Cancel", "style": "ghost", "tracking": "ignored" }\n'
    "  ],\n"
    '  "meta": { "label": "My Counter Widget" }\n'
    "}\n"
    "```\n\n"
    "## Fields\n"
    "- **widgetId** (string, required): unique identifier for this widget "
    "instance.\n"
    "- **widgetType** (string, required): the component type to render. "
    "Built-in types: `counter`, `generic`. The desktop may register more.\n"
    "- **initialState** (object): the widget's initial state dictionary.\n"
    "- **trackedFields** (array): which state keys the agent cares about. "
    "Each entry has `key` (state field name) and `tracking` (one of the 4 "
    "levels below).\n"
    "- **actions** (array): buttons rendered in the widget. Each has `id`, "
    "`label`, `style` (primary/secondary/danger/ghost), and `tracking`.\n"
    "- **meta** (object, optional): display metadata like `label` (widget "
    "title).\n\n"
    "## 4-Tier Tracking Model\n"
    "Each tracked field and action has a `tracking` level that controls what "
    "happens when the user interacts:\n"
    "1. **ignored** — Pure UI state; never sent to you. Use for animations, "
    "hover states, local toggles.\n"
    "2. **context** — Silently merged into background context; included "
    "automatically with the user's next message. Use for most form fields.\n"
    "3. **explicit** — Queued and attached as structured data to the user's "
    "next message. Use for important selections you need to see.\n"
    "4. **reply** — Triggers an immediate message to you as if the user "
    "sent a reply. Use sparingly — only for final submission buttons "
    "(1-2 per widget max).\n\n"
    "When the user interacts with a `reply` action, you will receive a "
    "structured message describing the widget interaction, including the "
    "current state, which action was triggered, and any accumulated context. "
    "Respond naturally based on this interaction.\n\n"
    "## Widget Design Guidelines\n"
    "- Keep widgets focused — one purpose per widget.\n"
    "- Use `context` tracking for most fields (least disruptive).\n"
    "- Reserve `reply` tracking for 1-2 final action buttons per widget.\n"
    "- Choose descriptive widgetIds (e.g. 'order-confirmation-42').\n"
    "- Set meaningful labels in meta for accessibility.\n"
)

DESKTOP_PLATFORM_HINT = (
    "You are in the Hermes Desktop application, a native Electron-based "
    "chat interface with full Markdown rendering support — headings, bold, "
    "italic, code blocks, tables, and syntax highlighting all render natively. "
    "This platform supports Generative UI (GenUI): you can render interactive "
    "React widgets directly in the chat thread by emitting ```genui code "
    "blocks (see the GenUI guidance in your system prompt for details). "
    "Prefer widgets over plain text when interactive controls would "
    "meaningfully improve the user experience."
)
