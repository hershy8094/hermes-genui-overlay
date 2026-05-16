/**
 * Text — Text display block.
 *
 * Props:
 *   content: string (required)
 *   variant?: "h1" | "h2" | "h3" | "body" | "caption" | "code" | "label" (default: "body")
 *   color?: string — CSS color or design token name
 *   weight?: "normal" | "medium" | "semibold" | "bold"
 *   align?: "left" | "center" | "right"
 */

import type { BlockProps } from "../blockRegistry";

const TAG_MAP: Record<string, keyof React.JSX.IntrinsicElements> = {
  h1: "h1", h2: "h2", h3: "h3",
  body: "p", caption: "span", code: "code", label: "label",
};

export default function Text({ props }: BlockProps): React.JSX.Element {
  const content = (props.content as string) ?? "";
  const variant = (props.variant as string) ?? "body";
  const color = props.color as string | undefined;
  const weight = props.weight as string | undefined;
  const align = props.align as string | undefined;

  const Tag = TAG_MAP[variant] ?? "p";

  return (
    <Tag
      className={`genui-block-text genui-block-text-${variant}`}
      style={{
        color: color ?? undefined,
        fontWeight: weight ?? undefined,
        textAlign: (align as React.CSSProperties["textAlign"]) ?? undefined,
      }}
    >
      {content}
    </Tag>
  );
}
