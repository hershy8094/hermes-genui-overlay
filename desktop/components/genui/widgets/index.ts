/**
 * Widget auto-registration.
 *
 * Import this module to register all built-in widgets with the registry.
 */

import { registerWidget } from "../registry";
import CounterWidget from "./CounterWidget";
import QuizWidget from "./QuizWidget";
import GenericWidget from "./GenericWidget";

// Built-in widgets
registerWidget("counter", CounterWidget);
registerWidget("quiz", QuizWidget);

// Fallback — must be registered last (looked up by getWidget("__generic__"))
registerWidget("__generic__", GenericWidget);

export { CounterWidget, GenericWidget };
