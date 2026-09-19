#!/usr/bin/env python3
import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from runtime import execute

PORT = 9876

# Upper bound on /api/execute request bodies. Tool calls are small XML/JSON
# blobs; anything larger is rejected before parsing.
MAX_BODY_SIZE = 10 * 1024 * 1024  # 10 MB


class BridgeHandler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/health":
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        else:
            self._respond(404, {"error": "Not found"})

    def do_POST(self):
        if self.path != "/api/execute":
            self._respond(404, {"error": "Not found"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", 0))
        except (ValueError, TypeError):
            self._respond(400, {"error": "Invalid Content-Length"})
            return

        if content_length < 0 or content_length > MAX_BODY_SIZE:
            self._respond(413, {"error": "Request body too large"})
            return

        try:
            body = self.rfile.read(content_length)
            data = json.loads(body)
            if not isinstance(data, dict):
                raise ValueError("Request body must be a JSON object")
        except (ValueError, json.JSONDecodeError) as e:
            self._respond(400, {"error": f"Invalid JSON body: {e}"})
            return

        text = data.get("text", "")
        source = data.get("source", "chatgpt")

        if not isinstance(text, str) or not text.strip():
            self._respond(400, {"error": "Empty text"})
            return

        try:
            result = execute(text, source)
        except Exception as e:
            self._respond(500, {"error": str(e)})
            return
        self._respond(200, result)

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _respond(self, status, payload):
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        try:
            self.wfile.write(json.dumps(payload).encode())
        except (BrokenPipeError, ConnectionResetError):
            pass

    def log_message(self, format, *args):
        pass


def main():
    server = HTTPServer(("127.0.0.1", PORT), BridgeHandler)
    from runtime import get_runtime
    get_runtime().execute("", "__boot__")
    print(f"\n  \033[1mBridge server\033[0m  http://127.0.0.1:{PORT}")
    print(f"  \033[90mEndpoints:\033[0m  POST /api/execute  |  GET /api/health\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Shutting down")
        server.server_close()


if __name__ == "__main__":
    main()
