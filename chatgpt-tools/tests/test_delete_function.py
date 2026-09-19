from pathlib import Path
from tools.delete_function import execute


class TestDeleteFunction:
    def test_delete_existing(self, tmp_path):
        path = tmp_path / "mod.py"
        path.write_text("def foo():\n    return 1\n\ndef bar():\n    return 2\n")
        result = execute(str(path), "foo")
        assert "result" in result
        assert result.get("syntax_ok") == "true"
        new = path.read_text()
        assert "def foo" not in new
        assert "def bar" in new

    def test_delete_nonexistent(self, tmp_path):
        path = tmp_path / "mod.py"
        path.write_text("def foo(): pass\n")
        result = execute(str(path), "nonexistent")
        assert "error" in result
        assert "not found" in result["error"]

    def test_delete_nonexistent_file(self, tmp_path):
        path = tmp_path / "nope.py"
        result = execute(str(path), "foo")
        assert "error" in result
        assert "File not found" in result["error"]

    def test_delete_ambiguous_function_name(self, tmp_path):
        path = tmp_path / "mod.py"

        path.write_text(
            "class A:\n"
            "    def execute(self):\n"
            "        return 1\n\n"
            "class B:\n"
            "    def execute(self):\n"
            "        return 2\n"
        )

        result = execute(str(path), "execute")

        assert "error" in result
        assert "ambiguous" in result["error"].lower()
