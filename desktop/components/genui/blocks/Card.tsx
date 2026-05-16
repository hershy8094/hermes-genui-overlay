/**
 * Card — Bordered container with optional header and collapse.
 *
 * Props:
 *   title?: string
 *   subtitle?: string
 *   variant?: "default" | "outlined" | "elevated" | "ghost" (default: "default")
 *   collapsible?: boolean (default: false)
 *   defaultCollapsed?: boolean (default: false)
 */

import { useState } from "react";
import type { BlockProps } from "../blockRegistry";

export default function Card({ props, children }: BlockProps): React.JSX.Element {
  const title = props.title as string | undefined;
  const subtitle = props.subtitle as string | undefined;
  const variant = (props.variant as string) ?? "default";
  const collapsible = Boolean(props.collapsible);
  const [collapsed, setCollapsed] = useState(Boolean(props.defaultCollapsed));

  const hasHeader = Boolean(title || subtitle);

  return (
    <div className={`genui-block-card genui-block-card-${variant}`}>
      {hasHeader && (
        <div
          className="genui-block-card-header"
          onClick={collapsible ? () => setCollapsed((c) => !c) : undefined}
          style={collapsible ? { cursor: "pointer" } : undefined}
        >
          <div className="genui-block-card-header-text">
            {title && <div className="genui-block-card-title">{title}</div>}
            {subtitle && <div className="genui-block-card-subtitle">{subtitle}</div>}
          </div>
          {collapsible && (
            <span className={`genui-block-card-chevron ${collapsed ? "collapsed" : ""}`}>
              ▾
            </span>
          )}
        </div>
      )}
      {!collapsed && (
        <div className="genui-block-card-body">{children}</div>
      )}
    </div>
  );
}
