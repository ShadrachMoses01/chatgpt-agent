from models.tool_result import ToolResult
from tools.registry import get_handler
from tools.contract import validate_tool_input, normalize_output
from tools.schema_validate import validate_against_schema
from tools.ast_utils import invalidate_symbol_cache
from tools.read_file import execute as read_file

POST_READ_TOOLS = {"WRITE_FILE", "CREATE_FILE", "PATCH_FILE"}

# Tools that add, remove, or rewrite Python files. After any of these run,
# the process-wide symbol index (tools.ast_utils.resolve_symbol cache) is
# stale and must be dropped.
MUTATING_TOOLS = {
    "WRITE_FILE",
    "CREATE_FILE",
    "DELETE_FILE",
    "PATCH_FILE",
    "PATCH_SYMBOL",
    "REPLACE_FUNCTION",
    "ADD_FUNCTION",
    "DELETE_FUNCTION",
}


def dispatch(tool_call):
    handler = get_handler(tool_call.tool)

    if handler is None:
        return ToolResult(
            success=False,
            data={"error": f"Unknown tool: {tool_call.tool}"},
            id=tool_call.id,
        )

    try:
        args = validate_tool_input(tool_call.args)
        args = validate_against_schema(tool_call.tool, args)

        result = handler(args)

        normalized = normalize_output(result)

        if tool_call.tool in POST_READ_TOOLS:
            try:
                path = args.get("path")
                if path:
                    read_file(path)
            except Exception:
                pass

        if tool_call.tool in MUTATING_TOOLS:
            try:
                invalidate_symbol_cache()
            except Exception:
                pass

        return ToolResult(success=True, data=normalized, id=tool_call.id)

    except Exception as e:
        return ToolResult(
            success=False,
            data=normalize_output({"error": str(e)}),
            id=tool_call.id,
        )
