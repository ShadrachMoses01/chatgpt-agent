import ast
import subprocess
from pathlib import Path


def _check_syntax(filepath: str):
    try:
        ast.parse(Path(filepath).read_text())
        return "OK"
    except SyntaxError as e:
        return f"SyntaxError: {e}"


def _check_imports(filepath: str):
    """Compile-check the file.

    NOTE: ``compile()`` only catches syntax errors; it cannot verify that
    imports are actually resolvable without executing the code, so a return
    value of "OK" means "compiles", not "imports resolve".
    """
    try:
        compile(Path(filepath).read_text(), filepath, "exec")
        return "OK"
    except SyntaxError as e:
        return f"SyntaxError: {e}"
    except Exception as e:
        return f"Warning: {e}"


def _find_impacted_tests(filepath: str):
    filename = Path(filepath).stem
    try:
        result = subprocess.run(
            ["rg", "-l", filename, "tests/"],
            capture_output=True, text=True,
        )
    except FileNotFoundError:
        result = None
    files = [f for f in result.stdout.strip().split("\n") if f] if result else []
    if not files:
        # try to infer test file from module name
        module = Path(filepath).parent.name if Path(filepath).parent.name != "." else ""
        test_file = f"tests/test_{filename}.py"
        if Path(test_file).exists():
            files = [test_file]
    return files if files else ["none inferred"]


def execute(path: str) -> str:
    if not Path(path).exists():
        return f"File not found: {path}"

    syntax = _check_syntax(path)
    imports = _check_imports(path)
    impacted = _find_impacted_tests(path)

    parts = [
        f"File: {path}",
        f"Syntax: {syntax}",
        f"Imports: {imports}",
        f"Impacted tests: {', '.join(impacted)}",
    ]

    if syntax == "OK" and imports == "OK":
        parts.append("Verdict: CHECKS PASSED (syntax + compile only; tests not run)")
    else:
        parts.append("Verdict: CHECKS FAILED (see Syntax/Imports lines above)")

    return "\n".join(parts)
