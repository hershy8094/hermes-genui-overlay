/**
 * Image — Image display block.
 *
 * Props:
 *   src: string (required)
 *   alt?: string
 *   width?: string | number
 *   height?: string | number
 *   fit?: "cover" | "contain" | "fill" | "none" (default: "cover")
 *   rounded?: boolean | string (true = md radius, string = specific radius)
 */

import type { BlockProps } from "../blockRegistry";

export default function Image({ props }: BlockProps): React.JSX.Element {
  const src = (props.src as string) ?? "";
  const alt = (props.alt as string) ?? "";
  const width = props.width as string | number | undefined;
  const height = props.height as string | number | undefined;
  const fit = (props.fit as string) ?? "cover";
  const rounded = props.rounded;

  const borderRadius = rounded === true
    ? "var(--radius-md, 10px)"
    : typeof rounded === "string"
    ? rounded
    : undefined;

  return (
    <img
      className="genui-block-image"
      src={src}
      alt={alt}
      style={{
        width: width ?? "100%",
        height: height ?? "auto",
        objectFit: fit as React.CSSProperties["objectFit"],
        borderRadius,
        display: "block",
      }}
    />
  );
}
