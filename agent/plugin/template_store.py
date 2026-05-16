"""
GenUI Template Store — Agent-Managed Template CRUD

Mirrors the Hermes skill_manager pattern: templates are persisted as
TEMPLATE.md files with YAML frontmatter under ~/.hermes/genui-templates/.
The agent can create, edit, patch, delete, list, and view templates.

Directory layout:
    ~/.hermes/genui-templates/
    ├── order-confirmation/
    │   └── TEMPLATE.md
    ├── category-name/
    │   └── data-dashboard/
    │       └── TEMPLATE.md
"""

import json
import logging
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def _get_templates_dir() -> Path:
    """Return the templates root directory."""
    hermes_home = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
    return hermes_home / "genui-templates"

VALID_NAME_RE = re.compile(r'^[a-z0-9][a-z0-9._-]*$')
MAX_NAME_LENGTH = 64
MAX_CONTENT_CHARS = 100_000


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _validate_name(name: str) -> Optional[str]:
    if not name:
        return "Template name is required."
    if len(name) > MAX_NAME_LENGTH:
        return f"Template name exceeds {MAX_NAME_LENGTH} characters."
    if not VALID_NAME_RE.match(name):
        return (
            f"Invalid template name '{name}'. Use lowercase letters, numbers, "
            f"hyphens, dots, and underscores. Must start with a letter or digit."
        )
    return None


def _validate_frontmatter(content: str) -> Optional[str]:
    if not content.strip():
        return "Content cannot be empty."
    if not content.startswith("---"):
        return "TEMPLATE.md must start with YAML frontmatter (---)."
    end_match = re.search(r'\n---\s*\n', content[3:])
    if not end_match:
        return "TEMPLATE.md frontmatter is not closed."
    if yaml:
        yaml_content = content[3:end_match.start() + 3]
        try:
            parsed = yaml.safe_load(yaml_content)
        except Exception as e:
            return f"YAML frontmatter parse error: {e}"
        if not isinstance(parsed, dict):
            return "Frontmatter must be a YAML mapping."
        if "name" not in parsed:
            return "Frontmatter must include 'name' field."
        if "description" not in parsed:
            return "Frontmatter must include 'description' field."
    body = content[end_match.end() + 3:].strip()
    if not body:
        return "TEMPLATE.md must have content after the frontmatter."
    return None


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.tmp.")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(temp, path)
    except Exception:
        try:
            os.unlink(temp)
        except OSError:
            pass
        raise


def _find_template(name: str) -> Optional[Path]:
    templates_dir = _get_templates_dir()
    if not templates_dir.exists():
        return None
    for md in templates_dir.rglob("TEMPLATE.md"):
        if md.parent.name == name:
            return md.parent
    return None


def _parse_frontmatter(content: str) -> Dict[str, Any]:
    if not yaml or not content.startswith("---"):
        return {}
    end = re.search(r'\n---\s*\n', content[3:])
    if not end:
        return {}
    try:
        return yaml.safe_load(content[3:end.start() + 3]) or {}
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# Core actions
# ---------------------------------------------------------------------------

def _create_template(name: str, content: str, category: str = None) -> Dict[str, Any]:
    err = _validate_name(name)
    if err:
        return {"success": False, "error": err}
    err = _validate_frontmatter(content)
    if err:
        return {"success": False, "error": err}

    existing = _find_template(name)
    if existing:
        return {"success": False, "error": f"Template '{name}' already exists at {existing}."}

    templates_dir = _get_templates_dir()
    tmpl_dir = templates_dir / category / name if category else templates_dir / name
    tmpl_dir.mkdir(parents=True, exist_ok=True)
    _atomic_write(tmpl_dir / "TEMPLATE.md", content)

    return {
        "success": True,
        "message": f"Template '{name}' created.",
        "path": str(tmpl_dir),
    }


def _edit_template(name: str, content: str) -> Dict[str, Any]:
    err = _validate_frontmatter(content)
    if err:
        return {"success": False, "error": err}
    existing = _find_template(name)
    if not existing:
        return {"success": False, "error": f"Template '{name}' not found."}
    _atomic_write(existing / "TEMPLATE.md", content)
    return {"success": True, "message": f"Template '{name}' updated.", "path": str(existing)}


