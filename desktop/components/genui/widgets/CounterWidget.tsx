/**
 * CounterWidget — Proof-of-concept GenUI widget.
 *
 * Demonstrates the 4-tier state tracking model with a simple counter:
 * - `count` field: tracked at whatever level the agent declares
 * - increment/decrement: context-level actions
 * - "Submit" action: reply-level trigger
 */

import type { GenUIWidgetProps } from "../registry";

export default function CounterWidget({
  state,
  actions,
  meta,
  onStateChange,
  onAction,
}: GenUIWidgetProps): React.JSX.Element {
  const count = (state.count as number) ?? 0;
  const label = (meta?.label as string) ?? "Counter";

  return (
    <div className="genui-counter">
      <div className="genui-counter-label">{label}</div>
      <div className="genui-counter-controls">
        <button
          className="genui-counter-btn"
          onClick={() => onStateChange("count", count - 1)}
        >
          −
        </button>
        <span className="genui-counter-value">{count}</span>
        <button
          className="genui-counter-btn"
          onClick={() => onStateChange("count", count + 1)}
        >
          +
        </button>
      </div>
      {actions.length > 0 && (
        <div className="genui-widget-actions">
          {actions.map((action) => (
            <button
              key={action.id}
              className={`genui-action-btn genui-action-${action.style}`}
              data-tracking={action.tracking}
              onClick={() => onAction(action.id, { ...state, count })}
            >
              {action.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
