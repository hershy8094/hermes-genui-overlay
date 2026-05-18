---
name: genui-blocks
description: "GenUI composable block reference — all block types, props, and bind fields."
version: 1.0.0
metadata:
  hermes:
    tags: [genui, widgets, ui, blocks, components, desktop]
---

# GenUI Block Reference

All blocks are used inside the `children` array of a GenUI composition payload. Every node follows this shape:

```json
{
  "type": "BlockType",
  "props": { ... },
  "children": [ ... ],
  "bind": "stateFieldName",
  "navigate": "pageId",
  "style": { "color": "red" },
  "key": "unique-key"
}
```

| Field | Purpose |
| ------- | --------- |
| `type` | Block type name (case-sensitive): `"Stack"`, `"Card"`, `"Input"`, etc. |
| `props` | Block-specific properties (see below). |
| `children` | Nested child blocks (for layout containers). |
| `bind` | Connects this block to a state field (for interactive blocks like Input, Select, Checkbox). |
| `navigate` | Page ID to navigate to when this block is activated (for Button blocks). |
| `style` | Inline CSS overrides as `{ property: value }`. |
| `key` | Unique key for React rendering (auto-generated if omitted). |

---

## Layout Blocks

### `Stack` — Flex container

```json
{ "type": "Stack", "props": { "direction": "vertical", "gap": "md" }, "children": [...] }
```

| Prop | Type | Default | Values |
| ------ | ------ | --------- | -------- |
| `direction` | string | `"vertical"` | `"vertical"`, `"horizontal"` |
| `gap` | string | `"md"` | `"none"`, `"xs"`, `"sm"`, `"md"`, `"lg"`, `"xl"` |
| `align` | string | `"stretch"` | `"start"`, `"center"`, `"end"`, `"stretch"` |
| `justify` | string | `"start"` | `"start"`, `"center"`, `"end"`, `"between"`, `"around"` |
| `wrap` | boolean | `false` | |
| `padding` | string | `"none"` | `"none"`, `"sm"`, `"md"`, `"lg"` |

### `Grid` — CSS Grid

```json
{ "type": "Grid", "props": { "columns": 3, "gap": "md" }, "children": [...] }
```

| Prop | Type | Default |
| ------ | ------ | --------- |
| `columns` | number | `2` |
| `gap` | string | `"md"` — same values as Stack |
| `minChildWidth` | string | — e.g. `"200px"` enables auto-fit responsive columns |

### `Card` — Container with optional header

```json
{ "type": "Card", "props": { "title": "Settings", "variant": "outlined" }, "children": [...] }
```

| Prop | Type | Default | Values |
| ------ | ------ | --------- | -------- |
| `title` | string | — | |
| `subtitle` | string | — | |
| `variant` | string | `"default"` | `"default"`, `"outlined"`, `"elevated"`, `"ghost"` |
| `collapsible` | boolean | `false` | |
| `defaultCollapsed` | boolean | `false` | |

### `PageView` — Multi-page container (children MUST be `Page` blocks)

```json
{ "type": "PageView", "children": [
  { "type": "Page", "props": { "pageId": "step1", "title": "Step 1" }, "children": [...] },
  { "type": "Page", "props": { "pageId": "step2", "title": "Step 2" }, "children": [...] }
]}
```

PageView shows only the active page. Navigation between pages is done via Button blocks with `"navigate": "pageId"`.

**IMPORTANT**: Set `"initialPage": "step1"` at the **payload root** (not inside PageView props) to control which page shows first.

### `Page` — A single page within PageView

| Prop | Type | Required |
| ------ | ------ | ---------- |
| `pageId` | string | YES — unique identifier for navigation |
| `title` | string | Display title shown in page indicators |

### `Tabs` — Tabbed container

Each direct child becomes a tab pane. The child's `props.label` is used as the tab title.

```json
{ "type": "Tabs", "props": { "defaultTab": 0 }, "children": [
  { "type": "Card", "props": { "label": "Tab 1" }, "children": [...] },
  { "type": "Card", "props": { "label": "Tab 2" }, "children": [...] }
]}
```

| Prop | Type | Default |
| ------ | ------ | --------- |
| `defaultTab` | number | `0` — index of initially active tab |

