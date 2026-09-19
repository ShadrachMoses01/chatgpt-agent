from pathlib import Path
from tools.file_utils import transactional_write, verify_edit


def execute(path: str, content: str) -> dict:
    file_path = Path(path)

    if file_path.exists():
        return {"result": f"File already exists: {path}"}

    result_msg = transactional_write(path, content)
    verification = verify_edit(path, "", content)

    return {
        "result": result_msg,
        **verification,
    }
