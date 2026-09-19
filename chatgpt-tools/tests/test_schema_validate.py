import pytest
from tools.schema_validate import validate_against_schema


class TestValidateAgainstSchema:
    def test_valid(self):
        result = validate_against_schema("READ_FILE", {"path": "README.md"})
        assert result == {"path": "README.md"}

    def test_missing_required_arg(self):
        with pytest.raises(ValueError, match="Missing required args"):
            validate_against_schema("READ_FILE", {})

    def test_unknown_tool(self):
        with pytest.raises(ValueError, match="No schema defined"):
            validate_against_schema("UNKNOWN_TOOL", {})

    def test_none_value(self):
        with pytest.raises(ValueError, match="cannot be None"):
            validate_against_schema("READ_FILE", {"path": None})

    def test_non_dict_args(self):
        with pytest.raises(ValueError, match="must be a dict"):
            validate_against_schema("READ_FILE", "not a dict")

    def test_additional_args_allowed(self):
        with pytest.raises(ValueError, match="Unknown args"):
            validate_against_schema(
                "READ_FILE", {"path": "f.txt", "extra": "ignored"}
            )

    def test_tool_with_no_required_args(self):
        result = validate_against_schema("HELP", {})
        assert result == {}

    def test_tool_with_no_required_args_but_extra(self):
        with pytest.raises(ValueError, match="Unknown args"):
            validate_against_schema("HELP", {"unexpected": "val"})
