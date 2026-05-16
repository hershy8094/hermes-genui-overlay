/**
 * TextArea — Multi-line text input block.
 *
 * Props:
 *   placeholder?: string
 *   rows?: number (default: 3)
 *   label?: string
 *
 * Bound via node.bind — reads/writes string.
 */

import type { BlockProps } from "../blockRegistry";

export default function TextArea({ node, props, state, onStateChange }: BlockProps): React.JSX.Element {
  const placeholder = (props.placeholder as string) ?? "";
  const rows = (props.rows as number) ?? 3;
  const label = props.label as string | undefined;
  const field = node.bind ?? "";
  const value = field ? (state[field] as string) ?? "" : "";

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    if (!field) return;
    onStateChange(field, e.target.value);
  };

  return (
    <div className="genui-block-textarea-wrapper">
      {label && <label className="genui-block-textarea-label">{label}</label>}
      <textarea
        className="genui-block-textarea"
        placeholder={placeholder}
        rows={rows}
        value={value}
        onChange={handleChange}
      />
    </div>
  );
}
