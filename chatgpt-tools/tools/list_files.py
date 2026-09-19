from pathlib import Path


def execute(path: str):

    files = []

    for item in Path(path).iterdir():
        files.append(str(item))

    return "\n".join(files)
