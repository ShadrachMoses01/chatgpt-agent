from tools.trace_call_graph import execute


class TestTraceCallGraph:
    def test_trace_dispatch(self):
        result = execute("dispatch")
        assert "dispatch" in result

    def test_trace_nonexistent(self):
        unique = "ZZZ_FUNC_DOES_NOT_EXIST_" + str(hash("trace_test"))
        result = execute(unique)
        assert "No call graph found" in result or "not found" in result
