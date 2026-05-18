---
name: genui-patterns
description: "GenUI composition patterns — wizards, forms, dashboards, with complete working examples."
version: 1.0.0
metadata:
  hermes:
    tags: [genui, widgets, patterns, composition, desktop]
---

# GenUI Composition Patterns

Complete, copy-paste-ready patterns for common widget compositions.

> Load `genui:blocks` if you need the props reference for individual block types.

---

## Pattern 1: Simple Form

```genui
{
  "widgetId": "contact-form",
  "widgetType": "composition",
  "initialState": { "name": "", "email": "", "message": "" },
  "trackedFields": [
    { "key": "name", "tracking": "context" },
    { "key": "email", "tracking": "context" },
    { "key": "message", "tracking": "context" }
  ],
  "actions": [
    { "id": "send", "label": "Send", "style": "primary", "tracking": "reply" }
  ],
  "children": [
    { "type": "Card", "props": { "title": "Contact Us" }, "children": [
      { "type": "Stack", "props": { "gap": "md" }, "children": [
        { "type": "Input", "props": { "label": "Name", "placeholder": "Full name" }, "bind": "name" },
        { "type": "Input", "props": { "label": "Email", "type": "email" }, "bind": "email" },
        { "type": "TextArea", "props": { "label": "Message", "rows": 4 }, "bind": "message" },
        { "type": "Button", "props": { "label": "Send", "style": "primary", "actionId": "send" } }
      ]}
    ]}
  ]
}
```

---

## Pattern 2: Multi-Page Wizard

```genui
{
  "widgetId": "signup-wizard",
  "widgetType": "composition",
  "initialState": { "name": "", "email": "", "plan": "" },
  "initialPage": "step1",
  "trackedFields": [
    { "key": "name", "tracking": "context" },
    { "key": "email", "tracking": "context" },
    { "key": "plan", "tracking": "context" }
  ],
  "actions": [
    { "id": "complete", "label": "Complete", "style": "primary", "tracking": "reply" }
  ],
  "children": [
    { "type": "PageView", "children": [
      { "type": "Page", "props": { "pageId": "step1", "title": "Your Info" }, "children": [
        { "type": "Stack", "props": { "gap": "md" }, "children": [
          { "type": "Text", "props": { "content": "Step 1: Your Information", "variant": "h3" } },
          { "type": "Input", "props": { "label": "Name" }, "bind": "name" },
          { "type": "Input", "props": { "label": "Email", "type": "email" }, "bind": "email" },
          { "type": "Stack", "props": { "direction": "horizontal", "justify": "end" }, "children": [
            { "type": "Button", "props": { "label": "Next →", "style": "primary" }, "navigate": "step2" }
          ]}
        ]}
      ]},
      { "type": "Page", "props": { "pageId": "step2", "title": "Plan" }, "children": [
        { "type": "Stack", "props": { "gap": "md" }, "children": [
          { "type": "Text", "props": { "content": "Step 2: Choose Plan", "variant": "h3" } },
          { "type": "RadioGroup", "props": { "label": "Plan", "options": [
            { "label": "Free", "value": "free" },
            { "label": "Pro ($9/mo)", "value": "pro" }
          ]}, "bind": "plan" },
          { "type": "Stack", "props": { "direction": "horizontal", "justify": "between" }, "children": [
            { "type": "Button", "props": { "label": "← Back", "style": "ghost" }, "navigate": "step1" },
            { "type": "Button", "props": { "label": "Complete", "style": "primary", "actionId": "complete" } }
          ]}
        ]}
      ]}
    ]}
  ]
}
```

Key points:
- `initialPage` at **payload root**, not inside PageView
- Navigation via `"navigate": "pageId"` on Button blocks
- Final submit uses `"actionId"` connecting to `actions`

---

## Pattern 3: Dashboard with Stats

