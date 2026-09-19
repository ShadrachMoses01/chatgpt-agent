from tools.read_file import execute as read_file
from tools.list_files import execute as list_files
from tools.search import execute as search
from tools.write_file import execute as write_file
from tools.create_file import execute as create_file
from tools.delete_file import execute as delete_file
from tools.patch_file import execute as patch_file
from tools.run_command import execute as run_command
from tools.run_interactive import execute as run_interactive
from tools.run_tests import execute as run_tests
from tools.git_status import execute as git_status
from tools.git_diff import execute as git_diff
from tools.git_log import execute as git_log
from tools.git_show import execute as git_show
from tools.git_blame import execute as git_blame
from tools.help import execute as help_tool
from tools.tool_info import execute as tool_info
from tools.todo_store import add_todo, list_todos, mark_done
from tools.find_references import execute as find_references
from tools.find_definition import execute as find_definition
from tools.read_symbol import execute as read_symbol
from tools.patch_symbol import execute as patch_symbol
from tools.trace_call_graph import execute as trace_call_graph
from tools.run_test import execute as run_test
from tools.verify_patch import execute as verify_patch
from tools.project_map import execute as project_map
from tools.impact_analysis import execute as impact_analysis
from tools.replace_function import execute as replace_function
from tools.add_function import execute as add_function
from tools.delete_function import execute as delete_function
from tools.schemas import DEFAULT_TOOL_SCHEMAS
from pathlib import Path
import os


def _make_result(tool_name, data, args=None):
    result = {"tool": tool_name}
    if args:
        result.update(args)
    if isinstance(data, dict):
        result.update(data)
    else:
        result["output"] = data
    return result


def _with_cwd(data):
    if isinstance(data, dict):
        data["cwd"] = os.getcwd()
    return data


HANDLERS = {
    "HELP": lambda args: _with_cwd(_make_result("HELP", help_tool())),
    "TOOL_INFO": lambda args: _with_cwd(
        _make_result("TOOL_INFO", tool_info(args.get("target", "")))
    ),
    "READ_FILE": lambda args: _with_cwd(
        _make_result(
            "READ_FILE",
            read_file(
                args["path"],
                start=args.get("start"),
                end=args.get("end"),
            ),
        )
    ),
    "LIST_FILES": lambda args: _with_cwd(
        _make_result("LIST_FILES", {"path": args["path"], "files": list_files(args["path"])})
    ),
    "SEARCH": lambda args: _with_cwd(
        _make_result("SEARCH", {"query": args["query"], "matches": search(args["query"])})
    ),
    "WRITE_FILE": lambda args: _with_cwd(
        _make_result("WRITE_FILE", {"path": args["path"], **write_file(
            args["path"],
            args["content"],
            args.get("expected_sha", ""),
        )})
    ),
    "CREATE_FILE": lambda args: _with_cwd(
        _make_result("CREATE_FILE", {"path": args["path"], **create_file(
            args["path"], args["content"],
        )})
    ),
    "DELETE_FILE": lambda args: _with_cwd(
        _make_result("DELETE_FILE", {"path": args["path"], "result": delete_file(args["path"])})
    ),
    "PATCH_FILE": lambda args: _with_cwd(
        _make_result("PATCH_FILE", {"path": args["path"], **patch_file(
            args["path"],
            args["find"],
            args["replace"],
            args.get("expected_sha", ""),
        )})
    ),
    "RUN_COMMAND": lambda args: _with_cwd(
        _make_result("RUN_COMMAND", {"command": args["command"], **run_command(args["command"])})
    ),
    "RUN_INTERACTIVE": lambda args: _with_cwd(
        _make_result("RUN_INTERACTIVE", {"command": args["command"], **run_interactive(
            args["command"],
            timeout=int(args.get("timeout", 30)),
        )})
    ),
    "RUN_TESTS": lambda args: _with_cwd(_make_result("RUN_TESTS", run_tests())),
    "GIT_STATUS": lambda args: _with_cwd(
        _make_result("GIT_STATUS", git_status())
    ),
    "GIT_DIFF": lambda args: _with_cwd(
        _make_result("GIT_DIFF", git_diff())
    ),
    "GIT_LOG": lambda args: _with_cwd(
        _make_result("GIT_LOG", git_log(args.get("limit", "10")))
    ),
    "GIT_SHOW": lambda args: _with_cwd(
        _make_result("GIT_SHOW", {"commit": args["commit"], **git_show(args["commit"])})
    ),
    "GIT_BLAME": lambda args: _with_cwd(
        _make_result("GIT_BLAME", {"path": args["path"], **git_blame(args["path"])})
    ),
    "TODO_ADD": lambda args: _with_cwd(
        _make_result("TODO_ADD", {"todo": add_todo(
            args["title"],
            args.get("priority", "medium"),
            args.get("category", "project"),
        )})
    ),
    "TODO_LIST": lambda args: _with_cwd(
        _make_result("TODO_LIST", {"todos": list_todos()})
    ),
    "TODO_DONE": lambda args: _with_cwd(
        _make_result("TODO_DONE", {"todo": mark_done(args["id"])})
    ),
    "FIND_REFERENCES": lambda args: _with_cwd(
        _make_result("FIND_REFERENCES", {"symbol": args["symbol"], "output": find_references(args["symbol"])})
    ),
    "FIND_DEFINITION": lambda args: _with_cwd(
        _make_result("FIND_DEFINITION", {"symbol": args["symbol"], "definition": find_definition(args["symbol"])})
    ),
    "READ_SYMBOL": lambda args: _with_cwd(
        _make_result("READ_SYMBOL", read_symbol(
            args["symbol"],
            path=args.get("path", ""),
        ))
    ),
    "PATCH_SYMBOL": lambda args: _with_cwd(
        _make_result("PATCH_SYMBOL", patch_symbol(
            args["path"],
            args["symbol"],
            args["content"],
            args.get("expected_sha", ""),
        ))
    ),
    "TRACE_CALL_GRAPH": lambda args: _with_cwd(
        _make_result("TRACE_CALL_GRAPH", {"symbol": args["symbol"], "output": trace_call_graph(args["symbol"])})
    ),
    "RUN_TEST": lambda args: _with_cwd(
        _make_result("RUN_TEST", {"test": args.get("test", ""), "output": run_test(args.get("test", ""))})
    ),
    "VERIFY_PATCH": lambda args: _with_cwd(
        _make_result("VERIFY_PATCH", {"path": args["path"], "report": verify_patch(args["path"])})
    ),
    "PROJECT_MAP": lambda args: _with_cwd(
        _make_result("PROJECT_MAP", {"map": project_map()})
    ),
    "IMPACT_ANALYSIS": lambda args: _with_cwd(
        _make_result("IMPACT_ANALYSIS", {"symbol": args["symbol"], "output": impact_analysis(args["symbol"])})
    ),
    "REPLACE_FUNCTION": lambda args: _with_cwd(
        _make_result("REPLACE_FUNCTION", replace_function(
            args["path"],
            args["symbol"],
            args["content"],
            args.get("expected_sha", ""),
        ))
    ),
    "ADD_FUNCTION": lambda args: _with_cwd(
        _make_result("ADD_FUNCTION", add_function(
            args["path"],
            args["content"],
            args.get("after", ""),
            args.get("expected_sha", ""),
        ))
    ),
    "DELETE_FUNCTION": lambda args: _with_cwd(
        _make_result("DELETE_FUNCTION", delete_function(
            args["path"],
            args["symbol"],
            args.get("expected_sha", ""),
        ))
    ),
}


def get_handler(name: str):
    return HANDLERS.get(name)
