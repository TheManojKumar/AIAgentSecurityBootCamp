# Securing AI Agents
### A Six-Week, Hands-On, Build → Attack → Defend Course (Self-Paced & Teachable)

---
## What this course is

- A practitioner course for learning, and then teaching to others, how to build multi-agent AI systems and secure them, entirely on local hardware.
- Every week you **build** a working agent system, **attack** it with real exploits you run yourself, and **defend** it by layering controls until the same attack fails.
- Everything runs offline against local models via Ollama; no cloud accounts, no API keys, no data leaving the machine.

---

## What's covered in 6-weeks

| Week  | Theme                                       | OWASP ASI          | Projects / Build                     | Attack Vectors                                      | Defend and Mitigate                                             |
| ----- | ------------------------------------------- | ------------------ | ------------------------------------ | --------------------------------------------------- | --------------------------------------------------------------- |
| **1** | Foundations + first agent + first injection | ASI01, ASI02       | A single tool-calling agent          | Direct prompt injection → goal hijack + tool misuse | Tool allow-listing, input separation, arg validation, guardrail |
| **2** | Multi-agent systems + trust boundaries      | ASI07, ASI08       | LangGraph supervisor + 2 specialists | Indirect injection that cascades agent→agent        | Inter-agent validation node, output schemas, trust labeling     |
| **3** | RAG & memory poisoning                      | ASI06              | RAG-backed research agent + memory   | Poisoned document + persistent memory poisoning     | Provenance tracking, context isolation, retrieval filtering     |
| **4** | Tool abuse & code execution (RCE)           | ASI02, ASI05       | Agent with a code-exec tool          | Sandbox-escape → RCE (+ real CrewAI CVE case study) | Docker sandboxing, HITL gate, capability scoping                |
| **5** | MCP security & supply chain                 | ASI03, ASI04       | Agent + local MCP server             | Malicious/poisoned MCP server, privilege abuse      | Least-privilege scoping, MCP allow-listing, server vetting      |
| **6** | Automated red-teaming + hardening + report  | ASI09, ASI10 + all | Harden the cumulative system         | Garak / DeepTeam / PyRIT automated scans            | Before/after delta + professional red-team report               |

**The loop is the pedagogy.** Build → Attack → Defend every single week. Students *see* the vulnerability happen on screen, then *see* it fixed. By Week 6 each student has a single repo that tells the whole story: a vulnerable baseline hardened into a defensible system, plus the teaching materials to deliver it themselves.

---

## Three hardware tiers

Every lab is written to **Tier C (CPU-only)**. Tiers A and B simply run faster. The vulnerabilities and defenses are **identical across all tiers**, only latency differs. GPU-only extensions are marked **[STRETCH]**.

| Role in the labs | Tier A — 24GB GPU | Tier B — 8–16GB GPU | Tier C — CPU only (16GB+ RAM) |
|------------------|-------------------|---------------------|-------------------------------|
| Orchestrator / reasoning | `qwen2.5:14b` | `qwen2.5:7b` | `qwen2.5:3b` |
| Specialist / subagent | `qwen2.5:7b` | `llama3.2:3b` | `llama3.2:3b` |
| Attacker model (want it compliant) | `llama3.2:3b` | `llama3.2:1b` | `llama3.2:1b` |
| Guardrail / judge model | `llama-guard3:8b` | `llama-guard3:1b` | `llama-guard3:1b` |
| Embeddings | `nomic-embed-text` | `nomic-embed-text` | `all-minilm` |

### Why small models are fine, and sometimes *better*, for this course

These labs study prompt injection, tool abuse, trust-boundary failures, and poisoning. **Weaker models follow injected instructions more eagerly**, so the vulnerabilities reproduce *more* reliably on a 3B model than on a frontier model. A small model that gets hijacked is a perfect teaching specimen. The one thing you sacrifice on CPU is speed (seconds per turn instead of sub-second), never the lesson.

### How tiering works mechanically

- Ollama decides GPU-vs-CPU placement itself, based on the host's hardware. Your code never knows the difference: the container always talks to Ollama's HTTP API at port `11434`, and the endpoint is identical whether the model runs on a 24GB GPU or entirely on CPU.
- **The only thing that changes per tier is which model string gets pulled and requested**, set by a single environment variable (`ORCHESTRATOR_MODEL`).
- One image, one codebase, three tiers. See each week's prep doc for the host-connection details (`host.docker.internal` on Mac/Windows; `host-gateway` or `--network=host` on Linux).

---

## Prerequisites (assumed, not taught)

This course does **not** teach the basics. Students should arrive with:

- **Python** : intermediate: functions, decorators, virtualenvs, reading/writing classes, basic async awareness.
- **CLI comfort** : Linux/macOS shell, environment variables, running processes.
- **Docker** : installed and working; able to run `docker compose up` and read a compose file.
- **LLM mental model** : tokens, context window, temperature, the difference between system / user / tool messages.
- **Security literacy** : CIA triad, least privilege, trust boundary, and what an injection attack *is* in the classic (e.g. SQL/command) sense.

> A separate **Prerequisite Session** (stretched over 1–2 sessions) will bring motivated-but-underprepared participants up to this bar. It will cover: a 90-minute Python-for-agents refresher, a Docker crash course, an "LLMs in 60 minutes" primer, and basics of security.

---

## Standards & frameworks anchored throughout

- **[OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)** (ASI01–ASI10) : finalized 9 Dec 2025; the spine of the course.
- **[OWASP LLM Top 10 (2025)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)** : the single-model baseline the agentic list builds on.
- **[MITRE ATLAS](https://atlas.mitre.org/)** : adversarial ML tactics/techniques, for the red-team report in Week 6.
- **[CSA MAESTRO](https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro)** : layered agentic threat modeling.
- **[NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework)** : governance framing for the closing discussion.

### Official OWASP Agentic Top 10 (2026) — canonical names

| ID | Name | Course week(s) |
|----|------|----------------|
| ASI01 | Agent Goal Hijack | 1, 2 |
| ASI02 | Tool Misuse & Exploitation | 1, 4 |
| ASI03 | Identity & Privilege Abuse | 5 |
| ASI04 | Agentic Supply Chain Vulnerabilities | 5 |
| ASI05 | Unexpected Code Execution (RCE) | 4 |
| ASI06 | Memory & Context Poisoning | 3 |
| ASI07 | Insecure Inter-Agent Communication | 2 |
| ASI08 | Cascading Failures | 2 |
| ASI09 | Human-Agent Trust Exploitation | 6 |
| ASI10 | Rogue Agents | 6 |

---

## Distribution model

- **Per-week Docker images** (`secure-agents-week1` … `week6`), each self-contained, so a student can start at any week without dragging prior weeks along.
- **Models in host Ollama**, pulled with provided commands (tier-dependent, too large to bake in).
- **Tracing via Arize Phoenix**, auto-instrumented and baked into every week's compose file — fully local, no account, captures tool-call decisions automatically so they're visible on screen.

---

