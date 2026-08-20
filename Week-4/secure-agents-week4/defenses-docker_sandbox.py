# defenses-docker_sandbox.py — Layer 1: real sandboxing
#
# Execute model code in a throwaway container with NO network, read-only FS,
# dropped capabilities, CPU/mem/pids limits, and a hard timeout — never
# in-process. Even successful "execution" is contained to a vanishing box:
# no exfiltration (SSRF dead), no persistence, no host access.
#
# The code is piped to the sandbox over STDIN (`docker run -i ... python -`),
# so no shared files or volumes are needed — this works identically under
# Docker-out-of-Docker on any host OS.
#
# Same agent as code_agent.py with ONLY this layer applied: run_python now
# ships the model-written code to a disposable sibling container.
import os
import sys
import subprocess
from langgraph.prebuilt   import create_react_agent
from langchain_ollama     import ChatOllama
from langchain_core.tools import tool
from tracing              import init_tracing

init_tracing("week4-defenses-docker_sandbox")

llm = ChatOllama(model = os.environ.get("ORCHESTRATOR_MODEL", "qwen2.5:3b"),
                 base_url = os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434"),
                 temperature = 0)


@tool
def run_python(code: str) -> str:
    """Execute Python code to help answer data/analysis questions."""

    # Log this function call in Red color
    print('\033[31m', "=================================================================")
    print('\033[31m', "Calling run_python (sandboxed) ...")
    print('\033[31m', "=================================================================")

    out = subprocess.run([
        "docker", "run", "--rm", "-i",  # -i: the code arrives on stdin
        "--network", "none",            # no exfiltration / SSRF
        "--read-only",                  # immutable FS
        "--cap-drop", "ALL",            # no privileged syscalls
        "--pids-limit", "64",
        "--memory", "256m", "--cpus", "0.5",
        "--security-opt", "no-new-privileges",
        "python:3.12-slim", "timeout", "5", "python", "-"
    ], input = code, capture_output = True, text = True, timeout = 15)
    return (out.stdout or "") + (out.stderr or "")


agent = create_react_agent(llm, tools = [run_python],
    prompt = "You are a data analysis assistant. Use run_python for calculations.")


if __name__ == "__main__":
    user_msg = sys.argv[1] if len(sys.argv) > 1 else \
        "What's the standard deviation of [4, 8, 15, 16, 23, 42]?"

    # Log this function call in Yellow color
    print('\033[33m', "=================================================================")
    print('\033[33m', "Running defenses-docker_sandbox with user_msg: " + user_msg)
    print('\033[33m', "=================================================================")

    result = agent.invoke({"messages": [("user", user_msg)]})

    # Print the output message in Cyan color
    print('\033[96m', result["messages"][-1].content)
