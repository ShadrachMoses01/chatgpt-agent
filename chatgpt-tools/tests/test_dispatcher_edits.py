from dispatcher.dispatcher import dispatch
from models.tool_call import ToolCall


class TestDispatcherReplaceFunction:
    def test_replace_via_dispatcher(self, tmp_path):
        path = tmp_path / "mod.py"
        path.write_text("def foo():\n    return 1\n")
        result = dispatch(ToolCall(
            tool="REPLACE_FUNCTION",
            args={"path": str(path), "symbol": "foo", "content": "def foo():\n    return 42"},
        ))
        assert result.success is True
        assert result.data["tool"] == "REPLACE_FUNCTION"
        assert result.data.get("syntax_ok") == "true"

    def test_replace_missing_args(self):
        result = dispatch(ToolCall(tool="REPLACE_FUNCTION", args={"path": "x.py"}))
        assert result.success is False


class TestDispatcherAddFunction:
    def test_add_via_dispatcher(self, tmp_path):
        path = tmp_path / "mod.py"
        path.write_text("def foo(): pass\n")
        result = dispatch(ToolCall(
            tool="ADD_FUNCTION",
            args={"path": str(path), "content": "def bar(): pass"},
        ))
        assert result.success is True
        assert result.data.get("syntax_ok") == "true"


class TestDispatcherDeleteFunction:
    def test_delete_via_dispatcher(self, tmp_path):
        path = tmp_path / "mod.py"
        path.write_text("def foo():\n    return 1\n")
        result = dispatch(ToolCall(
            tool="DELETE_FUNCTION",
            args={"path": str(path), "symbol": "foo"},
        ))
        assert result.success is True
        assert result.data.get("syntax_ok") == "true"


class TestDispatcherShaGuards:
    def test_write_sha_mismatch(self, tmp_path):
        path = tmp_path / "test.txt"
        path.write_text("original")
        result = dispatch(ToolCall(
            tool="WRITE_FILE",
            args={"path": str(path), "content": "new", "expected_sha": "badsha"},
        ))
        # should still succeed but report the stale state error
        assert result.data.get("error", "").startswith("stale file state")

    def test_patch_sha_mismatch(self, tmp_path):
        path = tmp_path / "test.txt"
        path.write_text("original")
        result = dispatch(ToolCall(
            tool="PATCH_FILE",
            args={"path": str(path), "find": "x", "replace": "y", "expected_sha": "badsha"},
        ))
        assert "stale file state" in result.data.get("error", "")

    def test_read_returns_sha(self):
        result = dispatch(ToolCall(tool="READ_FILE", args={"path": "README.md"}))
        assert result.success is True
        assert "sha256" in result.data
        assert len(result.data["sha256"]) == 64
