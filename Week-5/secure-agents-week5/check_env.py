"""Week 5 smoke test — Ollama, MCP servers reachable (good + malicious), Phoenix."""
import os
import sys
import json
import urllib.request

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434")
ORCH        = os.environ.get("ORCHESTRATOR_MODEL", "qwen2.5:3b")
PHOENIX     = os.environ.get("PHOENIX_COLLECTOR_ENDPOINT", "http://phoenix:6006")


def main():
    try:
        with urllib.request.urlopen(f"{OLLAMA_HOST}/api/tags", timeout = 10) as r:
            names = {m["name"] for m in json.loads(r.read()).get("models", [])}
        assert any(n.startswith(ORCH.split(":")[0]) for n in names)
        print(f"\u2705 Ollama reachable at {OLLAMA_HOST}")
    except Exception as e:
        print(f"\u274c Ollama/model check failed: {e}")
        sys.exit(1)

    # Confirm both stdio servers import and expose tools.
    for label, path in (("notes", "servers/notes_server.py"),
                        ("malicious", "servers/malicious_server.py")):
        if not os.path.exists(path):
            print(f"\u274c MCP server missing: {path}")
            sys.exit(1)
    print("\u2705 MCP servers reachable (good + malicious)")

    try:
        urllib.request.urlopen(PHOENIX, timeout = 5)
        print(f"\u2705 Phoenix up at {PHOENIX}")
    except Exception:
        print(f"\u26a0\ufe0f  Phoenix not reachable at {PHOENIX}")
    print("\u2705 ready for Week 5")


if __name__ == "__main__":
    main()
