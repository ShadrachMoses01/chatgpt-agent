import ast
from pathlib import Path


_DESCRIPTIONS = {
    "main.py": "entrypoint",
    "clipboard_runner.py": "clipboard-based execution",
    "dispatcher": "routing",
    "protocol": "xml handling",
    "models": "data models",
    "tools": "tool implementations",
    "tests": "validation",
    "workspace": "sandbox",
    "prompt.txt": "agent system prompt",
}


_SKIP_DIRS = {
    "__pycache__", ".git", ".venv", ".pytest_cache",
}

_SKIP_FILES = {
    ".DS_Store",
}

_SKIP_DIR_CONTENTS = {
    "logs", ".git", ".venv", "__pycache__", ".pytest_cache",
}


def _read_module_level_doc(filepath: Path):
    try:
        tree = ast.parse(filepath.read_text())
        if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant):
            return tree.body[0].value.value.split("\n")[0].strip()
    except Exception:
        pass
    return None


def _entry_name(filepath: Path):
    doc = _read_module_level_doc(filepath)
    if doc:
        return doc
    origin = _DESCRIPTIONS.get(filepath.stem)
    if origin:
        return origin
    return filepath.stem.replace("_", " ")


def _should_list(name: str) -> bool:
    if name.startswith("."):
        return False
    if name in _SKIP_DIRS:
        return False
    if name in _SKIP_FILES:
        return False
    return True


def execute() -> str:
    lines = []
    base = Path(".")

    top_order = [
        "main.py",
        "clipboard_runner.py",
        "prompt.txt",
        "models",
        "protocol",
        "dispatcher",
        "tools",
        "tests",
        "workspace",
    ]

    seen = set()
    for name in top_order:
        p = base / name
        if not p.exists():
            continue
        seen.add(name)
        entry = _entry_name(p) if p.is_file() else name
        lines.append(f"{name}  ({entry})")

        if p.is_dir() and name not in _SKIP_DIR_CONTENTS:
            for child in sorted(p.iterdir()):
                if _should_list(child.name):
                    lines.append(f"  {child.name}")

    for entry in sorted(base.iterdir()):
        name = entry.name
        if name.startswith("."):
            continue
        if name in seen:
            continue
        if name.endswith(".backup") or name.endswith(".bak"):
            continue
        if name in _SKIP_DIRS:
            continue
        desc = _entry_name(entry)
        lines.append(f"{name}  ({desc})")

    return "\n".join(lines)
