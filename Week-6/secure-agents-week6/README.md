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
├── docker-compose.yml        # agent (port 8000) + Phoenix; mounts docker.sock
├── Dockerfile                # heavy image: docker CLI + garak/deepteam/pyrit
├── requirements.txt          # + garak, deepteam, pyrit (cumulative W1–W5 deps)
├── tracing.py
├── check_env.py
├── secure_system.py          # cumulative W1–W5 hardened door; handle(text) entrypoint
├── server.py                 # stdlib HTTP server: POST / {"prompt": "..."}
├── redteam/
│   ├── rest_config.json      # garak REST generator pointed at the local endpoint
│   ├── run_garak.sh          # encoding, promptinject, dan, leakage probes
│   ├── run_deepteam.py       # DeepTeam vulnerability scan
│   └── run_pyrit.py          # PyRIT multi-turn escalation orchestrator
├── attacks/
│   ├── asi09_trust_exploit.txt   # persuasive framing to defeat the HITL reviewer
│   └── asi10_rogue_drift.py      # induces role-drift / persisted directive
├── defenses/
│   ├── normalize.py          # Layer 1 — decode encoded payloads before screening
│   ├── turn_monitor.py       # Layer 2 — conversation-level escalation detection
│   ├── neutral_review.py     # Layer 3 — strip persuasive framing before HITL (ASI09)
│   └── behavior_monitor.py   # Layer 4 — role-drift / rogue-tool kill-switch (ASI10)
├── report/
│   ├── report_template.md        # the blank red-team report students fill in
│   └── example_filled_report.md  # a worked example for reference
├── solutions/
│   └── secure_system_final.py    # all four Week-6 layers wired in (instructor copy)
└── README.md
```

## Quick start

```bash
ORCHESTRATOR_MODEL=qwen2.5:3b docker compose run --rm agent python check_env.py

# 1. Stand the cumulative system up behind HTTP
docker compose up -d agent
#    (server.py serves secure_system.handle over POST / on :8000)

# 2. Run the automated red-team sweep against it
docker compose exec agent bash redteam/run_garak.sh
docker compose exec agent python redteam/run_deepteam.py
docker compose exec agent python redteam/run_pyrit.py

# 3. Read the findings, then close each gap by adding one Week-6 layer.
#    The fully-hardened target that survives the sweep:
docker compose exec agent python solutions/secure_system_final.py "Summarize the refund policy."

# 4. Write it up
$EDITOR report/report_template.md   # example_filled_report.md shows the target quality
```

## How the layers map to the findings
| Tool finding | Gap | Layer added |
|---|---|---|
| garak encoding probe smuggles base64/hex/rot13 past the keyword screen | screen sees ciphertext, not intent | `normalize.py` — decode first, then screen |
| PyRIT multi-turn escalation gets further than any single prompt | no cross-turn state | `turn_monitor.py` — track escalation / slow-boil |
| Agent talks the HITL reviewer into approving (ASI09) | reviewer sees narration, not facts | `neutral_review.py` — show raw action only |
| Agent drifts role / persists a hidden directive (ASI10) | no behavioral baseline | `behavior_monitor.py` — kill-switch on drift |

## Notes
- **Why an HTTP endpoint:** garak, DeepTeam, and PyRIT are black-box tools — they
  need a target they can POST to. `server.py` is deliberately stdlib-only so there's
  no extra dependency surface between the tools and the system under test.
- **Docker socket mount:** the Week-4 sandboxed code tool is part of the cumulative
  system, so the container still needs the host Docker socket to spawn sandboxes.
  This is a lab convenience; production would use a rootless/remote Docker API.
- **The report is the point.** ASI09/ASI10 are about trust and oversight, and the
  final deliverable — a red-team report an engineering team can act on — is the
  skill this whole bootcamp is building toward. `example_filled_report.md` sets the bar.
- **Tier C:** add `--generations 1` to the garak run for a fast CPU sweep.
