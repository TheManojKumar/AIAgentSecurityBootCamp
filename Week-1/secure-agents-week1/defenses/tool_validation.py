# defenses/tool_validation.py — Layer 3: argument validation on the tool itself
#
# Never trust the model to call a tool safely, even an allowed one. The tool
# enforces its own invariants: read_file is restricted to a public root and
# refuses path traversal. Defense in depth — this holds even if Layers 1 and 2
# are bypassed.
import os
from langchain_core.tools import tool

SAFE_ROOT = "/workspace/public"


@tool
def read_file(path: str) -> str:
    """Read a file, restricted to the public workspace."""
    requested = os.path.realpath(path)
    if not requested.startswith(SAFE_ROOT + os.sep):
        return "DENIED: path outside the permitted directory."
    with open(requested) as f:
        return f.read()


if __name__ == "__main__":
    # Quick self-test: the secrets path and traversal are both refused.
    print(read_file.invoke({"path": "/workspace/public/notes.txt"}))
    print(read_file.invoke({"path": "/workspace/secrets/api_keys.txt"}))
    print(read_file.invoke({"path": "/workspace/public/../secrets/api_keys.txt"}))
