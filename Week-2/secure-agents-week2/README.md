# Week 2 — Multi-Agent Systems & Trust Boundaries

**ASI focus:** ASI07 (Insecure Inter-Agent Communication), ASI08 (Cascading Failures)
**Lab image:** `secure-agents-week2`

> The one thing to leave with: individually safe agents can compose into an unsafe
> system. An orchestrator that trusts a subagent's output implicitly will execute
> actions it would never take on its own. Trust between agents is a boundary that
> must be *designed*, not assumed.

## Layout

```
secure-agents-week2/
├── docker-compose.yml     # agent + Phoenix; now sets SPECIALIST_MODEL too
├── Dockerfile
├── requirements.txt       # + pydantic
├── tracing.py
├── check_env.py
├── team.py                # supervisor + researcher + writer (vulnerable)
├── attacks/
│   └── poisoned_corpus_note.txt   # the hidden instruction appended to solar.txt
├── defenses/
│   ├── data_framing.py      # Layer 1
│   ├── validator_node.py    # Layer 2
│   ├── output_schema.py     # Layer 3
│   └── scoped_tools.py      # Layer 4
├── workspace/
│   ├── corpus/
│   │   ├── solar.txt       # legit content + appended hidden instruction
│   │   └── wind.txt        # clean control document
│   └── secrets/api_keys.txt  # FAKE-KEY-DO-NOT-USE
├── solutions/
│   └── team_hardened.py    # all four layers
└── README.md
```

## Quick start

```bash
ORCHESTRATOR_MODEL=qwen2.5:3b docker compose run --rm agent python check_env.py

# benign
docker compose run --rm agent python team.py "Summarize what the corpus says about solar power."

# the cascade fires: poisoned solar.txt hijacks the supervisor
# (watch the three-node span tree in Phoenix at http://localhost:6006)

# hardened
docker compose run --rm agent python solutions/team_hardened.py "Summarize what the corpus says about solar power."
```

## Notes
- **Compose delta from Week 1:** adds `SPECIALIST_MODEL=${SPECIALIST_MODEL:-llama3.2:3b}`.
  Everything else (Phoenix, host-gateway, volume) is identical.
- **Why a mock corpus instead of live web:** keeps the lab fully offline and the
  attack 100% reproducible on screen. The corpus file *is* the "indirect" channel —
  same threat model as a poisoned web page, without needing network access.
- **Demo reliability:** small models sometimes ignore the injected note by luck.
  Run the attack 2–3 times, or set `SPECIALIST_MODEL=llama3.2:1b` (more compliant)
  so the cascade reliably fires on screen.
