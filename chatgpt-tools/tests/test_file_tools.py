import pytest
from tools.read_file import execute as read_file
from tools.write_file import execute as write_file
from tools.create_file import execute as create_file
from tools.delete_file import execute as delete_file
from tools.patch_file import execute as patch_file
from tools.list_files import execute as list_files


class TestReadFile:
    def test_read_existing(self):
        result = read_file("README.md")
        assert "ChatGPT Agent Tools" in result["content"]
        assert "sha256" in result
        assert len(result["sha256"]) == 64

    def test_read_non_existent(self):
        with pytest.raises(FileNotFoundError):
            read_file("does_not_exist_123")


class TestWriteFile:
    def test_write(self, tmp_path):
        path = tmp_path / "test.txt"
        result = write_file(str(path), "hello")
        assert result["result"] == f"Wrote {path}"
        assert "syntax_ok" in result
        assert path.read_text() == "hello"


class TestCreateFile:
    def test_create_new(self, tmp_path):
        path = tmp_path / "new.txt"
        result = create_file(str(path), "new content")
        assert result["result"] == f"Wrote {path}"
        assert "syntax_ok" in result
        assert path.read_text() == "new content"

    def test_create_existing(self, tmp_path):
        path = tmp_path / "existing.txt"
        path.write_text("original")
        result = create_file(str(path), "new content")
        assert "already exists" in result["result"]
        assert path.read_text() == "original"


class TestDeleteFile:
    def test_delete(self, tmp_path):
        path = tmp_path / "to_delete.txt"
        path.write_text("delete me")
        result = delete_file(str(path))
        assert result == f"Deleted {path}"
        assert not path.exists()

    def test_delete_non_existent(self, tmp_path):
        path = tmp_path / "no_file.txt"
        result = delete_file(str(path))
        assert "File not found" in result


class TestPatchFile:
    def test_patch_success(self, tmp_path):
        path = tmp_path / "patch.txt"
        path.write_text("hello world")
        result = patch_file(str(path), "hello", "goodbye")
        assert result["result"] == f"Wrote {path}"
        assert "syntax_ok" in result
        assert path.read_text() == "goodbye world"

    def test_patch_not_found(self, tmp_path):
        path = tmp_path / "patch.txt"
        path.write_text("hello world")
        result = patch_file(str(path), "zzz", "aaa")
        assert "not found" in result["result"]
        assert "zzz" in result["result"]
        assert path.read_text() == "hello world"

    def test_patch_non_existent(self, tmp_path):
        path = tmp_path / "no_file.txt"
        result = patch_file(str(path), "x", "y")
        assert "File not found" in result["result"]

    def test_patch_only_first_occurrence(self, tmp_path):
        path = tmp_path / "patch.txt"
        path.write_text("a a a")
        patch_file(str(path), "a", "b")
        assert path.read_text() == "b a a"

    def test_patch_sha_mismatch(self, tmp_path):
        path = tmp_path / "patch.txt"
        path.write_text("original")
        result = patch_file(str(path), "x", "y", expected_sha="badsha")
        assert "stale file state" in result.get("error", result.get("result", ""))


class TestListFiles:
    def test_list_current_dir(self):
        result = list_files(".")
        assert "main.py" in result

    def test_list_non_existent(self):
        with pytest.raises(FileNotFoundError):
            list_files("does_not_exist_123")
