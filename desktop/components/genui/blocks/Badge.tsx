/**
 * Badge — Status badge block.
 *
 * Props:
 *   label: string (required)
 *   color?: string — "green" | "red" | "yellow" | "blue" | "purple" | "gray" or CSS color
 *   variant?: "solid" | "outline" | "subtle" (default: "subtle")
 */

import type { BlockProps } from "../blockRegistry";

const COLOR_MAP: Record<string, { bg: string; text: string; border: string }> = {
  green:  { bg: "rgba(34,197,94,0.12)",  text: "#22c55e", border: "rgba(34,197,94,0.3)" },
  red:    { bg: "rgba(239,68,68,0.12)",   text: "#ef4444", border: "rgba(239,68,68,0.3)" },
  yellow: { bg: "rgba(234,179,8,0.12)",   text: "#eab308", border: "rgba(234,179,8,0.3)" },
  blue:   { bg: "rgba(59,130,246,0.12)",  text: "#3b82f6", border: "rgba(59,130,246,0.3)" },
  purple: { bg: "rgba(168,85,247,0.12)",  text: "#a855f7", border: "rgba(168,85,247,0.3)" },
  gray:   { bg: "rgba(156,163,175,0.12)", text: "#9ca3af", border: "rgba(156,163,175,0.3)" },
};

export default function Badge({ props }: BlockProps): React.JSX.Element {
  const label = (props.label as string) ?? "";
  const colorName = (props.color as string) ?? "blue";
  const variant = (props.variant as string) ?? "subtle";

  const palette = COLOR_MAP[colorName] ?? COLOR_MAP.blue;

  const style: React.CSSProperties = variant === "solid"
    ? { backgroundColor: palette.text, color: "#fff", border: "none" }
    : variant === "outline"
    ? { backgroundColor: "transparent", color: palette.text, border: `1px solid ${palette.border}` }
    : { backgroundColor: palette.bg, color: palette.text, border: `1px solid ${palette.border}` };

  return (
    <span className="genui-block-badge" style={style}>
      {label}
    </span>
  );
}
