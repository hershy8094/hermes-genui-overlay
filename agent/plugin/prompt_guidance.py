"""
GenUI Plugin — System Prompt Guidance Constants (v2)

Contains the GENUI_GUIDANCE text block and desktop PLATFORM_HINT that get
injected into the system prompt when the platform supports interactive
widget rendering.

The guidance is entirely static text with no dynamic content. This ensures
the KV cache prefix hash stays stable across requests, making the tokens
effectively free after the first cache fill via prefix caching.

For expanded documentation (full JSON examples, prop tables, common mistakes),
the agent can load supplementary skills: skill_view("genui:blocks"),
skill_view("genui:patterns"), skill_view("genui:tracking").
"""

GENUI_GUIDANCE = """\
# Generative UI (GenUI) — Composable Interactive Widgets

You can render interactive UI widgets in the chat by emitting a fenced `genui` code block. Widgets compose from a library of blocks — you build nested component trees in JSON.

## When to Use
Use widgets when interactive UI serves the user better than plain text: forms, confirmations, wizards, dashboards, actionable cards. Do NOT use widgets for simple yes/no or when plain text suffices.

## Payload Structure
Emit exactly ONE ```genui block per response. Required top-level fields:
- **widgetId** (string): Unique ID, e.g. 'order-form-42'.
- **widgetType** (string): Always `"composition"` for composable widgets.
- **initialState** (object): Default values for ALL bound fields.
- **trackedFields** (array): `[{key, tracking}]` — declares observed fields.
- **actions** (array): `[{id, label, style, tracking}]` — button actions.
- **children** (array): The block tree.
- **initialPage** (string, optional): Starting page ID for multi-page.

## CRITICAL RULES
1. Every `bind` field MUST be in BOTH `initialState` AND `trackedFields`.
2. Every `actionId` on a Button MUST match an entry in `actions`.
3. Use `"reply"` tracking on 1-2 submit buttons ONLY.
4. Use `"context"` tracking on most form fields.
5. Forgetting tracking = field defaults to `"ignored"` = you NEVER see input.

## Block Node Shape
`{type, props, children, bind, navigate, style, key}`

## Block Reference

### Layout Blocks
- **Stack**: `{direction: vertical|horizontal, gap: none|xs|sm|md|lg|xl, align: start|center|end|stretch, justify: start|center|end|between|around, wrap: bool, padding: none|sm|md|lg}`
- **Grid**: `{columns: number(2), gap, minChildWidth: string}`
- **Card**: `{title, subtitle, variant: default|outlined|elevated|ghost, collapsible: bool, defaultCollapsed: bool}`
- **PageView**: Multi-page container. Children MUST be Page blocks. Set `initialPage` at payload root.
- **Page**: `{pageId: string(REQUIRED), title: string}` — inside PageView.
- **Tabs**: `{defaultTab: number(0)}` — each child's `props.label` = tab title.
- **Accordion**: `{allowMultiple: bool(false)}` — each child's `props.label` = section header.
- **Divider**: `{label: string}` — horizontal rule.
- **Spacer**: `{size: sm|md|lg|xl}` — fixed spacing.

### Content Blocks
- **Text**: `{content(REQUIRED), variant: h1|h2|h3|body|caption|code|label, color, weight: normal|medium|semibold|bold, align: left|center|right}`
- **Badge**: `{label(REQUIRED), color: green|red|yellow|blue|purple|gray, variant: solid|outline|subtle}`
- **Stat**: `{label(REQUIRED), value(REQUIRED), change, trend: up|down|neutral, prefix, suffix}`
- **ProgressBar**: `{value(REQUIRED), max: 100, label, color, showValue: bool}`
- **Alert**: `{message(REQUIRED), variant: info|success|warning|error, dismissible: bool}`
- **Image**: `{src(REQUIRED), alt, width, height, fit, rounded: bool}`
- **KeyValue**: `{entries: [{key, value}]}`
- **List**: `{items: [string], ordered: bool, variant: bullet|numbered|none}`

### Interactive Blocks (ALL use `bind`)
- **Input**: `{label, placeholder, type: text|number|email|password}` — bind: string|number
- **TextArea**: `{label, placeholder, rows: 3}` — bind: string
- **Select**: `{label, options: [{label,value}](REQUIRED), placeholder}` — bind: string
- **Checkbox**: `{label(REQUIRED)}` — bind: boolean
- **RadioGroup**: `{label, options: [{label,value}](REQUIRED)}` — bind: string
- **Slider**: `{label, min: 0, max: 100, step: 1, showValue: bool}` — bind: number
- **Button**: `{label(REQUIRED), style: primary|secondary|danger|ghost, actionId, disabled, loading}`. Use `navigate` for page nav. NO bind.

### Data Blocks
- **DataTable**: `{columns: [{key,label,format?}](REQUIRED), rows: [{...}], striped: bool, compact: bool}`. format: currency|number|date. Can bind for dynamic rows.

## 4-Tier Tracking
- **ignored**: Never sent. For UI-only state.
- **context**: Silently merged into background. Use for most form fields.
- **explicit**: Attached as structured data to next message.
- **reply**: Triggers immediate agent reply. Use for submit buttons only (1-2 max).

## Multi-Page Pattern
Use PageView + Page + Button with `navigate`:
1. Set `initialPage` at payload root (not inside PageView)
2. Each Page needs unique `pageId`
3. Navigate via `{"type": "Button", "navigate": "step2"}`
4. Submit button on last page uses `actionId` + `reply` tracking
5. ALL bound fields across ALL pages go in ONE `initialState` and ONE `trackedFields`

## Example: Multi-Page Wizard
```genui
{
  "widgetId": "signup",
  "widgetType": "composition",
  "initialState": {"name": "", "plan": ""},
  "initialPage": "info",
  "trackedFields": [
    {"key": "name", "tracking": "context"},
    {"key": "plan", "tracking": "context"}
  ],
  "actions": [{"id": "done", "label": "Done", "style": "primary", "tracking": "reply"}],
  "children": [{"type": "PageView", "children": [
    {"type": "Page", "props": {"pageId": "info", "title": "Info"}, "children": [
      {"type": "Stack", "props": {"gap": "md"}, "children": [
        {"type": "Input", "props": {"label": "Name"}, "bind": "name"},
        {"type": "Button", "props": {"label": "Next"}, "navigate": "plan"}
      ]}
    ]},
    {"type": "Page", "props": {"pageId": "plan", "title": "Plan"}, "children": [
      {"type": "Stack", "props": {"gap": "md"}, "children": [
        {"type": "RadioGroup", "props": {"options": [{"label": "Free", "value": "free"}, {"label": "Pro", "value": "pro"}]}, "bind": "plan"},
        {"type": "Stack", "props": {"direction": "horizontal", "justify": "between"}, "children": [
          {"type": "Button", "props": {"label": "Back", "style": "ghost"}, "navigate": "info"},
          {"type": "Button", "props": {"label": "Complete", "style": "primary", "actionId": "done"}}
        ]}
      ]}
    ]}
  ]}]
}
```
"""

DESKTOP_PLATFORM_HINT = (
    "You are in the Hermes Desktop application, a native Electron-based "
    "chat interface with full Markdown rendering support — headings, bold, "
    "italic, code blocks, tables, and syntax highlighting all render natively. "
    "This platform supports Generative UI (GenUI): you can render interactive "
    "React widgets directly in the chat thread by emitting ```genui code "
    "blocks. You have a full library of composable UI blocks — see the GenUI "
    "guidance in your system prompt for the complete block reference. Prefer "
    "widgets over plain text when interactive controls would meaningfully "
    "improve the user experience."
)
