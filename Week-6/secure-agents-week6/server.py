# server.py — HTTP endpoint exposing the hardened system to the red-team tools
#
# Minimal, dependency-free HTTP server (stdlib) so Garak/DeepTeam/PyRIT can POST
# a prompt and receive the system's response. POST / with {"prompt": "..."}.
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from secure_system import handle
from tracing import init_tracing

init_tracing("week6-server")


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):

        # Log this function call in Blue color
        print('\033[94m', "=================================================================")
        print('\033[94m', "Calling do_POST ...")
        print('\033[94m', "=================================================================")

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode() if length else "{}"
        try:
            prompt = json.loads(body).get("prompt", "")
        except Exception:
            prompt = body
        reply = handle(prompt)

        # Log the response to stdout in Cyan color (never written into the wire payload)
        print('\033[96m', reply)

        payload = json.dumps({"response": reply}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass  # quiet


if __name__ == "__main__":

    # Log this function call in Yellow color
    print('\033[33m', "=================================================================")
    print('\033[33m', "Running server on 0.0.0.0:8000 ...")
    print('\033[33m', "=================================================================")

    ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
