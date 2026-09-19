import pytest
from dispatcher.dispatcher import dispatch
from models.tool_call import ToolCall


class TestDispatchUnknown:
    def test_unknown_tool(self):
        result = dispatch(ToolCall(tool="DOES_NOT_EXIST", args={}))
        assert result.success is False
        assert "Unknown tool" in result.data["error"]

    def test_empty_tool_name(self):
        result = dispatch(ToolCall(tool="", args={}))
        assert result.success is False


class TestDispatchHelp:
    def test_help(self):
        result = dispatch(ToolCall(tool="HELP", args={}))
        assert result.success is True
        assert result.data["tool"] == "HELP"
        assert "READ_FILE" in result.data["output"]


class TestDispatchReadFile:
    def test_read_existing(self):
        result = dispatch(ToolCall(tool="READ_FILE", args={"path": "README.md"}))
        assert result.success is True
        assert result.data["tool"] == "READ_FILE"
        assert "README.md" in result.data["path"]
        assert "content" in result.data

    def test_read_non_existent(self):
        result = dispatch(ToolCall(tool="READ_FILE", args={"path": "does_not_exist_123"}))
        assert result.success is False

    def test_read_missing_path(self):
        result = dispatch(ToolCall(tool="READ_FILE", args={}))
        assert result.success is False


class TestDispatchListFiles:
    def test_list_current_dir(self):
        result = dispatch(ToolCall(tool="LIST_FILES", args={"path": "."}))
        assert result.success is True
        assert result.data["tool"] == "LIST_FILES"
        assert "main.py" in result.data["files"]

    def test_list_non_existent(self):
        result = dispatch(ToolCall(tool="LIST_FILES", args={"path": "does_not_exist_123"}))
        assert result.success is False


class TestDispatchWriteFile:
    def test_write(self, tmp_path):
        path = tmp_path / "test_write.txt"
        result = dispatch(ToolCall(
            tool="WRITE_FILE",
            args={"path": str(path), "content": "test content"},
        ))
        assert result.success is True
        assert path.read_text() == "test content"

    def test_write_missing_args(self):
        result = dispatch(ToolCall(tool="WRITE_FILE", args={"path": "x.txt"}))
        assert result.success is False


class TestDispatchCreateFile:
    def test_create_new(self, tmp_path):
        path = tmp_path / "new_file.txt"
        result = dispatch(ToolCall(
            tool="CREATE_FILE",
            args={"path": str(path), "content": "new"},
        ))
        assert result.success is True
        assert path.read_text() == "new"

    def test_create_existing(self, tmp_path):
        path = tmp_path / "exists.txt"
        path.write_text("original")
        result = dispatch(ToolCall(
            tool="CREATE_FILE",
            args={"path": str(path), "content": "overwrite"},
        ))
        assert result.success is True
        assert "already exists" in result.data["result"]


class TestDispatchPatchFile:
    def test_patch(self, tmp_path):
        path = tmp_path / "patch_test.txt"
        path.write_text("hello world")
        result = dispatch(ToolCall(
            tool="PATCH_FILE",
            args={"path": str(path), "find": "hello", "replace": "goodbye"},
        ))
        assert result.success is True
        assert path.read_text() == "goodbye world"

    def test_patch_not_found(self, tmp_path):
        path = tmp_path / "patch_test2.txt"
        path.write_text("hello world")
        result = dispatch(ToolCall(
            tool="PATCH_FILE",
            args={"path": str(path), "find": "zzz", "replace": "aaa"},
        ))
        assert result.success is True
        assert "not found" in result.data["result"]

    def test_patch_non_existent(self, tmp_path):
        path = tmp_path / "no_file.txt"
        result = dispatch(ToolCall(
            tool="PATCH_FILE",
            args={"path": str(path), "find": "x", "replace": "y"},
        ))
        assert result.success is True
        assert "File not found" in result.data["result"]


class TestDispatchDeleteFile:
    def test_delete(self, tmp_path):
        path = tmp_path / "to_delete.txt"
        path.write_text("delete me")
        result = dispatch(ToolCall(
            tool="DELETE_FILE",
            args={"path": str(path)},
        ))
        assert result.success is True
        assert not path.exists()

    def test_delete_non_existent(self, tmp_path):
        path = tmp_path / "no_file.txt"
        result = dispatch(ToolCall(
            tool="DELETE_FILE",
            args={"path": str(path)},
        ))
        assert result.success is True
        assert "File not found" in result.data["result"]


