from tools.read_file import execute


def test_read_existing():
    result = execute("README.md")
    assert "ChatGPT Agent Tools" in result["content"]
    assert "sha256" in result
    assert len(result["sha256"]) == 64


def test_read_non_existent():
    try:
        execute("does_not_exist_123")
        assert False, "Should have raised"
    except FileNotFoundError:
        pass
