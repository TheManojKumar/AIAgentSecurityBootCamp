"""Week 6 smoke test — Ollama, Garak, DeepTeam, PyRIT, Phoenix."""
import os
import sys
import json
import importlib.util
import urllib.request

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434")
ORCH = os.environ.get("ORCHESTRATOR_MODEL", "qwen2.5:3b")
PHOENIX = os.environ.get("PHOENIX_COLLECTOR_ENDPOINT", "http://phoenix:6006")


def has(mod):
    return importlib.util.find_spec(mod) is not None


def main():
    try:
        with urllib.request.urlopen(f"{OLLAMA_HOST}/api/tags", timeout=10) as r:
            names = {m["name"] for m in json.loads(r.read()).get("models", [])}
        assert any(n.startswith(ORCH.split(":")[0]) for n in names)
        print(f"\u2705 Ollama reachable at {OLLAMA_HOST}")
    except Exception as e:
        print(f"\u274c Ollama/model check failed: {e}")
        sys.exit(1)

    for label, mod in (("Garak", "garak"), ("DeepTeam", "deepteam"), ("PyRIT", "pyrit")):
        if has(mod):
            print(f"\u2705 {label} installed")
        else:
            print(f"\u274c {label} not installed (module '{mod}')")
            sys.exit(1)

    try:
        urllib.request.urlopen(PHOENIX, timeout=5)
        print(f"\u2705 Phoenix up at {PHOENIX}")
    except Exception:
        print(f"\u26a0\ufe0f  Phoenix not reachable at {PHOENIX}")
    print("\u2705 ready for Week 6")


if __name__ == "__main__":
    main()
