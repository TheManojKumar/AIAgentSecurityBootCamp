# Week 3 — RAG & Memory Poisoning

**ASI focus:** ASI06 (Memory & Context Poisoning)
**Lab image:** `secure-agents-week3`

> The one thing to leave with: an agent's knowledge sources — retrieved documents
> and persistent memory — are an *attack surface*, not a trusted oracle. Poison
> what the agent reads or remembers, and you control what it does, often long
> after the attacker is gone.

## Layout

```
secure-agents-week3/
├── docker-compose.yml            # agent + Phoenix; Chroma embedded (PersistentClient)
├── Dockerfile
├── requirements.txt              # + chromadb, langchain-community
├── tracing.py
├── check_env.py
├── rag_agent.py                  # RAG + memory (vulnerable)
├── ingest.py                     # builds the Chroma collection from workspace/corpus
├── attacks/
│   ├── poison_refund.txt         # malicious RAG document
│   └── memory_poison.txt         # the OMEGA persistent-memory payload
├── defenses-provenance.py        # Layer 1
├── defenses-context_isolation.py # Layer 2
├── defenses-memory_guard.py      # Layer 3
├── defenses-rerank.py            # Layer 4
├── workspace/
│   ├── corpus/
│   │   ├── refund_policy.txt      # the real policy (30 days)
│   │   └── shipping.txt           # clean control doc
│   ├── chroma/                    # persistent vector store (created by ingest.py)
│   └── memory.txt                 # starts empty
├── rag_agent_hardened.py          # all four layers — INSTRUCTOR ONLY, omit from student distribution
└── README.md
```

## Quick start

```bash
$env:ORCHESTRATOR_MODEL = "qwen2.5:3b"
$env:EMBED_MODEL = "all-minilm"
docker compose run --rm agent python check_env.py

# build the vector store, then ask a clean question
docker compose run --rm agent python ingest.py
docker compose run --rm agent python rag_agent.py "What's the refund window?"    # -> 30 days

# ATTACK 1 (RAG poisoning): drop the poison doc into the corpus, re-ingest, re-ask
cp attacks/poison_refund.txt workspace/corpus/refund_update.txt
docker compose run --rm agent python ingest.py
docker compose run --rm agent python rag_agent.py "What's the refund window?"    # -> 9999 days

# ATTACK 2 (memory poisoning, persistent):
docker compose run --rm agent python rag_agent.py "remember: $(cat attacks/memory_poison.txt)"
#   then start a FRESH run mentioning OMEGA — the poison persists.

# hardened version refuses the poison write and filters the poison doc
docker compose run --rm agent python rag_agent_hardened.py "What's the refund window?"
```

## Notes
- **Why Chroma embedded (PersistentClient) not a separate service:** simpler for
  students, fully local, persists to a mounted volume so RAG/memory state survives
  between runs — exactly what makes the *persistent* memory-poisoning attack
  demonstrable.
- **The persistence beat:** open a *new* terminal/session for Attack 2 so the
  audience sees the attacker is gone but the poison remains.
