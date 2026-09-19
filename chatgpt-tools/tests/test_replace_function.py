from pathlib import Path
from tools.replace_function import execute


class TestReplaceFunction:
    def test_replace_existing(self, tmp_path):
        path = tmp_path / "mod.py"
        path.write_text("def foo():\n    return 1\n\ndef bar():\n    return 2\n")
        result = execute(str(path), "foo", "def foo():\n    return 42")
        assert "result" in result
        assert result.get("syntax_ok") == "true"
        new = path.read_text()
        assert "return 42" in new
        assert "return 1" not in new

    def test_replace_nonexistent_function(self, tmp_path):
        path = tmp_path / "mod.py"
        path.write_text("def foo(): pass\n")
        result = execute(str(path), "nonexistent", "def x(): pass")
        assert "error" in result
        assert "not found" in result["error"]

    def test_replace_nonexistent_file(self, tmp_path):
        path = tmp_path / "nope.py"
        result = execute(str(path), "foo", "def foo(): pass")
        assert "error" in result
        assert "File not found" in result["error"]

    def test_replace_sha_mismatch(self, tmp_path):
        path = tmp_path / "mod.py"
        path.write_text("def foo(): pass\n")
        result = execute(str(path), "foo", "def foo(): return 1", expected_sha="badsha")
        assert "stale file state" in result.get("error", "")

    def test_replace_ambiguous_function_name(self, tmp_path):
        path = tmp_path / "mod.py"
        path.write_text(
            "class A:\n"
            "    def execute(self):\n"
            "        return 1\n\n"
            "class B:\n"
            "    def execute(self):\n"
            "        return 2\n"
        )

        result = execute(
            str(path),
            "execute",
            "def execute(self):\n    return 42",
        )

        assert "error" in result
        assert "ambiguous" in result["error"].lower()

    def test_replace_cr_line_endings(self, tmp_path):
        path = tmp_path / "mod.py"
        path.write_text("def foo():\n    return 1\n")
        content = "def foo():\r    x = 42\r    return x\r"
        result = execute(str(path), "foo", content)
        assert "result" in result
        new = path.read_text()
        assert "x = 42" in new
        assert "return x" in new
        assert "return 1" not in new

    def test_replace_crlf_line_endings(self, tmp_path):
        path = tmp_path / "mod.py"
        path.write_text("def foo():\n    return 1\n")
        content = "def foo():\r\n    x = 42\r\n    return x\r\n"
        result = execute(str(path), "foo", content)
        assert "result" in result
        new = path.read_text()
        assert "x = 42" in new
        assert "return x" in new

    def test_replace_with_vtab_string(self, tmp_path):
        path = tmp_path / "mod.py"
        path.write_text("def foo():\n    return 1\n")
        content = "def foo():\n    x = 'hello\vworld'\n    return x\n"
        result = execute(str(path), "foo", content)
        assert "result" in result
        new = path.read_text()
        assert "hello" in new and "world" in new
