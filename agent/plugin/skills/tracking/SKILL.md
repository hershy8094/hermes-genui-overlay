---
name: genui-tracking
description: "GenUI tracking model — state binding, 4-tier tracking, initialState rules, common mistakes."
version: 1.0.0
metadata:
  hermes:
    tags: [genui, widgets, state, tracking, binding, desktop]
---

# GenUI State & Tracking Model

This skill covers the state management contract for GenUI widgets: how to bind interactive blocks to state, how tracking levels control data flow, and the critical rules that prevent broken widgets.

---

## Payload Structure (Required Top-Level Fields)

```json
{
  "widgetId": "unique-id",
  "widgetType": "composition",
  "initialState": { "field1": "", "field2": false },
  "trackedFields": [
    { "key": "field1", "tracking": "context" },
    { "key": "field2", "tracking": "context" }
  ],
  "actions": [
    { "id": "submit", "label": "Submit", "style": "primary", "tracking": "reply" }
  ],
  "children": [ ... ],
  "initialPage": "step1"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `widgetId` | string | Unique identifier. REQUIRED. |
| `widgetType` | string | **Always `"composition"`**. REQUIRED. |
| `initialState` | object | Default values for ALL bound fields. REQUIRED (use `{}` if none). |
| `trackedFields` | array | Declares which fields the agent observes. REQUIRED (use `[]` if none). |
| `actions` | array | Buttons with tracking. Usually at least one needed. |
| `children` | array | The component tree — nested block nodes. REQUIRED. |
| `initialPage` | string | Starting page ID for multi-page widgets (optional). |

---

## CRITICAL RULES

### Rule 1: bind ↔ initialState ↔ trackedFields Consistency

**Every field used with `bind` MUST be declared in BOTH `initialState` AND `trackedFields`.**

✅ Correct:
```json
{
  "initialState": { "name": "" },
  "trackedFields": [{ "key": "name", "tracking": "context" }],
  "children": [
    { "type": "Input", "props": { "label": "Name" }, "bind": "name" }
  ]
}
```

❌ BROKEN — missing from initialState:
```json
{
  "initialState": {},
  "trackedFields": [{ "key": "name", "tracking": "context" }],
  "children": [
    { "type": "Input", "props": { "label": "Name" }, "bind": "name" }
  ]
}
```

❌ BROKEN — missing from trackedFields:
```json
{
  "initialState": { "name": "" },
  "trackedFields": [],
  "children": [
    { "type": "Input", "props": { "label": "Name" }, "bind": "name" }
  ]
}
```

### Rule 2: actionId ↔ actions Consistency

**Every `actionId` on a Button MUST have a matching entry in `actions`.**

✅ Correct:
```json
{
  "actions": [{ "id": "submit", "label": "Submit", "style": "primary", "tracking": "reply" }],
  "children": [
    { "type": "Button", "props": { "label": "Submit", "actionId": "submit" } }
  ]
}
```

❌ BROKEN — actionId with no matching action:
```json
{
  "actions": [],
  "children": [
    { "type": "Button", "props": { "label": "Submit", "actionId": "submit" } }
  ]
}
```

### Rule 3: widgetType Must Be "composition"

**Always use `"widgetType": "composition"`**. Do NOT invent custom widget types like `"periodic-table"`, `"calculator"`, etc. Build everything from composable blocks.

---

## 4-Tier Tracking Model

Each `trackedFields` entry and each `actions` entry must have a `tracking` level:

| Level | Behavior | When to Use |
|-------|----------|-------------|
| `"ignored"` | Never sent to agent. Pure UI state. | Animations, hover, local toggles |
| `"context"` | Silently merged into background context with next message. | **Most form fields** — name, email, selections |
| `"explicit"` | Queued and attached as structured data to next message. | Important selections you need to reference explicitly |
| `"reply"` | **Triggers immediate agent reply** with full widget state. | **Final submit buttons only** — 1-2 per widget max |

### When to Use Each Level

**`"context"` (default for most fields)**:
- Text inputs, selects, checkboxes, radio groups, sliders
- Any field whose value you want to know when the user next speaks
- The agent sees these values silently — no interruption

**`"reply"` (submit buttons only)**:
- The final "Submit" / "Confirm" / "Complete" button
- Use sparingly — max 1-2 per widget
- Triggers an immediate response from the agent with all tracked state

**`"ignored"` (UI-only)**:
- Cancel/reset buttons that only affect the UI
- Local UI toggles (dark mode, expand/collapse)
- If you forget to set tracking, the default is `"ignored"` — **you will NEVER see the user's input**

**`"explicit"` (structured data)**:
- When you need to reference a specific field value in your reply
- Rarely needed — `"context"` covers most cases

### IMPORTANT: Default Is "ignored"

If you forget to add a tracking level to a field or action, it defaults to `"ignored"`. This means:
- Input fields without tracking → agent never sees what the user typed
- Buttons without tracking → clicking does nothing visible to the agent

**Always set tracking explicitly on every trackedField and every action.**

---

## Bind Types by Block

| Block | bind type | initialState default |
|-------|-----------|---------------------|
| `Input` (text) | string | `""` |
| `Input` (number) | number | `0` |
| `TextArea` | string | `""` |
| `Select` | string | `""` |
| `Checkbox` | boolean | `false` |
| `RadioGroup` | string | `""` |
| `Slider` | number | `0` |
| `DataTable` | array | `[]` (for dynamic rows) |
| `Button` | — | Buttons do NOT use bind; use `actionId` |

---

## Common Mistakes

1. **Inventing widget types**: Using `"widgetType": "my-custom-thing"` instead of `"composition"` → widget won't render.

2. **Missing initialState entries**: Binding to `"email"` but `initialState` doesn't have `"email": ""` → React controlled/uncontrolled input warning, state may not sync.

3. **Missing trackedFields entries**: Binding to `"email"` but `trackedFields` doesn't include it → agent never sees the user's input.

4. **Too many "reply" actions**: Every `"reply"` action triggers an immediate agent response. Using 5 reply buttons means the agent gets called 5 times on each click.

5. **navigate vs actionId confusion**: Page navigation uses `"navigate": "pageId"` on the block node. Form submission uses `"actionId": "id"` in `props`. Don't mix them.

6. **initialPage in wrong place**: `initialPage` goes at the **payload root**, not inside `PageView` props.
