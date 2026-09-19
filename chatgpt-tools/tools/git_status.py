import subprocess


def execute() -> dict:
    result = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return {
            "in_repository": False,
            "reason": result.stderr.strip(),
            "output": "",
        }

    return {
        "in_repository": True,
        "output": result.stdout,
    }
