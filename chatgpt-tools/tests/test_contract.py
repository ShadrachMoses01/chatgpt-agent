import pytest
from tools.contract import validate_tool_input, normalize_output, strict_output_check


class TestValidateToolInput:
    def test_valid_dict(self):
        assert validate_tool_input({"a": 1}) == {"a": 1}

    def test_non_dict(self):
        with pytest.raises(ValueError, match="must be a dict"):
            validate_tool_input("not a dict")

    def test_none(self):
        with pytest.raises(ValueError, match="must be a dict"):
            validate_tool_input(None)

    def test_non_string_keys(self):
        with pytest.raises(ValueError, match="must be strings"):
            validate_tool_input({1: "value"})

    def test_empty_dict(self):
        assert validate_tool_input({}) == {}


class TestNormalizeOutput:
    def test_simple_dict(self):
        assert normalize_output({"a": 1}) == {"a": 1}

    def test_with_nested(self):
        data = {"a": {"b": [1, 2, 3]}}
        assert normalize_output(data) == data

    def test_with_non_serializable(self):
        class Custom:
            def __str__(self):
                return "custom_str"
        result = normalize_output({"obj": Custom()})
        assert result["obj"] == "custom_str"

    def test_with_none(self):
        result = normalize_output({"a": None})
        assert result == {"a": None}

    def test_list(self):
        result = normalize_output([1, 2, 3])
        assert result == [1, 2, 3]


class TestStrictOutputCheck:
    def test_valid(self):
        assert strict_output_check({"a": 1}) == {"a": 1}

    def test_non_serializable(self):
        result = strict_output_check({"a": "string"})
        assert result == {"a": "string"}
