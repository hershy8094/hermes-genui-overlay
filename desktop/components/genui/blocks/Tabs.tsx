/**
 * Tabs — Tabbed container where each child is a tab pane.
 *
 * Each child should have props.label to display in the tab bar.
 * If no label is found, "Tab N" is used.
 *
 * Props:
 *   defaultTab?: number — index of the initially active tab (default: 0)
 */

import { useState, Children, isValidElement } from "react";
import type { BlockProps } from "../blockRegistry";

export default function Tabs({ props, children }: BlockProps): React.JSX.Element {
  const defaultTab = (props.defaultTab as number) ?? 0;
  const [activeTab, setActiveTab] = useState(defaultTab);

  const childArray = Children.toArray(children).filter(isValidElement);

  // Extract tab labels from children's wrapper data attributes
  const tabLabels = childArray.map((child, i) => {
    const el = child as React.ReactElement<{ "data-tab-label"?: string }>;
    return el.props?.["data-tab-label"] ?? `Tab ${i + 1}`;
  });

  return (
    <div className="genui-block-tabs">
      <div className="genui-block-tabs-bar" role="tablist">
        {tabLabels.map((label, i) => (
          <button
            key={i}
            role="tab"
            aria-selected={i === activeTab}
            className={`genui-block-tabs-tab ${i === activeTab ? "active" : ""}`}
            onClick={() => setActiveTab(i)}
          >
            {label}
          </button>
        ))}
      </div>
      <div className="genui-block-tabs-content" role="tabpanel">
        {childArray[activeTab] ?? null}
      </div>
    </div>
  );
}
