from models.tool_result import ToolResult
from protocol.response import to_xml, to_xml_batch, result_to_xml, batch_to_xml


class TestResponseId:
    def test_id_present(self):
        result = ToolResult(success=True, data={"tool": "TEST"}, id="42")
        xml = result_to_xml(result)
        assert 'id="42"' in xml

    def test_id_absent(self):
        result = ToolResult(success=True, data={"tool": "TEST"})
        xml = result_to_xml(result)
        assert 'id="' not in xml

    def test_batch_ids(self):
        results = [
            ToolResult(success=True, data={"tool": "A"}, id="1"),
            ToolResult(success=True, data={"tool": "B"}, id="2"),
        ]
        xml = batch_to_xml(results)
        assert xml.count('<tool_result ') == 2
        assert 'id="1"' in xml
        assert 'id="2"' in xml

    def test_batch_no_ids(self):
        results = [
            ToolResult(success=True, data={"tool": "A"}),
            ToolResult(success=True, data={"tool": "B"}),
        ]
        xml = batch_to_xml(results)
        assert xml.count('<tool_result>') == 2


class TestToXml:
    def test_success(self):
        result = ToolResult(success=True, data={"tool": "TEST"})
        xml = to_xml(result)
        assert "<success>true</success>" in xml
        assert "<tool>" in xml
        assert "TEST" in xml
        assert "<![CDATA[" in xml

    def test_failure(self):
        result = ToolResult(success=False, data={"error": "something broke"})
        xml = to_xml(result)
        assert "<success>false</success>" in xml
        assert "something broke" in xml

    def test_multiple_keys(self):
        result = ToolResult(success=True, data={"tool": "READ_FILE", "path": "x.txt", "content": "hello"})
        xml = to_xml(result)
        assert "READ_FILE" in xml
        assert "x.txt" in xml
        assert "hello" in xml

    def test_special_chars(self):
        result = ToolResult(success=True, data={"output": "foo <bar> & \"baz\""})
        xml = to_xml(result)
        assert "foo <bar> & \"baz\"" in xml

    def test_empty_data(self):
        result = ToolResult(success=True, data={})
        xml = to_xml(result)
        assert "<success>true</success>" in xml

    def test_boolean_values(self):
        result = ToolResult(success=True, data={"flag": True})
        xml = to_xml(result)
        assert "<success>true</success>" in xml


class TestToXmlBatch:
    def test_multiple_results(self):
        results = [
            ToolResult(success=True, data={"tool": "A"}),
            ToolResult(success=False, data={"error": "B failed"}),
        ]
        xml = to_xml_batch(results)
        assert "<tool_results>" in xml
        assert xml.count("</tool_result>") == 2
        assert "<success>true</success>" in xml
        assert "<success>false</success>" in xml

    def test_single_result(self):
        results = [ToolResult(success=True, data={"tool": "X"})]
        xml = to_xml_batch(results)
        assert "<tool_results>" in xml
        assert xml.count("</tool_result>") == 1
