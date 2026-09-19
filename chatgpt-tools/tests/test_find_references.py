from tools.find_references import execute


class TestFindReferences:
    def test_find_existing_symbol(self):
        result = execute("dispatch")
        assert "dispatcher" in result
        assert "definition" in result or "usage" in result or "import" in result

    def test_find_nonexistent_symbol(self):
        unique = "ZZZ_SYMBOL_DOES_NOT_EXIST_" + str(hash("ref_test"))
        result = execute(unique)
        assert "No references found" in result
