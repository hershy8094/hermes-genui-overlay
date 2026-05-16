/**
 * Stack — Flex container block (vertical or horizontal).
 *
 * Props:
 *   direction?: "vertical" | "horizontal" (default: "vertical")
 *   gap?: "none" | "xs" | "sm" | "md" | "lg" | "xl" (default: "md")
 *   align?: "start" | "center" | "end" | "stretch" (default: "stretch")
 *   justify?: "start" | "center" | "end" | "between" | "around"
 *   wrap?: boolean
 *   padding?: "none" | "sm" | "md" | "lg"
 */

import type { BlockProps } from "../blockRegistry";

const GAP_MAP: Record<string, string> = {
  none: "0", xs: "4px", sm: "8px", md: "12px", lg: "20px", xl: "32px",
};
const ALIGN_MAP: Record<string, string> = {
  start: "flex-start", center: "center", end: "flex-end", stretch: "stretch",
};
const JUSTIFY_MAP: Record<string, string> = {
  start: "flex-start", center: "center", end: "flex-end",
  between: "space-between", around: "space-around",
};
const PAD_MAP: Record<string, string> = {
  none: "0", sm: "8px", md: "16px", lg: "24px",
};

export default function Stack({ props, children }: BlockProps): React.JSX.Element {
  const direction = (props.direction as string) ?? "vertical";
  const gap = GAP_MAP[(props.gap as string) ?? "md"] ?? "12px";
  const align = ALIGN_MAP[(props.align as string) ?? "stretch"] ?? "stretch";
  const justify = JUSTIFY_MAP[(props.justify as string) ?? "start"] ?? "flex-start";
  const wrap = Boolean(props.wrap);
  const padding = PAD_MAP[(props.padding as string) ?? "none"] ?? "0";

  return (
    <div
      className="genui-block-stack"
      style={{
        display: "flex",
        flexDirection: direction === "horizontal" ? "row" : "column",
        gap,
        alignItems: align,
        justifyContent: justify,
        flexWrap: wrap ? "wrap" : "nowrap",
        padding,
      }}
    >
      {children}
    </div>
  );
}
