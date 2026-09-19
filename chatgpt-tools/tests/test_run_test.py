from tools.run_test import execute


class TestRunTest:
    def test_run_specific_file(self):
        result = execute("tests/test_help.py")
        assert "PASSED" in result or "passed" in result or "test session" in result

    def test_run_specific_test(self):
        result = execute("tests/test_response.py::TestToXml::test_success")
        assert "PASSED" in result or "passed" in result
