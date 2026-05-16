/**
 * Spacer — Fixed-height spacer element.
 *
 * Props:
 *   size?: "sm" | "md" | "lg" | "xl" | number (px) (default: "md")
 */

import type { BlockProps } from "../blockRegistry";

const SIZE_MAP: Record<string, number> = {
  sm: 8, md: 16, lg: 24, xl: 40,
};

export default function Spacer({ props }: BlockProps): React.JSX.Element {
  const sizeRaw = props.size ?? "md";
  const height = typeof sizeRaw === "number"
    ? sizeRaw
    : SIZE_MAP[sizeRaw as string] ?? 16;

  return <div className="genui-block-spacer" style={{ height }} />;
}
