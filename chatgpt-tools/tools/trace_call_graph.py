import ast
from pathlib import Path

from tools.ast_utils import find_python_files, get_function_body, classify_symbol


_MAX_DEPTH = 5


def _get_full_path(func_name, root="."):
    for filepath in find_python_files(root):
        try:
            tree = ast.parse(Path(filepath).read_text())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
                return filepath
    return None


def _resolve_callee_file(callee, current_file, root="."):
    filepath = _get_full_path(callee, root)
    if filepath:
        return filepath

    if current_file:
        try:
            tree = ast.parse(Path(current_file).read_text())
        except SyntaxError:
            return None
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == callee or (alias.asname and alias.asname == callee):
                        if node.module:
                            mod_path = node.module.replace(".", "/")
                            for candidate in [f"{mod_path}.py", f"{mod_path}/__init__.py"]:
                                if Path(candidate).exists():
                                    return candidate
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == callee or (alias.asname and alias.asname == callee):
                        for candidate in [f"{callee}.py", f"{callee}/__init__.py"]:
                            if Path(candidate).exists():
                                return candidate

    return None


def _trace(func_name, depth=0, visited=None, root=".", current_file=None):
    if visited is None:
        visited = set()

    if depth > _MAX_DEPTH or func_name in visited:
        return []

    visited.add(func_name)
    result = []
    indent = "  " * depth

    callee_file = _resolve_callee_file(func_name, current_file, root)
    if not callee_file:
        kind = classify_symbol(func_name)
        tag = {"builtin": "builtin", "stdlib": "stdlib module"}.get(kind, "not found in project")
        return [f"{indent}{func_name} ({tag})"]

    body = get_function_body(callee_file, func_name)
    if body is None:
        return [f"{indent}{func_name} (unparsable)"]

    import ast as _ast
    calls_seen = set()
    for child in _ast.walk(body):
        if isinstance(child, _ast.Call):
            callee = None
            if isinstance(child.func, _ast.Name):
                callee = child.func.id
            elif isinstance(child.func, _ast.Attribute):
                callee = child.func.attr
            if callee and callee not in calls_seen and callee != func_name:
                calls_seen.add(callee)
                sub = _trace(callee, depth + 1, visited, root, callee_file)
                result.append(f"{indent}{func_name} -> {callee}")
                result.extend(sub)

    if not calls_seen:
        result.append(f"{indent}{func_name}")

    return result


def execute(symbol: str) -> str:
    lines = _trace(symbol, root=".")
    if not lines:
        return f"No call graph found for '{symbol}'"
    return "\n".join(lines)
