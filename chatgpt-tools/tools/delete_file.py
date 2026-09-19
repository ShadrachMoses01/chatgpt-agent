from pathlib import Path


def execute(path: str) -> str:
    file_path = Path(path)

    if not file_path.exists():
        return f"File not found: {path}"

    file_path.unlink()

    return f"Deleted {path}"
