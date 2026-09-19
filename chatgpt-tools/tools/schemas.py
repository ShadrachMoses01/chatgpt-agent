import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# Default tool schemas with comprehensive documentation
DEFAULT_TOOL_SCHEMAS = {
    "HELP": {
        "required": [],
        "optional": [],
        "description": "Show help information about all available tools",
        "when_to_use": "Get started, learn available functionality",
        "examples": [
            "HELP",
            "HELP READ_FILE"
        ],
        "tags": ["information", "getting_started"],
    "category": 'info',
    "complexity": 'simple',
    "safety_level": 'safe',
    "supports_sha": False,
    "supports_rollback": False,
    "supports_preview" : False,
    "curated": False,
    },

    "READ_FILE": {
        "required": ["path"],
        "optional": ["start", "end"],
        "description": "Read file content, with optional line range",
        "when_to_use": [
            "Inspect file contents",
            "Read documentation or source code",
            "Preview specific file sections",
            "Verify file changes"
        ],
        "arguments": {
            "path": {
                "type": "string",
                "required": True,
                "description": "File path to read"
            },
            "start": {
                "type": "integer",
                "required": False,
                "description": "Starting line number (1-indexed)",
                "example": "10"
            },
            "end": {
                "type": "integer",
                "required": False,
                "description": "Ending line number (inclusive)",
                "example": "20"
            }
        },
        "returns": {
            "content": {
                "type": "string",
                "description": "File content (or specified line range)"
            },
            "sha256": {
                "type": "string",
                "description": "SHA-256 hash for file integrity"
            },
            "path": {
                "type": "string",
                "description": "Absolute path to the resolved file"
            },
            "total_lines": {
                "type": "integer",
                "description": "Total lines in the file"
            }
        },
        "failure_modes": [
            {
                "condition": "File does not exist",
                "message": "File not found: {path}"
            },
            {
                "condition": "Permission denied",
                "message": "Permission denied: {path}"
            },
            {
                "condition": "Invalid line range",
                "message": "Invalid line range: start={start}, end={end}"
            }
        ],
        "examples": [
            "READ_FILE README.md",
            "READ_FILE tools/registry.py start=10 end=20",
            "READ_FILE src/main.py"
        ],
        "tags": ["file", "read", "information"],
    "category": 'file',
    "complexity": 'simple',
    "safety_level": 'safe',
    "supports_sha": False,
    "supports_rollback": False,
    "supports_preview" : False,
    "curated": False,
    },

    "LIST_FILES": {
        "required": ["path"],
        "optional": [],
        "description": "List files and directories in specified path",
        "when_to_use": [
            "Explore project structure",
            "Find specific files",
            "Check directory contents",
            "Navigate project organization"
        ],
        "arguments": {
            "path": {
                "type": "string",
                "required": True,
                "description": "Directory path to list contents"
            }
        },
        "returns": {
            "files": {
                "type": "array",
                "description": "List of files and directories",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "is_directory": {"type": "boolean"},
                        "size": {"type": "integer"}
                    }
                }
            }
        },
        "failure_modes": [
            {
                "condition": "Directory does not exist",
                "message": "Directory not found: {path}"
            },
            {
                "condition": "Permission denied",
                "message": "Permission denied: {path}"
            }
        ],
        "examples": [
            "LIST_FILES .",
            "LIST_FILES tools",
            "LIST_FILES src/components"
        ],
        "tags": ["file", "list", "directory"],
    "category": 'file',
    "complexity": 'simple',
    "safety_level": 'safe',
    "supports_sha": False,
    "supports_rollback": False,
    "supports_preview" : False,
    "curated": False,
    },

    "READ_SYMBOL": {
        "required": ["symbol"],
        "optional": ["path"],
        "description": "Read source code of a function or class by name",
        "when_to_use": [
            "Understand specific functions",
            "Learn API usage",
            "Copy and modify existing code",
            "Analyze function logic"
        ],
        "supported_symbol_types": ["functions", "classes"],
        "unsupported_symbol_types": ["methods", "nested classes", "lambdas", "variables"],
        "accepted_formats": [
            "Game",
            "execute",
            "validate_input"
        ],
        "unsupported_formats": [
            "Game.run",
            "Game._run",
            "package.module.function"
        ],
        "arguments": {
            "symbol": {
                "type": "string",
                "required": True,
                "description": "Name of the function or class to read"
            },
            "path": {
                "type": "string",
                "required": False,
                "description": "Specific file to search in (searches all files if not specified)"
            }
        },
        "returns": {
            "symbol": {
                "type": "string",
                "description": "Name of the symbol"
            },
            "kind": {
                "type": "string",
                "description": "Type of symbol (function/class)"
            },
            "file": {
                "type": "string",
                "description": "File where symbol is defined"
            },
            "line": {
                "type": "integer",
                "description": "Line number where symbol is defined"
            },
            "source": {
                "type": "string",
                "description": "Full source code of the symbol"
            }
        },
        "failure_modes": [
            {
                "condition": "Symbol not found",
                "message": "Symbol '{symbol}' not found"
            },
            {
                "condition": "File not found",
                "message": "File not found: {path}"
            }
        ],
        "examples": [
            "READ_SYMBOL Game",
            "READ_SYMBOL run path=tools/game.py",
            "READ_SYMBOL execute"
        ],
        "tags": ["symbol", "read", "function", "class", "code"],
    "category": 'code',
    "complexity": 'simple',
    "safety_level": 'safe',
    "supports_sha": False,
    "supports_rollback": False,
    "supports_preview" : False,
    "curated": True,
    "limitations": [
        "Only top-level functions and classes are indexed",
        "Methods (e.g. Game.run) are not supported",
        "Nested classes and lambdas are not indexed",
        "Variables and assignments are not indexed"
    ],
    },

    "FIND_REFERENCES": {
        "required": ["symbol"],
        "optional": [],
        "description": "Find all references to a specific symbol",
        "when_to_use": [
            "Analyze symbol usage",
            "Find all usages of a function",
            "Understand code dependencies",
            "Refactor related code"
        ],
        "arguments": {
            "symbol": {
                "type": "string",
                "required": True,
                "description": "Symbol name to find references for"
            }
        },
        "returns": {
            "symbol": {
                "type": "string",
                "description": "The symbol being searched"
            },
            "occurrences": {
                "type": "array",
                "description": "List of all occurrences",
                "items": {
                    "type": "object",
                    "properties": {
                        "file": {"type": "string"},
                        "line": {"type": "integer"},
                        "text": {"type": "string"},
                        "kind": {"type": "string"}
                    }
                }
            },
            "summary": {
                "type": "object",
                "description": "Usage summary by category",
                "properties": {
                    "total": {"type": "integer"},
                    "code": {"type": "integer"},
                    "test": {"type": "integer"},
                    "other": {"type": "integer"}
                }
            }
        },
        "failure_modes": [
            {
                "condition": "Symbol not found",
                "message": "No references found for '{symbol}'"
            }
        ],
        "examples": [
            "FIND_REFERENCES Game",
            "FIND_REFERENCES execute"
        ],
        "supported_symbol_types": ["functions", "classes"],
        "unsupported_symbol_types": ["methods", "nested classes", "lambdas", "variables"],
        "accepted_formats": ["Game", "execute"],
        "unsupported_formats": ["Game.run", "package.module.function"],
        "tags": ["symbol", "references", "usage", "analysis"],
    "category": 'code',
    "complexity": 'moderate',
    "safety_level": 'safe',
    "supports_sha": False,
    "supports_rollback": False,
    "supports_preview" : False,
    "curated": True,
    "limitations": [
        "Only top-level functions and classes are indexed",
        "References found via text search, not AST",
        "Methods (e.g. Game.run) are not supported"
    ],
    },

    "FIND_DEFINITION": {
        "required": ["symbol"],
        "optional": [],
        "description": "Find the file and line where a symbol is defined",
        "when_to_use": [
            "Locate function definitions",
            "Find class definitions",
            "Navigate to symbol source",
            "Understand code organization"
        ],
        "arguments": {
            "symbol": {
                "type": "string",
                "required": True,
                "description": "Symbol name to find"
            }
        },
        "returns": {
            "symbol": {
                "type": "string",
                "description": "The symbol found"
            },
            "file": {
                "type": "string",
                "description": "File containing the symbol"
            },
            "line": {
                "type": "integer",
                "description": "Line number where symbol is defined"
            },
            "kind": {
                "type": "string",
                "description": "Type of symbol (function/class/assignment)"
            }
        },
        "failure_modes": [
            {
                "condition": "Symbol not found",
                "message": "Definition not found for '{symbol}'"
            }
        ],
        "examples": [
            "FIND_DEFINITION Game",
            "FIND_DEFINITION run"
        ],
        "supported_symbol_types": ["functions", "classes"],
        "unsupported_symbol_types": ["methods", "nested classes", "lambdas"],
        "accepted_formats": ["Game", "execute"],
        "unsupported_formats": ["Game.run", "package.module.function"],
        "tags": ["symbol", "definition", "locate", "navigation"],
    "category": 'code',
    "complexity": 'simple',
    "safety_level": 'safe',
    "supports_sha": False,
    "supports_rollback": False,
    "supports_preview" : False,
    "curated": True,
    "limitations": [
        "Only top-level functions and classes are indexed",
        "Methods (e.g. Game.run) are not found",
        "Nested classes are not indexed"
    ],
    },

    "PROJECT_MAP": {
        "required": [],
        "optional": [],
        "description": "Show project structure map with file dependencies",
        "when_to_use": [
            "Understand project organization",
            "Explore code relationships",
            "Plan refactoring",
            "Navigate complex projects"
        ],
        "arguments": {},
        "returns": {
            "map": {
                "type": "object",
                "description": "Project structure information",
                "properties": {
                    "files": {
                        "type": "array",
                        "description": "List of all files in project"
                    },
                    "directories": {
                        "type": "array",
                        "description": "List of directories"
                    },
                    "file_types": {
                        "type": "object",
                        "description": "Count of files by type"
                    },
                    "main_modules": {
                        "type": "array",
                        "description": "Top-level modules"
                    }
                }
            }
        },
        "examples": [
            "PROJECT_MAP",
            "PROJECT_MAP"
        ],
        "tags": ["project", "structure", "overview", "navigation"],
    "category": 'utility',
    "complexity": 'simple',
    "safety_level": 'safe',
    "supports_sha": False,
    "supports_rollback": False,
    "supports_preview" : False,
    "curated": False,
    },

    "TOOL_INFO": {
        "required": [],
        "optional": ["target"],
        "description": "Show detailed schemas and capabilities for one or all tools",
        "when_to_use": [
            "Discover available tools",
            "Learn a tool's required arguments",
            "Check what a tool returns",
            "Find the right tool for a task"
        ],
        "arguments": {
            "target": {
                "type": "string",
                "required": False,
                "description": "Tool name to inspect (e.g. PATCH_FILE). If omitted, lists all tools with descriptions"
            }
        },
        "returns": {
            "tool": {
                "type": "string",
                "description": "The requested tool name (only when target is specified)"
            },
            "description": {
                "type": "string",
                "description": "What the tool does"
            },
            "category": {
                "type": "string",
                "description": "Tool category (file, code, git, etc.)"
            },
            "complexity": {
                "type": "string",
                "description": "How complex the tool is (simple, moderate)"
            },
            "safety_level": {
                "type": "string",
                "description": "Risk level (safe, caution)"
            },
            "curated": {
                "type": "boolean",
                "description": "Whether semantic guidance has been manually written"
            },
            "required": {
                "type": "string",
                "description": "Comma-separated list of required arguments"
            },
            "optional": {
                "type": "string",
                "description": "Comma-separated list of optional arguments"
            },
            "arguments": {
                "type": "string",
                "description": "Detailed argument descriptions"
            },
            "returns": {
                "type": "string",
                "description": "Detailed return field descriptions"
            },
            "examples": {
                "type": "string",
                "description": "Usage examples"
            },
            "supports_sha": {
                "type": "boolean",
                "description": "Whether the tool supports SHA validation"
            },
            "supports_rollback": {
                "type": "boolean",
                "description": "Whether the tool supports rollback"
            },
            "tools": {
                "type": "string",
                "description": "Formatted tool listing (only when target is omitted)"
            },
            "count": {
                "type": "integer",
                "description": "Total number of tools"
            },
            "tool_list": {
                "type": "string",
                "description": "Comma-separated list of all tool names"
            }
        },
        "examples": [
            "TOOL_INFO",
            "TOOL_INFO PATCH_FILE",
            "TOOL_INFO WRITE_FILE"
        ],
        "tags": ["information", "metadata", "capabilities", "introspection"],
    "category": 'info',
    "complexity": 'simple',
    "safety_level": 'safe',
    "supports_sha": False,
    "supports_rollback": False,
    "supports_preview" : False,
    "curated": False,
    },

    "SEARCH": {
        "required": ["query"],
        "optional": [],
        "description": "Search text across the project",
        "when_to_use": [
            "Find specific code patterns",
            "Search for keywords",
            "Discover related functionality",
            "Navigate large codebases"
        ],
        "arguments": {
            "query": {
                "type": "string",
                "required": True,
                "description": "Search query text"
            }
        },
        "returns": {
            "query": {
                "type": "string",
                "description": "The search query"
            },
            "matches": {
                "type": "array",
                "description": "List of matching occurrences",
                "items": {
                    "type": "object",
                    "properties": {
                        "file": {"type": "string"},
                        "line": {"type": "integer"},
                        "text": {"type": "string"}
                    }
                }
            }
        },
        "failure_modes": [
            {
                "condition": "No matches found",
                "message": "No matches found for '{query}'"
            }
        ],
        "examples": [
            "SEARCH def execute",
            "SEARCH import os",
            "SEARCH function Game"
        ],
        "tags": ["search", "find", "pattern", "text"],
    "category": 'search',
    "complexity": 'simple',
    "safety_level": 'safe',
    "supports_sha": False,
    "supports_rollback": False,
    "supports_preview" : False,
    "curated": False,
    },

    "WRITE_FILE": {
        "required": ["path", "content"],
        "optional": ["expected_sha"],
        "description": "Write content to a file (overwrite)",
        "when_to_use": [
            "Create new files",
            "Update existing files",
            "Write configuration files",
            "Generate documentation"
        ],
        "arguments": {
            "path": {
                "type": "string",
                "required": True,
                "description": "File path to write"
            },
            "content": {
                "type": "string",
                "required": True,
                "description": "Content to write to file"
            },
            "expected_sha": {
                "type": "string",
                "required": False,
                "description": "Expected SHA-256 hash for validation"
            }
        },
        "returns": {
            "success": {
                "type": "boolean",
                "description": "Whether the write succeeded"
            },
            "path": {
                "type": "string",
                "description": "Absolute path to written file"
            },
            "sha256": {
                "type": "string",
                "description": "Actual SHA-256 hash of written content"
            },
            "previous_sha": {
                "type": "string",
                "description": "SHA-256 of previous content (if file existed)"
            }
        },
        "failure_modes": [
            {
                "condition": "Permission denied",
                "message": "Permission denied: {path}"
            },
            {
                "condition": "Validation failed",
                "message": "SHA validation failed: expected {expected}, got {actual}"
            }
        ],
        "examples": [
            "WRITE_FILE README.md # Documentation",
            "WRITE_FILE src/config.py print('Hello')",
            "WRITE_FILE tests/test_example.py \"def test_pass(): pass\""
        ],
        "tags": ["file", "write", "create", "overwrite"],
    "category": 'file',
    "complexity": 'simple',
    "safety_level": 'caution',
    "supports_sha": True,
    "supports_rollback": True,
    "supports_preview" : False,
    "curated": False,
    },

    "CREATE_FILE": {
        "required": ["path", "content"],
        "optional": [],
        "description": "Create a new file",
        "when_to_use": [
            "Add new files to project",
            "Create test files",
            "Generate documentation",
            "Initialize configuration"
        ],
        "arguments": {
            "path": {
                "type": "string",
                "required": True,
                "description": "File path to create"
            },
            "content": {
                "type": "string",
                "required": True,
                "description": "Content for the new file"
            }
        },
        "returns": {
            "success": {
                "type": "boolean",
                "description": "Whether the creation succeeded"
            },
            "path": {
                "type": "string",
                "description": "Absolute path to created file"
            },
            "sha256": {
                "type": "string",
                "description": "SHA-256 hash of created content"
            }
        },
        "failure_modes": [
            {
                "condition": "File already exists",
                "message": "File already exists: {path}"
            },
            {
                "condition": "Directory doesn't exist",
                "message": "Parent directory does not exist: {path}"
            }
        ],
        "examples": [
            "CREATE_FILE src/utils/helpers.py \"def helper(): return True\"",
            "CREATE_FILE docs/api.md \"# API Documentation\""
        ],
        "tags": ["file", "create", "new", "initialize"],
    "category": 'file',
    "complexity": 'simple',
    "safety_level": 'caution',
    "supports_sha": False,
    "supports_rollback": False,
    "supports_preview" : False,
    "curated": False,
    },

    "DELETE_FILE": {
        "required": ["path"],
        "optional": [],
        "description": "Delete a file",
        "when_to_use": [
            "Remove unwanted files",
            "Clean up temporary files",
            "Delete test files",
            "Remove backup files"
        ],
        "arguments": {
            "path": {
                "type": "string",
                "required": True,
                "description": "File path to delete"
            }
        },
        "returns": {
            "success": {
                "type": "boolean",
                "description": "Whether the deletion succeeded"
            },
            "path": {
                "type": "string",
                "description": "Absolute path that was deleted"
            },
            "previous_sha": {
                "type": "string",
                "description": "SHA-256 hash of file before deletion"
            }
        },
        "failure_modes": [
            {
                "condition": "File does not exist",
                "message": "File not found: {path}"
            },
            {
                "condition": "Directory doesn't exist",
                "message": "Directory not found: {path}"
            }
        ],
        "examples": [
            "DELETE_FILE temp.log",
            "DELETE_FILE build/",
            "DELETE_FILE outdated.md"
        ],
        "tags": ["file", "delete", "remove", "cleanup"],
    "category": 'file',
    "complexity": 'simple',
    "safety_level": 'caution',
    "supports_sha": False,
    "supports_rollback": False,
    "supports_preview" : False,
    "curated": False,
    },

    "PATCH_FILE": {
        "required": ["path", "find", "replace"],
        "optional": ["expected_sha"],
        "description": "Find-and-replace text in a file",
        "when_to_use": [
            "Update specific content",
            "Fix typos or errors",
            "Standardize formatting",
            "Refactor code patterns"
        ],
        "arguments": {
            "path": {
                "type": "string",
                "required": True,
                "description": "File path to patch"
            },
            "find": {
                "type": "string",
                "required": True,
                "description": "Text to find and replace"
            },
            "replace": {
                "type": "string",
                "required": True,
                "description": "Replacement text"
            },
            "expected_sha": {
                "type": "string",
                "required": False,
                "description": "Expected SHA-256 for safety validation"
            }
        },
        "returns": {
            "success": {
                "type": "boolean",
                "description": "Whether the patch succeeded"
            },
            "path": {
                "type": "string",
                "description": "Absolute path to patched file"
            },
            "sha256": {
                "type": "string",
                "description": "Actual SHA-256 hash after patch"
            },
            "changes": {
                "type": "object",
                "description": "Details about changes made",
                "properties": {
                    "lines_added": {"type": "integer"},
                    "lines_removed": {"type": "integer"},
                    "occurrences": {"type": "integer"}
                }
            }
        },
        "failure_modes": [
            {
                "condition": "File not found",
                "message": "File not found: {path}"
            },
            {
                "condition": "Validation failed",
                "message": "SHA validation failed: expected {expected}, got {actual}"
            }
        ],
        "examples": [
            "PATCH_FILE README.md Hello World Hello Universe",
            "PATCH_FILE src/style.css \"color: red\" \"color: blue\"",
            "PATCH_FILE lib/utils.py \"TODO remove this\" \"// Completed\""
        ],
        "tags": ["file", "patch", "replace", "find", "text"],
    "category": 'file',
    "complexity": 'simple',
    "safety_level": 'caution',
    "supports_sha": True,
    "supports_rollback": True,
    "supports_preview" : False,
    "curated": False,
    },

    "REPLACE_FUNCTION": {
        "required": ["path", "symbol", "content"],
        "optional": ["expected_sha"],
        "description": "Replace a function body by name",
        "when_to_use": [
            "Update function implementation",
            "Refactor existing functions",
            "Fix bugs in functions",
            "Improve function efficiency"
        ],
        "arguments": {
            "path": {
                "type": "string",
                "required": True,
                "description": "File containing the function"
            },
            "symbol": {
                "type": "string",
                "required": True,
                "description": "Name of the function to replace"
            },
            "content": {
                "type": "string",
                "required": True,
                "description": "New function source code"
            },
            "expected_sha": {
                "type": "string",
                "required": False,
                "description": "Expected SHA-256 for safety validation"
            }
        },
        "returns": {
            "success": {
                "type": "boolean",
                "description": "Whether the replacement succeeded"
            },
            "path": {
                "type": "string",
                "description": "Absolute path to modified file"
            },
            "sha256": {
                "type": "string",
                "description": "Actual SHA-256 hash after replacement"
            },
            "symbol": {
                "type": "string",
                "description": "Name of the replaced symbol"
            },
            "verification": {
                "type": "object",
                "description": "Validation results",
                "properties": {
                    "is_valid_python": {"type": "boolean"},
                    "line_count": {"type": "integer"},
                    "comment_count": {"type": "integer"}
                }
            }
        },
        "failure_modes": [
            {
                "condition": "Symbol not found",
                "message": "Function '{symbol}' not found in {path}"
            },
            {
                "condition": "Ambiguous symbol",
                "message": "Multiple functions named '{symbol}' in {path}"
            },
            {
                "condition": "Invalid syntax",
                "message": "Replacement has invalid syntax"
            },
            {
                "condition": "Validation failed",
                "message": "SHA validation failed: expected {expected}, got {actual}"
            }
        ],
        "examples": [
            "REPLACE_FUNCTION tools/registry.py update_config \"def update_config(): pass\"",
            "REPLACE_FUNCTION game.py Game.run \"def run(): print('Game over')\""
        ],
        "supported_symbol_types": ["functions", "classes"],
        "unsupported_symbol_types": ["methods", "nested classes", "lambdas"],
        "accepted_formats": ["Game", "execute"],
        "unsupported_formats": ["Game.run", "package.module.function"],
        "tags": ["function", "replace", "update", "refactor", "safe"],
    "category": 'code',
    "complexity": 'moderate',
    "safety_level": 'caution',
    "supports_sha": True,
    "supports_rollback": True,
    "supports_preview" : False,
    "curated": True,
    "limitations": [
        "Only top-level functions and classes can be replaced",
        "Methods (e.g. Game.run) are not supported",
        "Requires valid Python syntax in replacement"
    ],
    },

    "ADD_FUNCTION": {
        "required": ["path", "content"],
        "optional": ["after", "expected_sha"],
        "description": "Add a new function to a file",
        "when_to_use": [
            "Add new functions to existing files",
            "Extend module functionality",
            "Add helper functions",
            "Implement missing methods"
        ],
        "arguments": {
            "path": {
                "type": "string",
                "required": True,
                "description": "File to add function to"
            },
            "content": {
                "type": "string",
                "required": True,
                "description": "Function source code to add"
            },
            "after": {
                "type": "string",
                "required": False,
                "description": "Symbol name to add after (for organization)"
            },
            "expected_sha": {
                "type": "string",
                "required": False,
                "description": "Expected SHA-256 for safety validation"
            }
        },
        "returns": {
            "success": {
                "type": "boolean",
                "description": "Whether the addition succeeded"
            },
            "path": {
                "type": "string",
                "description": "Absolute path to modified file"
            },
            "sha256": {
                "type": "string",
                "description": "Actual SHA-256 hash after addition"
            },
            "position": {
                "type": "integer",
                "description": "Line number where function was added"
            }
        },
        "failure_modes": [
            {
                "condition": "File not found",
                "message": "File not found: {path}"
            },
            {
                "condition": "Reference symbol not found",
                "message": "Reference symbol '{after}' not found"
            },
            {
                "condition": "Invalid syntax",
                "message": "Added function has invalid syntax"
            }
        ],
        "examples": [
            "ADD_FUNCTION game.py def helper(): return True",
            "ADD_FUNCTION src/utils.py def validate_input(x): if x < 0: return False"
        ],
        "supported_symbol_types": ["functions", "classes"],
        "unsupported_symbol_types": ["methods", "nested classes", "lambdas"],
        "accepted_formats": ["Game", "execute"],
        "unsupported_formats": ["Game.run", "package.module.function"],
        "tags": ["function", "add", "insert", "extension", "safe"],
    "category": 'code',
    "complexity": 'moderate',
    "safety_level": 'safe',
    "supports_sha": True,
    "supports_rollback": True,
    "supports_preview" : False,
    "curated": True,
    "limitations": [
        "Only top-level functions and classes can be added",
        "File must contain valid Python",
        "Cannot insert methods into existing classes"
    ],
    },

    "DELETE_FUNCTION": {
        "required": ["path", "symbol"],
        "optional": ["expected_sha"],
        "description": "Delete a function from a file",
        "when_to_use": [
            "Remove unused functions",
            "Clean up code",
            "Refactor and simplify",
            "Remove debugging code"
        ],
        "arguments": {
            "path": {
                "type": "string",
                "required": True,
                "description": "File containing the function"
            },
            "symbol": {
                "type": "string",
                "required": True,
                "description": "Name of the function to delete"
            },
            "expected_sha": {
                "type": "string",
                "required": False,
                "description": "Expected SHA-256 for safety validation"
            }
        },
        "returns": {
            "success": {
                "type": "boolean",
                "description": "Whether the deletion succeeded"
            },
            "path": {
                "type": "string",
                "description": "Absolute path to modified file"
            },
            "sha256": {
                "type": "string",
                "description": "Actual SHA-256 hash after deletion"
            },
            "deleted_symbol": {
                "type": "string",
                "description": "Name of the deleted function"
            }
        },
        "failure_modes": [
            {
                "condition": "Symbol not found",
                "message": "Function '{symbol}' not found in {path}"
            },
            {
                "condition": "Function is referenced elsewhere",
                "message": "Function '{symbol}' is referenced elsewhere"
            },
            {
                "condition": "Ambiguous symbol",
                "message": "Multiple functions named '{symbol}' in {path}"
            }
        ],
        "examples": [
            "DELETE_FUNCTION game.py run",
            "DELETE_FUNCTION src/helpers.py debug_print"
        ],
        "supported_symbol_types": ["functions", "classes"],
        "unsupported_symbol_types": ["methods", "nested classes", "lambdas"],
        "accepted_formats": ["Game", "execute"],
        "unsupported_formats": ["Game.run", "package.module.function"],
        "tags": ["function", "delete", "remove", "cleanup", "safe"],
    "category": 'code',
    "complexity": 'simple',
    "safety_level": 'caution',
    "supports_sha": True,
    "supports_rollback": True,
    "supports_preview" : False,
    "curated": True,
    "limitations": [
        "Only top-level functions and classes can be deleted",
        "Methods (e.g. Game.run) are not supported",
        "Checks for remaining references before deletion"
    ],
    },

    "RUN_COMMAND": {
        "required": ["command"],
        "optional": [],
        "description": "Execute a shell command",
        "when_to_use": [
            "Run tests",
            "Execute scripts",
            "Build projects",
            "Check system status",
            "File operations"
        ],
        "arguments": {
            "command": {
                "type": "string",
                "required": True,
                "description": "Shell command to execute"
            }
        },
        "returns": {
            "success": {
                "type": "boolean",
                "description": "Whether the command executed successfully"
            },
            "exit_code": {
                "type": "integer",
                "description": "Command exit code"
            },
            "stdout": {
                "type": "string",
                "description": "Standard output from command"
            },
            "stderr": {
                "type": "string",
                "description": "Error output from command"
            },
            "duration": {
                "type": "number",
                "description": "Execution time in seconds"
            },
            "timed_out": {
                "type": "boolean",
                "description": "Whether command timed out"
            }
        },
        "failure_modes": [
            {
                "condition": "Command not allowed",
                "message": "Command not allowed: {command}"
            },
            {
                "condition": "Command not found",
                "message": "Command '{command}' not found"
            },
            {
                "condition": "Timeout",
                "message": "Command timed out after 5 seconds: {command}"
            }
        ],
        "examples": [
            "RUN_COMMAND python3 -m pytest tests/",
            "RUN_COMMAND git status",
            "RUN_COMMAND npm test"
        ],
        "tags": ["command", "execute", "shell", "system"],
    "category": 'execution',
    "complexity": 'simple',
    "safety_level": 'caution',
    "supports_sha": False,
    "supports_rollback": False,
    "supports_preview" : False,
    "curated": False,
    },

    "RUN_TESTS": {
        "required": [],
        "optional": [],
        "description": "Run the test suite",
        "when_to_use": [
            "Run all tests",
            "Check test results",
            "Validate code changes",
            "Quality assurance"
        ],
        "arguments": {},
        "returns": {
            "success": {
                "type": "boolean",
                "description": "Whether all tests passed"
            },
            "tests_run": {
                "type": "integer",
                "description": "Total number of tests executed"
            },
            "tests_passed": {
                "type": "integer",
                "description": "Number of tests that passed"
            },
            "tests_failed": {
                "type": "integer",
                "description": "Number of tests that failed"
            },
            "duration": {
                "type": "number",
                "description": "Execution time in seconds"
            },
            "test_results": {
                "type": "array",
                "description": "Detailed results for each test file",
                "items": {
                    "type": "object",
                    "properties": {
                        "file": {"type": "string"},
                        "tests": {"type": "integer"},
                        "passed": {"type": "integer"},
                        "failed": {"type": "integer"},
                        "duration": {"type": "number"}
                    }
                }
            }
        },
        "examples": [
            "RUN_TESTS",
            "RUN_TESTS tests/test_*.py"
        ],
        "tags": ["test", "execute", "quality", "validation"],
    "category": 'testing',
    "complexity": 'simple',
    "safety_level": 'safe',
    "supports_sha": False,
    "supports_rollback": False,
    "supports_preview" : False,
    "curated": False,
    },

    "TODO_ADD": {
        "required": ["title"],
        "optional": ["priority", "category"],
        "description": "Add a todo item",
        "when_to_use": [
            "Track tasks",
            "Plan features",
            "Manage work items",
            "Track action items"
        ],
        "arguments": {
            "title": {
                "type": "string",
                "required": True,
                "description": "Title/description of the todo"
            },
            "priority": {
                "type": "string",
                "required": False,
                "description": "Priority level (low/medium/high/default: medium)",
                "enum": ["low", "medium", "high"]
            },
            "category": {
                "type": "string",
                "required": False,
                "description": "Todo category (project/runtime/feature)"
            }
        },
        "returns": {
            "id": {
                "type": "string",
                "description": "Unique identifier for the todo"
            },
            "title": {
                "type": "string",
                "description": "Todo title"
            },
            "priority": {
                "type": "string",
                "description": "Priority level"
            },
            "category": {
                "type": "string",
                "description": "Todo category"
            },
            "done": {
                "type": "boolean",
                "description": "Whether the todo is completed"
            },
            "duplicate": {
                "type": "boolean",
                "description": "Whether this was a duplicate todo"
            }
        },
        "failure_modes": [
            {
                "condition": "Title too short",
                "message": "Title must be at least 3 characters"
            }
        ],
        "examples": [
            "TODO_ADD Implement new feature",
            "TODO_ADD Fix bug in authentication priority=high",
            "TODO_ADD Add error handling category=runtime"
        ],
        "tags": ["todo", "task", "planning", "management"],
    "category": 'management',
    "complexity": 'simple',
    "safety_level": 'safe',
    "supports_sha": False,
    "supports_rollback": False,
    "supports_preview" : False,
    "curated": False,
    },

    "TODO_LIST": {
        "required": [],
        "optional": [],
        "description": "List all todo items",
        "when_to_use": [
            "Review tasks",
            "Check progress",
            "Filter by category or priority",
            "Plan next actions"
        ],
        "arguments": {},
        "returns": {
            "todos": {
                "type": "array",
                "description": "List of all todo items",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "title": {"type": "string"},
                        "priority": {"type": "string"},
                        "category": {"type": "string"},
                        "done": {"type": "boolean"}
                    }
                }
            },
            "summary": {
                "type": "object",
                "description": "Todo summary by category",
                "properties": {
                    "total": {"type": "integer"},
                    "completed": {"type": "integer"},
                    "pending": {"type": "integer"},
                    "by_category": {
                        "type": "object",
                        "description": "Todos grouped by category"
                    },
                    "by_priority": {
                        "type": "object",
                        "description": "Todos grouped by priority"
                    }
                }
            }
        },
        "examples": [
            "TODO_LIST",
            "TODO_LIST category=project",
            "TODO_LIST priority=high"
        ],
        "tags": ["todo", "list", "view", "review"],
    "category": 'management',
    "complexity": 'simple',
    "safety_level": 'safe',
    "supports_sha": False,
    "supports_rollback": False,
    "supports_preview" : False,
    "curated": False,
    },

    "TODO_DONE": {
        "required": ["id"],
        "optional": [],
        "description": "Mark a todo as done",
        "when_to_use": [
            "Complete tasks",
            "Check off completed work",
            "Mark items as done",
            "Track progress"
        ],
        "arguments": {
            "id": {
                "type": "string",
                "required": True,
                "description": "Unique identifier of the todo to mark as done"
            }
        },
        "returns": {
            "success": {
                "type": "boolean",
                "description": "Whether the todo was marked as done"
            },
            "todo": {
                "type": "object",
                "description": "Updated todo information",
                "properties": {
                    "id": {"type": "string"},
                    "title": {"type": "string"},
                    "priority": {"type": "string"},
                    "category": {"type": "string"},
                    "done": {"type": "boolean"}
                }
            }
        },
        "failure_modes": [
            {
                "condition": "Todo not found",
                "message": "Todo not found: {id}"
            }
        ],
        "examples": [
            "TODO_DONE abc123",
            "TODO_DONE def456"
        ],
        "tags": ["todo", "complete", "update", "progress"],
    "category": 'management',
    "complexity": 'simple',
    "safety_level": 'safe',
    "supports_sha": False,
    "supports_rollback": False,
    "supports_preview" : False,
    "curated": False,
    },

    "GIT_STATUS": {
        "required": [],
        "optional": [],
        "description": "Show working tree status (git status)",
        "when_to_use": [
            "Check repository state",
            "Review uncommitted changes",
            "Verify file modifications",
            "Check branch status"
        ],
        "arguments": {},
        "returns": {
            "branch": {
                "type": "string",
                "description": "Current branch name"
            },
            "staged": {
                "type": "array",
                "description": "Staged changes"
            },
            "unstaged": {
                "type": "array",
                "description": "Unstaged changes"
            },
            "untracked": {
                "type": "array",
                "description": "Untracked files"
            }
        },
        "failure_modes": [
            {
                "condition": "Not a git repository",
                "message": "Not a git repository"
            }
        ],
        "examples": [
            "GIT_STATUS"
        ],
        "tags": ["git", "status", "version_control"],
    "category": 'git',
    "complexity": 'simple',
    "safety_level": 'safe',
    "supports_sha": False,
    "supports_rollback": False,
    "supports_preview" : False,
    "curated": False,
    },

    "GIT_DIFF": {
        "required": [],
        "optional": [],
        "description": "Show changes in working tree (git diff)",
        "when_to_use": [
            "Review unstaged changes",
            "Inspect file diffs",
            "Before committing changes",
            "Review working tree modifications"
        ],
        "arguments": {},
        "returns": {
            "diff": {
                "type": "string",
                "description": "Unified diff output"
            },
            "files_changed": {
                "type": "array",
                "description": "List of changed files"
            }
        },
        "failure_modes": [
            {
                "condition": "Not a git repository",
                "message": "Not a git repository"
            }
        ],
        "examples": [
            "GIT_DIFF"
        ],
        "tags": ["git", "diff", "version_control"],
    "category": 'git',
    "complexity": 'simple',
    "safety_level": 'safe',
    "supports_sha": False,
    "supports_rollback": False,
    "supports_preview" : False,
    "curated": False,
    },

    "GIT_LOG": {
        "required": [],
        "optional": ["limit"],
        "description": "Show commit log (git log)",
        "when_to_use": [
            "Review commit history",
            "Check recent changes",
            "Find commit SHAs",
            "Track project history"
        ],
        "arguments": {
            "limit": {
                "type": "integer",
                "required": False,
                "description": "Number of commits to show",
                "example": "10"
            }
        },
        "returns": {
            "commits": {
                "type": "array",
                "description": "List of recent commits",
                "items": {
                    "type": "object",
                    "properties": {
                        "sha": {"type": "string"},
                        "author": {"type": "string"},
                        "date": {"type": "string"},
                        "message": {"type": "string"}
                    }
                }
            }
        },
        "failure_modes": [
            {
                "condition": "Not a git repository",
                "message": "Not a git repository"
            }
        ],
        "examples": [
            "GIT_LOG",
            "GIT_LOG limit=5"
        ],
        "tags": ["git", "log", "history", "version_control"],
    "category": 'git',
    "complexity": 'simple',
    "safety_level": 'safe',
    "supports_sha": False,
    "supports_rollback": False,
    "supports_preview" : False,
    "curated": False,
    },

    "GIT_SHOW": {
        "required": ["commit"],
        "optional": [],
        "description": "Show details of a specific commit (git show)",
        "when_to_use": [
            "Inspect commit contents",
            "Review commit diff",
            "Check commit metadata",
            "Analyze specific changes"
        ],
        "arguments": {
            "commit": {
                "type": "string",
                "required": True,
                "description": "Commit SHA to show"
            }
        },
        "returns": {
            "commit": {
                "type": "string",
                "description": "Commit SHA"
            },
            "author": {
                "type": "string",
                "description": "Commit author"
            },
            "date": {
                "type": "string",
                "description": "Commit date"
            },
            "message": {
                "type": "string",
                "description": "Commit message"
            },
            "diff": {
                "type": "string",
                "description": "Commit diff output"
            }
        },
        "failure_modes": [
            {
                "condition": "Commit not found",
                "message": "Commit not found: {commit}"
            },
            {
                "condition": "Not a git repository",
                "message": "Not a git repository"
            }
        ],
        "examples": [
            "GIT_SHOW abc123def",
            "GIT_SHOW HEAD~1"
        ],
        "tags": ["git", "show", "commit", "version_control"],
    "category": 'git',
    "complexity": 'simple',
    "safety_level": 'safe',
    "supports_sha": False,
    "supports_rollback": False,
    "supports_preview" : False,
    "curated": False,
    },

    "GIT_BLAME": {
        "required": ["path"],
        "optional": [],
        "description": "Show line-by-line annotations (git blame)",
        "when_to_use": [
            "Find who changed specific lines",
            "Track code origins",
            "Investigate changes",
            "Code review audit"
        ],
        "arguments": {
            "path": {
                "type": "string",
                "required": True,
                "description": "File path to blame"
            }
        },
        "returns": {
            "path": {
                "type": "string",
                "description": "Path of blamed file"
            },
            "blame": {
                "type": "array",
                "description": "Line-by-line blame information",
                "items": {
                    "type": "object",
                    "properties": {
                        "line": {"type": "integer"},
                        "sha": {"type": "string"},
                        "author": {"type": "string"},
                        "date": {"type": "string"},
                        "content": {"type": "string"}
                    }
                }
            }
        },
        "failure_modes": [
            {
                "condition": "File not found",
                "message": "File not found: {path}"
            },
            {
                "condition": "Not a git repository",
                "message": "Not a git repository"
            }
        ],
        "examples": [
            "GIT_BLAME tools/schemas.py",
            "GIT_BLAME src/main.py"
        ],
        "tags": ["git", "blame", "annotate", "version_control"],
    "category": 'git',
    "complexity": 'simple',
    "safety_level": 'safe',
    "supports_sha": False,
    "supports_rollback": False,
    "supports_preview" : False,
    "curated": False,
    },

    "RUN_INTERACTIVE": {
        "required": ["command"],
        "optional": ["timeout"],
        "description": "Execute a command with PTY for interactive programs",
        "when_to_use": [
            "Run interactive programs",
            "Execute commands requiring PTY",
            "Run programs with prompts",
            "Handle long-running commands"
        ],
        "arguments": {
            "command": {
                "type": "string",
                "required": True,
                "description": "Command to execute"
            },
            "timeout": {
                "type": "integer",
                "required": False,
                "description": "Timeout in seconds (default: 30)",
                "example": "60"
            }
        },
        "returns": {
            "command": {
                "type": "string",
                "description": "Executed command"
            },
            "exit_code": {
                "type": "integer",
                "description": "Command exit code"
            },
            "output": {
                "type": "string",
                "description": "Full output from command"
            },
            "timed_out": {
                "type": "boolean",
                "description": "Whether command timed out"
            }
        },
        "failure_modes": [
            {
                "condition": "Command not found",
                "message": "Command not found: {command}"
            },
            {
                "condition": "Timeout",
                "message": "Command timed out after {timeout}s: {command}"
            }
        ],
        "examples": [
            "RUN_INTERACTIVE python3 -c \"print('hello')\"",
            "RUN_INTERACTIVE bash scripts/setup.sh"
        ],
        "tags": ["command", "execute", "interactive", "pty"],
    "category": 'execution',
    "complexity": 'simple',
    "safety_level": 'caution',
    "supports_sha": False,
    "supports_rollback": False,
    "supports_preview" : False,
    "curated": False,
    },

    "RUN_TEST": {
        "required": [],
        "optional": ["test"],
        "description": "Run a specific test or test file",
        "when_to_use": [
            "Run individual tests",
            "Test specific functionality",
            "Target test debugging",
            "Test selective modules"
        ],
        "arguments": {
            "test": {
                "type": "string",
                "required": False,
                "description": "Test path or pattern to run (runs all tests if omitted)",
                "example": "tests/test_schemas.py"
            }
        },
        "returns": {
            "test": {
                "type": "string",
                "description": "Test pattern that was run"
            },
            "output": {
                "type": "string",
                "description": "Test output"
            },
            "passed": {
                "type": "boolean",
                "description": "Whether tests passed"
            }
        },
        "failure_modes": [
            {
                "condition": "Test not found",
                "message": "No tests found matching: {test}"
            }
        ],
        "examples": [
            "RUN_TEST",
            "RUN_TEST tests/test_schemas.py",
            "RUN_TEST tests/test_schemas.py::TestSchemas"
        ],
        "tags": ["test", "execute", "quality", "debug"],
    "category": 'testing',
    "complexity": 'simple',
    "safety_level": 'safe',
    "supports_sha": False,
    "supports_rollback": False,
    "supports_preview" : False,
    "curated": False,
    },

    "PATCH_SYMBOL": {
        "required": ["path", "symbol", "content"],
        "optional": ["expected_sha"],
        "description": "Replace source code of a function or class by name",
        "when_to_use": [
            "Update function implementations",
            "Replace class methods",
            "Refactor symbol code",
            "Fix bugs in specific functions"
        ],
        "arguments": {
            "path": {
                "type": "string",
                "required": True,
                "description": "File path containing the symbol"
            },
            "symbol": {
                "type": "string",
                "required": True,
                "description": "Function or class name to replace"
            },
            "content": {
                "type": "string",
                "required": True,
                "description": "New source code for the symbol"
            },
            "expected_sha": {
                "type": "string",
                "required": False,
                "description": "Expected SHA-256 for safety validation"
            }
        },
        "returns": {
            "success": {
                "type": "boolean",
                "description": "Whether the patch succeeded"
            },
            "path": {
                "type": "string",
                "description": "Path to modified file"
            },
            "symbol": {
                "type": "string",
                "description": "Name of patched symbol"
            },
            "sha256": {
                "type": "string",
                "description": "SHA-256 after modification"
            }
        },
        "failure_modes": [
            {
                "condition": "Symbol not found",
                "message": "Symbol '{symbol}' not found in {path}"
            },
            {
                "condition": "File not found",
                "message": "File not found: {path}"
            },
            {
                "condition": "Validation failed",
                "message": "SHA validation failed: expected {expected}, got {actual}"
            }
        ],
        "examples": [
            "PATCH_SYMBOL tools/game.py Game.run \"def run(): print('Game over')\"",
            "PATCH_SYMBOL src/main.py setup \"def setup(): pass\""
        ],
        "supported_symbol_types": ["functions", "classes"],
        "unsupported_symbol_types": ["methods", "nested classes", "lambdas"],
        "accepted_formats": ["Game", "execute"],
        "unsupported_formats": ["Game.run", "package.module.function"],
        "tags": ["symbol", "patch", "replace", "function", "class", "code"],
    "category": 'code',
    "complexity": 'moderate',
    "safety_level": 'caution',
    "supports_sha": True,
    "supports_rollback": True,
    "supports_preview" : False,
    "curated": True,
    "limitations": [
        "Only top-level functions and classes can be patched",
        "Methods (e.g. Game.run) are not supported",
        "Requires valid Python syntax in replacement"
    ],
    },

    "TRACE_CALL_GRAPH": {
        "required": ["symbol"],
        "optional": [],
        "description": "Generate call graph for a symbol showing callers and callees",
        "when_to_use": [
            "Understand function dependencies",
            "Analyze code flow",
            "Identify call chains",
            "Plan refactoring impact"
        ],
        "arguments": {
            "symbol": {
                "type": "string",
                "required": True,
                "description": "Symbol name to trace"
            }
        },
        "returns": {
            "symbol": {
                "type": "string",
                "description": "Traced symbol"
            },
            "callers": {
                "type": "array",
                "description": "List of functions that call this symbol",
                "items": {
                    "type": "object",
                    "properties": {
                        "file": {"type": "string"},
                        "line": {"type": "integer"},
                        "caller": {"type": "string"}
                    }
                }
            },
            "callees": {
                "type": "array",
                "description": "List of functions called by this symbol",
                "items": {
                    "type": "object",
                    "properties": {
                        "file": {"type": "string"},
                        "line": {"type": "integer"},
                        "callee": {"type": "string"}
                    }
                }
            }
        },
        "failure_modes": [
            {
                "condition": "Symbol not found",
                "message": "Symbol '{symbol}' not found"
            }
        ],
        "examples": [
            "TRACE_CALL_GRAPH execute",
            "TRACE_CALL_GRAPH Game.run"
        ],
        "supported_symbol_types": ["functions", "classes"],
        "unsupported_symbol_types": ["methods", "nested classes", "lambdas"],
        "accepted_formats": ["Game", "execute"],
        "unsupported_formats": ["Game.run", "package.module.function"],
        "tags": ["symbol", "trace", "call_graph", "analysis"],
    "category": 'code',
    "complexity": 'moderate',
    "safety_level": 'safe',
    "supports_sha": False,
    "supports_rollback": False,
    "supports_preview" : False,
    "curated": True,
    "limitations": [
        "Only top-level functions and classes are traced",
        "Methods (e.g. Game.run) are not traced",
        "Static analysis only, no runtime call detection"
    ],
    },

    "VERIFY_PATCH": {
        "required": ["path"],
        "optional": [],
        "description": "Verify a file is valid Python and check syntax",
        "when_to_use": [
            "Validate patched file syntax",
            "Check for parsing errors",
            "Verify AST structure",
            "Ensure code quality after edits"
        ],
        "arguments": {
            "path": {
                "type": "string",
                "required": True,
                "description": "File path to verify"
            }
        },
        "returns": {
            "path": {
                "type": "string",
                "description": "Verified file path"
            },
            "is_valid_python": {
                "type": "boolean",
                "description": "Whether the file is valid Python"
            },
            "errors": {
                "type": "array",
                "description": "Syntax errors found"
            },
            "symbols_count": {
                "type": "object",
                "description": "Count of symbols by type",
                "properties": {
                    "classes": {"type": "integer"},
                    "functions": {"type": "integer"},
                    "imports": {"type": "integer"}
                }
            }
        },
        "failure_modes": [
            {
                "condition": "File not found",
                "message": "File not found: {path}"
            }
        ],
        "examples": [
            "VERIFY_PATCH tools/schemas.py",
            "VERIFY_PATCH src/main.py"
        ],
        "tags": ["verify", "validate", "syntax", "quality"],
    "category": 'testing',
    "complexity": 'simple',
    "safety_level": 'safe',
    "supports_sha": False,
    "supports_rollback": False,
    "supports_preview" : False,
    "curated": False,
    },

    "IMPACT_ANALYSIS": {
        "required": ["symbol"],
        "optional": [],
        "description": "Analyze impact of changing a symbol across the project",
        "when_to_use": [
            "Plan refactoring changes",
            "Assess change risk",
            "Identify dependent code",
            "Understand symbol usage patterns"
        ],
        "arguments": {
            "symbol": {
                "type": "string",
                "required": True,
                "description": "Symbol name to analyze"
            }
        },
        "returns": {
            "symbol": {
                "type": "string",
                "description": "Analyzed symbol"
            },
            "definition": {
                "type": "object",
                "description": "Symbol definition location",
                "properties": {
                    "file": {"type": "string"},
                    "line": {"type": "integer"},
                    "kind": {"type": "string"}
                }
            },
            "references": {
                "type": "array",
                "description": "All references to the symbol",
                "items": {
                    "type": "object",
                    "properties": {
                        "file": {"type": "string"},
                        "line": {"type": "integer"},
                        "text": {"type": "string"}
                    }
                }
            },
            "total_references": {
                "type": "integer",
                "description": "Total number of references"
            },
            "files_affected": {
                "type": "array",
                "description": "List of files that would be affected",
                "items": {"type": "string"}
            }
        },
        "failure_modes": [
            {
                "condition": "Symbol not found",
                "message": "Symbol '{symbol}' not found"
            }
        ],
        "examples": [
            "IMPACT_ANALYSIS execute",
            "IMPACT_ANALYSIS Game"
        ],
        "supported_symbol_types": ["functions", "classes"],
        "unsupported_symbol_types": ["methods", "nested classes", "lambdas"],
        "accepted_formats": ["Game", "execute"],
        "unsupported_formats": ["Game.run", "package.module.function"],
        "tags": ["symbol", "impact", "analysis", "refactor"],
    "category": 'code',
    "complexity": 'moderate',
    "safety_level": 'safe',
    "supports_sha": False,
    "supports_rollback": False,
    "supports_preview" : False,
    "curated": True,
    "limitations": [
        "Only top-level functions and classes are analyzed",
        "Methods (e.g. Game.run) are not included",
        "Impact estimation based on text references, not AST"
    ],
    }
}


