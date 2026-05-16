/**
 * GenUI Widget Registry
 *
 * Central registry mapping widget type names to React components.
 * The agent declares a `widgetType` in its render payload, and the
 * registry resolves it to the appropriate component at render time.
 */

import type { ComponentType } from "react";
import type {
  WidgetState,
  GenUIAction,
  GenUIStateField,
} from "../genui-types";

/** Props injected into every registered widget component. */
export interface GenUIWidgetProps {
  widgetId: string;
  state: WidgetState;
  trackedFields: GenUIStateField[];
  actions: GenUIAction[];
  meta?: Record<string, unknown>;
  /** Called when a state field changes. Routes through 4-tier tracking. */
  onStateChange: (field: string, value: unknown) => void;
  /** Called when an action button is clicked. */
  onAction: (actionId: string, newState: WidgetState) => void;
}

type WidgetComponent = ComponentType<GenUIWidgetProps>;

const registry = new Map<string, WidgetComponent>();

export function registerWidget(
  type: string,
  component: WidgetComponent,
): void {
  registry.set(type, component);
}

export function getWidget(type: string): WidgetComponent | undefined {
  return registry.get(type);
}

export function hasWidget(type: string): boolean {
  return registry.has(type);
}
