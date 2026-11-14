"""text-lowercase — Unicode-aware lowercase transform.

External Orqen capability, replacing the compiled Rust
LowercaseTextCapability with the same behavior.
"""
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

MAX_BODY_BYTES = 1_048_576


def handle(text: str) -> str:
    return text.lower()


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        if length > MAX_BODY_BYTES:
            self.send_response(413)
            self.end_headers()
            return
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
            result = handle(str(payload.get("input", "")))
            body = json.dumps({"result": result}).encode()
        except Exception as error:  # noqa: BLE001
            body = json.dumps({"error": str(error)}).encode()
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "9321"))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
