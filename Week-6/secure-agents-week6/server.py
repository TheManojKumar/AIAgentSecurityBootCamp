# server.py — HTTP endpoint exposing the hardened system to the red-team tools
#
# Minimal, dependency-free HTTP server (stdlib) so Garak/DeepTeam/PyRIT can POST
# a prompt and receive the system's response. POST / with {"prompt": "..."}.
# Add {"session": "<any id>"} to keep a conversation going across requests —
# the system then remembers earlier turns under that id. Leave it out and every
# request is its own single-shot conversation (what garak and DeepTeam send).
import importlib
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from tracing import init_tracing

init_tracing("week6-server")

# Which system stands behind :8000. The lab starts with the bare cumulative
# system; once the Week-6 layers are written, point this at secure_system_final
# to re-run the same attacks against the hardened one for the security delta.
SYSTEM_MODULE = os.environ.get("SYSTEM_MODULE", "secure_system")
handle        = importlib.import_module(SYSTEM_MODULE).handle

# What the target answers when it could not run the request at all. A red-team
# target that drops the connection takes the whole scan down with it: garak sees
# RemoteDisconnected, raises, and every probe still queued is lost. Answering is
# always better than dying — the run continues and this string shows up in the
# report, where it reads as "no answer", not as a leak.
ERROR_RESPONSE = "[error] the system could not process this request."


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):

        # Log this function call in Blue color
        print('\033[94m', "=================================================================")
        print('\033[94m', "Calling do_POST ...")
        print('\033[94m', "=================================================================")

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode() if length else "{}"
        try:
            request = json.loads(body)
            prompt  = request.get("prompt", "")
            session = str(request.get("session", ""))
        except Exception:
            prompt  = body
            session = ""

        try:
            reply = handle(prompt, session)
        except Exception as e:
            # Log the failure in Red color — loudly, because a run full of these
            # is a broken target, not a hardened one.
            print('\033[91m', f"handle() failed on a {len(prompt)}-character prompt: {e}")
            reply = ERROR_RESPONSE

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
    print('\033[33m', f"Running server on 0.0.0.0:8000 (serving {SYSTEM_MODULE}) ...")
    print('\033[33m', "=================================================================")

    ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
