/**
 * Input — Text input block.
 *
 * Props:
 *   placeholder?: string
 *   type?: "text" | "number" | "email" | "password" (default: "text")
 *   label?: string
 *
 * Bound via node.bind — reads/writes to a state field.
 */

import type { BlockProps } from "../blockRegistry";

export default function Input({ node, props, state, onStateChange }: BlockProps): React.JSX.Element {
  const placeholder = (props.placeholder as string) ?? "";
  const type = (props.type as string) ?? "text";
  const label = props.label as string | undefined;
  const field = node.bind ?? "";
  const value = field ? (state[field] as string) ?? "" : "";

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!field) return;
    const val = type === "number" ? Number(e.target.value) : e.target.value;
    onStateChange(field, val);
  };

  return (
    <div className="genui-block-input-wrapper">
      {label && <label className="genui-block-input-label">{label}</label>}
      <input
        className="genui-block-input"
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={handleChange}
      />
    </div>
  );
}
