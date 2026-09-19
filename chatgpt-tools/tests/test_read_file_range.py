from tools.read_file import execute as read_file


class TestReadFileRange:
    def test_read_without_range(self):
        result = read_file("tools/read_file.py")
        assert "content" in result
        assert "sha256" in result
        assert "total_lines" in result

    def test_read_with_start(self):
        result = read_file("tools/read_file.py", start=1, end=3)
        lines = result["content"].split("\n")
        assert len(lines) <= 3

    def test_read_with_single_line(self):
        result = read_file("tools/read_file.py", start=2, end=2)
        assert len(result["content"].split("\n")) == 1

    def test_resolved_path(self):
        result = read_file("tools/read_file.py")
        assert result["path"].endswith("tools/read_file.py")
