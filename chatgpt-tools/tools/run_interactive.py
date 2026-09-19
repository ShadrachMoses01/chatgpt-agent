import os
import pty
import select
import shlex
import signal
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

DEFAULT_TIMEOUT = 30


def _decode_exit_status(status: int) -> int:
    """Portable replacement for os.waitstatus_to_exitstatus (3.9+ only).

    Returns the process exit code, or a negative signal number when killed
    by a signal (same convention as subprocess return codes).
    """
    if os.WIFEXITED(status):
        return os.WEXITSTATUS(status)
    if os.WIFSIGNALED(status):
        return -os.WTERMSIG(status)
    return status


def execute(command: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    try:
        parts = shlex.split(command)
    except ValueError as e:
        return {"success": False, "error": f"Could not parse command: {e}"}

    if not parts:
        return {"success": False, "error": "Empty command"}

    if parts[0] not in ALLOWED:
        return {
            "success": False,
            "allowed": False,
            "reason": f"Command not allowed: {parts[0]}",
        }

    start = time.time()
    pid, fd = pty.fork()

    if pid == 0:
        os.execvp(parts[0], parts)

    output = bytearray()

    try:
        deadline = start + timeout
        exit_code = None
        while time.time() < deadline:
            r, _, _ = select.select([fd], [], [], 1.0)
            if r:
                try:
                    data = os.read(fd, 4096)
                    if data:
                        output.extend(data)
                    # Empty read or OSError (EIO once the child side of the
                    # pty is closed): fall through to the waitpid check
                    # below instead of abandoning the loop.
                except OSError:
                    pass

            wpid, status = os.waitpid(pid, os.WNOHANG)
            if wpid == pid:
                exit_code = _decode_exit_status(status)
                break

        if exit_code is None:
            # Deadline reached with the child still alive: kill it below
            # and report a timeout.
            raise TimeoutError(f"Process timed out after {timeout}s")

        # Drain any output that arrived between the last read and exit,
        # without blocking: the pty master raises OSError once drained.
        while True:
            rr, _, _ = select.select([fd], [], [], 0.2)
            if not rr:
                break
            try:
                data = os.read(fd, 4096)
                if not data:
                    break
                output.extend(data)
            except OSError:
                break

        try:
            os.close(fd)
        except OSError:
            pass
        return {
            "success": True,
            "exit_code": exit_code,
            "output": output.decode("utf-8", errors="replace"),
            "timed_out": False,
            "duration": round(time.time() - start, 2),
        }
    except Exception:
        pass

    try:
        os.kill(pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        pass
    try:
        os.waitpid(pid, 0)
    except (ChildProcessError, OSError):
        pass
    try:
        os.close(fd)
    except OSError:
        pass

    return {
        "success": True,
        "timed_out": True,
        "output": output.decode("utf-8", errors="replace"),
        "duration": round(time.time() - start, 2),
        "message": f"Process terminated after {timeout}s timeout.",
    }
