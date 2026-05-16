/**
 * GenUI Block Registry
 *
 * Maps block type strings to React components for the composable
 * component tree. Separate from the legacy widget registry.
 *
 * Block types are case-sensitive and should use PascalCase
 * (e.g., "Stack", "Card", "DataTable").
 */

import type { ComponentType } from "react";
import type { GenUINode, WidgetState, TrackingLevel } from "../../../../shared/genui-types";

/** Props injected into every registered block component. */
export interface BlockProps {
  /** The node descriptor from the component tree. */
  node: GenUINode;
  /** The props extracted from node.props for convenience. */
  props: Record<string, unknown>;
  /** The full widget state. */
  state: WidgetState;
  /** Pre-rendered child nodes (from recursive BlockRenderer). */
  children?: React.ReactNode;
  /** Called when a bound state field changes. */
  onStateChange: (field: string, value: unknown) => void;
  /** Called when an action button is clicked. */
  onAction: (actionId: string, state: WidgetState) => void;
  /** Called when a navigation action is triggered (for PageView routing). */
  onNavigate: (pageId: string) => void;
}

type BlockComponent = ComponentType<BlockProps>;

const blockRegistry = new Map<string, BlockComponent>();

/**
 * Register a block component for a given type name.
 *
 * @param type - PascalCase block type (e.g., "Stack", "Card")
 * @param component - React component implementing BlockProps
 */
export function registerBlock(type: string, component: BlockComponent): void {
  blockRegistry.set(type, component);
}

/**
 * Look up a block component by type name.
 */
export function getBlock(type: string): BlockComponent | undefined {
  return blockRegistry.get(type);
}

/**
 * Check if a block type is registered.
 */
export function hasBlock(type: string): boolean {
  return blockRegistry.has(type);
}

/**
 * List all registered block type names.
 * Useful for agent introspection and debugging.
 */
export function listBlocks(): string[] {
  return Array.from(blockRegistry.keys()).sort();
}
