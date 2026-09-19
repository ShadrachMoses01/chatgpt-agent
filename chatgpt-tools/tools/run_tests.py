import subprocess
import sys


def execute() -> str:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-v"],
        capture_output=True,
        text=True,
    )

    return result.stdout + result.stderr
