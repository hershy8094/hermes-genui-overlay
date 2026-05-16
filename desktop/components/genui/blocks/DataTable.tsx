/**
 * DataTable — Tabular data display block.
 *
 * Props:
 *   columns: Array<{ key: string; label: string; format?: "currency" | "number" | "date" }>
 *   rows?: Array<Record<string, unknown>> — static rows (or use bind)
 *   striped?: boolean (default: true)
 *   compact?: boolean (default: false)
 *
 * If node.bind is set, reads rows from state[bind] (must be an array).
 */

import type { BlockProps } from "../blockRegistry";

interface Column {
  key: string;
  label: string;
  format?: string;
}

function formatCell(value: unknown, format?: string): string {
  if (value == null) return "—";
  if (format === "currency") return `$${Number(value).toFixed(2)}`;
  if (format === "number") return Number(value).toLocaleString();
  return String(value);
}

export default function DataTable({ node, props, state }: BlockProps): React.JSX.Element {
  const columns = (props.columns as Column[]) ?? [];
  const striped = props.striped !== false;
  const compact = Boolean(props.compact);

  // Rows from bind or props
  let rows: Array<Record<string, unknown>> = [];
  if (node.bind && Array.isArray(state[node.bind])) {
    rows = state[node.bind] as Array<Record<string, unknown>>;
  } else if (Array.isArray(props.rows)) {
    rows = props.rows as Array<Record<string, unknown>>;
  }

  return (
    <div className={`genui-block-datatable ${compact ? "compact" : ""}`}>
      <table className="genui-block-datatable-table">
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col.key} className="genui-block-datatable-th">
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, ri) => (
            <tr
              key={ri}
              className={`genui-block-datatable-tr ${striped && ri % 2 === 1 ? "striped" : ""}`}
            >
              {columns.map((col) => (
                <td key={col.key} className="genui-block-datatable-td">
                  {formatCell(row[col.key], col.format)}
                </td>
              ))}
            </tr>
          ))}
          {rows.length === 0 && (
            <tr>
              <td
                colSpan={columns.length}
                className="genui-block-datatable-empty"
              >
                No data
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
