from typing import List
from xml.sax.saxutils import quoteattr

from models.tool_result import ToolResult


def _escape_cdata(text: str) -> str:
    return text.replace("]]>", "]]]]><![CDATA[>")


def _safe_tag(key: str) -> str:
    """Sanitize a result-dict key for use as an XML element name.

    Result keys originate from tool output; an unsanitized key could break
    the response XML. Anything that is not alphanumeric/underscore/dot/dash
    becomes "_", and a leading digit or empty result gets an "k_" prefix.
    """
    safe = "".join(c if (c.isalnum() or c in "_.-") else "_" for c in str(key))
    if not safe or safe[0].isdigit() or safe in ("xml", "XML"):
        safe = f"k_{safe}"
    return safe


def result_to_xml(result: ToolResult) -> str:
    out = "<tool_result"

    if result.id:
        out += f' id={quoteattr(result.id)}'

    out += ">"

    out += "<success>" + str(result.success).lower() + "</success>"

    for key, value in result.data.items():
        tag = _safe_tag(key)
        out += f"<{tag}><![CDATA[{_escape_cdata(str(value))}]]></{tag}>"

    out += "</tool_result>"

    return out


def batch_to_xml(results: List[ToolResult]) -> str:
    out = "<tool_results>"

    for result in results:
        out += result_to_xml(result)

    out += "</tool_results>"

    return out


to_xml = result_to_xml
to_xml_batch = batch_to_xml
