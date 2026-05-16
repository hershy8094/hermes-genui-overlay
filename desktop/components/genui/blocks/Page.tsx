/**
 * Page — A single page within a PageView container.
 *
 * Props:
 *   pageId: string (required — unique identifier for navigation)
 *   title?: string — display title for page indicators
 */

import type { BlockProps } from "../blockRegistry";

export default function Page({ props, children }: BlockProps): React.JSX.Element {
  const pageId = (props.pageId as string) ?? "";
  const title = (props.title as string) ?? pageId;

  return (
    <div
      className="genui-block-page"
      data-page-id={pageId}
      data-page-title={title}
    >
      {children}
    </div>
  );
}
