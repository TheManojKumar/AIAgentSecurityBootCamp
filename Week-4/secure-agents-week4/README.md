# Week 4 — Tool Abuse & Code Execution (RCE)

**ASI focus:** ASI02 (Tool Misuse), ASI05 (Unexpected Code Execution / RCE)
**Lab image:** `secure-agents-week4`

> The one thing to leave with: the most dangerous tool an agent can have is one
> that runs code. Prompt injection plus a code-execution tool with unsafe
> defaults equals an unauthenticated shell on the host. This is a documented
> 2026 CVE class (CrewAI, VU#221883).

## Safety note
This week demonstrates **real RCE against an intentionally vulnerable agent**,
contained inside Docker. The exploit only ever touches a throwaway container with
fake data. Run it **only** inside the provided lab.

## Layout

```
secure-agents-week4/
├── docker-compose.yml           # agent + Phoenix; mounts docker.sock for sandbox-spawning
├── Dockerfile                   # includes docker CLI for Docker-out-of-Docker
├── requirements.txt
├── tracing.py
├── check_env.py
├── code_agent.py                # agent with naive in-process run_python (vulnerable)
├── attacks/
│   ├── rce_direct.txt           # direct injection → os.popen shell-out
│   └── rce_indirect.txt         # injection delivered via a 'data file'
├── defenses-docker_sandbox.py   # Layer 1 — ephemeral network-less container exec
├── defenses-fail_closed.py      # Layer 2 — no silent fallback (the CrewAI fix)
├── defenses-hitl.py             # Layer 3 — LangGraph interrupt approval gate
├── defenses-capability_scope.py # Layer 4 — AST-allow-listed safe evaluator
├── casestudy/
│   └── crewai_cve_chain.md      # VU#221883 walkthrough mapped to the lab
├── workspace/
│   ├── secrets/api_keys.txt     # FAKE-KEY-DO-NOT-USE
│   └── data/sales.csv           # benign data; indirect-injection variant hides here
├── sandbox_io/                  # scratch dir for sandboxed scripts (mounted)
├── code_agent_hardened.py       # all four controls — INSTRUCTOR ONLY, omit from student distribution
└── README.md
```

## Quick start

```bash
$env:ORCHESTRATOR_MODEL = "qwen2.5:3b"
docker compose run --rm agent python check_env.py

# benign
docker compose run --rm agent python code_agent.py "What's the standard deviation of [4, 8, 15, 16, 23, 42]?"

# ATTACK: prompt injection -> RCE (contained to the throwaway agent container)
docker compose run --rm agent python code_agent.py "$(cat attacks/rce_direct.txt)"

# DEFEND: the AST-scoped evaluator refuses os.popen outright
docker compose run --rm agent python defenses-capability_scope.py
```

## Notes
- **Docker-out-of-Docker:** the agent container mounts the host's
  `/var/run/docker.sock` so it can spawn the *sibling* sandbox container.
  On Docker Desktop this works out of the box; on Linux the host user needs
  Docker-group permissions.
- **The host is never targeted** — the demonstrated shell-out runs in the agent
  container (vulnerable demo) or the disposable sandbox (defended demo), both
  throwaway, both fake-data-only.
- **Demo reliability:** `llama3.2:1b` as the agent makes the RCE fire
  consistently. Bigger models sometimes refuse the crude payload — use that as a
  teachable contrast.