```genui
{
  "widgetId": "dashboard",
  "widgetType": "composition",
  "initialState": {},
  "trackedFields": [],
  "actions": [
    { "id": "refresh", "label": "Refresh", "style": "secondary", "tracking": "reply" }
  ],
  "children": [
    { "type": "Stack", "props": { "gap": "lg" }, "children": [
      { "type": "Grid", "props": { "columns": 3, "gap": "md" }, "children": [
        { "type": "Stat", "props": { "label": "Revenue", "value": "$12.4k", "change": "+8%", "trend": "up" } },
        { "type": "Stat", "props": { "label": "Orders", "value": "142", "trend": "up" } },
        { "type": "Stat", "props": { "label": "Returns", "value": "3", "trend": "down" } }
      ]},
      { "type": "DataTable", "props": {
        "columns": [
          { "key": "product", "label": "Product" },
          { "key": "revenue", "label": "Revenue", "format": "currency" }
        ],
        "rows": [
          { "product": "Widget A", "revenue": 4250 },
          { "product": "Widget B", "revenue": 8550 }
        ]
      }},
      { "type": "Button", "props": { "label": "Refresh", "style": "secondary", "actionId": "refresh" } }
    ]}
  ]
}
```

---

## Pattern 4: Tabbed Settings

```genui
{
  "widgetId": "settings",
  "widgetType": "composition",
  "initialState": { "displayName": "", "theme": "dark", "notifications": true },
  "trackedFields": [
    { "key": "displayName", "tracking": "context" },
    { "key": "theme", "tracking": "context" },
    { "key": "notifications", "tracking": "context" }
  ],
  "actions": [
    { "id": "save", "label": "Save", "style": "primary", "tracking": "reply" }
  ],
  "children": [
    { "type": "Card", "props": { "title": "Settings" }, "children": [
      { "type": "Tabs", "children": [
        { "type": "Stack", "props": { "label": "Profile", "gap": "md", "padding": "md" }, "children": [
          { "type": "Input", "props": { "label": "Display Name" }, "bind": "displayName" }
        ]},
        { "type": "Stack", "props": { "label": "Preferences", "gap": "md", "padding": "md" }, "children": [
          { "type": "Select", "props": { "label": "Theme", "options": [
            { "label": "Dark", "value": "dark" },
            { "label": "Light", "value": "light" }
          ]}, "bind": "theme" },
          { "type": "Checkbox", "props": { "label": "Enable notifications" }, "bind": "notifications" }
        ]}
      ]},
      { "type": "Button", "props": { "label": "Save", "style": "primary", "actionId": "save" } }
    ]}
  ]
}
```

---

## Pattern 5: Confirmation Dialog

```genui
{
  "widgetId": "delete-confirm",
  "widgetType": "composition",
  "initialState": {},
  "trackedFields": [],
  "actions": [
    { "id": "confirm", "label": "Confirm", "style": "danger", "tracking": "reply" },
    { "id": "cancel", "label": "Cancel", "style": "ghost", "tracking": "reply" }
  ],
  "children": [
    { "type": "Card", "props": { "variant": "outlined" }, "children": [
      { "type": "Stack", "props": { "gap": "md" }, "children": [
        { "type": "Alert", "props": { "message": "This action cannot be undone.", "variant": "warning" } },
        { "type": "Text", "props": { "content": "Are you sure you want to delete these items?" } },
        { "type": "Stack", "props": { "direction": "horizontal", "justify": "end", "gap": "sm" }, "children": [
          { "type": "Button", "props": { "label": "Cancel", "style": "ghost", "actionId": "cancel" } },
          { "type": "Button", "props": { "label": "Delete", "style": "danger", "actionId": "confirm" } }
        ]}
      ]}
    ]}
  ]
}
```

---

## Design Guidelines

- **One purpose per widget** — don't mix unrelated forms
- Use `Card` for visual grouping, `Stack` for flow, `Grid` for side-by-side
- Always provide `initialState` (use `{}` for read-only) and `trackedFields` (use `[]`)
- Choose descriptive `widgetId` values (e.g., `"order-review-42"`)
