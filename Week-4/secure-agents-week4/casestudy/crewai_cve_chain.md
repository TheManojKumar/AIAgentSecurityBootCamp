# Case Study — CrewAI Silent-Sandbox-Fallback Chain (VU#221883)

**CVEs:** CVE-2026-2275, CVE-2026-2285, CVE-2026-2286, CVE-2026-2287

This is the real-world anchor for Week 4: a shipping agent framework carried
exactly the bug class students reproduce by hand.

## The chain, step by step

1. **Intended design.** The Code Interpreter is meant to run model-written code
   inside a Docker container.
2. **Silent fallback (CVE-2026-2275 / -2287).** If Docker is unreachable, the
   interpreter *silently* falls back to an in-process sandbox instead of
   refusing. The security posture degrades with no signal to the operator.
3. **Sandbox escape.** That in-process sandbox does not block `ctypes` / C-level
   calls, so model code can escape it and reach the host → RCE.
4. **File read (CVE-2026-2285).** A JSON-loader path allows arbitrary file read.
5. **SSRF (CVE-2026-2286).** A RAG fetch path can be steered to make server-side
   requests to internal endpoints.

## Mapping to what students just did by hand

| Lab step (this week)                         | CrewAI CVE analogue          |
|----------------------------------------------|------------------------------|
| `exec(code)` in `code_agent.py`              | in-process sandbox execution |
| injected `os.popen(...)` shell-out           | sandbox escape → host RCE    |
| reading `workspace/secrets/api_keys.txt`     | arbitrary file read (-2285)  |
| network exfiltration attempt                 | RAG SSRF (-2286)             |
| Docker-down → refuse (Layer 2)               | the fix for -2275 / -2287    |

## The single lesson

> A sandbox that silently turns off is not a sandbox. **Fail closed, not open.**
> `defenses-fail_closed.py` — the one-line refusal — is the entire CVE.
