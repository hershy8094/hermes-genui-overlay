/**
 * RadioGroup — Radio button group block.
 *
 * Props:
 *   options: Array<{ label: string; value: string }> (required)
 *   label?: string — group label
 *
 * Bound via node.bind — reads/writes the selected value string.
 */

import type { BlockProps } from "../blockRegistry";

interface RadioOption {
  label: string;
  value: string;
}

export default function RadioGroup({ node, props, state, onStateChange }: BlockProps): React.JSX.Element {
  const options = (props.options as RadioOption[]) ?? [];
  const label = props.label as string | undefined;
  const field = node.bind ?? "";
  const value = field ? (state[field] as string) ?? "" : "";

  const handleChange = (optValue: string) => {
    if (!field) return;
    onStateChange(field, optValue);
  };

  const groupName = `radio-${field}-${Math.random().toString(36).slice(2, 8)}`;

  return (
    <div className="genui-block-radiogroup">
      {label && <div className="genui-block-radiogroup-label">{label}</div>}
      <div className="genui-block-radiogroup-options">
        {options.map((opt) => (
          <label key={opt.value} className="genui-block-radiogroup-option">
            <input
              type="radio"
              name={groupName}
              value={opt.value}
              checked={value === opt.value}
              onChange={() => handleChange(opt.value)}
              className="genui-block-radiogroup-input"
            />
            <span className="genui-block-radiogroup-text">{opt.label}</span>
          </label>
        ))}
      </div>
    </div>
  );
}
