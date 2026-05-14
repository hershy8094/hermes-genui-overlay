"""
Marker-based patching utilities for hermes-genui-overlay.

Instead of fragile git-diff patches that break when line numbers shift,
we find stable code anchors (function signatures, dict keys, import blocks)
and insert/modify code relative to those anchors.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Optional


class PatchError(Exception):
    """Raised when a patch cannot be applied."""
    pass


class FilePatcher:
    """Reads a file, applies marker-based patches, and writes back."""

    def __init__(self, filepath: str | Path):
        self.filepath = Path(filepath)
        if not self.filepath.exists():
            raise PatchError(f"Target file not found: {self.filepath}")
        self.original = self.filepath.read_text(encoding="utf-8")
        self.content = self.original
        self.applied: list[str] = []
        self.skipped: list[str] = []

    # ── Core patch operations ──

    def insert_after(
        self,
        anchor: str,
        insertion: str,
        *,
        name: str = "",
        marker: str = "",
        regex: bool = False,
    ) -> "FilePatcher":
        """Insert text after the first line matching `anchor`.

        If `marker` is set, checks whether the marker already exists in the
        file and skips if so (idempotent).
        """
        if marker and marker in self.content:
            self.skipped.append(name or f"insert_after({anchor[:40]}...)")
            return self

        lines = self.content.split("\n")
        found = False
        for i, line in enumerate(lines):
            match = (re.search(anchor, line) if regex else anchor in line)
            if match:
                # Insert after this line, preserving indentation
                indent = re.match(r"^(\s*)", line).group(1)
                # Add the insertion lines with the same base indent
                insert_lines = insertion.split("\n")
                for j, ins_line in enumerate(insert_lines):
                    lines.insert(i + 1 + j, ins_line)
                found = True
                break

        if not found:
            raise PatchError(
                f"Anchor not found for '{name or 'insert_after'}':\n"
                f"  Pattern: {anchor}\n"
                f"  File: {self.filepath}\n"
                f"  → Upstream may have changed this code. Manual resolution needed."
            )

        self.content = "\n".join(lines)
        self.applied.append(name or f"insert_after({anchor[:40]}...)")
        return self

    def insert_before(
        self,
        anchor: str,
        insertion: str,
        *,
        name: str = "",
        marker: str = "",
        regex: bool = False,
    ) -> "FilePatcher":
        """Insert text before the first line matching `anchor`."""
        if marker and marker in self.content:
            self.skipped.append(name or f"insert_before({anchor[:40]}...)")
            return self

        lines = self.content.split("\n")
        found = False
        for i, line in enumerate(lines):
            match = (re.search(anchor, line) if regex else anchor in line)
            if match:
                insert_lines = insertion.split("\n")
                for j, ins_line in enumerate(insert_lines):
                    lines.insert(i + j, ins_line)
                found = True
                break

        if not found:
            raise PatchError(
                f"Anchor not found for '{name or 'insert_before'}':\n"
                f"  Pattern: {anchor}\n"
                f"  File: {self.filepath}\n"
                f"  → Upstream may have changed this code. Manual resolution needed."
            )

        self.content = "\n".join(lines)
        self.applied.append(name or f"insert_before({anchor[:40]}...)")
        return self

    def append_to_dict(
        self,
        dict_anchor: str,
        key: str,
        value: str,
        *,
        name: str = "",
        marker: str = "",
    ) -> "FilePatcher":
        """Add a key-value pair to a Python dict literal.

        Finds the dict anchor (e.g. 'PLATFORM_HINTS = {') and inserts the
        new entry before the closing brace.
        """
        if marker and marker in self.content:
            self.skipped.append(name or f"append_to_dict({key})")
            return self

        # Find the dict block and its closing brace
        anchor_idx = self.content.find(dict_anchor)
        if anchor_idx == -1:
            raise PatchError(
                f"Dict anchor not found for '{name or 'append_to_dict'}':\n"
                f"  Pattern: {dict_anchor}\n"
                f"  File: {self.filepath}"
            )

        # Find the matching closing brace
        brace_depth = 0
        search_start = self.content.index("{", anchor_idx)
        for i in range(search_start, len(self.content)):
            if self.content[i] == "{":
                brace_depth += 1
            elif self.content[i] == "}":
                brace_depth -= 1
                if brace_depth == 0:
                    # Insert before this closing brace
                    entry = f'    {key}: {value},\n'
                    self.content = (
                        self.content[:i] + entry + self.content[i:]
                    )
                    self.applied.append(name or f"append_to_dict({key})")
                    return self

        raise PatchError(f"Could not find closing brace for dict at '{dict_anchor}'")

    def append_to_imports(
        self,
        module: str,
        names: list[str],
        *,
        name: str = "",
        marker: str = "",
    ) -> "FilePatcher":
        """Add names to an existing 'from module import ...' statement.

        If the import doesn't exist, creates a new one after the last import block.
        """
        check_name = names[0] if names else ""
        if marker and marker in self.content:
            self.skipped.append(name or f"append_to_imports({module})")
            return self
        # Check if already imported
        if check_name and re.search(rf'\b{re.escape(check_name)}\b', self.content):
            self.skipped.append(name or f"append_to_imports({module}) - already present")
            return self

        # Try to find existing import from the same module
        # Handle multi-line imports: from module import (\n    name1,\n    name2,\n)
        pattern = rf'^(\s*from\s+{re.escape(module)}\s+import\s+)'
        lines = self.content.split("\n")
        for i, line in enumerate(lines):
            if re.match(pattern, line):
                # Found existing import — check if it's multi-line
                if "(" in line:
                    # Multi-line import — find the closing paren
                    for j in range(i, len(lines)):
                        if ")" in lines[j]:
                            # Insert before closing paren
                            indent = "    "
                            new_names = ",\n".join(f"{indent}{n}" for n in names)
                            lines[j] = lines[j].replace(")", f"{new_names},\n)")
                            self.content = "\n".join(lines)
                            self.applied.append(name or f"append_to_imports({module})")
                            return self
                else:
                    # Single-line import — append names
                    names_str = ", ".join(names)
                    lines[i] = lines[i].rstrip().rstrip(",") + f", {names_str}"
                    self.content = "\n".join(lines)
                    self.applied.append(name or f"append_to_imports({module})")
                    return self

        # No existing import — create new one after last import block
        names_str = ", ".join(names)
        new_import = f"from {module} import {names_str}"
        last_import_idx = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                last_import_idx = i
            elif stripped.startswith(")") and last_import_idx == i - 1:
                last_import_idx = i  # closing paren of multi-line import

        lines.insert(last_import_idx + 1, new_import)
        self.content = "\n".join(lines)
        self.applied.append(name or f"append_to_imports({module})")
        return self

    def replace_pattern(
        self,
        pattern: str,
        replacement: str,
        *,
        name: str = "",
        marker: str = "",
        count: int = 1,
    ) -> "FilePatcher":
        """Replace a regex pattern with replacement text."""
        if marker and marker in self.content:
            self.skipped.append(name or f"replace_pattern({pattern[:40]}...)")
            return self

        new_content, n = re.subn(pattern, replacement, self.content, count=count)
        if n == 0:
            raise PatchError(
                f"Pattern not found for '{name or 'replace_pattern'}':\n"
                f"  Pattern: {pattern}\n"
                f"  File: {self.filepath}"
            )
        self.content = new_content
        self.applied.append(name or f"replace_pattern({pattern[:40]}...)")
        return self

    def append_to_file(
        self,
        content: str,
        *,
        name: str = "",
        marker: str = "",
    ) -> "FilePatcher":
        """Append content to the end of the file."""
        if marker and marker in self.content:
            self.skipped.append(name or "append_to_file")
            return self

        if not self.content.endswith("\n"):
            self.content += "\n"
        self.content += content
        self.applied.append(name or "append_to_file")
        return self

    # ── Write and report ──

    def write(self) -> bool:
        """Write modified content back to file. Returns True if changed."""
        if self.content == self.original:
            return False
        self.filepath.write_text(self.content, encoding="utf-8")
        return True

    def report(self) -> str:
        """Generate a human-readable report of what was applied."""
        lines = [f"  File: {self.filepath.name}"]
        for a in self.applied:
            lines.append(f"    ✓ {a}")
        for s in self.skipped:
            lines.append(f"    ⏭ {s} (already applied)")
        if not self.applied and not self.skipped:
            lines.append("    (no patches matched)")
        return "\n".join(lines)


def resolve_sibling(overlay_dir: Path, repo_name: str) -> Path:
    """Resolve sibling repo path relative to the overlay directory."""
    sibling = overlay_dir.parent / repo_name
    if not sibling.exists():
        print(f"ERROR: Expected sibling repo not found: {sibling}", file=sys.stderr)
        print(f"  Overlay dir: {overlay_dir}", file=sys.stderr)
        print(f"  Expected layout:", file=sys.stderr)
        print(f"    {overlay_dir.parent}/", file=sys.stderr)
        print(f"    ├── hermes-agent/", file=sys.stderr)
        print(f"    ├── hermes-desktop/", file=sys.stderr)
        print(f"    └── hermes-genui-overlay/  ← you are here", file=sys.stderr)
        sys.exit(1)
    return sibling
