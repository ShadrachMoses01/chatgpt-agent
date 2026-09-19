# Agent Wire Protocol

This document describes the tool-call protocol spoken between ChatGPT and
the local runtime. It is the contract; `chatgpt-tools/protocol/` is the
implementation. If they ever disagree, the implementation wins and this
file must be updated.

For how the *agent* is instructed to behave (bootstrap rule, one-batch
rule, discovery-before-edit workflow), see
`chatgpt-tools/prompt.txt` — that is the system prompt, not the wire
format.

## Single tool call

```xml
<tool_call id="optional-request-id">
  <tool>READ_FILE</tool>
  <path>tools/registry.py</path>
  <start>10</start>
  <end>20</end>
</tool_call>
```

- `<tool>` names the tool (required, non-empty). One of the 32 names in
  `chatgpt-tools/tools/registry.py` (`HELP`, `TOOL_INFO`, `READ_FILE`,
  `LIST_FILES`, `SEARCH`, `WRITE_FILE`, `CREATE_FILE`, `DELETE_FILE`,
  `PATCH_FILE`, `RUN_COMMAND`, `RUN_INTERACTIVE`, `RUN_TEST`, `RUN_TESTS`,
  `GIT_STATUS`, `GIT_DIFF`, `GIT_LOG`, `GIT_SHOW`, `GIT_BLAME`, `TODO_ADD`,
  `TODO_LIST`, `TODO_DONE`, `FIND_REFERENCES`, `FIND_DEFINITION`,
  `READ_SYMBOL`, `PATCH_SYMBOL`, `TRACE_CALL_GRAPH`, `VERIFY_PATCH`,
  `PROJECT_MAP`, `IMPACT_ANALYSIS`, `REPLACE_FUNCTION`, `ADD_FUNCTION`,
  `DELETE_FUNCTION`).
- Every other child element is an argument. **All argument values arrive
  as strings** (`child.text or ""`); numeric coercion happens inside
  handlers (e.g. `RUN_INTERACTIVE` casts `timeout` to `int`, `READ_FILE`
  casts `start`/`end`).
- The optional `id` attribute correlates request and result. `runtime.py`
  also adopts the root `id` as its log request id.
- Per-tool required/optional arguments are declared in
  `chatgpt-tools/tools/schemas.py` and enforced by
  `validate_against_schema`: missing required args, unknown args, and
  `None` values are rejected. `TOOL_INFO <tool>` reports a tool's schema.

## Batch requests

```xml
<tool_batch>
  <tool_call>
    <tool>READ_FILE</tool>
    <path>a.py</path>
  </tool_call>
  <tool_call>
    <tool>GIT_STATUS</tool>
  </tool_call>
</tool_batch>
```

- Batch children may each carry their own `id`.
- Execution is **sequential in document order** — each call observes the
  effects of earlier calls in the same batch.
- A `tool_call` child with a missing or empty `<tool>` is **silently
  skipped**; a batch with a wrong root tag raises `ValueError`.

## Tool results

```xml
<tool_result id="optional-request-id">
  <success>true</success>
  <tool><![CDATA[READ_FILE]]></tool>
  <content><![CDATA[...file contents...]]></content>
</tool_result>
```

Batch results are wrapped in `<tool_results>...</tool_results>`.

- Payload values are wrapped in `CDATA` (`]]>` inside values is escaped).
- Result-dict keys are sanitized to legal XML tag names (anything outside
  `[A-Za-z0-9_.-]` becomes `_`; leading digits get a `k_` prefix).
- The `id` attribute is XML-attribute-escaped and echoed only when the
  call carried one.

## Errors

Dispatch never raises. Every failure becomes a result or an envelope:

| Condition | Representation |
|---|---|
| Unknown tool name | `ToolResult(success=False, data={"error": "Unknown tool: ..."})` |
| Schema violation (missing/unknown/`None` arg) | `success=false` + `{"error": ...}` |
| Handler exception (e.g. file not found) | `success=false` + `{"error": ...}` |
| No valid tool XML in the message | `{"success": false, "error": "No valid XML found in message"}` (JSON; nothing is written to the clipboard) |
| Malformed XML / parse failure (clipboard runner) | `<tool_result><success>false</success><error_type>…</error_type><error_message>…</error_message><traceback><![CDATA[…]]></traceback></tool_result>` on the clipboard, details appended to `logs/errors.log` |
| Malformed XML (file runner `main.py`) | `<error><type>…</type><message>…</message><traceback>…</traceback></error>` written to `response.xml` |

Tracebacks contain local absolute paths. They are written to local logs
and (clipboard/file runners) echoed back into the result envelope.

## Extraction: chat text → XML

`chatgpt-bridge/bridge/xml_extractor.py` pulls candidate XML out of
free-form chat text before parsing:

1. Fenced code blocks first: ```` ```(xml)? … ``` ```` (non-greedy).
2. Then `<tool_batch …>…</tool_batch>` matches.
3. Then `<tool_call …>…</tool_call>` matches.

Each candidate is stripped, deduplicated, and validated with
`xml.etree.ElementTree`: the root tag must be `tool_call` or
`tool_batch`. `extract_xml` returns the **first** valid candidate;
`extract_all_xml` returns all of them. A batch written *outside* a fence
with several calls is found as one `tool_batch` candidate; bare sibling
`<tool_call>` blocks are found individually (the bridge executes the
first; the clipboard runner supports full batches).

Practical consequences: exactly one protocol block per model response is
expected (also enforced socially by `prompt.txt`'s one-batch rule);
anything outside the XML block is ignored, not executed.

## Dispatch: XML → tool → XML

`chatgpt-tools/dispatcher/dispatcher.py::dispatch`:

```
parse (ToolCall) → validate_tool_input (dict/str keys)
  → validate_against_schema (required/optional/unknown/None)
  → HANDLERS[tool](args) → normalize_output (JSON round-trip)
  → ToolResult(success=True, data, id)
```

- After `WRITE_FILE` / `CREATE_FILE` / `PATCH_FILE`, the dispatched file
  is re-read (best-effort cache warm; result discarded).
- After any mutating tool (`WRITE_FILE`, `CREATE_FILE`, `DELETE_FILE`,
  `PATCH_FILE`, `PATCH_SYMBOL`, `REPLACE_FUNCTION`, `ADD_FUNCTION`,
  `DELETE_FUNCTION`), the process-wide `ast_utils` symbol cache is
  invalidated. There is no mtime-based invalidation for edits made by
  other processes.
- `runtime.py` (bridge) writes the serialized result XML to the clipboard
  (`pbcopy`) and returns a JSON summary
  `{request_id, source, success, results:[{tool, success}], error}` to the
  HTTP caller.
