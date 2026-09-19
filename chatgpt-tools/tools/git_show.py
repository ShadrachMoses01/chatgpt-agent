import subprocess


def execute(commit: str) -> dict:
    result = subprocess.run(
        ["git", "show", commit, "--stat"],
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
