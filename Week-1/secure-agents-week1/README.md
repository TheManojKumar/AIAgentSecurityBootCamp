# Week 1 — Foundations, Your First Agent, Your First Injection

**ASI focus:** ASI01 (Agent Goal Hijack), ASI02 (Tool Misuse)
**Lab image:** `secure-agents-week1`

> The one thing to leave with: the agent did *exactly what the text told it to*.
> Security lives in the architecture **around** the model — in layers — not in the
> model itself.

## Layout

```
secure-agents-week1/
├── docker-compose.yml            # agent container + Arize Phoenix (tracing)
├── Dockerfile                    # python:3.12-slim + pinned deps
├── requirements.txt              # langgraph, langchain-ollama, arize-phoenix, openinference
├── tracing.py                    # Phoenix auto-instrumentation helper
├── check_env.py                  # prep-doc smoke test
├── agent.py                      # buildable vulnerable baseline (Part A)
├── attacks/
│   ├── 01_direct_override.txt
│   └── 02_subtle_embed.txt
├── defenses-allowlist.py         # Layer 1 — least agency
├── defenses-input_separation.py  # Layer 2 — instruction/data separation
├── defenses-tool_validation.py   # Layer 3 — argument validation
├── defenses-guardrail.py         # Layer 4 — input guardrail
├── workspace/
│   ├── public/notes.txt          # safe file the agent MAY read
│   └── secrets/api_keys.txt      # contains only: FAKE-KEY-DO-NOT-USE
├── agent_hardened.py             # all four layers (instructor copy)
└── README.md
```

## Quick start

```bash
# 1. Smoke test (must print all green before the session)
$env:ORCHESTRATOR_MODEL = "qwen2.5:3b"
docker compose run --rm agent python check_env.py

# 2. Benign run
docker compose run --rm agent python agent.py "What's the weather in Seattle?"

# 3. Attack the vulnerable baseline
docker compose run --rm agent python agent.py (cat .\attacks\01_direct_override.txt)
docker compose run --rm agent python agent.py (cat .\attacks\02_subtle_embed.txt)

# 4. Open Phoenix to watch the span tree
#    http://localhost:6006
```

## Design choices that matter
- **Models stay in host Ollama** — image is small (~400MB) and tier-agnostic; one env var swaps models.
- **All "secrets" are obviously fake** (`FAKE-KEY-DO-NOT-USE`) — nothing real is ever at risk.
- **Pinned dependencies** — Week-6 behavior matches Week-1 behavior exactly.
- **`extra_hosts: host-gateway`** — the single line that makes the container reach host Ollama on Linux, Mac, and Windows uniformly.
- **`solutions/` ships only to instructors** — student distribution omits that folder.

## Build & publish (run on a networked machine)

```bash
docker build -t ghcr.io/<yourorg>/secure-agents-week1:latest .
docker push ghcr.io/<yourorg>/secure-agents-week1:latest
```
