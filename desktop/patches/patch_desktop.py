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
DESKTOP_DIR = OVERLAY_ROOT / "hermes-desktop"


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
    #    Use insert_before so the genui check is a sibling, not nested inside tool.progress
    patcher.insert_before(
        anchor='if (eventType === "hermes.tool.progress" && cb.onToolProgress) {',
        insertion=(
            '  // [GENUI-OVERLAY] Handle genui render events\n'
            '  if (eventType === "hermes.genui.render" && cb.onGenUIRender) {\n'
            '    try {\n'
            '      const payload = JSON.parse(data);\n'
            '      cb.onGenUIRender(payload);\n'
            '    } catch {\n'
            '      /* malformed genui payload — skip */\n'
            '    }\n'
            '    return;\n'
            '  }\n'
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
    #    Use insert_before so the genui check is a sibling, not nested inside tool.progress
    patcher.insert_before(
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
            '  }\n\n'
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

    # Insert onGenUIRender callback as a sibling of onUsage in the sendMessage callback object
    patcher.insert_before(
        anchor='onUsage: (usage) =>',
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

    # Insert onGenUIRender before onChatError (as a sibling property)
    patcher.insert_before(
        anchor='onChatError: (callback: (error: string) => void)',
        insertion=(
            '  // [GENUI-OVERLAY] GenUI render events\n'
            '  onGenUIRender: (callback: (payload: unknown) => void): (() => void) => {\n'
            '    const handler = (_event: Electron.IpcRendererEvent, payload: unknown): void =>\n'
            '      callback(payload);\n'
            '    ipcRenderer.on("chat-genui-render", handler);\n'
            '    return () => ipcRenderer.removeListener("chat-genui-render", handler);\n'
            '  },\n\n'
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
    """Chat.tsx: Add GenUI widget state management and inline rendering."""
    target = DESKTOP_DIR / "src" / "renderer" / "src" / "screens" / "Chat" / "Chat.tsx"
    patcher = FilePatcher(target)

    # 0. Ensure useMemo is imported (needed for widgetsByMessageId)
    patcher.replace_text(
        target='import { useCallback, useEffect, useRef, useState } from "react";',
        replacement='import { useCallback, useEffect, useMemo, useRef, useState } from "react";',
        name="Add useMemo import",
        marker="useMemo",
    )

    # 1. Add GenUI imports (+ React for React.Fragment, + MessageRow for inline render)
    patcher.insert_after(
        anchor='import type { ChatMessage, UsageState } from "./types";',
        insertion=(
            '// [GENUI-OVERLAY] GenUI imports\n'
            'import React from "react";\n'
            'import { MessageRow } from "./MessageRow";\n'
            'import GenUIWidgetContainer from "../../components/genui/GenUIWidget";\n'
            'import type { GenUIRenderPayload, WidgetState, TrackingLevel, GenUIStateUpdate } from "../../../../shared/genui-types";\n'
            '\n'
            '// [GENUI-OVERLAY] Widget with message association\n'
            'interface PlacedWidget {\n'
            '  payload: GenUIRenderPayload;\n'
            '  afterMessageId: string | null;\n'
            '}\n'
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
            '  const [genUIWidgets, setGenUIWidgets] = useState<PlacedWidget[]>([]);\n'
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

    # 4. Add the GenUI render listener effect — stamp each widget with
    #    the ID of the last message so we can render it after that message
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
            '          // Determine which message this widget should appear after\n'
            '          const lastMsg = messages.length > 0 ? messages[messages.length - 1] : null;\n'
            '          const afterMessageId = lastMsg?.id ?? null;\n'
            '          // Replace existing widget with same ID, or add new\n'
            '          const existing = prev.findIndex((w) => w.payload.widgetId === p.widgetId);\n'
            '          if (existing >= 0) {\n'
            '            const next = [...prev];\n'
            '            next[existing] = { payload: p, afterMessageId: next[existing].afterMessageId };\n'
            '            return next;\n'
            '          }\n'
            '          return [...prev, { payload: p, afterMessageId }];\n'
            '        });\n'
            '      }\n'
            '    });\n'
            '    return cleanup;\n'
            '  }, [messages]);\n'
        ),
        name="GenUI render listener effect",
        marker="[GENUI-OVERLAY] Listen for GenUI render events",
    )

    # 4b. Add effect to parse genui blocks from stored messages (session restore)
    #     When messages are loaded from a saved session, they contain raw ```genui
    #     fenced code blocks. This effect extracts them into widget state and
    #     strips the raw JSON from the displayed message content.
    patcher.insert_after(
        anchor='// [GENUI-OVERLAY] Listen for GenUI render events',
        insertion=(
            '\n'
            '  // [GENUI-OVERLAY] Rehydrate genui blocks from stored messages (session restore)\n'
            '  useEffect(() => {\n'
            '    const GENUI_RE = /```genui\\s*([\\s\\S]*?)```/g;\n'
            '    const found: PlacedWidget[] = [];\n'
            '    let needsClean = false;\n'
            '    for (const msg of messages) {\n'
            '      if (msg.role !== "agent") continue;\n'
            '      let match: RegExpExecArray | null;\n'
            '      GENUI_RE.lastIndex = 0;\n'
            '      while ((match = GENUI_RE.exec(msg.content)) !== null) {\n'
            '        try {\n'
            '          const payload = JSON.parse(match[1].trim()) as GenUIRenderPayload;\n'
            '          if (payload.widgetId && payload.widgetType) {\n'
            '            if (!genUIWidgets.some((w) => w.payload.widgetId === payload.widgetId)) {\n'
            '              found.push({ payload, afterMessageId: msg.id });\n'
            '            }\n'
            '            needsClean = true;\n'
            '          }\n'
            '        } catch { /* ignore invalid JSON */ }\n'
            '      }\n'
            '    }\n'
            '    if (found.length > 0) {\n'
            '      setGenUIWidgets((prev) => [...prev, ...found]);\n'
            '    }\n'
            '    if (needsClean) {\n'
            '      setMessages((prev) =>\n'
            '        prev.map((m) => {\n'
            '          if (m.role !== "agent" || !m.content.includes("```genui")) return m;\n'
            '          return { ...m, content: m.content.replace(/```genui[\\s\\S]*?```/g, "").trim() };\n'
            '        }),\n'
            '      );\n'
            '    }\n'
            '  // eslint-disable-next-line react-hooks/exhaustive-deps\n'
            '  }, [messages.length]);\n'
        ),
        name="Rehydrate genui blocks from stored messages",
        marker="[GENUI-OVERLAY] Rehydrate genui blocks from stored messages",
    )

    # 5. Add genUI dispatch handler — placed just before the component return
    patcher.insert_before(
        anchor=r'^  return \($',
        insertion=(
            '  // [GENUI-OVERLAY] Handle widget state dispatches (4-tier tracking)\n'
            '  const handleGenUIDispatch = useCallback(\n'
            '    (widgetId: string, field: string | undefined, actionId: string | undefined,\n'
            '     widgetState: WidgetState, tracking: TrackingLevel) => {\n'
            '      const update: GenUIStateUpdate = {\n'
            '        widgetId,\n'
            '        widgetType: genUIWidgets.find((w) => w.payload.widgetId === widgetId)?.payload.widgetType || "unknown",\n'
            '        field,\n'
            '        actionId,\n'
            '        state: widgetState,\n'
            '        tracking,\n'
            '        timestamp: Date.now(),\n'
            '      };\n'
            '\n'
            '      if (tracking === "context") {\n'
            '        genUIContextRef.current[widgetId] = widgetState;\n'
            '      } else if (tracking === "explicit") {\n'
            '        genUIExplicitRef.current.push(update);\n'
            '      } else if (tracking === "reply") {\n'
            '        const replyPayload = {\n'
            '          trigger: { widgetId, widgetType: update.widgetType, field, actionId, state: widgetState },\n'
            '          backgroundContext: { ...genUIContextRef.current },\n'
            '          explicitUpdates: [...genUIExplicitRef.current],\n'
            '        };\n'
            '        genUIExplicitRef.current = [];\n'
            '        const replyMsg = `[genui:reply] ${JSON.stringify(replyPayload)}`;\n'
            '        actions.handleSend(replyMsg);\n'
            '      }\n'
            '    },\n'
            '    [genUIWidgets, actions],\n'
            '  );\n\n'
            '  // [GENUI-OVERLAY] Build a map of messageId -> widgets for inline rendering\n'
            '  const widgetsByMessageId = useMemo(() => {\n'
            '    const map = new Map<string | null, PlacedWidget[]>();\n'
            '    for (const w of genUIWidgets) {\n'
            '      const key = w.afterMessageId;\n'
            '      if (!map.has(key)) map.set(key, []);\n'
            '      map.get(key)!.push(w);\n'
            '    }\n'
            '    return map;\n'
            '  }, [genUIWidgets]);\n\n'
        ),
        name="GenUI dispatch handler",
        marker="[GENUI-OVERLAY] Handle widget state dispatches",
        regex=True,
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

    # 7. Replace the MessageList ternary branch with a true interleaved render
    #    that places widgets directly after their associated message.
    #    We expand MessageList inline so messages and widgets alternate.
    patcher.replace_text(
        target=(
            '        ) : (\n'
            '          <MessageList\n'
            '            messages={messages}\n'
            '            isLoading={isLoading}\n'
            '            toolProgress={toolProgress}\n'
            '            onApprove={actions.handleApprove}\n'
            '            onDeny={actions.handleDeny}\n'
            '          />\n'
            '        )}'
        ),
        replacement=(
            '        ) : (\n'
            '          <>\n'
            '            {/* [GENUI-OVERLAY] Interleaved messages + widgets */}\n'
            '            {messages.filter((m) => (m.content || "").trim()).map((msg, i, arr) => (\n'
            '              <React.Fragment key={msg.id}>\n'
            '                <MessageRow\n'
            '                  msg={msg}\n'
            '                  isLast={i === arr.length - 1}\n'
            '                  isLoading={isLoading}\n'
            '                  onApprove={actions.handleApprove}\n'
            '                  onDeny={actions.handleDeny}\n'
            '                />\n'
            '                {(widgetsByMessageId.get(msg.id) || []).map((w) => (\n'
            '                  <GenUIWidgetContainer\n'
            '                    key={w.payload.widgetId}\n'
            '                    payload={w.payload}\n'
            '                    isLatest={false}\n'
            '                    onDispatch={handleGenUIDispatch}\n'
            '                  />\n'
            '                ))}\n'
            '              </React.Fragment>\n'
            '            ))}\n'
            '            {isLoading && messages.length > 0 && messages[messages.length - 1].role !== "agent" && (\n'
            '              <div className="chat-message chat-message-agent">\n'
            '                <div className="chat-bubble chat-bubble-agent">\n'
            '                  <div className="chat-typing">\n'
            '                    <span className="chat-typing-dot" />\n'
            '                    <span className="chat-typing-dot" />\n'
            '                    <span className="chat-typing-dot" />\n'
            '                  </div>\n'
            '                </div>\n'
            '              </div>\n'
            '            )}\n'
            '          </>\n'
            '        )}'
        ),
        name="Render GenUI widgets inline",
        marker="[GENUI-OVERLAY] Render widgets inline",
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
