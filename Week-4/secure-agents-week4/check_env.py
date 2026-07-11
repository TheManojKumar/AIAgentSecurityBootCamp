"""Week 4 smoke test — Ollama, Docker-in-the-loop, Phoenix."""
import os
import sys
import json
import shutil
import subprocess
import urllib.request

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434")
ORCH = os.environ.get("ORCHESTRATOR_MODEL", "qwen2.5:3b")
PHOENIX = os.environ.get("PHOENIX_COLLECTOR_ENDPOINT", "http://phoenix:6006")


def main():
    try:
        with urllib.request.urlopen(f"{OLLAMA_HOST}/api/tags", timeout=10) as r:
            names = {m["name"] for m in json.loads(r.read()).get("models", [])}
        assert any(n.startswith(ORCH.split(":")[0]) for n in names)
        print(f"\u2705 Ollama reachable at {OLLAMA_HOST}")
    except Exception as e:
        print(f"\u274c Ollama/model check failed: {e}")
        sys.exit(1)

    # Docker-in-the-loop: can the agent container reach a Docker daemon?
    if shutil.which("docker"):
        try:
            subprocess.run(["docker", "info"], capture_output=True, timeout=15, check=True)
            print("\u2705 Docker-in-the-loop available")
        except Exception:
            print("\u26a0\ufe0f  docker CLI present but daemon unreachable "
                  "(mount /var/run/docker.sock; Linux users need docker-group perms)")
    else:
        print("\u274c docker CLI not found in the agent image")
        sys.exit(1)

    try:
        urllib.request.urlopen(PHOENIX, timeout=5)
        print(f"\u2705 Phoenix up at {PHOENIX}")
    except Exception:
        print(f"\u26a0\ufe0f  Phoenix not reachable at {PHOENIX}")
    print("\u2705 ready for Week 4")


if __name__ == "__main__":
    main()