### `Accordion` — Collapsible sections

Each direct child becomes a collapsible section. The child's `props.label` is the section header.

```json
{ "type": "Accordion", "props": { "allowMultiple": false }, "children": [
  { "type": "Stack", "props": { "label": "Section 1" }, "children": [...] },
  { "type": "Stack", "props": { "label": "Section 2" }, "children": [...] }
]}
```

| Prop | Type | Default |
| ------ | ------ | --------- |
| `allowMultiple` | boolean | `false` |

### `Divider` — Horizontal rule

```json
{ "type": "Divider", "props": { "label": "Optional Label" } }
```

### `Spacer` — Fixed spacing

```json
{ "type": "Spacer", "props": { "size": "lg" } }
```

| Prop | Type | Default | Values |
| ------ | ------ | --------- | -------- |
| `size` | string or number | `"md"` | `"sm"`, `"md"`, `"lg"`, `"xl"` or pixel number |

---

## Content Blocks

### `Text` — Text display

```json
{ "type": "Text", "props": { "content": "Hello World", "variant": "h2" } }
```

| Prop | Type | Default | Values |
| ------ | ------ | --------- | -------- |
| `content` | string | `""` | REQUIRED — the text to display |
| `variant` | string | `"body"` | `"h1"`, `"h2"`, `"h3"`, `"body"`, `"caption"`, `"code"`, `"label"` |
| `color` | string | — | CSS color or design token |
| `weight` | string | — | `"normal"`, `"medium"`, `"semibold"`, `"bold"` |
| `align` | string | — | `"left"`, `"center"`, `"right"` |

### `Badge` — Status indicator

```json
{ "type": "Badge", "props": { "label": "Active", "color": "green" } }
```

| Prop | Type | Default | Values |
| ------ | ------ | --------- | -------- |
| `label` | string | REQUIRED | |
| `color` | string | `"gray"` | `"green"`, `"red"`, `"yellow"`, `"blue"`, `"purple"`, `"gray"` |
| `variant` | string | `"solid"` | `"solid"`, `"outline"`, `"subtle"` |

### `Stat` — KPI statistic

```json
{ "type": "Stat", "props": { "label": "Revenue", "value": "$12,400", "change": "+12%", "trend": "up" } }
```

| Prop | Type | Required |
| ------ | ------ | ---------- |
| `label` | string | YES |
| `value` | string or number | YES |
| `change` | string | — e.g. `"+12%"`, `"-3"` |
| `trend` | string | `"up"`, `"down"`, `"neutral"` |
| `prefix` | string | — e.g. `"$"` |
| `suffix` | string | — e.g. `"units"` |

### `ProgressBar` — Progress indicator

```json
{ "type": "ProgressBar", "props": { "value": 65, "max": 100, "label": "Upload" } }
```

| Prop | Type | Default |
| ------ | ------ | --------- |
| `value` | number | REQUIRED |
| `max` | number | `100` |
| `label` | string | — |
| `color` | string | — |
| `showValue` | boolean | `true` |

### `Alert` — Alert banner

```json
{ "type": "Alert", "props": { "message": "Changes saved!", "variant": "success" } }
```

| Prop | Type | Default | Values |
| ------ | ------ | --------- | -------- |
| `message` | string | REQUIRED | |
| `variant` | string | `"info"` | `"info"`, `"success"`, `"warning"`, `"error"` |
| `dismissible` | boolean | `false` | |

### `Image` — Image display

```json
{ "type": "Image", "props": { "src": "https://...", "alt": "description" } }
```

| Prop | Type | Default |
| ------ | ------ | --------- |
| `src` | string | REQUIRED |
| `alt` | string | `""` |
| `width` | string | — |
| `height` | string | — |
| `fit` | string | `"cover"` |
| `rounded` | boolean | `false` |

### `KeyValue` — Key-value pair list

```json
{ "type": "KeyValue", "props": { "entries": [{"key": "Name", "value": "Alice"}, {"key": "Role", "value": "Admin"}] } }
```

### `List` — Ordered/unordered list

```json
{ "type": "List", "props": { "items": ["Item 1", "Item 2"], "ordered": false } }
```

