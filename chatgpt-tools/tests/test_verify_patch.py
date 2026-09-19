from tools.verify_patch import execute


class TestVerifyPatch:
    def test_verify_valid_file(self):
        result = execute("tools/help.py")
        assert "Syntax: OK" in result
        assert "Verdict:" in result

    def test_verify_nonexistent(self):
        result = execute("nonexistent_file.py")
        assert "File not found" in result
