/**
 * Button — Action button block.
 *
 * Props:
 *   label: string (required)
 *   style?: "primary" | "secondary" | "danger" | "ghost" (default: "primary")
 *   actionId?: string — fires onAction when clicked
 *   disabled?: boolean
 *   loading?: boolean
 *
 * Also reads node.navigate — if set, fires onNavigate for PageView routing.
 */

import type { BlockProps } from "../blockRegistry";

export default function Button({ node, props, state, onAction, onNavigate }: BlockProps): React.JSX.Element {
  const label = (props.label as string) ?? "Button";
  const style = (props.style as string) ?? "primary";
  const actionId = props.actionId as string | undefined;
  const disabled = Boolean(props.disabled);
  const loading = Boolean(props.loading);

  const handleClick = () => {
    if (disabled || loading) return;

    // Navigation takes priority
    if (node.navigate) {
      onNavigate(node.navigate);
    }

    // Fire action if set
    if (actionId) {
      onAction(actionId, state);
    }
  };

  return (
    <button
      className={`genui-action-btn genui-action-${style}`}
      onClick={handleClick}
      disabled={disabled || loading}
    >
      {loading && <span className="genui-block-button-spinner" />}
      {label}
    </button>
  );
}
