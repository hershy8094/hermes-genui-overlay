/**
 * Stat — KPI statistic display block.
 *
 * Props:
 *   label: string (required)
 *   value: string | number (required)
 *   change?: string — e.g., "+12%", "-3"
 *   trend?: "up" | "down" | "neutral"
 *   prefix?: string — e.g., "$"
 *   suffix?: string — e.g., "units"
 */

import type { BlockProps } from "../blockRegistry";

const TREND_COLORS: Record<string, string> = {
  up: "#22c55e",
  down: "#ef4444",
  neutral: "var(--text-muted, #8e8e8e)",
};

const TREND_ARROWS: Record<string, string> = {
  up: "↑", down: "↓", neutral: "→",
};

export default function Stat({ props }: BlockProps): React.JSX.Element {
  const label = (props.label as string) ?? "";
  const value = props.value ?? "";
  const change = props.change as string | undefined;
  const trend = (props.trend as string) ?? "neutral";
  const prefix = (props.prefix as string) ?? "";
  const suffix = (props.suffix as string) ?? "";

  return (
    <div className="genui-block-stat">
      <div className="genui-block-stat-label">{label}</div>
      <div className="genui-block-stat-value">
        {prefix}{String(value)}{suffix && <span className="genui-block-stat-suffix"> {suffix}</span>}
      </div>
      {change && (
        <div
          className="genui-block-stat-change"
          style={{ color: TREND_COLORS[trend] ?? TREND_COLORS.neutral }}
        >
          {TREND_ARROWS[trend] ?? ""} {change}
        </div>
      )}
    </div>
  );
}
