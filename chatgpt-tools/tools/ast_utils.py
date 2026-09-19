import ast
import builtins
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


DEFAULT_EXCLUDES = {".git", ".venv", "__pycache__", "logs", ".pytest_cache"}

_BUILTIN_NAMES = frozenset(dir(builtins))

_STDLIB_MODULES = frozenset({
    "abc", "argparse", "ast", "asyncio", "base64", "collections",
    "contextlib", "copy", "csv", "datetime", "decimal", "difflib",
    "enum", "functools", "glob", "hashlib", "html", "http",
    "importlib", "inspect", "io", "itertools", "json", "logging",
    "math", "multiprocessing", "operator", "os", "pathlib",
    "pickle", "platform", "pprint", "queue", "random", "re",
    "shutil", "signal", "socket", "sqlite3", "string", "subprocess",
    "sys", "tempfile", "textwrap", "threading", "time", "traceback",
    "typing", "unittest", "uuid", "warnings", "weakref", "xml",
})


def _is_excluded(filepath: str, excludes: set):
    parts = Path(filepath).parts
    for ex in excludes:
        if ex in parts:
            return True
    return False


def find_python_files(root=".", excludes: set = None):
    if excludes is None:
        excludes = DEFAULT_EXCLUDES
    try:
        result = subprocess.run(
            ["rg", "--type", "py", "--files", root],
            capture_output=True, text=True,
        )
    except FileNotFoundError:
        # ripgrep not available: fall back to a pathlib walk.
        files = [
            str(p) for p in Path(root).rglob("*.py")
            if not _is_excluded(str(p), excludes)
        ]
        return files
    files = [f for f in result.stdout.strip().split("\n") if f]
    return [f for f in files if not _is_excluded(f, excludes)]


def find_occurrences(symbol: str, root=".", excludes: set = None):
    if excludes is None:
        excludes = DEFAULT_EXCLUDES
    try:
        result = subprocess.run(
            ["rg", "-n", "--no-heading", symbol, root],
            capture_output=True, text=True,
        )
    except FileNotFoundError:
        return []
    if not result.stdout.strip():
        return []
    lines = result.stdout.strip().split("\n")
    occurrences = []
    for line in lines:
        parts = line.split(":", 2)
        if len(parts) < 2:
            continue
        filepath = parts[0]
        if _is_excluded(filepath, excludes):
            continue
        lineno = int(parts[1])
        text = parts[2] if len(parts) > 2 else ""
        occurrences.append((filepath, lineno, text))
    return occurrences


def classify_occurrence(symbol: str, filepath: str, lineno: int, text: str):
    stripped = text.strip()
    if stripped.startswith("import ") or stripped.startswith("from "):
        if symbol in stripped:
            return "import"
    for pat in [f"def {symbol}", f"class {symbol}", f"async def {symbol}"]:
        if pat in stripped:
            return "definition"
    if "=" in stripped and symbol in stripped.split("=")[0]:
        return "assignment"
    return "usage"


def classify_symbol(name: str) -> str:
    if name in _BUILTIN_NAMES:
        return "builtin"
    if name in _STDLIB_MODULES:
        return "stdlib"
    return "project"


def _load_symbols_from_file(filepath: str) -> dict:
    """Load all symbols from a single Python file into our shared symbol store."""
    if not Path(filepath).exists():
        return {}
    
    try:
        source = Path(filepath).read_text()
        tree = ast.parse(source)
    except SyntaxError:
        return {}
    
    symbols = {}
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols[node.name] = {
                "type": "function",
                "file": filepath,
                "line": node.lineno,
                "end_line": getattr(node, "end_lineno", node.lineno),
                "col_offset": node.col_offset,
            }
        elif isinstance(node, ast.ClassDef):
            symbols[node.name] = {
                "type": "class",
                "file": filepath,
                "line": node.lineno,
                "end_line": getattr(node, "end_lineno", node.lineno),
                "col_offset": node.col_offset,
            }
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    symbols[target.id] = {
                        "type": "assignment",
                        "file": filepath,
                        "line": node.lineno,
                        "end_line": getattr(node, "end_lineno", node.lineno),
                        "col_offset": node.col_offset,
                    }
    
    return symbols


