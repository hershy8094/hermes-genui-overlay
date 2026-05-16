/**
 * Accordion — Collapsible section container.
 *
 * Each child becomes a collapsible section. The child's node should
 * have props.label for the section header.
 *
 * Props:
 *   allowMultiple?: boolean — allow multiple sections open at once (default: false)
 */

import { useState, Children, isValidElement } from "react";
import type { BlockProps } from "../blockRegistry";

export default function Accordion({ props, children }: BlockProps): React.JSX.Element {
  const allowMultiple = Boolean(props.allowMultiple);
  const childArray = Children.toArray(children).filter(isValidElement);
  const [openSections, setOpenSections] = useState<Set<number>>(new Set([0]));

  const toggle = (index: number) => {
    setOpenSections((prev) => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        if (!allowMultiple) next.clear();
        next.add(index);
      }
      return next;
    });
  };

  return (
    <div className="genui-block-accordion">
      {childArray.map((child, i) => {
        const el = child as React.ReactElement<{ "data-accordion-label"?: string }>;
        const label = el.props?.["data-accordion-label"] ?? `Section ${i + 1}`;
        const isOpen = openSections.has(i);

        return (
          <div key={i} className={`genui-block-accordion-item ${isOpen ? "open" : ""}`}>
            <button
              className="genui-block-accordion-header"
              onClick={() => toggle(i)}
              aria-expanded={isOpen}
            >
              <span className="genui-block-accordion-label">{label}</span>
              <span className={`genui-block-accordion-chevron ${isOpen ? "open" : ""}`}>▾</span>
            </button>
            {isOpen && (
              <div className="genui-block-accordion-body">{child}</div>
            )}
          </div>
        );
      })}
    </div>
  );
}
