import difflib
import ast
from pathlib import Path

from tools.file_utils import file_sha256, transactional_write, verify_edit
from tools.ast_utils import find_function_nodes


def execute(
    path: str,
    symbol: str,
    expected_sha: str = "",
) -> dict:
    file_path = Path(path)

    if not file_path.exists():
        return {"error": f"File not found: {path}"}

    if expected_sha:
        current_sha = file_sha256(path)
        if current_sha != expected_sha:
            return {
                "error": f"stale file state: expected sha {expected_sha}, got {current_sha}",
            }

    source = file_path.read_text()
    lines = source.split("\n")

    tree = ast.parse(source)

    matches = find_function_nodes(tree, symbol)

    if not matches:
        available = [node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
        similar = difflib.get_close_matches(symbol, available, n=5, cutoff=0.3)
        parts = [f"Function '{symbol}' not found in {path}"]
        if available:
            parts.append(f"  Available functions ({len(available)}): {', '.join(available[:10])}")
            if len(available) > 10:
                parts[-1] += f" ... and {len(available) - 10} more"
        if similar:
            parts.append(f"  Closest matches: {', '.join(similar)}")
        if "." in symbol:
            parts.append(f"  Hint: Use plain function names (e.g. '{symbol.split('.')[0]}'). Methods are not indexed.")
        return {"error": "\n".join(parts)}

    if len(matches) > 1:
        return {
            "error": (
                f"Ambiguous function name '{symbol}' "
                f"({len(matches)} matches found). Use a more specific name."
            )
        }

    target_node = matches[0]

    start = target_node.lineno - 1
    end = target_node.end_lineno

    new_source = "\n".join(lines[:start] + lines[end:])

    result_msg = transactional_write(path, new_source)
    verification = verify_edit(path, source, new_source)

    return {
        "result": result_msg,
        "symbol": symbol,
        **verification,
    }
