/**
 * Select — Dropdown select block.
 *
 * Props:
 *   options: Array<{ label: string; value: string }> (required)
 *   placeholder?: string
 *   label?: string
 *
 * Bound via node.bind.
 */

import type { BlockProps } from "../blockRegistry";

interface SelectOption {
  label: string;
  value: string;
}

export default function Select({ node, props, state, onStateChange }: BlockProps): React.JSX.Element {
  const options = (props.options as SelectOption[]) ?? [];
  const placeholder = (props.placeholder as string) ?? "Select...";
  const label = props.label as string | undefined;
  const field = node.bind ?? "";
  const value = field ? (state[field] as string) ?? "" : "";

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    if (!field) return;
    onStateChange(field, e.target.value);
  };

  return (
    <div className="genui-block-select-wrapper">
      {label && <label className="genui-block-select-label">{label}</label>}
      <select
        className="genui-block-select"
        value={value}
        onChange={handleChange}
      >
        {!value && <option value="" disabled>{placeholder}</option>}
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}
