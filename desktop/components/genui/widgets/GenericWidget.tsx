/**
 * GenericWidget — Fallback renderer for unknown widget types.
 *
 * Displays the widget state as formatted key-value pairs with the
 * agent-defined action buttons. Ensures every widget type the agent
 * sends is renderable even without a dedicated component.
 */

import type { GenUIWidgetProps } from "../registry";

export default function GenericWidget({
  widgetId,
  state,
  actions,
  meta,
  onAction,
}: GenUIWidgetProps): React.JSX.Element {
  const title = (meta?.title as string) ?? (meta?.label as string) ?? widgetId;
  const description = meta?.description as string | undefined;

  return (
    <div className="genui-generic">
      <div className="genui-generic-header">
        <span className="genui-generic-title">{title}</span>
      </div>
      {description && (
        <div className="genui-generic-description">{description}</div>
      )}
      <div className="genui-generic-state">
        {Object.entries(state).map(([key, value]) => (
          <div key={key} className="genui-generic-field">
            <span className="genui-generic-key">{key}</span>
            <span className="genui-generic-value">
              {typeof value === "object"
                ? JSON.stringify(value, null, 2)
                : String(value)}
            </span>
          </div>
        ))}
      </div>
      {actions.length > 0 && (
        <div className="genui-widget-actions">
          {actions.map((action) => (
            <button
              key={action.id}
              className={`genui-action-btn genui-action-${action.style}`}
              data-tracking={action.tracking}
              onClick={() => onAction(action.id, state)}
            >
              {action.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
