import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from bridge.xml_extractor import extract_xml, extract_all_xml


def test_bare_tool_call():
    text = """<tool_call> <tool>HELP</tool>
</tool_call>"""
    assert extract_xml(text) is not None


def test_in_code_fence():
    text = """Some analysis here.

```xml
<tool_call>
  <tool>READ_FILE</tool>
  <path>main.py</path>
</tool_call>
```

STOP."""
    xml = extract_xml(text)
    assert xml is not None
    assert "<tool>READ_FILE</tool>" in xml


def test_protocol_section():
    text = """Analysis:
Observed:
* nothing

Protocol:

<tool_call> <tool>LIST_FILES</tool> <path>.</path>
</tool_call>

STOP."""
    xml = extract_xml(text)
    assert xml is not None
    assert "<tool>LIST_FILES</tool>" in xml


def test_tool_batch():
    text = """```xml
<tool_batch>
<tool_call> <tool>READ_FILE</tool> <path>a.py</path>
</tool_call>
<tool_call> <tool>READ_FILE</tool> <path>b.py</path>
</tool_call>
</tool_batch>
```"""
    xml = extract_xml(text)
    assert xml is not None
    assert "<tool_batch>" in xml


def test_extract_all():
    text = """<tool_call> <tool>HELP</tool>
</tool_call>
Some text
<tool_call> <tool>LIST_FILES</tool> <path>.</path>
</tool_call>"""
    results = extract_all_xml(text)
    assert len(results) == 2


def test_invalid_xml_returns_none():
    text = "```\n<tool_call> <tool>UNKNOWN_TOOL\n```"
    assert extract_xml(text) is None


def test_code_fence_no_lang():
    text = """```
<tool_call>
  <tool>READ_FILE</tool>
  <path>test.py</path>
</tool_call>
```"""
    xml = extract_xml(text)
    assert xml is not None
    assert "<tool>READ_FILE</tool>" in xml


def test_preserves_indentation():
    text = """<tool_call>
  <tool>REPLACE_FUNCTION</tool>
  <path>mod.py</path>
  <symbol>foo</symbol>
  <content>def foo():
    return 42</content>
</tool_call>"""
    xml = extract_xml(text)
    assert xml is not None
    assert "    return 42" in xml, "Indentation inside content must be preserved!"


if __name__ == "__main__":
    test_bare_tool_call()
    test_in_code_fence()
    test_protocol_section()
    test_tool_batch()
    test_extract_all()
    test_invalid_xml_returns_none()
    test_code_fence_no_lang()
    test_preserves_indentation()
    print("All tests passed")
