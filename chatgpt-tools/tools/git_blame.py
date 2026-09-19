import subprocess


def execute(path: str) -> dict:
    result = subprocess.run(
        ["git", "blame", path],
        capture_output=True, text=True,
    )

    if result.returncode != 0:
        return {
            "in_repository": False,
            "reason": result.stderr.strip(),
            "output": "",
        }

    return {
        "in_repository": True,
        "output": result.stdout or result.stderr,
    }