def _patch_template(name: str, old_string: str, new_string: str) -> Dict[str, Any]:
    if not old_string:
        return {"success": False, "error": "old_string is required."}
    existing = _find_template(name)
    if not existing:
        return {"success": False, "error": f"Template '{name}' not found."}
    md = existing / "TEMPLATE.md"
    content = md.read_text(encoding="utf-8")
    if old_string not in content:
        return {"success": False, "error": f"old_string not found in template '{name}'."}
    new_content = content.replace(old_string, new_string, 1)
    _atomic_write(md, new_content)
    return {"success": True, "message": f"Template '{name}' patched."}


def _delete_template(name: str) -> Dict[str, Any]:
    existing = _find_template(name)
    if not existing:
        return {"success": False, "error": f"Template '{name}' not found."}
    shutil.rmtree(existing)
    # Clean empty parent
    parent = existing.parent
    templates_dir = _get_templates_dir()
    if parent != templates_dir and parent.exists() and not any(parent.iterdir()):
        parent.rmdir()
    return {"success": True, "message": f"Template '{name}' deleted."}


# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------

def template_list(category: str = None) -> str:
    """List all templates with name + description."""
    templates_dir = _get_templates_dir()
    if not templates_dir.exists():
        return json.dumps({"templates": [], "count": 0})

    results = []
    search_dir = templates_dir / category if category else templates_dir
    if not search_dir.exists():
        return json.dumps({"templates": [], "count": 0})

    for md in search_dir.rglob("TEMPLATE.md"):
        content = md.read_text(encoding="utf-8")
        fm = _parse_frontmatter(content)
        results.append({
            "name": fm.get("name", md.parent.name),
            "description": fm.get("description", ""),
            "tags": fm.get("tags", []),
            "path": str(md.parent.relative_to(templates_dir)),
        })

    results.sort(key=lambda x: x["name"])
    return json.dumps({"templates": results, "count": len(results)}, ensure_ascii=False)


def template_view(name: str) -> str:
    """Load full template content."""
    existing = _find_template(name)
    if not existing:
        return json.dumps({"success": False, "error": f"Template '{name}' not found."})
    content = (existing / "TEMPLATE.md").read_text(encoding="utf-8")
    return json.dumps({"success": True, "name": name, "content": content}, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def template_manage(
    action: str,
    name: str,
    content: str = None,
    category: str = None,
    old_string: str = None,
    new_string: str = None,
) -> str:
    """Manage GenUI templates. Dispatches to the appropriate action handler."""
    if action == "create":
        if not content:
            return json.dumps({"success": False, "error": "content is required for 'create'."})
        result = _create_template(name, content, category)
    elif action == "edit":
        if not content:
            return json.dumps({"success": False, "error": "content is required for 'edit'."})
        result = _edit_template(name, content)
    elif action == "patch":
        result = _patch_template(name, old_string or "", new_string or "")
    elif action == "delete":
        result = _delete_template(name)
    else:
        result = {"success": False, "error": f"Unknown action '{action}'. Use: create, edit, patch, delete"}

    return json.dumps(result, ensure_ascii=False)


# ---------------------------------------------------------------------------
# OpenAI Function-Calling Schema
# ---------------------------------------------------------------------------

TEMPLATE_MANAGE_SCHEMA = {
    "name": "template_manage",
    "description": (
        "Manage GenUI component templates (create, edit, patch, delete). "
        "Templates are reusable UI compositions saved as TEMPLATE.md files. "
        "Use this to save novel component arrangements for future reuse."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["create", "edit", "patch", "delete"],
                "description": "The action to perform.",
            },
            "name": {
                "type": "string",
                "description": "Template name (lowercase, hyphens allowed). E.g., 'order-confirmation'.",
            },
            "content": {
                "type": "string",
                "description": "Full TEMPLATE.md content (YAML frontmatter + body). Required for create/edit.",
            },
            "category": {
                "type": "string",
                "description": "Optional category folder. E.g., 'commerce', 'forms'.",
            },
            "old_string": {
                "type": "string",
                "description": "Text to find (for patch).",
            },
            "new_string": {
                "type": "string",
                "description": "Replacement text (for patch).",
            },
        },
        "required": ["action", "name"],
    },
}

TEMPLATE_LIST_SCHEMA = {
    "name": "template_list",
    "description": (
        "List available GenUI component templates with name and description. "
        "Returns a summary of each template for quick browsing."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "Optional category to filter by.",
            },
        },
    },
}

TEMPLATE_VIEW_SCHEMA = {
    "name": "template_view",
    "description": (
        "View the full content of a GenUI template including its JSON schema, "
        "state fields, and usage examples."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Template name to view.",
            },
        },
        "required": ["name"],
    },
}
