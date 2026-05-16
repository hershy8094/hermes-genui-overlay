/**
 * List — Ordered/unordered list display block.
 *
 * Props:
 *   items?: string[] — static items (or use bind for dynamic)
 *   ordered?: boolean (default: false)
 *   variant?: "bullet" | "numbered" | "none" (default: "bullet")
 *
 * If node.bind is set, reads items from state[bind] (must be string[]).
 */

import type { BlockProps } from "../blockRegistry";

export default function List({ node, props, state }: BlockProps): React.JSX.Element {
  const ordered = Boolean(props.ordered);
  const variant = (props.variant as string) ?? "bullet";

  let items: string[] = [];
  if (node.bind && Array.isArray(state[node.bind])) {
    items = (state[node.bind] as unknown[]).map(String);
  } else if (Array.isArray(props.items)) {
    items = (props.items as unknown[]).map(String);
  }

  const Tag = ordered ? "ol" : "ul";

  return (
    <Tag className={`genui-block-list genui-block-list-${variant}`}>
      {items.map((item, i) => (
        <li key={i} className="genui-block-list-item">
          {item}
        </li>
      ))}
    </Tag>
  );
}
