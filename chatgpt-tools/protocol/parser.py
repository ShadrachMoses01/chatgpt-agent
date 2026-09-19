import xml.etree.ElementTree as ET

from models.tool_call import ToolCall


def parse_tool_call(xml_text: str) -> ToolCall:
    root = ET.fromstring(xml_text)
    return parse_tool_call_from_root(root)


def parse_tool_call_from_root(root: ET.Element) -> ToolCall:
    tool = root.find("tool")

    if tool is None or not (tool.text or "").strip():
        raise ValueError("Missing <tool> tag")

    call_id = root.get("id", "")

    args = {}

    for child in root:
        if child.tag == "tool":
            continue
        args[child.tag] = child.text or ""

    return ToolCall(
        tool=tool.text.strip(),
        args=args,
        id=call_id,
    )


def parse_tool_batch(xml_text: str):
    root = ET.fromstring(xml_text)
    return parse_tool_batch_from_root(root)


def parse_tool_batch_from_root(root: ET.Element):
    if root.tag != "tool_batch":
        raise ValueError("Expected <tool_batch>")

    calls = []

    for node in root.findall("tool_call"):
        tool = node.find("tool")

        if tool is None or not (tool.text or "").strip():
            continue

        call_id = node.get("id", "")
        args = {}

        for child in node:
            if child.tag == "tool":
                continue
            args[child.tag] = child.text or ""

        calls.append(
            ToolCall(
                tool=tool.text.strip(),
                args=args,
                id=call_id,
            )
        )

    return calls