def get_tool_schema(name: str) -> Optional[Dict[str, Any]]:
    """Get schema for a specific tool"""
    return DEFAULT_TOOL_SCHEMAS.get(name)


def get_all_tool_schemas() -> Dict[str, Any]:
    """Get all tool schemas"""
    return DEFAULT_TOOL_SCHEMAS


def validate_tool_schema(name: str, args: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Validate tool arguments against schema"""
    schema = DEFAULT_TOOL_SCHEMAS.get(name)
    if not schema:
        return False, [f"Unknown tool: {name}"]

    errors = []
    
    # Check required arguments
    for required in schema.get("required", []):
        if required not in args:
            errors.append(f"Missing required argument: {required}")
    
    # Check for unknown arguments
    allowed = set(schema.get("required", []) + schema.get("optional", []))
    for arg in args:
        if arg not in allowed:
            errors.append(f"Unknown argument for {name}: {arg}")
    
    return len(errors) == 0, errors


def format_tool_name(name: str) -> str:
    """Convert tool name to human-readable format"""
    return name.replace("_", " ").title()


def get_tool_tags(name: str) -> List[str]:
    """Get tags for a tool"""
    schema = DEFAULT_TOOL_SCHEMAS.get(name, {})
    return schema.get("tags", [])


def search_tools_by_tag(tag: str) -> List[str]:
    """Find all tools that use a specific tag"""
    return [name for name, schema in DEFAULT_TOOL_SCHEMAS.items() 
            if tag in schema.get("tags", [])]


def get_tools_by_category(category: str) -> Dict[str, Any]:
    """Filter tools by category"""
    if category not in ["file", "code", "command", "search", "help", "management", "analysis"]:
        return {}
    
    return {name: schema for name, schema in DEFAULT_TOOL_SCHEMAS.items() 
            if category in schema.get("tags", [])}