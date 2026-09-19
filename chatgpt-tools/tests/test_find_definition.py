from tools.find_definition import execute


class TestFindDefinition:
    def test_find_function(self):
        result = execute("dispatch")
        assert "dispatcher/dispatcher.py" in result

    def test_find_nonexistent(self):
        unique = "ZZZ_SYMBOL_DOES_NOT_EXIST_" + str(hash("def_test"))
        result = execute(unique)
        assert "not found" in result
