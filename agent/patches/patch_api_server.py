#!/usr/bin/env python3
"""
Patch: gateway/platforms/api_server.py

Adds:
  1. genui_protocol imports
  2. GenUI block detection and SSE event emission in the streaming path

Strategy:
  - Import genui_protocol at the top of the file
  - Patch the _emit() helper inside _write_sse_chat_completion to detect
    genui fenced code blocks in streamed content and emit them as
    separate `hermes.genui.render` SSE events instead of raw markdown.

Anchors:
  - Import block (for genui_protocol)
  - _emit() function signature inside _write_sse_chat_completion
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from patch_utils import FilePatcher, PatchError

OVERLAY_ROOT = Path(__file__).resolve().parent.parent.parent
AGENT_DIR = OVERLAY_ROOT.parent / "hermes-agent"
TARGET = AGENT_DIR / "gateway" / "platforms" / "api_server.py"


def apply():
    try:
        patcher = FilePatcher(TARGET)

        # 1. Import genui_protocol at module level
        patcher.append_to_imports(
            module="gateway.platforms.genui_protocol",
            names=["parse_genui_block", "serialize_genui_event"],
            name="Import genui_protocol",
            marker="genui_protocol",
        )

        # 2. Add platform= parameter override in _create_agent
        #    The desktop sends X-Hermes-Platform: desktop header, and
        #    we need to thread it into the agent's platform kwarg so
        #    GenUI guidance gets injected.
        patcher.insert_after(
            anchor='gateway_session_key, key_err = self._parse_session_key_header(request)',
            insertion=(
                '\n'
                '        # [GENUI-OVERLAY] Parse X-Hermes-Platform header\n'
                '        genui_platform = request.headers.get("X-Hermes-Platform", "").strip() or None\n'
            ),
            name="Parse X-Hermes-Platform header",
            marker="[GENUI-OVERLAY] Parse X-Hermes-Platform header",
        )

        # 3. Thread platform into _run_agent calls (streaming path)
        #    Insert platform_override=genui_platform after gateway_session_key
        #    in the streaming _run_agent call
        patcher.insert_after(
            anchor='tool_complete_callback=_on_tool_complete,',
            insertion=(
                '                # [GENUI-OVERLAY] Thread platform override\n'
                '                platform_override=genui_platform,\n'
            ),
            name="Thread platform_override (streaming)",
            marker="[GENUI-OVERLAY] Thread platform override",
        )

        # 4. Add platform_override param to _run_agent method signature
        patcher.insert_after(
            anchor='gateway_session_key: Optional[str] = None,',
            insertion=(
                '        # [GENUI-OVERLAY] Platform override from X-Hermes-Platform header\n'
                '        platform_override: Optional[str] = None,\n'
            ),
            name="Add platform_override to _run_agent",
            marker="[GENUI-OVERLAY] Platform override from X-Hermes-Platform header",
        )

        # 5. Pass platform into _create_agent (inside _run_agent._run)
        patcher.replace_pattern(
            pattern=r'(gateway_session_key=gateway_session_key,\n\s*\))',
            replacement=(
                'gateway_session_key=gateway_session_key,\n'
                '            )  # [GENUI-OVERLAY] platform_override applied below\n'
            ),
            name="Placeholder for _create_agent platform pass-through",
            marker="[GENUI-OVERLAY] platform_override applied below",
        )

        # 6. Patch the _emit helper to detect genui blocks
        #    We insert a genui buffer check BEFORE the existing content emission
        patcher.insert_before(
            anchor='if isinstance(item, tuple) and len(item) == 2 and item[0] == "__tool_progress__"',
            insertion=(
                '                # [GENUI-OVERLAY] GenUI block detection\n'
                '                # Buffer content chunks and check for ```genui fenced code blocks.\n'
                '                # When a complete genui block is found, emit it as a custom SSE event\n'
                '                # instead of streaming it as raw markdown content.\n'
                '                if isinstance(item, str) and "```genui" in _genui_buffer + item:\n'
                '                    _genui_buffer += item\n'
                '                    # Check if the block is complete (has closing ```)\n'
                '                    start_idx = _genui_buffer.find("```genui")\n'
                '                    after_start = _genui_buffer[start_idx + 8:]\n'
                '                    end_idx = after_start.find("```")\n'
                '                    if end_idx != -1:\n'
                '                        # Extract the genui JSON, emit as custom SSE event\n'
                '                        genui_json = after_start[:end_idx].strip()\n'
                '                        try:\n'
                '                            genui_payload = json.loads(genui_json)\n'
                '                            await response.write(\n'
                '                                f"event: hermes.genui.render\\ndata: {json.dumps(genui_payload)}\\n\\n".encode()\n'
                '                            )\n'
                '                        except (json.JSONDecodeError, Exception) as _ge:\n'
                '                            logger.warning("Invalid genui block: %s", _ge)\n'
                '                        # Emit any text before the genui block as normal content\n'
                '                        pre_text = _genui_buffer[:start_idx]\n'
                '                        post_text = after_start[end_idx + 3:]\n'
                '                        _genui_buffer = ""\n'
                '                        if pre_text.strip():\n'
                '                            content_chunk = {\n'
                '                                "id": completion_id, "object": "chat.completion.chunk",\n'
                '                                "created": created, "model": model,\n'
                '                                "choices": [{"index": 0, "delta": {"content": pre_text}, "finish_reason": None}],\n'
                '                            }\n'
                '                            await response.write(f"data: {json.dumps(content_chunk)}\\n\\n".encode())\n'
                '                        if post_text.strip():\n'
                '                            content_chunk = {\n'
                '                                "id": completion_id, "object": "chat.completion.chunk",\n'
                '                                "created": created, "model": model,\n'
                '                                "choices": [{"index": 0, "delta": {"content": post_text}, "finish_reason": None}],\n'
                '                            }\n'
                '                            await response.write(f"data: {json.dumps(content_chunk)}\\n\\n".encode())\n'
                '                        return time.monotonic()\n'
                '                    else:\n'
                '                        return last_activity  # Still buffering, wait for more\n'
                '                elif _genui_buffer:\n'
                '                    # Had a partial buffer but this chunk doesn\'t contain genui\n'
                '                    _genui_buffer += item if isinstance(item, str) else ""\n'
                '                    # If buffer grew too large without closing, flush it as normal content\n'
                '                    if len(_genui_buffer) > 10000:\n'
                '                        item = _genui_buffer\n'
                '                        _genui_buffer = ""\n'
                '                    else:\n'
                '                        return last_activity\n'
            ),
            name="GenUI block detection in _emit",
            marker="[GENUI-OVERLAY] GenUI block detection",
        )

        # 7. Initialize _genui_buffer before the _emit function
        patcher.insert_before(
            anchor='async def _emit(item):',
            insertion=(
                '            # [GENUI-OVERLAY] Buffer for accumulating genui fenced code blocks\n'
                '            _genui_buffer = ""\n'
            ),
            name="Initialize _genui_buffer",
            marker="[GENUI-OVERLAY] Buffer for accumulating genui",
        )

        changed = patcher.write()
        print(patcher.report())
        return changed

    except PatchError as e:
        print(f"  ✗ FAILED: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    success = apply()
    sys.exit(0)
