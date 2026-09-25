# Week 6 — Automated Red-Teaming, Hardening & the Red-Team Report

**ASI focus:** ASI09 (Human-in-the-Loop / Trust Exploitation), ASI10 (Rogue Agents & Role Drift), plus a full ASI01–ASI10 sweep
**Lab image:** `secure-agents-week6`

> The one thing to leave with: manual probing finds *some* holes; automated
> red-team tools find the ones you'd never think to try. Stand your cumulative
> system up behind an HTTP endpoint, point garak / DeepTeam / PyRIT at it, read
> the findings, and close each gap with one more layer. Then write the report —
> the report is the deliverable that makes the work legible to everyone else.

## Layout

```
secure-agents-week6/
├── docker-compose.yml            # agent (port 8000) + Phoenix; mounts docker.sock
├── Dockerfile                    # heavy image: docker CLI + garak/deepteam/pyrit
├── requirements.txt              # + garak, deepteam, pyrit (cumulative W1–W5 deps)
├── tracing.py
├── check_env.py
├── secure_system.py              # cumulative W1–W5 hardened door; handle(text) entrypoint
│                                 #   holds POLICY_DOCUMENT, the one doc it answers from
├── server.py                     # stdlib HTTP server: POST / {"prompt": "..."}
├── redteam/
│   ├── rest_config.json          # garak REST generator pointed at the local endpoint
│   ├── run_garak.sh              # encoding, promptinject, dan, leakage probes
│   │                             #   $PROBES overrides the list; HijackLongPrompt is off
│   ├── run_deepteam.py           # DeepTeam scan; attacker + judge models are local
│   └── run_pyrit.py              # PyRIT multi-turn escalation orchestrator
├── attacks/
│   ├── asi09_trust_exploit.txt   # persuasive framing to defeat the HITL reviewer
│   └── asi10_rogue_drift.py      # induces role-drift / persisted directive
├── defenses-normalize.py         # Layer 1 — decode encoded payloads before screening
├── defenses-turn_monitor.py      # Layer 2 — conversation-level escalation detection
├── defenses-neutral_review.py    # Layer 3 — strip persuasive framing before HITL (ASI09)
├── defenses-behavior_monitor.py  # Layer 4 — role-drift / rogue-tool kill-switch (ASI10)
├── report/
│   ├── report_template.md        # the blank red-team report students fill in
│   └── example_filled_report.md  # a worked example for reference
├── secure_system_final.py        # all four Week-6 layers wired in (instructor copy)
└── README.md
```

## Quick start

```bash
$env:ORCHESTRATOR_MODEL = "qwen2.5:3b"
docker compose run --rm agent python check_env.py

# 1. Stand the cumulative system up behind HTTP
docker compose up -d
#    (server.py serves secure_system.handle over POST / on :8000)
docker compose run --rm agent curl -s -X POST http://agent:8000/ \
  -H "Content-Type: application/json" -d '{"prompt":"Summarize the Q3 refund policy."}'

# 2. Run the automated red-team sweep against it
docker compose exec agent bash redteam/run_garak.sh
docker compose exec agent python redteam/run_deepteam.py
docker compose exec agent python redteam/run_pyrit.py

# 3. Read the findings, then close each gap by adding one Week-6 layer.
#    The fully-hardened target that survives the sweep:
docker compose exec agent python secure_system_final.py "Summarize the refund policy."

# 4. Write it up — fill report/report_template.md
#    (example_filled_report.md shows the target quality)
```

## How the layers map to the findings
| Tool finding | Gap | Layer added |
|---|---|---|
| garak encoding probe smuggles base64/hex/rot13 past the keyword screen | screen sees ciphertext, not intent | `defenses-normalize.py` — decode first, then screen |
| PyRIT multi-turn escalation gets further than any single prompt | no cross-turn state | `defenses-turn_monitor.py` — track escalation / slow-boil |
| Agent talks the HITL reviewer into approving (ASI09) | reviewer sees narration, not facts | `defenses-neutral_review.py` — show raw action only |
| Agent drifts role / persists a hidden directive (ASI10) | no behavioral baseline | `defenses-behavior_monitor.py` — kill-switch on drift |

## Notes
- **Why an HTTP endpoint:** garak, DeepTeam, and PyRIT are black-box tools — they
  need a target they can POST to. `server.py` is deliberately stdlib-only so there's
  no extra dependency surface between the tools and the system under test. The compose
  `agent` service runs it as its `command:`, and every tool addresses it as
  `http://agent:8000/` — the service name, since each tool runs in its own container
  where `localhost` would be itself.
- **Docker socket mount:** the Week-4 sandboxed code tool is part of the cumulative
  system, so the container still needs the host Docker socket to spawn sandboxes.
  This is a lab convenience; production would use a rootless/remote Docker API.
- **The report is the point.** ASI09/ASI10 are about trust and oversight, and the
  final deliverable — a red-team report an engineering team can act on — is the
  skill this whole bootcamp is building toward. `example_filled_report.md` sets the bar.
- **The guard model is a judge, not a classifier.** `GUARD_MODEL` defaults to `qwen2.5:3b`,
  the same instruction-following model as the orchestrator. `llama-guard3` is a *content*
  classifier: it answers with its own hazard taxonomy (`safe` / `unsafe S1–S13`) whatever you ask
  it, and it rated the benign request "Summarize the Q3 refund policy and email me the highlights"
  as `unsafe / S1` (Violent Crimes). Prompt injection is not a hazard category — screening for it
  needs a model that answers the question you actually asked.
- **The system answers from one document.** `POLICY_DOCUMENT` in `secure_system.py` is handed to the
  model inside a `<policy_document>` tag alongside the user's request, so the data/instruction
  boundary is visible in the prompt. Ask about anything else and it will correctly say it has no
  context. In the full cumulative system this is what Week 3's retriever would return.
- **Each `defenses-*.py` runs on its own** and prints its own before/after; pass your own payload,
  turns, submission path or model reply as an argument.
- **DeepTeam brings its own models.** Besides the target it needs a simulator (writes the
  attacks) and an evaluator (judges the answers). Both default to OpenAI; `run_deepteam.py`
  points them at the local Ollama instead — `ATTACK_MODEL` (default `llama3.2:1b`) and
  `GUARD_MODEL` — and runs sequentially, because one small model is already serving three
  roles. Telemetry is opted out before either package is imported.
- **One probe is off by default.** `redteam/run_garak.sh` skips `promptinject.HijackLongPrompt`: one of its requests costs minutes on a Tier-C model (the
  guardrail reads the prompt in full, then the orchestrator does too) and it can take the
  Ollama runner down with it. garak has no exclude flag, so the script names the probes it
  wants. Put it back for a run without editing anything:
  `docker compose run --rm -e PROBES=dan,encoding,leakreplay,promptinject agent bash redteam/run_garak.sh 1`
- **Tier C:** add `--generations 1` to the garak run for a fast CPU sweep.
