from tools.git_log import execute as git_log
from tools.git_show import execute as git_show
from tools.git_blame import execute as git_blame


class TestGitLog:
    def test_log_default(self):
        result = git_log("10")
        assert result["in_repository"] is True
        assert len(result["output"].split("\n")) > 0

    def test_log_custom_limit(self):
        result = git_log("3")
        assert result["in_repository"] is True
        lines = [l for l in result["output"].strip().split("\n") if l]
        assert len(lines) <= 3


class TestGitShow:
    def test_show_latest(self):
        result = git_show("HEAD")
        assert result["in_repository"] is True
        assert "commit" in result["output"]


class TestGitBlame:
    def test_blame_file(self):
        result = git_blame("README.md")
        assert result["in_repository"] is True
        assert len(result["output"]) > 0
