# Prerequisites — Command & Concept Reference
### Securing Local AI Agents · Get-Ready Guide

> **How to use this:** The fastest path is the **Setup Runbook** (Section 0), copy-paste it end-to-end and you're ready.
> The later sections explain the pieces and give you the commands worth knowing. The deck is a fast refresher; this file is the lookup.

---

## Section 0 — Install pre-requisites

### Windows (PowerShell)

```powershell
winget install python3                    # python to compile and run code
winget install Docker.DockerDesktop       # to install and run containers
winget install Ollama.Ollama              # models
winget install Git.Git                    # optional if you want to create your own git repo
winget install Microsoft.VisualStudioCode # will use it as our development environment
```
### Ubuntu (Bash)

```bash
sudo apt install python3                        # python to compile and run code
sudo apt install docker.io                      # to install and run containers
curl -fsSL https://ollama.com/install.sh | sh   # models
sudo apt install git                            # optional if you want to create your own git repo
sudo snap install code --classic                # will use it as our development environment
```

## Section 0 — Check if everything is working (do this once, in order, same for windows/linux)

```bash
# 0.1 — Confirm Python 3.11+ and pip
python --version            # need 3.11 or newer
pip --version

# 0.2 — Install Docker (see docker.com/get-started), then verify
# if this image is not available locally, it will download it and then run it
docker run --rm hello-world  # should print "Hello from Docker!"
# If you get an error that says:
# failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine; check if the path is correct and if the daemon is running
# that means docker is not installed or not running, start it
docker compose version       # should print v2.x

# 0.3 — Install Ollama (see ollama.com/download), then start it
ollama --version
ollama serve &               # leave running; on macOS the app does this for you

# 0.4 — Pull your TIER's models (pick ONE tier; see the tier table below)
# --- Tier C (CPU only, 16GB+ RAM) ---
ollama pull qwen2.5:3b
ollama pull llama3.2:3b
ollama pull llama3.2:1b
ollama pull all-minilm
ollama pull llama-guard3:1b

# 0.5 — Confirm the models are present and Ollama answers over HTTP
ollama list
curl http://localhost:11434/api/tags        # JSON list of your models
# Test if model is working from command / HTTP
curl http://localhost:11434/api/generate -d '{"model":"qwen2.5:3b","prompt":"say ready","stream":false}'

# 0.6 — Optional - Create your portfolio repo (you'll fill this in each week)
mkdir secure-multi-agent-lab
cd secure-multi-agent-lab
git init
echo "# Securing Local AI Agents — my lab" > README.md
git add . 
git commit -m "init lab"
git remote add origin https://github.com/<YOUR_USER_NAME>/<REPO_NAME>.git
git remote -v # verify the remote url
git push -u origin main
```

### Tier table (which models to pull in 0.4)

| Role | Tier A — 24GB GPU | Tier B — 8–16GB GPU | Tier C — CPU only |
|------|-------------------|---------------------|-------------------|
| Orchestrator | `qwen2.5:14b` | `qwen2.5:7b` | `qwen2.5:3b` |
| Specialist | `qwen2.5:7b` | `llama3.2:3b` | `llama3.2:3b` |
| Attacker | `llama3.2:3b` | `llama3.2:1b` | `llama3.2:1b` |
| Guardrail | `llama-guard3:8b` | `llama-guard3:1b` | `llama-guard3:1b` |
| Embeddings | `nomic-embed-text` | `nomic-embed-text` | `all-minilm` |

You don't need to know your GPU's exact VRAM — Ollama auto-detects hardware and runs the model on GPU, CPU, or a split, whichever fits. The only thing **you** choose is which model string to pull. Everything else in the course is identical across tiers; only speed differs.

---

## Section 1 — Command Line (CLI) essentials

You should be comfortable moving around a shell. The commands worth knowing for this course:
### Windows (PowerShell)
```PowerShell
pwd                       # where am I (or: Get-Location)
ls -Force                 # list files, including hidden, with details (or: Get-ChildItem -Force)
cd path\to\dir            # change directory ('cd ..' goes up one)
cat file.txt              # print a file (or: Get-Content file.txt)
more file.txt             # scroll a file (q to quit; or: Get-Content file.txt | Out-Host -Paging)
mkdir a\b\c               # make nested directories (New-Item creates parents automatically)
cp src dst ; mv src dst   # copy / move (or rename)
rm file ; rm -r dir       # remove file / directory (careful)

# Environment variables — how we select models and point at Ollama
$env:ORCHESTRATOR_MODEL = "qwen2.5:3b"
echo $env:ORCHESTRATOR_MODEL             # read one back (or: Write-Output)

# Inspect what's running / listening
Get-Process ollama         # is ollama running? (or: ps | findstr ollama)
curl http://localhost:11434/api/tags     # talk to a local HTTP service (or: Invoke-RestMethod)
```

