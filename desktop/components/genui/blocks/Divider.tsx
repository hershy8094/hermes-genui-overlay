/**
 * Divider — Horizontal rule with optional label text.
 *
 * Props:
 *   label?: string — centered label within the divider
 */

import type { BlockProps } from "../blockRegistry";

export default function Divider({ props }: BlockProps): React.JSX.Element {
  const label = props.label as string | undefined;

  if (label) {
    return (
      <div className="genui-block-divider genui-block-divider-labeled">
        <span className="genui-block-divider-line" />
        <span className="genui-block-divider-label">{label}</span>
        <span className="genui-block-divider-line" />
      </div>
    );
  }

  return <hr className="genui-block-divider" />;
}
