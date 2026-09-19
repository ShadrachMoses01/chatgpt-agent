import subprocess


def execute() -> dict:
    result = subprocess.run(
        ["git", "diff"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return {
            "in_repository": False,
            "reason": result.stderr.strip(),
            "diff": "",
        }

    return {
        "in_repository": True,
        "diff": result.stdout,
    }