### Linux (Bash)
```bash
pwd                       # where am I
ls -la                    # list files, including hidden, with details
cd path/to/dir            # change directory ('cd ..' goes up one)
cat file.txt              # print a file
less file.txt             # scroll a file (q to quit)
mkdir -p a/b/c            # make nested directories
cp src dst ; mv src dst   # copy / move (or rename)
rm file ; rm -r dir       # remove file / directory (careful)

# Environment variables — how we select models and point at Ollama
export ORCHESTRATOR_MODEL=qwen2.5:3b
echo $ORCHESTRATOR_MODEL                 # read one back

# Inspect what's running / listening
ps aux | grep ollama       # is ollama running?
curl http://localhost:11434/api/tags     # talk to a local HTTP service
```

**Key ideas:** the shell is how you run everything in this course; environment variables are how the labs are configured (especially `ORCHESTRATOR_MODEL` and `OLLAMA_HOST`); `curl` is how you confirm a local service is alive.

---

## Section 2 — Python (for agents, not from scratch)

You don't need to be an expert. You need to read agent code, edit it, and run it. The constructs that show up constantly:

```bash
# Virtual environments — isolate dependencies (do this per project)
python -m venv Week1
source Week1/bin/activate          # Linux
.\Week1\Scripts\activate           # Windows 
pip install -r requirements.txt
deactivate

# How to check if I am running inside an environment
where python # Windows
Get-Command python # Windows / PowerShell, shows the name of the active environment in the path

which python # For Linux
```

```python
# Functions and type hints (tools are typed functions)
def add_note(text: str) -> str:
    return f"saved: {text}"

# Decorators (LangChain marks tools with @tool)
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """Return weather for a city."""   # the docstring becomes the tool description
    return f"{city}: 72F"

# f-strings (building prompts)
name = "world"
prompt = f"Hello, {name}. Summarize the text below."

# Classes / Pydantic models (structured outputs in Week 2+)
from pydantic import BaseModel
class Research(BaseModel):
    topic: str
    findings: list[str]

# Reading env + files (every lab does this)
import os
model = os.environ.get("ORCHESTRATOR_MODEL", "qwen2.5:3b")
text  = open("/workspace/notes.txt").read()

# async basics (MCP + some agent calls are async)
import asyncio
async def main():
    result = await agent.ainvoke({"messages": [("user", "hi")]})
asyncio.run(main())
```

**Key ideas to be familiar with:** functions + type hints; **decorators** (especially `@tool`, and that a tool's **docstring becomes its description the model reads** — that's a security-relevant detail in Week 5); **f-strings** for prompt building; **Pydantic models** for structured/validated output; reading **environment variables** and **files**; and just enough **async** (`await`, `asyncio.run`) to not be surprised when you see it.

You do **not** need: training models, NumPy/Pandas mastery, web frameworks, or advanced OOP.

---

## Section 3 — Docker (run and reason about containers)

Containers are how the labs are distributed so everyone runs an identical environment. You mostly *use* Docker; you don't have to author images.

```bash
# Images vs containers: an image is the blueprint, a container is a running instance
docker pull dyego/snake-game
docker pull docker/doodle
docker pull dyego/snake-game:latest   # download an image
docker images                          # list local images
docker ps                              # running containers
docker ps -a                           # all containers, including stopped

# Run things
docker run --rm hello-world            # run, then auto-remove
docker run -it docker/doodle           # interactive shell in the containers
docker run -ti dyego/snake-game

# Compose — bring up a multi-container lab (agent + Phoenix) from one file
# Will cover in future sessions
docker compose up                      # start everything in docker-compose.yml
docker compose run --rm agent python check_env.py   # run one command in the 'agent' service
docker compose down                    # stop and clean up

# The networking detail that matters: a container reaching the HOST's Ollama
#   Mac/Windows: use host.docker.internal
#   Linux: our compose adds  extra_hosts: ["host.docker.internal:host-gateway"]
#          or run with --network=host and use localhost
# We will dig more into it in future
docker run --rm --network=host my-image   # container shares host network (Linux)
```

**Minimal compose mental model** — you'll see files like this and should be able to read them:
# Let's revisit them in future, not really required to be productive
```yaml
services:
  phoenix:                              # tracing UI, no account needed
    image: arizephoenix/phoenix:latest
    ports: ["6006:6006"]
  agent:                                # the lab code
    build: .
    environment:
      - ORCHESTRATOR_MODEL=${ORCHESTRATOR_MODEL:-qwen2.5:3b}   # the one knob you change
      - OLLAMA_HOST=${OLLAMA_HOST:-http://host.docker.internal:11434}
    extra_hosts: ["host.docker.internal:host-gateway"]        # reach host Ollama on Linux
```

