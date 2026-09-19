import traceback
import xml.etree.ElementTree as ET
from pathlib import Path

from protocol.parser import parse_tool_call_from_root
from protocol.response import to_xml
from dispatcher.dispatcher import dispatch

_BASE_DIR = Path(__file__).resolve().parent

CALL_LOG = str(_BASE_DIR / "logs" / "tool_calls.log")
RESULT_LOG = str(_BASE_DIR / "logs" / "tool_results.log")
ERROR_LOG = str(_BASE_DIR / "logs" / "errors.log")

REQUEST_FILE = str(_BASE_DIR / "request.xml")
RESPONSE_FILE = str(_BASE_DIR / "response.xml")


def log(path: str, content: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write("\n")
        f.write("=" * 80)
        f.write("\n")
        f.write(content)
        f.write("\n")


def process(xml_input: str) -> str:
    log(CALL_LOG, xml_input)

    root = ET.fromstring(xml_input)
    tool_call = parse_tool_call_from_root(root)
    result = dispatch(tool_call)
    xml_output = to_xml(result)

    log(RESULT_LOG, xml_output)

    return xml_output


def main():
    request_path = Path(REQUEST_FILE)

    if not request_path.exists():
        print("request.xml not found")
        return

    xml_input = request_path.read_text()

    if not xml_input.strip():
        print("request.xml is empty")
        return

    try:
        xml_output = process(xml_input)

        Path(RESPONSE_FILE).write_text(xml_output)

        print("response.xml written")

    except Exception as e:
        tb = traceback.format_exc()
        log(ERROR_LOG, f"{type(e).__name__}: {e}\n{tb}")

        Path(RESPONSE_FILE).write_text(
            f"<error>"
            f"<type>{type(e).__name__}</type>"
            f"<message>{e}</message>"
            f"<traceback>{tb}</traceback>"
            f"</error>"
        )

        print(f"ERROR: {e}")


if __name__ == "__main__":
    main()
