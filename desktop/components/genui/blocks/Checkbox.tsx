/**
 * Checkbox — Boolean toggle block.
 *
 * Props:
 *   label: string (required)
 *
 * Bound via node.bind — reads/writes boolean.
 */

import type { BlockProps } from "../blockRegistry";

export default function Checkbox({ node, props, state, onStateChange }: BlockProps): React.JSX.Element {
  const label = (props.label as string) ?? "";
  const field = node.bind ?? "";
  const checked = field ? Boolean(state[field]) : false;

  const handleChange = () => {
    if (!field) return;
    onStateChange(field, !checked);
  };

  return (
    <label className="genui-block-checkbox">
      <input
        type="checkbox"
        checked={checked}
        onChange={handleChange}
        className="genui-block-checkbox-input"
      />
      <span className="genui-block-checkbox-label">{label}</span>
    </label>
  );
}
