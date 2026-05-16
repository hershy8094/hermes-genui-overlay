# hermes-genui-overlay

An overlay package that adds **Generative UI (GenUI)** capabilities to [Hermes Agent](https://github.com/NousResearch/hermes-agent) and [Hermes Desktop](https://github.com/fathah/hermes-desktop) — enabling the agent to render interactive React widgets as first-class chat responses.

## Quick Start

```bash
# Clone this repo
git clone https://github.com/hershy8094/hermes-genui-overlay.git
cd hermes-genui-overlay

# Clone dependency repos (hermes-agent + hermes-desktop)
./setup.sh

# Install agent, apply overlay, and launch desktop
./dev.sh
```

That's it — one repo, three commands.

## Architecture

This overlay is designed to survive frequent upstream updates. Changes are separated into three tiers:

| Tier | Conflict Risk | Strategy |
| ------ | -------------- | ---------- |
| **Plugin** | ✅ None | Hermes plugin installed via symlink to `~/.hermes/plugins/genui/` |
| **Standalone files** | ✅ None | New files copied into target repos (no upstream equivalent exists) |
| **Patches** | ⚠️ Low | Marker-based insertions that find stable anchors in core files |

## Directory Structure

``` text
hermes-genui-overlay/          ← this repo (top-level workspace)
├── setup.sh                   ← Clone dependency repos
├── dev.sh                     ← Install + apply + launch
├── apply.sh                   ← Apply overlay patches
├── revert.sh                  ← Clean revert
├── pull-and-patch.sh          ← Pull upstream + re-apply
│
├── hermes-agent/              ← Cloned by setup.sh (gitignored)
├── hermes-desktop/            ← Cloned by setup.sh (gitignored)
│
├── agent/                     ← Backend overlay (hermes-agent)
│   ├── plugin/                ← Zero-conflict hermes plugin
│   │   ├── plugin.yaml
│   │   ├── __init__.py
│   │   ├── genui_protocol.py
│   │   ├── prompt_guidance.py
│   │   └── template_store.py
│   └── patches/               ← Marker-based patches for core files
│       └── *.py
│
├── desktop/                   ← Frontend overlay (hermes-desktop)
│   ├── components/
│   │   ├── genui-types.ts     ← Shared type definitions
│   │   └── genui/
│   │       ├── blockRegistry.ts
│   │       ├── BlockRenderer.tsx
│   │       ├── GenUIWidget.tsx
│   │       └── blocks/        ← 25 composable block components
│   ├── styles/
│   │   ├── genui.css
│   │   └── genui-blocks.css
│   └── patches/
│       └── *.py
│
└── tsconfig.json              ← IDE support (resolves types from hermes-desktop)
```

## Usage

### First-time setup

```bash
./setup.sh   # Clone hermes-agent + hermes-desktop
./dev.sh     # Install + apply + launch
```

### After pulling upstream updates

```bash
./pull-and-patch.sh
```

### Clean revert (restore upstream state)

```bash
./revert.sh
```

### Individual commands

```bash
./dev.sh --apply       # Apply overlay only (no install/launch)
./dev.sh --install     # Install agent from source only
./dev.sh --no-install  # Apply + launch (skip agent install)
./setup.sh --force     # Re-clone dependency repos
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
