from pathlib import Path
from tools.file_utils import file_sha256


def execute(path: str, start: int = None, end: int = None) -> dict:
    content = Path(path).read_text()
    lines = content.split("\n")

    if start is not None:
        start = max(1, int(start))
        if end is not None:
            end = min(int(end), len(lines))
        else:
            end = len(lines)
        content = "\n".join(lines[start - 1:end])

    resolved = str(Path(path).resolve())
    return {
        "content": content,
        "sha256": file_sha256(path),
        "path": resolved,
        "total_lines": len(lines),
    }
