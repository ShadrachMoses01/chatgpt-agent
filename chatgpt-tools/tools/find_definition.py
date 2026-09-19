import difflib
import ast
from pathlib import Path

from tools.ast_utils import find_python_files


def execute(symbol: str) -> str:
    all_symbols = {}
    for filepath in find_python_files():
        try:
            tree = ast.parse(Path(filepath).read_text())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == symbol:
                return f"{filepath}:{node.lineno}"
            if isinstance(node, ast.ClassDef) and node.name == symbol:
                return f"{filepath}:{node.lineno}"
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == symbol:
                        return f"{filepath}:{node.lineno}"
            # Collect symbol names for error context
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                all_symbols[node.name] = filepath
            elif isinstance(node, ast.ClassDef):
                all_symbols[node.name] = filepath

    similar = difflib.get_close_matches(symbol, list(all_symbols.keys()), n=5, cutoff=0.3)
    parts = [f"Definition not found for '{symbol}'"]
    if all_symbols:
        parts.append(f"  Total symbols found: {len(all_symbols)}")
    if similar:
        parts.append(f"  Closest matches: {', '.join(similar)}")
    if "." in symbol:
        parts.append(f"  Hint: Use plain symbol names (e.g. '{symbol.split('.')[0]}'). Methods are not indexed.")
    return "\n".join(parts)
