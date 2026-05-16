/**
 * GenUI Block Library — Auto-registration
 *
 * Imports all built-in blocks and registers them with the block registry.
 * Import this module once (e.g., from BlockRenderer.tsx) to ensure all
 * blocks are available for rendering.
 */

import { registerBlock } from "../blockRegistry";

// Layout blocks
import Stack from "./Stack";
import Grid from "./Grid";
import Card from "./Card";
import Divider from "./Divider";
import Spacer from "./Spacer";
import PageView from "./PageView";
import Page from "./Page";
import Tabs from "./Tabs";
import Accordion from "./Accordion";

// Content blocks
import Text from "./Text";
import Badge from "./Badge";
import Image from "./Image";
import ProgressBar from "./ProgressBar";
import Stat from "./Stat";
import Alert from "./Alert";
import KeyValue from "./KeyValue";

// Interactive blocks
import Button from "./Button";
import Input from "./Input";
import Select from "./Select";
import Checkbox from "./Checkbox";
import RadioGroup from "./RadioGroup";
import Slider from "./Slider";
import TextArea from "./TextArea";

// Data blocks
import DataTable from "./DataTable";
import List from "./List";

// ── Register all blocks ──

// Layout
registerBlock("Stack", Stack);
registerBlock("Grid", Grid);
registerBlock("Card", Card);
registerBlock("Divider", Divider);
registerBlock("Spacer", Spacer);
registerBlock("PageView", PageView);
registerBlock("Page", Page);
registerBlock("Tabs", Tabs);
registerBlock("Accordion", Accordion);

// Content
registerBlock("Text", Text);
registerBlock("Badge", Badge);
registerBlock("Image", Image);
registerBlock("ProgressBar", ProgressBar);
registerBlock("Stat", Stat);
registerBlock("Alert", Alert);
registerBlock("KeyValue", KeyValue);

// Interactive
registerBlock("Button", Button);
registerBlock("Input", Input);
registerBlock("Select", Select);
registerBlock("Checkbox", Checkbox);
registerBlock("RadioGroup", RadioGroup);
registerBlock("Slider", Slider);
registerBlock("TextArea", TextArea);

// Data
registerBlock("DataTable", DataTable);
registerBlock("List", List);
