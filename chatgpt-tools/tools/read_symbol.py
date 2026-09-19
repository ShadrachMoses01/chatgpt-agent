import difflib
import ast
from pathlib import Path

from tools.ast_utils import find_python_files


def _find_symbols_in_files(files: list[str]) -> dict[str, list[tuple[str, str, int]]]:
    """Collect all function and class names across files.
    Returns {filepath: [(name, kind, lineno)]}."""
    index = {}
    for filepath in files:
        try:
            tree = ast.parse(Path(filepath).read_text())
        except SyntaxError:
            continue
        entries = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                entries.append((node.name, "function", node.lineno))
            elif isinstance(node, ast.ClassDef):
                entries.append((node.name, "class", node.lineno))
        if entries:
            index[filepath] = entries
    return index


def execute(symbol: str, path: str = "") -> dict:
    files = [path] if path else find_python_files()

    for filepath in files:
        try:
            tree = ast.parse(Path(filepath).read_text())
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == symbol:
                lines = Path(filepath).read_text().split("\n")
                source = "\n".join(lines[node.lineno - 1:node.end_lineno])
                return {
                    "symbol": symbol,
                    "kind": "function",
                    "file": filepath,
                    "line": node.lineno,
                    "source": source,
                }

            if isinstance(node, ast.ClassDef) and node.name == symbol:
                lines = Path(filepath).read_text().split("\n")
                source = "\n".join(lines[node.lineno - 1:node.end_lineno])
                return {
                    "symbol": symbol,
                    "kind": "class",
                    "file": filepath,
                    "line": node.lineno,
                    "source": source,
                }

    # Build helpful error context
    index = _find_symbols_in_files(files)
    all_symbols = [name for entries in index.values() for name, _, _ in entries]
    similar = difflib.get_close_matches(symbol, all_symbols, n=5, cutoff=0.3)
    total_files_searched = len(files)
    total_symbols_found = len(all_symbols)

    parts = [f"Symbol '{symbol}' not found"]
    if path:
        parts.append(f"  Searched: {path}")
    else:
        parts.append(f"  Searched: {total_files_searched} Python files")
    parts.append(f"  Total symbols found: {total_symbols_found}")
    if similar:
        parts.append(f"  Closest matches: {', '.join(similar)}")
    if "." in symbol:
        parts.append(f"  Hint: Symbol names should be plain (e.g. '{symbol.split('.')[0]}'), not qualified (e.g. '{symbol}'). Methods are not indexed.")
    return {"error": "\n".join(parts)}
