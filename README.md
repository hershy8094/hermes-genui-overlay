# hermes-genui-overlay

An overlay package that adds **Generative UI (GenUI)** capabilities to [Hermes Agent](https://github.com/NousResearch/hermes-agent) and [Hermes Desktop](https://github.com/fathah/hermes-desktop) — enabling the agent to render interactive React widgets as first-class chat responses.

## Architecture

This overlay is designed to survive frequent upstream updates. Changes are separated into three tiers:

| Tier | Conflict Risk | Strategy |
|------|--------------|----------|
| **Plugin** | ✅ None | Hermes plugin installed via symlink to `~/.hermes/plugins/genui/` |
| **Standalone files** | ✅ None | New files copied into target repos (no upstream equivalent exists) |
| **Patches** | ⚠️ Low | Marker-based insertions that find stable anchors in core files |

## Directory Structure

```
hermes-genui-overlay/
├── apply.sh              ← Master apply script
├── revert.sh             ← Clean revert script
├── pull-and-patch.sh     ← Pull upstream + re-apply
│
├── agent/                ← Backend overlay (hermes-agent)
│   ├── plugin/           ← Zero-conflict hermes plugin
│   │   ├── plugin.yaml
│   │   ├── __init__.py
│   │   ├── genui_protocol.py
│   │   └── prompt_guidance.py
│   └── patches/          ← Marker-based patches for core files
│       └── *.py          ← Patch scripts (not raw diffs)
│
└── desktop/              ← Frontend overlay (hermes-desktop)
    ├── components/       ← Standalone files (copy-in)
    │   ├── genui-types.ts
    │   └── genui/
    └── patches/          ← Marker-based patches for core files
        └── *.py          ← Patch scripts (not raw diffs)
```

## Prerequisites

- `hermes-agent` and `hermes-desktop` cloned as siblings:
  ```
  parent-dir/
  ├── hermes-agent/
  ├── hermes-desktop/
  └── hermes-genui-overlay/   ← this repo
  ```

## Usage

### First-time setup

```bash
./apply.sh
```

### After pulling upstream updates

```bash
./pull-and-patch.sh
```

### Clean revert (restore upstream state)

```bash
./revert.sh
```

## How Patches Work

Instead of fragile `git diff` patches that break when line numbers shift, this overlay uses **marker-based patching**: Python scripts that find stable code anchors (function signatures, dictionary keys, import blocks) and insert/modify code relative to those anchors. This approach survives upstream refactors as long as the anchor patterns remain.

Each patch script:
1. Reads the target file
2. Finds a stable anchor pattern (regex or literal)
3. Inserts, appends, or wraps code relative to the anchor
4. Writes the modified file
5. Reports success/failure with clear diagnostics

If an anchor is not found (upstream removed or renamed it), the patch fails loudly with instructions for manual resolution.

## License

MIT
