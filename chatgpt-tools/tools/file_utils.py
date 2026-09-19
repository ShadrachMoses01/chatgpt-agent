import ast
import hashlib
import os
import tempfile
from pathlib import Path


def sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def file_sha256(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _py_suffix(path: str) -> bool:
    return Path(path).suffix.lower() in {".py", ".pyw", ".pyx"}


def validate_syntax(content: str) -> tuple[bool, str]:
    try:
        ast.parse(content)
        return True, "OK"
    except SyntaxError as e:
        return False, str(e)


def validate_imports(content: str, filepath: str = "<string>") -> tuple[bool, str]:
    """Compile-check the content.

    NOTE: ``compile()`` only catches syntax errors; it cannot verify that
    imports are actually resolvable without executing the code.
    """
    try:
        compile(content, filepath, "exec")
        return True, "OK"
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)


def transactional_write(path: str, content: str):
    """Write via temp file + atomic rename. Returns result message.

    A unique temp file in the same directory is used so concurrent writes
    to the same path cannot clobber each other's temp file, and the final
    ``os.replace`` is atomic on POSIX.
    """
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(file_path.parent),
        prefix=file_path.name + ".",
        suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_name, file_path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
    return f"Wrote {path}"


def verify_edit(path: str, old_content: str, new_content: str) -> dict:
    if _py_suffix(path):
        s_ok, s_msg = validate_syntax(new_content)
        i_ok, i_msg = validate_imports(new_content, path)
    else:
        s_ok, s_msg = True, ""
        i_ok, i_msg = True, ""

    old_lines = old_content.count("\n")
    new_lines = new_content.count("\n")
    diff_size = abs(new_lines - old_lines)

    return {
        "syntax_ok": str(s_ok).lower(),
        "syntax_msg": "" if s_ok else s_msg,
        "imports_ok": str(i_ok).lower(),
        "import_msg": "" if i_ok else i_msg,
        "diff_size": str(diff_size),
    }
