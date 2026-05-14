/**
 * GenUI Protocol — Shared Type Definitions
 *
 * Defines the wire format for the bidirectional GenUI state-sync loop
 * between the Hermes agent (Python backend) and the desktop renderer.
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
}

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
