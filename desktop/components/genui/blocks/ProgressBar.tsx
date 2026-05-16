/**
 * ProgressBar — Progress indicator block.
 *
 * Props:
 *   value: number (required, 0-max)
 *   max?: number (default: 100)
 *   label?: string
 *   color?: string — CSS color or preset name
 *   showValue?: boolean (default: true)
 */

import type { BlockProps } from "../blockRegistry";

export default function ProgressBar({ props }: BlockProps): React.JSX.Element {
  const value = (props.value as number) ?? 0;
  const max = (props.max as number) ?? 100;
  const label = props.label as string | undefined;
  const color = (props.color as string) ?? "var(--accent, #003f7a)";
  const showValue = props.showValue !== false;

  const pct = Math.min(100, Math.max(0, (value / max) * 100));

  return (
    <div className="genui-block-progress">
      {(label || showValue) && (
        <div className="genui-block-progress-header">
          {label && <span className="genui-block-progress-label">{label}</span>}
          {showValue && (
            <span className="genui-block-progress-value">{Math.round(pct)}%</span>
          )}
        </div>
      )}
      <div className="genui-block-progress-track">
        <div
          className="genui-block-progress-fill"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
}
