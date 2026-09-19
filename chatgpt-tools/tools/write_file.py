from pathlib import Path
from tools.file_utils import file_sha256, transactional_write, verify_edit


def execute(path: str, content: str, expected_sha: str = "") -> dict:
    file_path = Path(path)

    if expected_sha and file_path.exists():
        current_sha = file_sha256(path)
        if current_sha != expected_sha:
            return {
                "error": f"stale file state: expected sha {expected_sha}, got {current_sha}",
            }

    old_content = file_path.read_text() if file_path.exists() else ""

    result_msg = transactional_write(path, content)
    verification = verify_edit(path, old_content, content)

    return {
        "result": result_msg,
        **verification,
    }
