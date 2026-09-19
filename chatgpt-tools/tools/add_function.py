import difflib
import ast
from pathlib import Path

from tools.file_utils import file_sha256, transactional_write, verify_edit


def execute(
    path: str,
    content: str,
    after: str = "",
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

    if after:
        tree = ast.parse(source)
        insert_line = None
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == after:
                insert_line = node.end_lineno
                break
        if insert_line is None:
            available = [node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
            similar = difflib.get_close_matches(after, available, n=5, cutoff=0.3)
            parts = [f"Symbol '{after}' not found in {path}"]
            if available:
                parts.append(f"  Available symbols ({len(available)}): {', '.join(available[:10])}")
                if len(available) > 10:
                    parts[-1] += f" ... and {len(available) - 10} more"
            if similar:
                parts.append(f"  Closest matches: {', '.join(similar)}")
            return {"error": "\n".join(parts)}
        # add a blank line before the new function
        new_source = "\n".join(
            lines[:insert_line] + [""] + content.split("\n") + lines[insert_line:]
        )
    else:
        new_source = source + "\n\n" + content

    try:
        ast.parse(new_source)
    except SyntaxError as e:
        return {"error": f"Addition has invalid syntax: {e}"}

    result_msg = transactional_write(path, new_source)
    verification = verify_edit(path, source, new_source)

    return {
        "result": result_msg,
        **verification,
    }