**Key ideas:** image vs container; `pull` / `run` / `ps` / `compose up`/`down`; that **models live in host Ollama, not in the container**, so the container must reach *out* to the host — and the `host.docker.internal` / `host-gateway` line is how. This is the single most common setup snag; know where it lives.

---

## Section 4 — LLM & agent mental model (just enough to be productive)

You don't need to know how models are trained. You need the working vocabulary, that's all.

**Core terms**
- **Token** : the unit a model reads/writes (~¾ of a word). Models have a **context window** (a max number of tokens they can see at once).
- **Prompt** : the text you send. Composed of roles: **system** (instructions/persona), **user** (the request), **assistant** (the model's reply), **tool** (results returned from a tool call).
- **Temperature** : randomness. `0` = deterministic-ish (what we use for reproducible labs); higher = more varied.
- **Inference** : running the model to get output (what Ollama does locally).
- **Embedding** : a vector representing text's meaning; used to search a corpus by similarity (RAG).

**Agent terms (the heart of the course)**
- **Tool / function calling** : the model emits a structured request to call a function (e.g. `read_file(path=...)`); your code runs it and feeds the result back. *This is where text becomes action : the core security surface.*
- **Agent** : an LLM in a loop that can call tools, observe results, and decide next steps. A chatbot answers; an **agent acts**.
- **ReAct** : a common agent pattern: the model alternates Reasoning and Acting (tool calls) until done.
- **Orchestrator / supervisor + specialists** : a multi-agent topology where one agent routes work to others and combines results.
- **RAG (Retrieval-Augmented Generation)** : retrieve relevant documents, put them in the prompt, then generate. Quality and **trust** of the answer depend on the retrieved docs.
- **Memory** : facts/summaries persisted across turns or sessions and reloaded into context.
- **MCP (Model Context Protocol)** : a standard way for agents to discover and call tools hosted by external servers. The server's tool **descriptions enter the model's context**.

**The one security idea that frames everything**
> The model does **what the text says** : and "the text" includes user input, retrieved documents, memory, and tool descriptions. Any of those can carry an attacker's instructions. Security is the **architecture around the model** (allow-listing, validation, isolation, sandboxing, human gates), not a property of the model itself.

**Security vocabulary used throughout** (you likely know these):
- **CIA triad** : Confidentiality, Integrity, Availability.
- **Least privilege** : give a component only the access it needs. In agents: **least agency** - autonomy is earned, not default.
- **Trust boundary** : where data crosses from less-trusted to more-trusted; must be guarded.
- **Injection** : untrusted input treated as instructions/code. **Prompt injection** is this idea applied to LLM context. **Direct** = in the user turn; **indirect** = hidden in content the agent reads.
- **Defense in depth** : layered controls, so one failure isn't fatal. This is the course's repeated lesson.

---

## Section 5 — Troubleshooting

| Symptom                                     | Likely cause                         | Fix                                                                                                                                                                    |
| ------------------------------------------- | ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Container: "connection refused" to Ollama   | Container can't reach host Ollama    | Mac/Win: use `host.docker.internal`. Linux: ensure `extra_hosts: ["host.docker.internal:host-gateway"]` or run `--network=host` + `OLLAMA_HOST=http://localhost:11434` |
| `model 'X' not found`                       | Pulled a different tier's model      | `ollama list`; pull the exact string your `ORCHESTRATOR_MODEL` expects                                                                                                 |
| First response very slow (CPU)              | Model loading into RAM on first call | Normal; subsequent calls are faster. Keep `ollama serve` running                                                                                                       |
| `docker: permission denied ... docker.sock` | User not in docker group (Linux)     | Add user to `docker` group or use Docker Desktop                                                                                                                       |
| `curl localhost:11434` fails                | Ollama not running                   | `ollama serve &` (or start the Ollama app)                                                                                                                             |
| Phoenix UI not loading                      | Port not mapped / container down     | Confirm `ports: ["6006:6006"]` and `docker compose up` is running; open `http://localhost:6006`                                                                        |
| Out of memory on a big model                | Tier too high for hardware           | Drop a tier (e.g. `qwen2.5:7b` → `qwen2.5:3b`); Ollama will also CPU-offload automatically                                                                             |

---

## Section 6 — Readiness checklist

You're ready for Week 1 when you can honestly tick all of these:

- [ ] I can open a terminal, move between directories, and set an environment variable.
- [ ] `docker run --rm hello-world` works, and I can read a `docker-compose.yml`.
- [ ] `ollama list` shows my tier's models and `curl http://localhost:11434/api/tags` returns JSON.
- [ ] I can read a ~40-line Python file with `@tool` functions and f-string prompts and roughly follow it.
- [ ] I can explain, in a sentence each: tool calling, prompt injection (direct vs indirect), least privilege, trust boundary, defense in depth.

If any box is unticked, the matching section above (or the deck) is where to look. Tick them all, and the rest of the course is hands-on.
