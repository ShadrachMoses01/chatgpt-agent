"""
Unified Symbol Engine for the ChatGPT Agent.

This module provides a centralized symbol resolution system that all
truly symbol-aware tools can use. It eliminates ambiguity and provides
consistent symbol handling across the entire codebase.

Key Features:
- Single source of truth for all symbol information
- Supports functions, classes, and assignments
- Efficient caching for fast lookups
- Consistency guarantees across all tools
- Backward compatibility with existing tools
"""

import ast
import builtins
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


# Project excludes
DEFAULT_EXCLUDES = {".git", ".venv", "__pycache__", "logs", ".pytest_cache"}

# Standard library modules for classification
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


class SymbolInfo:
    """Information about a symbol."""
    
    def __init__(self, name: str, symbol_type: str, filepath: str, 
                 line: int, col_offset: int, end_line: Optional[int] = None):
        self.name = name
        self.type = symbol_type  # "function", "class", or "assignment"
        self.filepath = filepath
        self.line = line
        self.col_offset = col_offset
        self.end_line = end_line or line
    
    def __repr__(self):
        return f"SymbolInfo({self.name}, {self.type} at {self.filepath}:{self.line})"
class SymbolEngine:
    """
    Centralized symbol resolution and management system.
    
    Provides consistent symbol handling across all tools that need to
    work with functions, classes, and other named elements in Python code.
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self._symbols: Dict[str, SymbolInfo] = {}
        self._inverse_index: Dict[str, List[SymbolInfo]] = {}
        self._loaded_files: set = set()
        
    def load_project_symbols(self, force_reload: bool = False) -> bool:
        """
        Load symbols from all Python files in the project.
        
        Args:
            force_reload: If True, reload even if symbols are already loaded
            
        Returns:
            True if symbols were loaded/updated, False if already loaded and no changes
        """
        # Check if we need to reload
        if not force_reload and self._symbols:
            return False
        
        # Clear existing data
        self._symbols.clear()
        self._inverse_index.clear()
        self._loaded_files.clear()
        
        # Find and process all Python files
        python_files = self._find_python_files()
        
        for filepath in python_files:
            self._load_file_symbols(filepath)
        
        return True
    
    def _find_python_files(self) -> List[Path]:
        """Find all Python files in the project."""
        try:
            result = subprocess.run(
                ["rg", "--type", "py", "--files", str(self.project_root)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            files = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    filepath = Path(line).resolve()
                    # Skip excluded directories
                    if not self._is_excluded(filepath):
                        files.append(filepath)
            
            return files
        except subprocess.TimeoutExpired:
            print(f"Warning: rg timed out, falling back to glob")
            return list(self.project_root.rglob("*.py"))
        except Exception as e:
            print(f"Warning: Failed to find Python files: {e}")
            return list(self.project_root.rglob("*.py"))
    
    def _is_excluded(self, filepath: Path) -> bool:
        """Check if filepath should be excluded based on directory names."""
        parts = filepath.parts
        for ex in DEFAULT_EXCLUDES:
            if ex in parts:
                return True
        return False
    
    def _load_file_symbols(self, filepath: Path):
        """Load all symbols from a single Python file."""
        try:
            source = filepath.read_text(encoding="utf-8")
            tree = ast.parse(source)
            
            for node in ast.walk(tree):
                self._process_node(node, filepath)
                
        except SyntaxError:
            # Skip files with syntax errors
            pass
        except Exception as e:
            print(f"Warning: Failed to process {filepath}: {e}")
    
    def _process_node(self, node: ast.AST, filepath: Path):
        """Process an AST node and extract symbols."""
        current_line = getattr(node, 'lineno', 1)
        
        # Handle function definitions
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            self._add_symbol(
                node.name, "function", filepath,
                current_line, getattr(node, 'col_offset', 0),
                getattr(node, 'end_lineno', current_line)
            )
        
        # Handle class definitions
        elif isinstance(node, ast.ClassDef):
            self._add_symbol(
                node.name, "class", filepath,
                current_line, getattr(node, 'col_offset', 0),
                getattr(node, 'end_lineno', current_line)
            )
        
        # Handle assignments
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    # Only add if it's not a common builtin or stdlib pattern
                    if not self._is_builtin_or_stdlib(target.id):
                        self._add_symbol(
                            target.id, "assignment", filepath,
                            current_line, getattr(node, 'col_offset', 0),
                            getattr(node, 'end_lineno', current_line)
                        )
    
    def _is_builtin_or_stdlib(self, name: str) -> bool:
        """Check if name is a builtin or stdlib element."""
        if name in _BUILTIN_NAMES:
            return True
        # Check if it's a common stdlib module or attribute
        if name in _STDLIB_MODULES:
            return True
        
        # Common stdlib-related names that are likely not project symbols
        stdlib_patterns = {
            'str', 'int', 'float', 'bool', 'list', 'dict', 'tuple',
            'set', 'print', 'input', 'len', 'range', 'enumerate',
            'zip', 'map', 'filter', 'type', 'isinstance', 'hasattr',
            'getattr', 'setattr', 'delattr', 'callable', 'super',
            'property', 'staticmethod', 'classmethod'
        }
        
        return name in stdlib_patterns
    
    def _add_symbol(self, name: str, symbol_type: str, filepath: Path,
                    line: int, col_offset: int, end_line: int):
        """Add a symbol to the index."""
        # Create SymbolInfo
        symbol_info = SymbolInfo(name, symbol_type, str(filepath), line, col_offset, end_line)
        
        # Add to main index
        self._symbols[name] = symbol_info
        
        # Add to inverse index (file -> symbols)
        str_path = str(filepath)
        if str_path not in self._inverse_index:
            self._inverse_index[str_path] = []
        self._inverse_index[str_path].append(symbol_info)
    
    def resolve_symbol(self, symbol_name: str) -> Optional[SymbolInfo]:
        """
        Resolve a symbol to its information.
        
        Args:
            symbol_name: Name of symbol to resolve
            
        Returns:
            SymbolInfo if found, None otherwise
        """
        return self._symbols.get(symbol_name)
    
    def find_symbols(self, partial_name: str = None) -> List[SymbolInfo]:
        """
        Find symbols that match a partial name.
        
        Args:
            partial_name: String to match in symbol names
            
        Returns:
            List of matching SymbolInfo objects
        """
        if not partial_name:
            return list(self._symbols.values())
        
        partial_lower = partial_name.lower()
        return [
            info for info in self._symbols.values()
            if partial_lower in info.name.lower()
        ]
    
    def get_symbols_by_file(self, filepath: str) -> List[SymbolInfo]:
        """
        Get all symbols defined in a specific file.
        
        Args:
            filepath: Path to file
            
        Returns:
            List of SymbolInfo objects from that file
        """
        return self._inverse_index.get(filepath, [])
    
    def is_ambiguous_symbol(self, symbol_name: str) -> bool:
        """
        Check if a symbol name resolves to multiple definitions.
        
        Args:
            symbol_name: Symbol name to check
            
        Returns:
            True if symbol is ambiguous (multiple definitions), False otherwise
        """
        return sum(1 for name in self._symbols.keys() if name == symbol_name) > 1
    
    def validate_symbol(self, symbol_name: str, expected_type: str = None) -> Tuple[bool, str]:
        """
        Validate that a symbol exists and optionally has a specific type.
        
        Args:
            symbol_name: Name of symbol to validate
            expected_type: Expected symbol type ("function", "class", or "assignment")
            
        Returns:
            Tuple of (is_valid, message)
        """
        symbol_info = self.resolve_symbol(symbol_name)
        if not symbol_info:
            return False, f"Symbol '{symbol_name}' not found"
        
        if expected_type and symbol_info.type != expected_type:
            return False, (
                f"Symbol '{symbol_name}' is a {symbol_info.type}, "
                f"expected {expected_type}"
            )
        
        return True, "Symbol is valid"


# Global symbol engine instance
_symbol_engine = None


def get_symbol_engine(project_root: str = ".") -> SymbolEngine:
    """Get or create the global symbol engine instance."""
    global _symbol_engine
    if _symbol_engine is None or _symbol_engine.project_root != Path(project_root).resolve():
        _symbol_engine = SymbolEngine(project_root)
        _symbol_engine.load_project_symbols()
    return _symbol_engine


def resolve_symbol(symbol_name: str, project_root: str = ".") -> Optional[SymbolInfo]:
    """Global helper to resolve a symbol name."""
    engine = get_symbol_engine(project_root)
    return engine.resolve_symbol(symbol_name)


def find_symbols(symbol_name: str = None, project_root: str = ".") -> List[SymbolInfo]:
    """Global helper to find symbols."""
    engine = get_symbol_engine(project_root)
    return engine.find_symbols(symbol_name)


def get_symbols_by_file(filepath: str, project_root: str = ".") -> List[SymbolInfo]:
    """Global helper to get symbols from a file."""
    engine = get_symbol_engine(project_root)
    return engine.get_symbols_by_file(filepath)