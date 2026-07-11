# Attack — STDIO Command Injection (2026 class)

A second betrayal: the server's *code* runs with whatever access you grant it.
The malicious `ping_host` tool naively passes a model-supplied parameter into a
shell:

```python
subprocess.run(f"echo pinging {host}", shell=True, ...)
```

A crafted parameter such as:

```
host = "localhost; id"
```

executes `id` on the server process. This is the real-world MCP STDIO
command-injection class flagged by the 2026 OX Security advisories (LangFlow,
GPT Researcher, LiteLLM).

## The fix (Layer 4)
Never pass agent/model-supplied params into a shell. Validate, and use an
`argv` list with `shell=False`, so the crafted parameter is treated as a literal
string, not a command. See `defenses/param_validation.py`.
