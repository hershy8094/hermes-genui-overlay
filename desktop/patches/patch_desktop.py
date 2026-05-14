#!/usr/bin/env python3
"""
Patch: Desktop (hermes-desktop) — all frontend GenUI modifications.

Patches:
  1. hermes.ts → processCustomEvent handles hermes.genui.render + X-Hermes-Platform header
  2. sse-parser.ts → processCustomEvent handles hermes.genui.render
  3. index.ts → IPC: main process receives genui events and forwards to renderer
  4. preload/index.ts → onGenUIRender bridge
  5. preload/index.d.ts → type declaration for onGenUIRender
  6. Chat.tsx → widget state, rendering, and dispatch logic
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from patch_utils import FilePatcher, PatchError

OVERLAY_ROOT = Path(__file__).resolve().parent.parent.parent
DESKTOP_DIR = OVERLAY_ROOT.parent / "hermes-desktop"


def patch_hermes_ts():
    """hermes.ts: Add X-Hermes-Platform header + genui.render event handling."""
    target = DESKTOP_DIR / "src" / "main" / "hermes.ts"
    patcher = FilePatcher(target)

    # 1. X-Hermes-Platform header in sendMessageViaApi
    patcher.insert_after(
        anchor='...getRemoteAuthHeader(),',
        insertion=(
            '    "X-Hermes-Platform": "desktop",  // [GENUI-OVERLAY]'
        ),
        name="Add X-Hermes-Platform header",
        marker="X-Hermes-Platform",
    )

    # 2. Add onGenUIRender to ChatCallbacks interface
    patcher.insert_after(
        anchor='onToolProgress?: (tool: string) => void;',
        insertion=(
            '  onGenUIRender?: (payload: unknown) => void;  // [GENUI-OVERLAY]'
        ),
        name="Add onGenUIRender callback",
        marker="onGenUIRender",
    )

    # 3. Handle hermes.genui.render in processCustomEvent
    patcher.insert_after(
        anchor='if (eventType === "hermes.tool.progress" && cb.onToolProgress) {',
        insertion=(
            '    // [GENUI-OVERLAY] Handle genui render events\n'
            '    if (eventType === "hermes.genui.render" && cb.onGenUIRender) {\n'
            '      try {\n'
            '        const payload = JSON.parse(data);\n'
            '        cb.onGenUIRender(payload);\n'
            '      } catch {\n'
            '        /* malformed genui payload — skip */\n'
            '      }\n'
            '      return;\n'
            '    }\n'
        ),
        name="Handle hermes.genui.render event",
        marker="[GENUI-OVERLAY] Handle genui render events",
    )

    changed = patcher.write()
    print(patcher.report())
    return changed


def patch_sse_parser():
    """sse-parser.ts: Add genui.render to processCustomEvent + SseCallbacks."""
    target = DESKTOP_DIR / "src" / "main" / "sse-parser.ts"
    patcher = FilePatcher(target)

    # 1. Add onGenUIRender to SseCallbacks
    patcher.insert_after(
        anchor='onError?: (message: string) => void;',
        insertion=(
            '  onGenUIRender?: (payload: unknown) => void;  // [GENUI-OVERLAY]'
        ),
        name="Add onGenUIRender to SseCallbacks",
        marker="onGenUIRender",
    )

    # 2. Handle hermes.genui.render in processCustomEvent
    patcher.insert_after(
        anchor='if (eventType === "hermes.tool.progress" && cb.onToolProgress) {',
        insertion=(
            '  // [GENUI-OVERLAY] Handle genui render events\n'
            '  if (eventType === "hermes.genui.render") {\n'
            '    try {\n'
            '      const payload = JSON.parse(data);\n'
            '      // Forward via the extended callbacks type\n'
            '      (cb as { onGenUIRender?: (p: unknown) => void }).onGenUIRender?.(payload);\n'
            '      return true;\n'
            '    } catch {\n'
            '      /* malformed genui payload — skip */\n'
            '    }\n'
            '  }\n'
        ),
        name="Handle genui.render in sse-parser",
        marker="[GENUI-OVERLAY] Handle genui render events",
    )

    changed = patcher.write()
    print(patcher.report())
    return changed


def patch_index_ts():
    """index.ts: Forward genui render events from main process to renderer via IPC."""
    target = DESKTOP_DIR / "src" / "main" / "index.ts"
    patcher = FilePatcher(target)

    # Insert onGenUIRender callback inside sendMessage handler's callback object
    patcher.insert_after(
        anchor='onUsage: (usage) => {',
        insertion=(
            '          // [GENUI-OVERLAY] Forward genui render events to renderer\n'
            '          onGenUIRender: (payload: unknown) => {\n'
            '            event.sender.send("chat-genui-render", payload);\n'
            '          },\n'
        ),
        name="Forward genui render to renderer",
        marker="[GENUI-OVERLAY] Forward genui render events",
    )

    changed = patcher.write()
    print(patcher.report())
    return changed


def patch_preload_ts():
    """preload/index.ts: Expose onGenUIRender bridge to renderer."""
    target = DESKTOP_DIR / "src" / "preload" / "index.ts"
    patcher = FilePatcher(target)

    # Insert onGenUIRender after onChatUsage
    patcher.insert_after(
        anchor='return () => ipcRenderer.removeListener("chat-usage", handler);',
        insertion=(
            '\n'
            '  // [GENUI-OVERLAY] GenUI render events\n'
            '  onGenUIRender: (callback: (payload: unknown) => void): (() => void) => {\n'
            '    const handler = (_event: Electron.IpcRendererEvent, payload: unknown): void =>\n'
            '      callback(payload);\n'
            '    ipcRenderer.on("chat-genui-render", handler);\n'
            '    return () => ipcRenderer.removeListener("chat-genui-render", handler);\n'
            '  },\n'
        ),
        name="Add onGenUIRender bridge",
        marker="[GENUI-OVERLAY] GenUI render events",
    )

    changed = patcher.write()
    print(patcher.report())
    return changed


def patch_preload_dts():
    """preload/index.d.ts: Add type declaration for onGenUIRender."""
    target = DESKTOP_DIR / "src" / "preload" / "index.d.ts"
    patcher = FilePatcher(target)

    # Find a good anchor — onChatError is declared near the chat IPC methods
    patcher.insert_after(
        anchor='onChatError: (callback: (error: string) => void) => () => void;',
        insertion=(
            '    onGenUIRender: (callback: (payload: unknown) => void) => () => void;  // [GENUI-OVERLAY]'
        ),
        name="Add onGenUIRender type declaration",
        marker="[GENUI-OVERLAY]",
    )

    changed = patcher.write()
    print(patcher.report())
    return changed


def patch_chat_tsx():
    """Chat.tsx: Add GenUI widget state management and rendering."""
    target = DESKTOP_DIR / "src" / "renderer" / "src" / "screens" / "Chat" / "Chat.tsx"
    patcher = FilePatcher(target)

    # 1. Add GenUI imports
    patcher.insert_after(
        anchor='import type { ChatMessage, UsageState } from "./types";',
        insertion=(
            '// [GENUI-OVERLAY] GenUI imports\n'
            'import GenUIWidgetContainer from "../../components/genui/GenUIWidget";\n'
            'import type { GenUIRenderPayload, WidgetState, TrackingLevel, GenUIStateUpdate } from "../../../../shared/genui-types";\n'
        ),
        name="Add GenUI imports to Chat.tsx",
        marker="[GENUI-OVERLAY] GenUI imports",
    )

    # 2. Add GenUI state hooks inside the Chat component
    patcher.insert_after(
        anchor='const chatInputRef = useRef<ChatInputHandle>(null);',
        insertion=(
            '\n'
            '  // [GENUI-OVERLAY] GenUI state management\n'
            '  const [genUIWidgets, setGenUIWidgets] = useState<GenUIRenderPayload[]>([]);\n'
            '  const genUIContextRef = useRef<Record<string, WidgetState>>({});\n'
            '  const genUIExplicitRef = useRef<GenUIStateUpdate[]>([]);\n'
        ),
        name="Add GenUI state hooks",
        marker="[GENUI-OVERLAY] GenUI state management",
    )

    # 3. Add GenUI IPC listener (useEffect)
    patcher.insert_after(
        anchor='useChatIPC({',
        insertion=(
            '    // [GENUI-OVERLAY] setGenUIWidgets passed to IPC listener below\n'
        ),
        name="Comment for GenUI IPC",
        marker="[GENUI-OVERLAY] setGenUIWidgets passed",
    )

    # 4. Add the GenUI render listener effect
    patcher.insert_after(
        anchor='}, [messages]);',
        insertion=(
            '\n'
            '  // [GENUI-OVERLAY] Listen for GenUI render events from main process\n'
            '  useEffect(() => {\n'
            '    const cleanup = window.hermesAPI.onGenUIRender((payload: unknown) => {\n'
            '      const p = payload as GenUIRenderPayload;\n'
            '      if (p && p.widgetId && p.widgetType) {\n'
            '        setGenUIWidgets((prev) => {\n'
            '          // Replace existing widget with same ID, or add new\n'
            '          const existing = prev.findIndex((w) => w.widgetId === p.widgetId);\n'
            '          if (existing >= 0) {\n'
            '            const next = [...prev];\n'
            '            next[existing] = p;\n'
            '            return next;\n'
            '          }\n'
            '          return [...prev, p];\n'
            '        });\n'
            '      }\n'
            '    });\n'
            '    return cleanup;\n'
            '  }, []);\n'
        ),
        name="GenUI render listener effect",
        marker="[GENUI-OVERLAY] Listen for GenUI render events",
    )

    # 5. Add genUI dispatch handler
    patcher.insert_before(
        anchor='return (',
        insertion=(
            '  // [GENUI-OVERLAY] Handle widget state dispatches (4-tier tracking)\n'
            '  const handleGenUIDispatch = useCallback(\n'
            '    (widgetId: string, field: string | undefined, actionId: string | undefined,\n'
            '     state: WidgetState, tracking: TrackingLevel) => {\n'
            '      const update: GenUIStateUpdate = {\n'
            '        widgetId,\n'
            '        widgetType: genUIWidgets.find((w) => w.widgetId === widgetId)?.widgetType || "unknown",\n'
            '        field,\n'
            '        actionId,\n'
            '        state,\n'
            '        tracking,\n'
            '        timestamp: Date.now(),\n'
            '      };\n'
            '\n'
            '      if (tracking === "context") {\n'
            '        genUIContextRef.current[widgetId] = state;\n'
            '      } else if (tracking === "explicit") {\n'
            '        genUIExplicitRef.current.push(update);\n'
            '      } else if (tracking === "reply") {\n'
            '        // Compose a structured reply message and send it\n'
            '        const replyPayload = {\n'
            '          trigger: { widgetId, widgetType: update.widgetType, field, actionId, state },\n'
            '          backgroundContext: { ...genUIContextRef.current },\n'
            '          explicitUpdates: [...genUIExplicitRef.current],\n'
            '        };\n'
            '        // Clear accumulated explicit updates after sending\n'
            '        genUIExplicitRef.current = [];\n'
            '        const replyMsg = `[genui:reply] ${JSON.stringify(replyPayload)}`;\n'
            '        actions.handleSend(replyMsg);\n'
            '      }\n'
            '    },\n'
            '    [genUIWidgets, actions],\n'
            '  );\n'
            '\n'
        ),
        name="GenUI dispatch handler",
        marker="[GENUI-OVERLAY] Handle widget state dispatches",
    )

    # 6. Clear widgets on new chat
    patcher.insert_after(
        anchor='setUsage(null);',
        insertion=(
            '    setGenUIWidgets([]);  // [GENUI-OVERLAY] Clear widgets on new chat\n'
            '    genUIContextRef.current = {};  // [GENUI-OVERLAY]\n'
            '    genUIExplicitRef.current = [];  // [GENUI-OVERLAY]\n'
        ),
        name="Clear GenUI state on new chat",
        marker="[GENUI-OVERLAY] Clear widgets on new chat",
    )

    # 7. Render GenUI widgets in the chat area
    patcher.insert_after(
        anchor='<div ref={bottomRef} />',
        insertion=(
            '        {/* [GENUI-OVERLAY] Render active GenUI widgets */}\n'
            '        {genUIWidgets.map((widget, idx) => (\n'
            '          <GenUIWidgetContainer\n'
            '            key={widget.widgetId}\n'
            '            payload={widget}\n'
            '            isLatest={idx === genUIWidgets.length - 1}\n'
            '            onDispatch={handleGenUIDispatch}\n'
            '          />\n'
            '        ))}\n'
        ),
        name="Render GenUI widgets",
        marker="[GENUI-OVERLAY] Render active GenUI widgets",
    )

    changed = patcher.write()
    print(patcher.report())
    return changed


def apply():
    results = []
    for fn, label in [
        (patch_hermes_ts, "hermes.ts"),
        (patch_sse_parser, "sse-parser.ts"),
        (patch_index_ts, "index.ts"),
        (patch_preload_ts, "preload/index.ts"),
        (patch_preload_dts, "preload/index.d.ts"),
        (patch_chat_tsx, "Chat.tsx"),
    ]:
        try:
            r = fn()
            results.append((label, r, None))
        except PatchError as e:
            print(f"  ✗ {label} FAILED: {e}", file=sys.stderr)
            results.append((label, False, str(e)))

    # Summary
    for label, success, err in results:
        if err:
            print(f"  ✗ {label}: {err}")
        elif success:
            print(f"  ✓ {label}")
        else:
            print(f"  ⏭ {label} (already applied)")

    return all(r[2] is None for r in results)


if __name__ == "__main__":
    success = apply()
    sys.exit(0)
