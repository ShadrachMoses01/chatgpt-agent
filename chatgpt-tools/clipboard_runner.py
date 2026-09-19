import os
import traceback
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

from protocol.parser import (
    parse_tool_call_from_root,
    parse_tool_batch_from_root,
)

from protocol.response import (
    to_xml,
    to_xml_batch,
)

from dispatcher.dispatcher import dispatch

_BASE_DIR = Path(__file__).resolve().parent

CALL_LOG = str(_BASE_DIR / "logs" / "tool_calls.log")
RESULT_LOG = str(_BASE_DIR / "logs" / "tool_results.log")
ERROR_LOG = str(_BASE_DIR / "logs" / "errors.log")

MAX_XML_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_LOG_SIZE = 5 * 1024 * 1024   # 5 MB per log file


def read_clipboard() -> str:
    return subprocess.check_output(
        ["pbpaste"],
        text=True,
        timeout=5,
    )


def write_clipboard(text: str):
    subprocess.run(
        ["pbcopy"],
        input=text,
        text=True,
        check=True,
        timeout=5,
    )


def _rotate_log(path: str):
    """Truncate log if it exceeds MAX_LOG_SIZE."""
    try:
        size = os.path.getsize(path)
        if size > MAX_LOG_SIZE:
            with open(path, "w") as f:
                f.write(f"<truncated at {size} bytes>\n")
    except FileNotFoundError:
        pass


def log(path: str, content: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    _rotate_log(path)
    with open(path, "a") as f:
        f.write("\n")
        f.write("=" * 80)
        f.write("\n")
        f.write(content)
        f.write("\n")


def _build_error_xml(exc: Exception) -> str:
    tb = traceback.format_exc()
    exc_type = type(exc).__name__
    return f"""<tool_result>
  <success>false</success>
  <error_type>{exc_type}</error_type>
  <error_message>{exc}</error_message>
  <traceback><![CDATA[{tb}]]></traceback>
</tool_result>"""


def main():
    try:
        xml_input = read_clipboard()

        if not xml_input.strip():
            print("Clipboard is empty")
            return

        if len(xml_input) > MAX_XML_SIZE:
            msg = f"Clipboard content exceeds {MAX_XML_SIZE // (1024*1024)} MB"
            print(msg)
            write_clipboard(_build_error_xml(ValueError(msg)))
            return

        # Log request BEFORE execution so forensics survive a crash
        log(CALL_LOG, xml_input)

        root = ET.fromstring(xml_input)

        if root.tag == "tool_batch":
            # Batch execution is sequential — each tool call sees changes
            # from prior calls in the same batch.
            calls = parse_tool_batch_from_root(root)
            results = [dispatch(call) for call in calls]
            xml_output = to_xml_batch(results)
        else:
            tool_call = parse_tool_call_from_root(root)
            result = dispatch(tool_call)
            xml_output = to_xml(result)

        log(RESULT_LOG, xml_output)
        write_clipboard(xml_output)

        print("Tool executed")
        print("Result copied to clipboard")

    except Exception as e:
        tb = traceback.format_exc()
        log(ERROR_LOG, f"{type(e).__name__}: {e}\n{tb}")

        error_xml = _build_error_xml(e)
        write_clipboard(error_xml)

        print("Tool failed")
        print("Error copied to clipboard")


if __name__ == "__main__":
    main()
