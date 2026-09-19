import subprocess
import sys


def execute(test: str = "") -> str:
    parts = [sys.executable, "-m", "pytest", "-v"]
    if test.strip():
        parts.append(test.strip())

    result = subprocess.run(parts, capture_output=True, text=True)
    return result.stdout + result.stderr
