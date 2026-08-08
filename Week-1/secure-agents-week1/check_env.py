"""Week 1 smoke test — the gate that must pass before the live session.

Checks:
  - host Ollama is reachable
  - the selected ORCHESTRATOR_MODEL responds
  - Phoenix tracing endpoint is up
"""
import os
import sys
import urllib.request
import urllib.error
import json

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434")
MODEL       = os.environ.get("ORCHESTRATOR_MODEL", "qwen2.5:3b")
PHOENIX     = os.environ.get("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006")


def _get(url, timeout=10):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return r.status, r.read()


def check_ollama():
    try:
        status, body = _get(f"{OLLAMA_HOST}/api/tags")
        tags = json.loads(body)
        names = {m["name"] for m in tags.get("models", [])}
        print(f"\u2705 Ollama reachable at {OLLAMA_HOST}")
        return names
    except Exception as e:
        print(f"\u274c Ollama NOT reachable at {OLLAMA_HOST}: {e}")
        print("   Mac/Win: use host.docker.internal. Linux: extra_hosts host-gateway "
              "or --network=host + OLLAMA_HOST=http://localhost:11434")
        sys.exit(1)


def check_model(available_models):
    # Ollama tag names often include ':latest'; match loosely on the base name.
    base = MODEL.split(":")[0]
    if not any(name.startswith(base) for name in available_models):
        print(f"\u274c model '{MODEL}' not found. `ollama list` shows: {sorted(available_models)}")
        sys.exit(1)
    try:
        payload = json.dumps({"model": MODEL, "prompt": "say ready", "stream": False}).encode()
        req = urllib.request.Request(f"{OLLAMA_HOST}/api/generate", data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            json.loads(r.read())
        print(f"\u2705 model '{MODEL}' responded")
    except Exception as e:
        print(f"\u274c model '{MODEL}' did not respond: {e}")
        sys.exit(1)


def check_phoenix():
    try:
        _get(PHOENIX, timeout=5)
        print(f"\u2705 Phoenix tracing up at {PHOENIX}")
    except Exception:
        # Non-fatal: tracing is a teaching aid, not a hard dependency.
        print(f"\u26a0\ufe0f  Phoenix not reachable at {PHOENIX} (traces will be unavailable)")


if __name__ == "__main__":
    models = check_ollama()
    check_model(models)
    check_phoenix()
    print("\u2705 ready for Week 1")
