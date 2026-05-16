/**
 * Slider — Range slider block.
 *
 * Props:
 *   min?: number (default: 0)
 *   max?: number (default: 100)
 *   step?: number (default: 1)
 *   label?: string
 *   showValue?: boolean (default: true)
 *
 * Bound via node.bind — reads/writes a numeric value.
 */

import type { BlockProps } from "../blockRegistry";

export default function Slider({ node, props, state, onStateChange }: BlockProps): React.JSX.Element {
  const min = (props.min as number) ?? 0;
  const max = (props.max as number) ?? 100;
  const step = (props.step as number) ?? 1;
  const label = props.label as string | undefined;
  const showValue = props.showValue !== false;
  const field = node.bind ?? "";
  const value = field ? (state[field] as number) ?? min : min;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!field) return;
    onStateChange(field, Number(e.target.value));
  };

  return (
    <div className="genui-block-slider-wrapper">
      {(label || showValue) && (
        <div className="genui-block-slider-header">
          {label && <span className="genui-block-slider-label">{label}</span>}
          {showValue && <span className="genui-block-slider-value">{value}</span>}
        </div>
      )}
      <input
        className="genui-block-slider"
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={handleChange}
      />
    </div>
  );
}
