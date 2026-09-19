# ChatGPT Agent Tools

Local tool runtime for the ChatGPT Agent project. It receives structured
`ToolCall`s (parsed from `<tool_call>` / `<tool_batch>` XML), validates them
against schemas, dispatches them to handlers, and returns structured
`ToolResult`s serialized back to XML.

No third-party dependencies. Standard library only, plus `rg` (ripgrep) for
the search-based tools and `pytest` for the test tools.

## Layout

```
chatgpt-tools/
├── main.py               # File-based runner: request.xml -> response.xml
├── clipboard_runner.py   # Clipboard-based runner (macOS pbpaste/pbcopy)
├── prompt.txt            # Agent operating instructions (system prompt)
├── dispatcher/
│   └── dispatcher.py     # ToolCall -> handler routing + validation
├── protocol/
│   ├── parser.py         # <tool_call>/<tool_batch> XML -> ToolCall
│   └── response.py       # ToolResult -> <tool_result> XML
├── models/
│   ├── tool_call.py      # ToolCall dataclass (tool, args, id)
│   └── tool_result.py    # ToolResult dataclass (success, data, id)
├── tools/
│   ├── registry.py       # HANDLERS table (32 tools) + arg plumbing
│   ├── schemas.py        # Per-tool required/optional arg schemas
│   ├── schema_validate.py# Schema enforcement
│   ├── contract.py       # Input validation + output normalization
│   ├── file_utils.py     # SHA-256, atomic writes, syntax checks
│   ├── ast_utils.py      # Symbol index, occurrence search, AST helpers
│   ├── symbol_engine.py  # Per-instance symbol index (see note below)
│   ├── read_file.py / write_file.py / create_file.py / delete_file.py
│   ├── patch_file.py     # Single-occurrence find-and-replace + stale checks
│   ├── list_files.py / search.py
│   ├── run_command.py    # Allowlisted subprocess execution (timeout 5s)
│   ├── run_interactive.py# Allowlisted PTY execution (timeout 30s)
│   ├── run_test.py / run_tests.py
│   ├── git_status.py / git_diff.py / git_log.py / git_show.py / git_blame.py
│   ├── find_definition.py / find_references.py / read_symbol.py
│   ├── patch_symbol.py / replace_function.py / add_function.py
│   ├── delete_function.py
│   ├── trace_call_graph.py / impact_analysis.py
│   ├── verify_patch.py   # Syntax + compile check (NOT a safety proof)
│   ├── project_map.py / help.py / tool_info.py / todo_store.py
├── tests/                # pytest suite (195 tests)
├── request.xml / *_test.xml
│                         # Hand-written example tool calls. Try them with:
│                         #   cp list_test.xml request.xml && python3 main.py
├── response.xml          # Output of the last main.py run (regenerated)
└── workspace/            # Example outputs produced by the *_test.xml fixtures
```

## The 32 tools

Filesystem: `READ_FILE` (with `sha256` + line ranges), `LIST_FILES`,
`WRITE_FILE` (optimistic `expected_sha` stale check), `CREATE_FILE`,
`DELETE_FILE`, `PATCH_FILE` (first-occurrence replace, `expected_sha`).

Execution: `RUN_COMMAND` (allowlist: `python python3 pytest git uv npm pnpm`,
5s timeout), `RUN_INTERACTIVE` (same allowlist via PTY, 30s timeout),
`RUN_TEST` / `RUN_TESTS` (run the local pytest suite).

Git (read-only except through the working tree): `GIT_STATUS`, `GIT_DIFF`,
`GIT_LOG` (integer `limit`, clamped 1-100), `GIT_SHOW`, `GIT_BLAME`.

Code intelligence (AST + ripgrep): `FIND_DEFINITION`, `FIND_REFERENCES`,
`READ_SYMBOL`, `PATCH_SYMBOL`, `REPLACE_FUNCTION`, `ADD_FUNCTION`,
`DELETE_FUNCTION`, `TRACE_CALL_GRAPH` (depth-capped at 5), `IMPACT_ANALYSIS`.

Project/task: `PROJECT_MAP`, `VERIFY_PATCH`, `TODO_ADD` / `TODO_LIST` /
`TODO_DONE` (stored in `todos.json` next to this package), `HELP`,
`TOOL_INFO`.

## Request flow

```
XML text
  -> protocol.parser.parse_tool_call[_from_root] / parse_tool_batch_from_root
  -> dispatcher.dispatch:
       validate_tool_input -> validate_against_schema -> handler(args)
       -> normalize_output -> ToolResult(success, data, id)
  -> protocol.response.to_xml / to_xml_batch
```

Unknown tool, missing/extra args, or a handler exception all produce
`ToolResult(success=False, ...)` — dispatch never raises.

Symbol lookups (`tools/ast_utils.py`) keep a process-wide cache. The
dispatcher drops that cache after every mutating tool
(`WRITE_FILE`, `CREATE_FILE`, `DELETE_FILE`, `PATCH_FILE`, `PATCH_SYMBOL`,
`REPLACE_FUNCTION`, `ADD_FUNCTION`, `DELETE_FUNCTION`), but there is no
mtime-based invalidation: external edits made behind the runtime's back
(in another process) can still read stale until the next dispatched
mutation. `symbol_engine.SymbolEngine` is a newer per-instance index that
supports explicit `force_reload()`; most tools still use the
`ast_utils` helpers.

## Security model (read this before running)

- **Filesystem tools resolve paths against your current working directory
  and perform no sandboxing.** `READ_FILE`, `WRITE_FILE`, etc. accept
  absolute paths and `..` segments anywhere the OS user can reach.
- **`RUN_COMMAND` / `RUN_INTERACTIVE` are an allowlist, not a sandbox.**
  `python`/`python3` on the list means arbitrary code execution is one
  tool call away by design — that is the point of a coding agent, but do
  not expose the runtime to untrusted input.
- No authentication exists anywhere in the tool layer; trust comes from
  "localhost only" (see the bridge README).
- External requirements: `rg` must be on `PATH` for `SEARCH`,
  `FIND_REFERENCES`, and the symbol tools (`find_python_files` falls back
  to a `pathlib` walk; the others report an error string). `pytest` must
  be importable for `RUN_TEST` / `RUN_TESTS` (invoked as
  `sys.executable -m pytest`).

## Running

```bash
python3 -m pytest tests/ -q        # full suite
cp list_test.xml request.xml && python3 main.py   # file-based run
python3 clipboard_runner.py        # clipboard-based run (macOS only)
```

`main.py` and `clipboard_runner.py` anchor their log/request paths to this
directory, so they work from any working directory. Logs go to
`logs/` (git-ignored); `todos.json` lives next to this package.
