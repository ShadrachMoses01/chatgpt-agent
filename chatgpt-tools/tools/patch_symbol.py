import difflib
import ast
import textwrap
from pathlib import Path

from tools.file_utils import file_sha256, transactional_write, verify_edit
from tools.ast_utils import find_function_nodes


def execute(path: str, symbol: str, content: str, expected_sha: str = "") -> dict:
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
    content = content.replace("\r\n", "\n").replace("\r", "\n")

    tree = ast.parse(source)
    matches = find_function_nodes(tree, symbol)

    if not matches:
        # Collect available symbols for helpful error
        available = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                available.append(node.name)
            elif isinstance(node, ast.ClassDef):
                available.append(node.name)
        similar = difflib.get_close_matches(symbol, available, n=5, cutoff=0.3)

        parts = [f"Symbol '{symbol}' not found in {path}"]
        if available:
            parts.append(f"  Available symbols ({len(available)}): {', '.join(available[:10])}")
            if len(available) > 10:
                parts[-1] += f" ... and {len(available) - 10} more"
        if similar:
            parts.append(f"  Closest matches: {', '.join(similar)}")
        if "." in symbol:
            parts.append(f"  Hint: Use plain symbol names (e.g. '{symbol.split('.')[0]}'). Methods are not indexed.")
        return {"error": "\n".join(parts)}

    if len(matches) > 1:
        return {
            "error": f"Ambiguous symbol name '{symbol}' ({len(matches)} matches found). Use a more specific name.",
        }

    target = matches[0]
    start = target.lineno - 1
    end = target.end_lineno
    lines = source.split("\n")

    if target.col_offset == 0:
        content = textwrap.dedent(content).strip()
    else:
        content = content.strip("\n")

    new_lines = content.split("\n")
    new_source = "\n".join(lines[:start] + new_lines + lines[end:])

    try:
        ast.parse(new_source)
    except SyntaxError as e:
        return {"error": f"Replacement has invalid syntax: {e}"}

    result_msg = transactional_write(path, new_source)
    verification = verify_edit(path, source, new_source)

    return {
        "result": result_msg,
        "symbol": symbol,
        **verification,
    }
