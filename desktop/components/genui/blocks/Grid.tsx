/**
 * Grid — CSS Grid layout block.
 *
 * Props:
 *   columns?: number (default: 2)
 *   gap?: "none" | "xs" | "sm" | "md" | "lg" | "xl" (default: "md")
 *   minChildWidth?: string (e.g., "200px" — enables auto-fit)
 */

import type { BlockProps } from "../blockRegistry";

const GAP_MAP: Record<string, string> = {
  none: "0", xs: "4px", sm: "8px", md: "12px", lg: "20px", xl: "32px",
};

export default function Grid({ props, children }: BlockProps): React.JSX.Element {
  const columns = (props.columns as number) ?? 2;
  const gap = GAP_MAP[(props.gap as string) ?? "md"] ?? "12px";
  const minChildWidth = props.minChildWidth as string | undefined;

  const gridTemplate = minChildWidth
    ? `repeat(auto-fit, minmax(${minChildWidth}, 1fr))`
    : `repeat(${columns}, 1fr)`;

  return (
    <div
      className="genui-block-grid"
      style={{
        display: "grid",
        gridTemplateColumns: gridTemplate,
        gap,
      }}
    >
      {children}
    </div>
  );
}
