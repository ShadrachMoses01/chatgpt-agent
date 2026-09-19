from tools.project_map import execute


class TestProjectMap:
    def test_map_contains_key_elements(self):
        result = execute()
        assert "main.py" in result
        assert "dispatcher" in result
        assert "tools" in result
        assert "tests" in result
