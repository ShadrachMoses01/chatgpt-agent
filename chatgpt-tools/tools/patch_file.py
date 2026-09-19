import difflib
from pathlib import Path
from tools.file_utils import file_sha256, transactional_write, verify_edit


def _find_similar(text: str, target: str, max_suggestions: int = 3) -> list[tuple[str, float]]:
    words = set(text.split())
    matches = difflib.get_close_matches(target, words, n=max_suggestions, cutoff=0.4)
    return matches


def _count_occurrences(text: str, target: str) -> int:
    return text.count(target)


def _describe_search(find: str, old_content: str) -> str:
    lines = old_content.split("\n")
    partial_matches = [l for l in lines if find.lower() in l.lower()]
    similar = _find_similar(old_content, find)

    parts = [f"Text '{find}' not found in {len(lines)} lines"]
    if partial_matches:
        parts.append(f"  Partial matches (case-insensitive): {len(partial_matches)}")
        for m in partial_matches[:3]:
            parts.append(f"    - {m.strip()[:80]}")
    if similar:
        parts.append(f"  Closest matches: {', '.join(similar)}")
    return "\n".join(parts)


def execute(path: str, find: str, replace: str, expected_sha: str = "") -> dict:
    file_path = Path(path)

    if not file_path.exists():
        return {"result": f"File not found: {path}"}

    if expected_sha:
        current_sha = file_sha256(path)
        if current_sha != expected_sha:
            return {
                "error": f"stale file state: expected sha {expected_sha}, got {current_sha}",
            }

    old_content = file_path.read_text()

    if find not in old_content:
        return {"result": _describe_search(find, old_content)}

    updated = old_content.replace(find, replace, 1)

    result_msg = transactional_write(path, updated)
    verification = verify_edit(path, old_content, updated)

    return {
        "result": result_msg,
        **verification,
    }
