/**
 * GenUI Protocol — Shared Type Definitions
 *
 * Defines the wire format for the bidirectional GenUI state-sync loop
 * between the Hermes agent (Python backend) and the desktop renderer.
 *
 * v2: Adds composable component trees via GenUINode and multi-page support.
 */

export type WidgetId = string;
export type WidgetState = Record<string, unknown>;

/**
 * 4-tier tracking model — determines what the frontend does
 * when a state field or action changes.
 *
 *  0. ignored  — Pure UI control (hover, focus, animation). Never leaves the widget.
 *  1. context  — Silently merged into background context the agent sees on its next turn.
 *  2. explicit — Attached explicitly as structured data in the next outbound message.
 *  3. reply    — Triggers an immediate full agent reply cycle on change.
 */
export type TrackingLevel = "ignored" | "context" | "explicit" | "reply";

/** Agent-declared interest in a specific state field. */
export interface GenUIStateField {
  key: string;
  tracking: TrackingLevel;
  /** Human-readable label for the agent's benefit (optional). */
  label?: string;
}

/** A clickable action within a widget. */
export interface GenUIAction {
  id: string;
  label: string;
  style: "primary" | "secondary" | "danger" | "ghost";
  /** What tier this action operates at when fired. */
  tracking: TrackingLevel;
  /** Optional payload sent back with the action. */
  value?: unknown;
}

// ---------------------------------------------------------------------------
// v2: Composable Component Tree
// ---------------------------------------------------------------------------

/**
 * A single node in the GenUI component tree.
 *
 * Nodes can be layout containers (Stack, Grid, Card, PageView), content
 * elements (Text, Badge, Image, Stat), interactive controls (Button, Input,
 * Select), or data displays (DataTable, List). They nest arbitrarily via
 * the `children` array, enabling Shopify-like block composition.
 */
export interface GenUINode {
  /** Block type: "Stack", "Card", "Text", "Button", "Input", etc. */
  type: string;
  /** Unique key for this node (optional, auto-generated if missing). */
  key?: string;
  /** Props passed to this block (type-specific). */
  props?: Record<string, unknown>;
  /** Nested children — enables composition. */
  children?: GenUINode[];
  /** Bind this node to a widget state field (for inputs, selects, etc.). */
  bind?: string;
  /** Tracking level for this specific node's interactions. */
  tracking?: TrackingLevel;
  /** Navigate to a page when this node is activated (for Button). */
  navigate?: string;
  /** Custom inline style overrides (design token keys or CSS properties). */
  style?: Record<string, string>;
}

// ---------------------------------------------------------------------------
// Render Payload (v1 flat + v2 composable)
// ---------------------------------------------------------------------------

/** Payload for a `hermes.genui.render` SSE event. */
export interface GenUIRenderPayload {
  widgetId: WidgetId;
  widgetType: string;
  initialState: WidgetState;
  /** Agent-declared interest levels per state field. */
  trackedFields: GenUIStateField[];
  actions: GenUIAction[];
  /** Agent-provided metadata (labels, descriptions, etc.). */
  meta?: Record<string, unknown>;

  // --- v2 fields ---

  /** Component tree — if present, uses BlockRenderer instead of legacy widgetType registry. */
  children?: GenUINode[];
  /** Template ID this was instantiated from (for agent reference). */
  templateId?: string;
  /** Initial page to show (for multi-page widgets). Defaults to first Page child. */
  initialPage?: string;
}

// ---------------------------------------------------------------------------
// State Updates (unchanged from v1)
// ---------------------------------------------------------------------------

/** A single state update record, tagged with its tracking level. */
export interface GenUIStateUpdate {
  widgetId: WidgetId;
  widgetType: string;
  /** State field that changed (for field-level updates). */
  field?: string;
  /** Action that was fired (for action-level updates). */
  actionId?: string;
  /** Snapshot of tracked state (excludes `ignored` fields). */
  state: WidgetState;
  tracking: TrackingLevel;
  timestamp: number;
}

/** Payload sent as `[genui:reply]` when a tier-3 action fires. */
export interface GenUIReplyPayload {
  trigger: {
    widgetId: WidgetId;
    widgetType: string;
    field?: string;
    actionId?: string;
    state: WidgetState;
  };
  backgroundContext: Record<string, WidgetState>;
  explicitUpdates: GenUIStateUpdate[];
}
