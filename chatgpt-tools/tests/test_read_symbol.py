from tools.read_symbol import execute as read_symbol


class TestReadSymbol:
    def test_find_known_function(self):
        result = read_symbol("execute", path="tools/read_symbol.py")
        assert result["symbol"] == "execute"
        assert result["kind"] == "function"
        assert result["file"] == "tools/read_symbol.py"

    def test_symbol_not_found(self):
        result = read_symbol("NONEXISTENT_SYMBOL_XYZ123")
        assert "error" in result

    def test_read_class(self):
        result = read_symbol("ToolCall", path="models/tool_call.py")
        assert result["symbol"] == "ToolCall"
        assert result["kind"] == "class"
