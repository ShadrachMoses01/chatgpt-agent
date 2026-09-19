"""Regression tests for bugs found during the public-release audit.

Each test pins a real defect that was fixed — not trivial behavior:
stale symbol cache after mutations, a registered tool with no schema,
quoted-argument splitting in the PTY runner, XML injection via result
ids/keys, empty <tool> tags, and git-log flag injection.
"""
import xml.etree.ElementTree as ET

from dispatcher.dispatcher import dispatch
from models.tool_call import ToolCall
from models.tool_result import ToolResult
from protocol.parser import parse_tool_call, parse_tool_batch
from protocol.response import result_to_xml
from tools import ast_utils
from tools.git_log import execute as git_log
from tools.registry import HANDLERS
from tools.run_interactive import execute as run_interactive
from tools.schemas import DEFAULT_TOOL_SCHEMAS


class TestRegistrySchemaParity:
    def test_every_handler_has_schema(self):
        missing = sorted(set(HANDLERS) - set(DEFAULT_TOOL_SCHEMAS))
        assert missing == [], f"handlers without schema: {missing}"

    def test_every_schema_has_handler(self):
        missing = sorted(set(DEFAULT_TOOL_SCHEMAS) - set(HANDLERS))
        assert missing == [], f"schemas without handler: {missing}"

    def test_find_references_dispatches(self):
        result = dispatch(ToolCall(tool="FIND_REFERENCES", args={"symbol": "dispatch"}))
        assert result.success is True


class TestSymbolCacheInvalidation:
    def test_mutation_drops_cache(self, tmp_path):
        path = tmp_path / "mod.py"
        path.write_text("def foo():\n    return 1\n")
        ast_utils.resolve_symbol("anything_at_all", root=str(tmp_path))
        assert hasattr(ast_utils.resolve_symbol, "_symbol_cache")

        result = dispatch(ToolCall(
            tool="WRITE_FILE",
            args={"path": str(path), "content": "def foo():\n    return 2\n"},
        ))
        assert result.success is True
        assert not hasattr(ast_utils.resolve_symbol, "_symbol_cache")

    def test_ambiguity_detected_across_files(self, tmp_path):
        (tmp_path / "a.py").write_text("def dup():\n    return 1\n")
        (tmp_path / "b.py").write_text("def dup():\n    return 2\n")
        assert ast_utils._is_ambiguous_symbol("dup", root=str(tmp_path)) is True
        assert ast_utils._is_ambiguous_symbol("missing_xyz", root=str(tmp_path)) is False


class TestRunInteractiveParsing:
    def test_quoted_args_preserved(self):
        result = run_interactive("python3 -c \"print('hello world')\"", timeout=15)
        assert result["success"] is True
        assert result["timed_out"] is False
        assert "hello world" in result["output"]

    def test_disallowed_command(self):
        result = run_interactive("rm -rf /")
        assert result["success"] is False
        assert "not allowed" in result["reason"]


class TestResponseEscaping:
    def test_id_with_quote_is_escaped_and_parseable(self):
        result = ToolResult(success=True, data={"tool": "X"}, id='a"b')
        xml = result_to_xml(result)
        root = ET.fromstring(xml)  # must still parse
        assert root.get("id") == 'a"b'

    def test_unsafe_key_is_sanitized_and_parseable(self):
        result = ToolResult(success=True, data={"a b<c>": "v"})
        xml = result_to_xml(result)
        root = ET.fromstring(xml)  # must still parse
        assert root.find("a_b_c_").text == "v"


class TestParserEdgeCases:
    def test_empty_tool_tag_rejected(self):
        import pytest
        with pytest.raises(ValueError, match="Missing <tool> tag"):
            parse_tool_call("<tool_call><tool>   </tool><path>x</path></tool_call>")

    def test_batch_skips_empty_tool(self):
        xml = (
            "<tool_batch>"
            "<tool_call><tool></tool><path>x</path></tool_call>"
            "<tool_call><tool>HELP</tool></tool_call>"
            "</tool_batch>"
        )
        calls = parse_tool_batch(xml)
        assert [c.tool for c in calls] == ["HELP"]


class TestGitLogLimit:
    def test_non_integer_limit_rejected(self):
        result = git_log("--help")
        assert result["output"] == ""
        assert "Invalid limit" in result["reason"]

    def test_injection_style_limit_rejected(self):
        result = git_log("10 --oneline")
        assert result["output"] == ""
        assert "Invalid limit" in result["reason"]