---

## Interactive Blocks

**All interactive blocks use `bind` to connect to state. The bound field MUST appear in `initialState` and `trackedFields`.**

### `Input` — Text input

```json
{ "type": "Input", "props": { "label": "Email", "placeholder": "you@example.com", "type": "email" }, "bind": "email" }
```

| Prop | Type | Default | Values |
| ------ | ------ | --------- | -------- |
| `label` | string | — | |
| `placeholder` | string | `""` | |
| `type` | string | `"text"` | `"text"`, `"number"`, `"email"`, `"password"` |

**bind type**: string (or number if type="number")

### `TextArea` — Multi-line text input

```json
{ "type": "TextArea", "props": { "label": "Notes", "placeholder": "Enter details...", "rows": 4 }, "bind": "notes" }
```

| Prop | Type | Default |
| ------ | ------ | --------- |
| `label` | string | — |
| `placeholder` | string | `""` |
| `rows` | number | `3` |

**bind type**: string

### `Select` — Dropdown

```json
{ "type": "Select", "props": { "label": "Country", "options": [{"label": "USA", "value": "us"}, {"label": "UK", "value": "uk"}], "placeholder": "Choose..." }, "bind": "country" }
```

| Prop | Type | Required |
| ------ | ------ | ---------- |
| `options` | `[{label, value}]` | YES |
| `label` | string | — |
| `placeholder` | string | `"Select..."` |

**bind type**: string (the selected option's `value`)

### `Checkbox` — Boolean toggle

```json
{ "type": "Checkbox", "props": { "label": "I agree to the terms" }, "bind": "agreed" }
```

| Prop | Type | Required |
| ------ | ------ | ---------- |
| `label` | string | YES |

**bind type**: boolean

### `RadioGroup` — Radio button group

```json
{ "type": "RadioGroup", "props": { "label": "Priority", "options": [{"label": "Low", "value": "low"}, {"label": "High", "value": "high"}] }, "bind": "priority" }
```

| Prop | Type | Required |
| ------ | ------ | ---------- |
| `options` | `[{label, value}]` | YES |
| `label` | string | — |

**bind type**: string (the selected option's `value`)

### `Slider` — Range slider

```json
{ "type": "Slider", "props": { "label": "Volume", "min": 0, "max": 100, "step": 5 }, "bind": "volume" }
```

| Prop | Type | Default |
| ------ | ------ | --------- |
| `label` | string | — |
| `min` | number | `0` |
| `max` | number | `100` |
| `step` | number | `1` |
| `showValue` | boolean | `true` |

**bind type**: number

### `Button` — Action button

Buttons trigger actions and/or page navigation. They do NOT use `bind`.

```json
{ "type": "Button", "props": { "label": "Submit", "style": "primary", "actionId": "submit" } }
```

| Prop | Type | Default | Values |
| ------ | ------ | --------- | -------- |
| `label` | string | `"Button"` | REQUIRED |
| `style` | string | `"primary"` | `"primary"`, `"secondary"`, `"danger"`, `"ghost"` |
| `actionId` | string | — | Must match an entry in top-level `actions` array |
| `disabled` | boolean | `false` | |
| `loading` | boolean | `false` | |

For navigation: `{ "type": "Button", "props": { "label": "Next" }, "navigate": "step2" }`

---

## Data Blocks

### `DataTable` — Tabular data

```json
{ "type": "DataTable", "props": {
  "columns": [{"key": "name", "label": "Name"}, {"key": "price", "label": "Price", "format": "currency"}],
  "rows": [{"name": "Widget", "price": 9.99}, {"name": "Gadget", "price": 24.99}]
} }
```

| Prop | Type | Default |
| ------ | ------ | --------- |
| `columns` | `[{key, label, format?}]` | REQUIRED |
| `rows` | `[{...}]` | — static data OR use `bind` for dynamic |
| `striped` | boolean | `true` |
| `compact` | boolean | `false` |

Column `format` options: `"currency"` ($X.XX), `"number"` (localized), `"date"` (date string).

Can also use `bind` to read rows from state: `{ "type": "DataTable", "bind": "tableRows", ... }`
