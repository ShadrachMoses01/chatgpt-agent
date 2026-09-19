import shlex
import subprocess
import time


ALLOWED = {
    "python",
    "python3",
    "pytest",
    "git",
    "uv",
    "npm",
    "pnpm",
}

DEFAULT_TIMEOUT = 5


def execute(command: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    parts = shlex.split(command)

    if not parts:
        return {"success": False, "error": "Empty command"}

    if parts[0] not in ALLOWED:
        return {
            "success": False,
            "allowed": False,
            "reason": f"Command not allowed: {parts[0]}",
        }

    start = time.time()
    proc = subprocess.Popen(
        parts,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        stdout, stderr = proc.communicate(timeout=timeout)
        duration = time.time() - start
        return {
            "success": True,
            "exit_code": proc.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "timed_out": False,
            "duration": round(duration, 2),
        }
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        duration = time.time() - start
        return {
            "success": True,
            "timed_out": True,
            "stdout": stdout or "",
            "stderr": stderr or "",
            "duration": round(duration, 2),
            "message": f"Process terminated after {timeout}s timeout.",
        }
