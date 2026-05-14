/**
 * GenUIWidget — In-thread widget renderer with 4-tier state tracking.
 *
 * This wrapper is rendered inside MessageRow for agent messages that
 * carry a widget payload. It:
 * - Resolves the widget component from the registry
 * - Manages local widget state
 * - Routes state changes through the 4-tier tracking system
 * - Applies magnetic viewport sticking when active
 */

import { useState, useCallback, useRef, useMemo } from "react";
import { getWidget } from "./registry";
import type {
  GenUIRenderPayload,
  GenUIStateField,
  WidgetState,
  TrackingLevel,
} from "../../../../shared/genui-types";

// Ensure all built-in widgets are registered
import "./widgets";

export interface GenUIWidgetContainerProps {
  payload: GenUIRenderPayload;
  isLatest: boolean;
  onDispatch: (
    widgetId: string,
    field: string | undefined,
    actionId: string | undefined,
    state: WidgetState,
    tracking: TrackingLevel,
  ) => void;
}

/** Extract only the fields the agent cares about from full state. */
function getTrackedSnapshot(
  trackedFields: GenUIStateField[],
  fullState: WidgetState,
): WidgetState {
  const snap: WidgetState = {};
  for (const f of trackedFields) {
    if (f.tracking !== "ignored" && f.key in fullState) {
      snap[f.key] = fullState[f.key];
    }
  }
  return snap;
}

export default function GenUIWidgetContainer({
  payload,
  isLatest,
  onDispatch,
}: GenUIWidgetContainerProps): React.JSX.Element {
  const [state, setState] = useState<WidgetState>(payload.initialState);
  const wrapperRef = useRef<HTMLDivElement>(null);

  // Resolve the widget component
  const WidgetComponent = useMemo(() => {
    return getWidget(payload.widgetType) ?? getWidget("__generic__");
  }, [payload.widgetType]);

  // Look up tracking level for a given field
  const getFieldTracking = useCallback(
    (field: string): TrackingLevel => {
      const tracked = payload.trackedFields.find((f) => f.key === field);
      return tracked?.tracking ?? "ignored";
    },
    [payload.trackedFields],
  );

  // Handle state field changes — route through 4-tier tracking
  const handleStateChange = useCallback(
    (field: string, value: unknown) => {
      const newState = { ...state, [field]: value };
      setState(newState);

      const tracking = getFieldTracking(field);
      if (tracking === "ignored") return;

      const snapshot = getTrackedSnapshot(payload.trackedFields, newState);
      onDispatch(payload.widgetId, field, undefined, snapshot, tracking);
    },
    [state, getFieldTracking, payload.trackedFields, payload.widgetId, onDispatch],
  );

  // Handle action button clicks
  const handleAction = useCallback(
    (actionId: string, newState: WidgetState) => {
      setState(newState);

      const action = payload.actions.find((a) => a.id === actionId);
      const tracking: TrackingLevel = action?.tracking ?? "ignored";
      if (tracking === "ignored") return;

      const snapshot = getTrackedSnapshot(payload.trackedFields, newState);
      onDispatch(payload.widgetId, undefined, actionId, snapshot, tracking);
    },
    [payload.actions, payload.trackedFields, payload.widgetId, onDispatch],
  );

  if (!WidgetComponent) {
    return (
      <div className="genui-widget-error">
        Unknown widget type: {payload.widgetType}
      </div>
    );
  }

  return (
    <div
      ref={wrapperRef}
      className={`genui-widget-wrapper ${isLatest ? "genui-widget--sticky" : "genui-widget--settled"}`}
    >
      <div className="genui-widget">
        <WidgetComponent
          widgetId={payload.widgetId}
          state={state}
          trackedFields={payload.trackedFields}
          actions={payload.actions}
          meta={payload.meta}
          onStateChange={handleStateChange}
          onAction={handleAction}
        />
      </div>
    </div>
  );
}
