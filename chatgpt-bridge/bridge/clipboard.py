import shutil
import subprocess


def _require_cmd(name: str):
    if shutil.which(name) is None:
        raise RuntimeError(
            f"Clipboard command {name!r} not found. "
            "The clipboard bridge currently supports macOS only (pbpaste/pbcopy)."
        )


def read() -> str:
    _require_cmd("pbpaste")
    return subprocess.check_output(
        ["pbpaste"],
        text=True,
        timeout=5,
    )


def write(text: str):
    _require_cmd("pbcopy")
    subprocess.run(
        ["pbcopy"],
        input=text,
        text=True,
        check=True,
        timeout=5,
    )
