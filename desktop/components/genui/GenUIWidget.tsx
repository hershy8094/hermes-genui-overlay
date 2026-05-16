/**
 * GenUIWidget — In-thread widget renderer with 4-tier state tracking.
 *
 * This wrapper is rendered inside MessageRow for agent messages that
 * carry a widget payload. It:
 * - Routes to BlockRenderer for v2 composable trees (payload.children)
 * - Falls back to legacy widget registry for v1 flat widgets (payload.widgetType)
 * - Manages local widget state
 * - Routes state changes through the 4-tier tracking system
 * - Handles multi-page navigation for PageView blocks
 */

import { useState, useCallback, useRef, useMemo } from "react";
import { getWidget } from "./registry";
import BlockRenderer from "./BlockRenderer";
import type {
  GenUIRenderPayload,
  GenUIStateField,
  WidgetState,
  TrackingLevel,
} from "../../../../shared/genui-types";

// Ensure all built-in widgets are registered (legacy)
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
  const [currentPage, setCurrentPage] = useState<string>(
    payload.initialPage ?? "",
  );
  const wrapperRef = useRef<HTMLDivElement>(null);

  // Determine if this is a v2 composable widget
  const isComposable = Boolean(payload.children && payload.children.length > 0);

  // Resolve the legacy widget component (only for v1 path)
  const WidgetComponent = useMemo(() => {
    if (isComposable) return null;
    return getWidget(payload.widgetType) ?? getWidget("__generic__");
  }, [payload.widgetType, isComposable]);

  // Look up tracking level for a given field
  const getFieldTracking = useCallback(
    (field: string): TrackingLevel => {
      const tracked = payload.trackedFields.find((f: GenUIStateField) => f.key === field);
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

      const action = payload.actions.find((a: { id: string }) => a.id === actionId);
      const tracking: TrackingLevel = action?.tracking ?? "ignored";
      if (tracking === "ignored") return;

      const snapshot = getTrackedSnapshot(payload.trackedFields, newState);
      onDispatch(payload.widgetId, undefined, actionId, snapshot, tracking);
    },
    [payload.actions, payload.trackedFields, payload.widgetId, onDispatch],
  );

  // Handle page navigation (for v2 PageView blocks)
  const handleNavigate = useCallback(
    (pageId: string) => {
      setCurrentPage(pageId);
    },
    [],
  );

  // --- v2 Composable Rendering Path ---
  if (isComposable) {
    return (
      <div
        ref={wrapperRef}
        className="genui-widget-wrapper"
        data-widget-id={payload.widgetId}
        data-current-page={currentPage || undefined}
      >
        <div className="genui-widget">
          <BlockRenderer
            nodes={payload.children!}
            state={{ ...state, __currentPage: currentPage }}
            onStateChange={handleStateChange}
            onAction={(actionId) => handleAction(actionId, state)}
            onNavigate={handleNavigate}
          />
        </div>
      </div>
    );
  }

  // --- v1 Legacy Rendering Path ---
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
      className="genui-widget-wrapper"
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
