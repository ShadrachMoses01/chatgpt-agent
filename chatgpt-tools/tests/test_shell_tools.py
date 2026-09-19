import pytest
from tools.run_command import execute as run_command
from tools.git_status import execute as git_status
from tools.git_diff import execute as git_diff
from tools.search import execute as search
from tools.help import execute as help_tool


class TestRunCommand:
    def test_allowed_command(self):
        result = run_command("python3 --version")
        assert result["success"] is True
        assert "Python" in result["stdout"]

    def test_quoted_args(self):
        result = run_command("python3 -c \"print('hello world')\"")
        assert result["success"] is True
        assert "hello world" in result["stdout"]

    def test_disallowed_command(self):
        result = run_command("rm -rf /")
        assert result["success"] is False
        assert "not allowed" in result["reason"]

    def test_empty_command(self):
        result = run_command("")
        assert result["success"] is False
        assert result["error"] == "Empty command"

    def test_timeout_kills(self):
        result = run_command("python3 -c \"import time; time.sleep(10)\"", timeout=1)
        assert result["success"] is True
        assert result["timed_out"] is True
        assert "timeout" in result["message"].lower()


class TestGitStatus:
    def test_status(self):
        result = git_status()
        assert "in_repository" in result


class TestGitDiff:
    def test_diff(self):
        result = git_diff()
        assert "in_repository" in result


class TestSearch:
    def test_search(self):
        result = search("def execute")
        assert "execute" in result

    def test_search_no_matches(self):
        unique = "NONEXISTENT_" + str(hash("unique_salt_42"))
        result = search(unique)
        assert result == ""


class TestHelp:
    def test_help(self):
        result = help_tool()
        assert "READ_FILE" in result
        assert "WRITE_FILE" in result
        assert "HELP" in result
        assert "Examples" in result
