/**
 * Alert — Alert/notification banner block.
 *
 * Props:
 *   message: string (required)
 *   variant?: "info" | "success" | "warning" | "error" (default: "info")
 *   dismissible?: boolean (default: false)
 */

import { useState } from "react";
import type { BlockProps } from "../blockRegistry";

const VARIANT_STYLES: Record<string, { bg: string; border: string; text: string; icon: string }> = {
  info:    { bg: "rgba(59,130,246,0.08)",  border: "rgba(59,130,246,0.2)",  text: "#3b82f6", icon: "ℹ" },
  success: { bg: "rgba(34,197,94,0.08)",   border: "rgba(34,197,94,0.2)",   text: "#22c55e", icon: "✓" },
  warning: { bg: "rgba(234,179,8,0.08)",   border: "rgba(234,179,8,0.2)",   text: "#eab308", icon: "⚠" },
  error:   { bg: "rgba(239,68,68,0.08)",   border: "rgba(239,68,68,0.2)",   text: "#ef4444", icon: "✕" },
};

export default function Alert({ props }: BlockProps): React.JSX.Element {
  const message = (props.message as string) ?? "";
  const variant = (props.variant as string) ?? "info";
  const dismissible = Boolean(props.dismissible);
  const [dismissed, setDismissed] = useState(false);

  if (dismissed) return <></>;

  const styles = VARIANT_STYLES[variant] ?? VARIANT_STYLES.info;

  return (
    <div
      className={`genui-block-alert genui-block-alert-${variant}`}
      style={{
        backgroundColor: styles.bg,
        border: `1px solid ${styles.border}`,
      }}
    >
      <span className="genui-block-alert-icon" style={{ color: styles.text }}>
        {styles.icon}
      </span>
      <span className="genui-block-alert-message">{message}</span>
      {dismissible && (
        <button
          className="genui-block-alert-dismiss"
          onClick={() => setDismissed(true)}
          aria-label="Dismiss"
        >
          ×
        </button>
      )}
    </div>
  );
}
