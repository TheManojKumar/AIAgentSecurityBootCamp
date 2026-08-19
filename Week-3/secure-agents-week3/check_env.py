"""Week 3 smoke test — Ollama, embeddings, Chroma, Phoenix."""
import os
import sys
import json
import urllib.request

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434")
ORCH        = os.environ.get("ORCHESTRATOR_MODEL", "qwen2.5:3b")
EMBED       = os.environ.get("EMBED_MODEL", "all-minilm")
PHOENIX     = os.environ.get("PHOENIX_COLLECTOR_ENDPOINT", "http://phoenix:6006")


def _tags():
    with urllib.request.urlopen(f"{OLLAMA_HOST}/api/tags", timeout=10) as r:
        return {m["name"] for m in json.loads(r.read()).get("models", [])}


def main():
    try:
        available = _tags()
        print(f"\u2705 Ollama reachable at {OLLAMA_HOST}")
    except Exception as e:
        print(f"\u274c Ollama NOT reachable: {e}")
        sys.exit(1)

    for model in (ORCH, EMBED):
        if not any(n.startswith(model.split(":")[0]) for n in available):
            print(f"\u274c model '{model}' not found. Have: {sorted(available)}")
            sys.exit(1)

    # confirm embeddings actually produce a vector
    try:
        payload = json.dumps({"model": EMBED, "prompt": "hello"}).encode()
        req = urllib.request.Request(f"{OLLAMA_HOST}/api/embeddings", data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            vec = json.loads(r.read()).get("embedding", [])
        assert len(vec) > 0
        print("\u2705 embeddings work")
    except Exception as e:
        print(f"\u274c embeddings failed: {e}")
        sys.exit(1)

    try:
        import chromadb  # noqa: F401
        print("\u2705 Chroma up")
    except Exception as e:
        print(f"\u274c Chroma import failed: {e}")
        sys.exit(1)

    try:
        urllib.request.urlopen(PHOENIX, timeout=5)
        print(f"\u2705 Phoenix up at {PHOENIX}")
    except Exception:
        print(f"\u26a0\ufe0f  Phoenix not reachable at {PHOENIX}")
    print("\u2705 ready for Week 3")


if __name__ == "__main__":
    main()
