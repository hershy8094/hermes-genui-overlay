/**
 * PageView — Multi-page container that shows only the active page.
 *
 * Children must be Page blocks. The active page is determined by the
 * `__currentPage` state field injected by GenUIWidget. If no page
 * matches, defaults to the first Page child.
 *
 * Navigation between pages is done via Button blocks with `navigate` prop.
 */

import { Children, isValidElement, useMemo } from "react";
import type { BlockProps } from "../blockRegistry";

export default function PageView({ state, children }: BlockProps): React.JSX.Element {
  const currentPage = state.__currentPage as string | undefined;

  // Collect page info for the tab/breadcrumb bar
  const childArray = Children.toArray(children).filter(isValidElement);

  // Find the active page
  const activePage = useMemo(() => {
    if (!currentPage) return childArray[0] ?? null;

    // Find the child whose underlying Page block has a matching pageId
    const found = childArray.find((child) => {
      const el = child as React.ReactElement<{ "data-page-id"?: string }>;
      return el.props?.["data-page-id"] === currentPage;
    });
    return found ?? childArray[0] ?? null;
  }, [currentPage, childArray]);

  // Build page indicator dots
  const pageIds = childArray.map((child) => {
    const el = child as React.ReactElement<{ "data-page-id"?: string; "data-page-title"?: string }>;
    return {
      id: el.props?.["data-page-id"] ?? "",
      title: el.props?.["data-page-title"] ?? "",
    };
  });

  const activeId = currentPage || pageIds[0]?.id || "";

  return (
    <div className="genui-block-pageview">
      {pageIds.length > 1 && (
        <div className="genui-block-pageview-indicators">
          {pageIds.map((p) => (
            <span
              key={p.id}
              className={`genui-block-pageview-dot ${p.id === activeId ? "active" : ""}`}
              title={p.title || p.id}
            />
          ))}
        </div>
      )}
      <div className="genui-block-pageview-content">
        {activePage}
      </div>
    </div>
  );
}
