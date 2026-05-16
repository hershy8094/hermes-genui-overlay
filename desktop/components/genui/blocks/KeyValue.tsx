/**
 * KeyValue — Key-value pairs display block.
 *
 * Props:
 *   entries?: Array<{ key: string; value: string | number }> — static entries
 *
 * Also reads from `bind` — if node.bind is set, reads an object from state
 * and displays its entries as key-value pairs.
 */

import type { BlockProps } from "../blockRegistry";

export default function KeyValue({ node, props, state }: BlockProps): React.JSX.Element {
  let entries: Array<{ key: string; value: unknown }> = [];

  // Static entries from props
  if (Array.isArray(props.entries)) {
    entries = props.entries as Array<{ key: string; value: unknown }>;
  }
  // Bound entries from state
  else if (node.bind && state[node.bind]) {
    const obj = state[node.bind] as Record<string, unknown>;
    entries = Object.entries(obj).map(([key, value]) => ({ key, value }));
  }

  return (
    <div className="genui-block-keyvalue">
      {entries.map((entry, i) => (
        <div key={i} className="genui-block-keyvalue-row">
          <span className="genui-block-keyvalue-key">{entry.key}</span>
          <span className="genui-block-keyvalue-value">
            {typeof entry.value === "object"
              ? JSON.stringify(entry.value)
              : String(entry.value ?? "")}
          </span>
        </div>
      ))}
    </div>
  );
}