def load_all_symbols(root=".") -> Dict[str, Any]:
    """Build comprehensive symbol index for the project.
    
    Returns:
        Dict mapping symbol name to symbol info dict with keys:
        - type: "function" | "class" | "assignment"
        - file: absolute path
        - line: line number
        - end_line: end line number
        - col_offset: column offset
    """
    symbols = {}
    files = find_python_files(root)
    
    for filepath in files:
        file_symbols = _load_symbols_from_file(filepath)
        symbols.update(file_symbols)
    
    return symbols


def invalidate_symbol_cache() -> None:
    """Drop the cached symbol index built by :func:`resolve_symbol`.

    Must be called after any operation that adds, removes, or edits Python
    files so subsequent lookups are not served stale entries. The cache is
    keyed on nothing (a single global index), so any mutation invalidates
    the whole index.
    """
    if hasattr(resolve_symbol, '_symbol_cache'):
        delattr(resolve_symbol, '_symbol_cache')


def resolve_symbol(symbol_name: str, root=".") -> Optional[Dict[str, Any]]:
    """Look up a symbol by name.

    Args:
        symbol_name: Name of symbol to resolve
        root: Project root directory

    Returns:
        Symbol info dict or None if not found

    NOTE: results are cached process-wide. Call
    :func:`invalidate_symbol_cache` after editing files; there is no
    automatic mtime-based invalidation.
    """
    # Check if we have cached symbols
    if not hasattr(resolve_symbol, '_symbol_cache'):
        resolve_symbol._symbol_cache = load_all_symbols(root)

    return resolve_symbol._symbol_cache.get(symbol_name)


def get_function_body(filepath: str, func_name: str):
    """Get the AST function node for a function name.
    
    This is a helper function maintained for compatibility with existing tools.
    The unified SymbolEngine should be used instead.
    """
    import ast
    from pathlib import Path
    
    try:
        source = Path(filepath).read_text(encoding="utf-8")
        tree = ast.parse(source)
    except SyntaxError:
        return None
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
            return node
    
    return None


def get_symbol_location(symbol_name: str, root=".") -> tuple:
    """Get file and line number for a symbol.
    
    This is a convenience wrapper for compatibility with existing code.
    """
    symbol_info = resolve_symbol(symbol_name, root)
    if symbol_info:
        return symbol_info['file'], symbol_info['line']
    return None, None


def get_symbol_source(symbol_name: str, root=".") -> tuple:
    """Get the source code for a symbol.
    
    Args:
        symbol_name: Name of symbol to retrieve
        root: Project root directory
    
    Returns:
        Tuple of (source_code, file_path, line_number) or (None, None, None) if not found
    """
    symbol_info = resolve_symbol(symbol_name, root)
    if not symbol_info:
        return None, None, None
    
    try:
        lines = Path(symbol_info['file']).read_text(encoding="utf-8").split('\n')
        start_line = symbol_info['line'] - 1
        end_line = symbol_info.get('end_line', start_line + 1)
        source = '\n'.join(lines[start_line:end_line])
        return source, symbol_info['file'], symbol_info['line']
    except Exception:
        return None, None, None


def _is_ambiguous_symbol(symbol_name: str, root=".") -> bool:
    """Check if a symbol name resolves to multiple definitions.

    The shared cache maps each name to a single entry (last file wins),
    so ambiguity is determined by scanning every file directly instead of
    counting cache keys (which can never exceed one per name).
    """
    count = 0
    for filepath in find_python_files(root):
        if symbol_name in _load_symbols_from_file(filepath):
            count += 1
            if count > 1:
                return True
    return False


def find_function_nodes(tree, symbol: str):
    """Find function nodes matching a symbol name.
    
    This is a helper function for the original find_function_nodes implementation,
    now using the shared symbol index for consistency.
    """
    matches = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == symbol:
            matches.append(node)

    return matches


def extract_calls(node):
    """Extract function calls from an AST node."""
    calls = []
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            if isinstance(child.func, ast.Name):
                calls.append(child.func.id)
            elif isinstance(child.func, ast.Attribute):
                calls.append(f"{child.func.attr}")
    return calls


def split_by_domain(occurrences):
    """Split occurrences into code, tests, and other categories."""
    code = []
    tests = []
    other = []
    for fp, ln, text in occurrences:
        if fp.startswith("tests/") or "/tests/" in fp:
            tests.append((fp, ln, text))
        elif fp.startswith("logs/"):
            other.append((fp, ln, text))
        else:
            code.append((fp, ln, text))
    return code, tests, other