class TestDispatchRunCommand:
    def test_run_allowed(self):
        result = dispatch(ToolCall(tool="RUN_COMMAND", args={"command": "python3 --version"}))
        assert result.success is True
        assert "Python" in result.data["stdout"]

    def test_run_disallowed(self):
        result = dispatch(ToolCall(tool="RUN_COMMAND", args={"command": "rm -rf /"}))
        assert result.success is True
        assert "not allowed" in result.data["reason"]

    def test_run_empty(self):
        result = dispatch(ToolCall(tool="RUN_COMMAND", args={"command": ""}))
        assert result.success is True
        assert "Empty command" in result.data["error"]


class TestDispatchGit:
    def test_git_status(self):
        result = dispatch(ToolCall(tool="GIT_STATUS", args={}))
        assert result.success is True

    def test_git_diff(self):
        result = dispatch(ToolCall(tool="GIT_DIFF", args={}))
        assert result.success is True


class TestDispatchSearch:
    def test_search(self):
        result = dispatch(ToolCall(tool="SEARCH", args={"query": "def execute"}))
        assert result.success is True
        assert "execute" in result.data["matches"]


class TestDispatchTodo:
    def test_todo_add_list_done(self, monkeypatch):
        import json, pathlib
        p = pathlib.Path("/tmp/test_todos_dispatcher.json")
        if p.exists():
            p.unlink()
        monkeypatch.setattr("tools.todo_store.DB_PATH", p)

        add = dispatch(ToolCall(tool="TODO_ADD", args={"title": "test dispatch", "priority": "high"}))
        assert add.success is True
        todo_id = add.data["todo"]["id"]

        lst = dispatch(ToolCall(tool="TODO_LIST", args={}))
        assert lst.success is True
        assert any(t["id"] == todo_id for t in lst.data["todos"])

        done = dispatch(ToolCall(tool="TODO_DONE", args={"id": todo_id}))
        assert done.success is True
        assert done.data["todo"]["done"] is True

        p.unlink(missing_ok=True)

    def test_todo_done_not_found(self):
        result = dispatch(ToolCall(tool="TODO_DONE", args={"id": "nonexistent"}))
        assert result.success is True
        assert "error" in result.data["todo"]


class TestDispatchIdPropagation:
    def test_id_propagates_to_result(self):
        result = dispatch(ToolCall(tool="HELP", args={}, id="42"))
        assert result.id == "42"

    def test_empty_id_defaults(self):
        result = dispatch(ToolCall(tool="HELP", args={}))
        assert result.id == ""

    def test_id_propagates_on_error(self):
        result = dispatch(ToolCall(tool="DOES_NOT_EXIST", args={}, id="99"))
        assert result.id == "99"


class TestDispatchNewTools:
    def test_tool_info(self):
        result = dispatch(ToolCall(tool="TOOL_INFO", args={}))
        assert result.success is True
        assert "tools" in result.data

    def test_tool_info_specific(self):
        result = dispatch(ToolCall(tool="TOOL_INFO", args={"target": "READ_FILE"}))
        assert result.success is True
        assert result.data["tool"] == "READ_FILE"

    def test_read_symbol(self):
        result = dispatch(ToolCall(
            tool="READ_SYMBOL",
            args={"symbol": "execute", "path": "tools/read_symbol.py"},
        ))
        assert result.success is True
        assert result.data["symbol"] == "execute"

    def test_read_symbol_not_found(self):
        result = dispatch(ToolCall(
            tool="READ_SYMBOL",
            args={"symbol": "NONEXISTENT_SYMBOL_XYZ"},
        ))
        assert result.success is True
        assert "error" in result.data

    def test_run_interactive(self):
        result = dispatch(ToolCall(
            tool="RUN_INTERACTIVE",
            args={"command": "python3 --version", "timeout": "5"},
        ))
        assert result.success is True
        assert "Python" in result.data["output"]
