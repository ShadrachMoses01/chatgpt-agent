import xml.etree.ElementTree as ET
import pytest
from protocol.parser import (
    parse_tool_call,
    parse_tool_batch,
    parse_tool_call_from_root,
    parse_tool_batch_from_root,
)
from models.tool_call import ToolCall


class TestParseToolCall:
    def test_basic(self):
        xml = """<tool_call><tool>READ_FILE</tool><path>foo.txt</path></tool_call>"""
        result = parse_tool_call(xml)
        assert result.tool == "READ_FILE"
        assert result.args == {"path": "foo.txt"}

    def test_multiple_args(self):
        xml = """<tool_call><tool>WRITE_FILE</tool><path>f.txt</path><content>hello</content></tool_call>"""
        result = parse_tool_call(xml)
        assert result.tool == "WRITE_FILE"
        assert result.args == {"path": "f.txt", "content": "hello"}

    def test_no_args(self):
        xml = """<tool_call><tool>HELP</tool></tool_call>"""
        result = parse_tool_call(xml)
        assert result.tool == "HELP"
        assert result.args == {}

    def test_missing_tool_tag(self):
        xml = """<tool_call><path>foo.txt</path></tool_call>"""
        with pytest.raises(ValueError, match="Missing <tool> tag"):
            parse_tool_call(xml)

    def test_invalid_xml(self):
        with pytest.raises(Exception):
            parse_tool_call("not xml")

    def test_empty_value(self):
        xml = """<tool_call><tool>READ_FILE</tool><path></path></tool_call>"""
        result = parse_tool_call(xml)
        assert result.args == {"path": ""}

    def test_whitespace_in_tool_name(self):
        xml = """<tool_call><tool>  READ_FILE  </tool><path>f.txt</path></tool_call>"""
        result = parse_tool_call(xml)
        assert result.tool == "READ_FILE"

    def test_with_id(self):
        xml = """<tool_call id="42"><tool>READ_FILE</tool><path>f.txt</path></tool_call>"""
        result = parse_tool_call(xml)
        assert result.id == "42"
        assert result.tool == "READ_FILE"

    def test_without_id(self):
        xml = """<tool_call><tool>HELP</tool></tool_call>"""
        result = parse_tool_call(xml)
        assert result.id == ""


class TestParseToolCallFromRoot:
    """Same tests as above but using pre-parsed root (avoiding double-parse)."""

    def test_basic(self):
        root = ET.fromstring("<tool_call><tool>HELP</tool></tool_call>")
        result = parse_tool_call_from_root(root)
        assert result.tool == "HELP"

    def test_with_args(self):
        root = ET.fromstring(
            "<tool_call><tool>WRITE_FILE</tool><path>x</path><content>y</content></tool_call>"
        )
        result = parse_tool_call_from_root(root)
        assert result.args == {"path": "x", "content": "y"}

    def test_missing_tool(self):
        root = ET.fromstring("<tool_call><path>x</path></tool_call>")
        with pytest.raises(ValueError, match="Missing <tool> tag"):
            parse_tool_call_from_root(root)

    def test_with_id(self):
        root = ET.fromstring('<tool_call id="99"><tool>HELP</tool></tool_call>')
        result = parse_tool_call_from_root(root)
        assert result.id == "99"

    def test_without_id(self):
        root = ET.fromstring("<tool_call><tool>HELP</tool></tool_call>")
        result = parse_tool_call_from_root(root)
        assert result.id == ""


class TestParseToolBatch:
    def test_basic_batch(self):
        xml = """<tool_batch>
  <tool_call><tool>HELP</tool></tool_call>
  <tool_call><tool>READ_FILE</tool><path>f.txt</path></tool_call>
</tool_batch>"""
        results = parse_tool_batch(xml)
        assert len(results) == 2
        assert results[0].tool == "HELP"
        assert results[1].tool == "READ_FILE"
        assert results[1].args == {"path": "f.txt"}

    def test_wrong_root_tag(self):
        xml = """<tool_call><tool>HELP</tool></tool_call>"""
        with pytest.raises(ValueError, match="Expected <tool_batch>"):
            parse_tool_batch(xml)

    def test_empty_batch(self):
        xml = """<tool_batch></tool_batch>"""
        results = parse_tool_batch(xml)
        assert results == []

    def test_skips_missing_tool(self):
        xml = """<tool_batch>
  <tool_call><path>f.txt</path></tool_call>
  <tool_call><tool>HELP</tool></tool_call>
</tool_batch>"""
        results = parse_tool_batch(xml)
        assert len(results) == 1
        assert results[0].tool == "HELP"

    def test_batch_with_ids(self):
        xml = """<tool_batch>
  <tool_call id="1"><tool>HELP</tool></tool_call>
  <tool_call id="2"><tool>HELP</tool></tool_call>
</tool_batch>"""
        results = parse_tool_batch(xml)
        assert results[0].id == "1"
        assert results[1].id == "2"

    def test_batch_mixed_ids(self):
        xml = """<tool_batch>
  <tool_call id="1"><tool>A</tool></tool_call>
  <tool_call><tool>B</tool></tool_call>
</tool_batch>"""
        results = parse_tool_batch(xml)
        assert results[0].id == "1"
        assert results[1].id == ""


class TestParseToolBatchFromRoot:
    def test_basic(self):
        root = ET.fromstring(
            "<tool_batch><tool_call><tool>A</tool></tool_call></tool_batch>"
        )
        results = parse_tool_batch_from_root(root)
        assert len(results) == 1
        assert results[0].tool == "A"

    def test_wrong_root(self):
        root = ET.fromstring("<tool_call><tool>X</tool></tool_call>")
        with pytest.raises(ValueError, match="Expected <tool_batch>"):
            parse_tool_batch_from_root(root)
