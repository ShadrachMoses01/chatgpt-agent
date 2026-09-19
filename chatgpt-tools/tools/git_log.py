import subprocess


def execute(limit: str = "10") -> dict:
    try:
        count = max(1, min(int(str(limit).strip()), 100))
    except (ValueError, TypeError):
        return {
            "in_repository": True,
            "reason": f"Invalid limit: {limit!r} (expected an integer 1-100)",
            "output": "",
        }

    result = subprocess.run(
        ["git", "log", f"--max-count={count}", "--oneline"],
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
