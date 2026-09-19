from tools.ast_utils import (
    classify_symbol,
    _is_excluded,
    split_by_domain,
    find_occurrences,
    DEFAULT_EXCLUDES,
)


class TestClassifySymbol:
    def test_builtin(self):
        assert classify_symbol("str") == "builtin"
        assert classify_symbol("dict") == "builtin"
        assert classify_symbol("len") == "builtin"
        assert classify_symbol("ValueError") == "builtin"

    def test_stdlib(self):
        assert classify_symbol("os") == "stdlib"
        assert classify_symbol("sys") == "stdlib"
        assert classify_symbol("json") == "stdlib"
        assert classify_symbol("ast") == "stdlib"

    def test_project(self):
        assert classify_symbol("dispatch") == "project"
        assert classify_symbol("ToolCall") == "project"
        assert classify_symbol("nonexistent_12345") == "project"


class TestIsExcluded:
    def test_logs_excluded(self):
        assert _is_excluded("logs/tool_calls.log", DEFAULT_EXCLUDES)

    def test_git_excluded(self):
        assert _is_excluded(".git/config", DEFAULT_EXCLUDES)

    def test_source_not_excluded(self):
        assert not _is_excluded("tools/registry.py", DEFAULT_EXCLUDES)
        assert not _is_excluded("main.py", DEFAULT_EXCLUDES)
        assert not _is_excluded("tests/test_parser.py", DEFAULT_EXCLUDES)


class TestSplitByDomain:
    def test_split(self):
        occs = [
            ("tools/registry.py", 1, "def dispatch():"),
            ("tests/test_dispatcher.py", 5, "dispatch(x)"),
            ("logs/tool_calls.log", 10, "dispatch called"),
        ]
        code, tests, other = split_by_domain(occs)
        assert len(code) == 1
        assert len(tests) == 1
        assert len(other) == 1

    def test_empty(self):
        code, tests, other = split_by_domain([])
        assert code == []
        assert tests == []
        assert other == []


class TestFindOccurrencesExcludes:
    def test_logs_not_included(self):
        occs = find_occurrences("dispatch")
        for fp, _, _ in occs:
            assert not fp.startswith("logs/"), f"logs should be excluded: {fp}"
