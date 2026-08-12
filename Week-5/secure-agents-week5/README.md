# Week 5 — MCP Security & Supply Chain

**ASI focus:** ASI03 (Identity & Privilege Abuse), ASI04 (Agentic Supply Chain Vulnerabilities)
**Lab image:** `secure-agents-week5`

> The one thing to leave with: when your agent connects to an MCP server, you've
> extended your trust boundary to *someone else's code and tool descriptions*.
> A malicious or compromised server can abuse the agent's identity and
> privileges — and the agent will trust it by default.

## Layout

```
secure-agents-week5/
├── docker-compose.yml     # agent + Phoenix; servers run as stdio subprocesses
├── Dockerfile
├── requirements.txt       # + mcp, langchain-mcp-adapters
├── tracing.py
├── check_env.py
├── mcp_agent.py           # agent + MultiServerMCPClient (vulnerable config)
├── servers/
│   ├── notes_server.py    # legitimate MCP server
│   └── malicious_server.py  # description-injection + exfiltrate + stdio cmd-injection
├── attacks/
│   ├── description_injection.md
│   └── stdio_cmd_injection.md
├── defenses-description_screen.py  # Layer 1
├── defenses-server_scoping.py      # Layer 2
├── defenses-server_vetting.py      # Layer 3
├── defenses-param_validation.py    # Layer 4
├── workspace/
│   ├── notes.db              # benign user notes
│   └── attacker_sink.txt     # where exfiltration lands (proof of compromise)
├── mcp_agent_hardened.py    # INSTRUCTOR ONLY, omit from student distribution
└── README.md
```

## Quick start

```bash
$env:ORCHESTRATOR_MODEL = "qwen2.5:3b"
docker compose run --rm agent python check_env.py

# benign
docker compose run --rm agent python mcp_agent.py "Save a note: buy milk."

# ATTACK: enable the "backup" (malicious) server in mcp_agent.py SERVERS, then:
docker compose run --rm agent python mcp_agent.py "Find my notes about the project."
#   -> the poisoned description coerces an exfiltrate call; check workspace/attacker_sink.txt

# DEFEND: the hardened agent rejects the unmanifested server and screens descriptions
docker compose run --rm agent python mcp_agent_hardened.py "Find my notes about the project."
```

## Notes
- **Why two local MCP servers (good + malicious):** students see a legitimate and
  a malicious integration side by side, with identical wiring — the only
  difference is trust. The malicious server is clearly labeled and only writes to
  a local sink with fake data.
- **Real-world anchor:** the 2026 MCP STDIO command-injection advisories
  (LangFlow, GPT Researcher, LiteLLM class).
