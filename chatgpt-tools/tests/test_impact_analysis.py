from tools.impact_analysis import execute


class TestImpactAnalysis:
    def test_impact_of_dispatch(self):
        result = execute("dispatch")
        assert "Symbol: dispatch" in result
        assert "Total references:" in result

    def test_impact_nonexistent(self):
        unique = "ZZZ_SYMBOL_DOES_NOT_EXIST_" + str(hash("impact_test"))
        result = execute(unique)
        assert "Symbol:" in result
