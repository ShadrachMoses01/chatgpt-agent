from tools.tool_info import execute as tool_info


class TestToolInfo:
    def test_list_all_tools(self):
        result = tool_info()
        assert "tools" in result
        assert result["count"] > 0
        assert "READ_FILE" in result["tools"]

    def test_specific_tool(self):
        result = tool_info(tool="READ_FILE")
        assert result["tool"] == "READ_FILE"
        assert result["required"] != ""
        assert result["description"] != ""
        assert result["curated"] == "false"

    def test_unknown_tool(self):
        result = tool_info(tool="FAKE_TOOL")
        assert "error" in result
