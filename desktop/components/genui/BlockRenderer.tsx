/**
 * BlockRenderer — Recursive rendering engine for GenUI component trees.
 *
 * Takes a GenUINode[] tree and renders it depth-first, resolving each node
 * type from the block registry. Handles:
 * - Recursive nesting (children → React children)
 * - State binding (node.bind → onStateChange)
 * - Page navigation (node.navigate → onNavigate)
 * - Custom inline styles (node.style → CSS)
 * - Graceful fallback for unknown block types
 */

import { useMemo } from "react";
import { getBlock } from "./blockRegistry";
import type { GenUINode, WidgetState } from "../../../../shared/genui-types";

// Ensure all built-in blocks are registered
import "./blocks";

export interface BlockRendererProps {
  /** Array of root-level nodes to render. */
  nodes: GenUINode[];
  /** The full widget state. */
  state: WidgetState;
  /** Called when a bound state field changes. */
  onStateChange: (field: string, value: unknown) => void;
  /** Called when an action button is clicked. */
  onAction: (actionId: string, state: WidgetState) => void;
  /** Called when a navigation action is triggered. */
  onNavigate: (pageId: string) => void;
}

/** Render a single GenUINode and its children recursively. */
function RenderNode({
  node,
  index,
  state,
  onStateChange,
  onAction,
  onNavigate,
}: {
  node: GenUINode;
  index: number;
  state: WidgetState;
  onStateChange: (field: string, value: unknown) => void;
  onAction: (actionId: string, state: WidgetState) => void;
  onNavigate: (pageId: string) => void;
}): React.JSX.Element {
  const BlockComponent = getBlock(node.type);

  if (!BlockComponent) {
    return (
      <div
        key={node.key ?? index}
        className="genui-block-unknown"
        title={`Unknown block type: ${node.type}`}
      >
        <span className="genui-block-unknown-label">⚠ {node.type}</span>
      </div>
    );
  }

  // Recursively render children
  const renderedChildren = node.children?.map((child, i) => (
    <RenderNode
      key={child.key ?? `${node.type}-${i}`}
      node={child}
      index={i}
      state={state}
      onStateChange={onStateChange}
      onAction={onAction}
      onNavigate={onNavigate}
    />
  ));

  // Merge custom styles
  const style = node.style ?? undefined;

  return (
    <div
      key={node.key ?? index}
      className="genui-block-wrapper"
      style={style}
    >
      <BlockComponent
        node={node}
        props={node.props ?? {}}
        state={state}
        onStateChange={onStateChange}
        onAction={onAction}
        onNavigate={onNavigate}
      >
        {renderedChildren}
      </BlockComponent>
    </div>
  );
}

/**
 * BlockRenderer — entry point for rendering a composable component tree.
 *
 * Usage: <BlockRenderer nodes={payload.children} state={state} ... />
 */
export default function BlockRenderer({
  nodes,
  state,
  onStateChange,
  onAction,
  onNavigate,
}: BlockRendererProps): React.JSX.Element {
  const rendered = useMemo(
    () =>
      nodes.map((node, i) => (
        <RenderNode
          key={node.key ?? `root-${i}`}
          node={node}
          index={i}
          state={state}
          onStateChange={onStateChange}
          onAction={onAction}
          onNavigate={onNavigate}
        />
      )),
    [nodes, state, onStateChange, onAction, onNavigate],
  );

  return <div className="genui-block-tree">{rendered}</div>;
}
