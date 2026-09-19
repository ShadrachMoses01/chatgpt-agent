import os
import sys
import uuid
import time
import datetime
import xml.etree.ElementTree as ET

TOOLS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "chatgpt-tools")
sys.path.insert(0, TOOLS_DIR)

from bridge.xml_extractor import extract_xml
from bridge.clipboard import write as write_clipboard
from protocol.parser import parse_tool_call_from_root, parse_tool_batch_from_root
from protocol.response import to_xml, to_xml_batch
from dispatcher.dispatcher import dispatch


C = {
    "dim": "\033[90m",
    "cyan": "\033[96m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "red": "\033[91m",
    "bold": "\033[1m",
    "reset": "\033[0m",
}


def _ts():
    return datetime.datetime.now().strftime("%H:%M:%S")


def _pline(req_id, tag, color, msg, detail=""):
    c = C.get(color, "")
    ts = f"{C['dim']}[{_ts()}]{C['reset']}"
    rid = f"{C['dim']}{req_id}{C['reset']}" if req_id else ""
    tag_fmt = f"  {c}{tag:>12}{C['reset']}" if tag else ""
    det = f"  {C['dim']}{detail}{C['reset']}" if detail else ""
    print(f"{ts} {rid}{tag_fmt}  {c}{msg}{C['reset']}{det}")


def _rule():
    print(f"  {C['dim']}{'─' * 60}{C['reset']}")


class Logger:
    def __init__(self, req_id):
        self.req_id = req_id

    def received(self, source, nchars):
        _pline(self.req_id, "RECEIVED", "cyan", f"source={source}  chars={nchars}")

    def extracted(self, success=True):
        if success:
            _pline(self.req_id, "EXTRACT", "green", "Valid XML found")
        else:
            _pline(self.req_id, "EXTRACT", "yellow", "No XML found")

    def dispatch(self, tool, i=None, total=None):
        idx = f"[{i}/{total}] " if i else ""
        _pline(self.req_id, "DISPATCH", "cyan", f"{idx}{tool}")

    def result(self, tool, success, elapsed=None):
        status = "SUCCESS" if success else "FAILED"
        color = "green" if success else "red"
        detail = f" ({elapsed:.2f}s)" if elapsed else ""
        _pline(self.req_id, status, color, tool, detail)

    def clipboard(self):
        _pline(self.req_id, "CLIPBOARD", "green", "Written")

    def response(self, status_code, elapsed):
        _pline(self.req_id, "RESPONSE", "bold", f"{status_code}", f"({elapsed:.2f}s)")

    def error(self, msg):
        _pline(self.req_id, "ERROR", "red", msg)

    def info(self, msg):
        _pline(self.req_id, "INFO", "dim", msg)


class Runtime:
    def execute(self, text, source="unknown"):
        start = time.time()
        req_id = uuid.uuid4().hex[:12]
        log = Logger(req_id)

        _rule()
        log.received(source, len(text))

        xml = extract_xml(text)
        if not xml:
            log.extracted(success=False)
            elapsed = time.time() - start
            log.response(200, elapsed)
            _rule()
            return self._response(req_id, source, False, [], error="No valid XML found in message")

        log.extracted(success=True)

        try:
            root = ET.fromstring(xml)
            call_id = root.get("id", "")

            if call_id:
                req_id = call_id
                log = Logger(req_id)

            if root.tag == "tool_batch":
                calls = parse_tool_batch_from_root(root)
                log.info(f"Batch of {len(calls)} tool calls")
                tool_results = []
                for i, call in enumerate(calls, 1):
                    t0 = time.time()
                    log.dispatch(call.tool, i, len(calls))
                    r = dispatch(call)
                    log.result(call.tool, r.success, time.time() - t0)
                    tool_results.append(r)

                xml_output = to_xml_batch(tool_results)
                write_clipboard(xml_output)
                log.clipboard()
                results = [{"tool": call.tool, "success": r.success} for call, r in zip(calls, tool_results)]

            else:
                tool_call = parse_tool_call_from_root(root)
                t0 = time.time()
                log.dispatch(tool_call.tool)
                tool_result = dispatch(tool_call)
                log.result(tool_call.tool, tool_result.success, time.time() - t0)

                xml_output = to_xml(tool_result)
                write_clipboard(xml_output)
                log.clipboard()

                results = [{"tool": tool_call.tool, "success": tool_result.success}]

            overall = all(r["success"] for r in results)
            elapsed = time.time() - start
            log.response(200, elapsed)
            _rule()
            return self._response(req_id, source, overall, results)

        except Exception as e:
            elapsed = time.time() - start
            log.error(str(e))
            log.response(500, elapsed)
            _rule()
            return self._response(req_id, source, False, [], error=str(e))

    @staticmethod
    def _response(req_id, source, success, results, error=None):
        return {
            "request_id": req_id,
            "source": source,
            "success": success,
            "results": results,
            "error": error,
        }


_runtime = None


def get_runtime():
    global _runtime
    if _runtime is None:
        _runtime = Runtime()
    return _runtime


def execute(text, source="unknown"):
    return get_runtime().execute(text, source)
