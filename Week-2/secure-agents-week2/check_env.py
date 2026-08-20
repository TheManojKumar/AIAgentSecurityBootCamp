"""Week 2 smoke test — orchestrator + specialist models must both respond."""
import os
import sys
import json
import urllib.request

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434")
MODELS = [
    os.environ.get("ORCHESTRATOR_MODEL", "qwen2.5:3b"),
    os.environ.get("SPECIALIST_MODEL", "llama3.2:3b"),
]
PHOENIX = os.environ.get("PHOENIX_COLLECTOR_ENDPOINT", "http://phoenix:6006")


def _tags():
    with urllib.request.urlopen(f"{OLLAMA_HOST}/api/tags", timeout = 10) as r:
        return {m["name"] for m in json.loads(r.read()).get("models", [])}


def main():
    try:
        available = _tags()
        print(f"\u2705 Ollama reachable at {OLLAMA_HOST}")
    except Exception as e:
        print(f"\u274c Ollama NOT reachable at {OLLAMA_HOST}: {e}")
        sys.exit(1)

    ok = 0
    for model in MODELS:
        base = model.split(":")[0]
        if any(n.startswith(base) for n in available):
            ok += 1
        else:
            print(f"\u274c model '{model}' not found. Have: {sorted(available)}")
            sys.exit(1)
    print(f"\u2705 {ok} models respond")

    try:
        urllib.request.urlopen(PHOENIX, timeout = 5)
        print(f"\u2705 Phoenix up at {PHOENIX}")
    except Exception:
        print(f"\u26a0\ufe0f  Phoenix not reachable at {PHOENIX}")
    print("\u2705 ready for Week 2")


if __name__ == "__main__":
    main()
