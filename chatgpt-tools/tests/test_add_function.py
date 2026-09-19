from pathlib import Path
from tools.add_function import execute


class TestAddFunction:
    def test_add_to_end(self, tmp_path):
        path = tmp_path / "mod.py"
        path.write_text("def foo():\n    return 1\n")
        result = execute(str(path), "def bar():\n    return 2")
        assert "result" in result
        assert result.get("syntax_ok") == "true"
        new = path.read_text()
        assert "def bar()" in new

    def test_add_after_symbol(self, tmp_path):
        path = tmp_path / "mod.py"
        path.write_text("def foo():\n    return 1\n\ndef bar():\n    return 2\n")
        result = execute(str(path), "def middle():\n    return 0", after="foo")
        assert "result" in result
        new = path.read_text()
        lines = new.split("\n")
        # middle should be before bar
        foo_idx = next(i for i, l in enumerate(lines) if "def foo" in l)
        middle_idx = next(i for i, l in enumerate(lines) if "def middle" in l)
        bar_idx = next(i for i, l in enumerate(lines) if "def bar" in l)
        assert foo_idx < middle_idx < bar_idx

    def test_add_nonexistent_after(self, tmp_path):
        path = tmp_path / "mod.py"
        path.write_text("def foo(): pass\n")
        result = execute(str(path), "def bar(): pass", after="nonexistent")
        assert "error" in result
        assert "not found" in result["error"]

    def test_add_invalid_syntax(self, tmp_path):
        path = tmp_path / "mod.py"
        path.write_text("def foo(): pass\n")
        result = execute(str(path), "def bar(:")
        assert "error" in result

