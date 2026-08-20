# defenses-fail_closed.py — Layer 2: no silent fallback (the CrewAI lesson)
#
# If the sandbox can't be created, REFUSE — never degrade to in-process exec.
# This one rule is the entire CrewAI CVE class (CVE-2026-2275/2287): a sandbox
# that silently degrades is not a sandbox. Fail CLOSED, not open.
#
# Same agent as code_agent.py with ONLY this layer applied: run_python gates on
# sandbox availability, and only runs code in the disposable container (Layer 1,
# inlined) once the sandbox is confirmed present.
import os
import sys
import shutil
import subprocess
from langgraph.prebuilt   import create_react_agent
from langchain_ollama     import ChatOllama
from langchain_core.tools import tool
from tracing              import init_tracing

init_tracing("week4-defenses-fail_closed")

llm = ChatOllama(model = os.environ.get("ORCHESTRATOR_MODEL", "qwen2.5:3b"),
                 base_url = os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434"),
                 temperature = 0)


# --- Layer 1 (inlined): sandboxed execution ---
def sandboxed_exec(code: str) -> str:
    # The code is piped to the sandbox over STDIN — no shared files or volumes,
    # so this works identically under Docker-out-of-Docker on any host OS.
    out = subprocess.run([
        "docker", "run", "--rm", "-i", "--network", "none", "--read-only",
        "--cap-drop", "ALL", "--pids-limit", "64",
        "--memory", "256m", "--cpus", "0.5",
        "--security-opt", "no-new-privileges",
        "python:3.12-slim", "timeout", "5", "python", "-"
    ], input = code, capture_output = True, text = True, timeout = 15)
    return (out.stdout or "") + (out.stderr or "")


def docker_available() -> bool:

    # Log this function call in Magenta color
    print('\033[95m', "=================================================================")
    print('\033[95m', "Calling docker_available ...")
    print('\033[95m', "=================================================================")

    if not shutil.which("docker"):
        return False
    try:
        subprocess.run(["docker", "info"], capture_output = True, timeout = 10, check = True)
        return True
    except Exception:
        return False


@tool
def run_python(code: str) -> str:
    """Execute Python code to help answer data/analysis questions."""

    # Log this function call in Magenta color
    print('\033[95m', "=================================================================")
    print('\033[95m', "Calling run_python (fail-closed) ...")
    print('\033[95m', "=================================================================")

    if not docker_available():
        # Log the decision in Magenta color
        print('\033[95m', "Fail-closed decision: DENIED (sandbox unavailable)")
        return "DENIED: secure sandbox unavailable; refusing to execute."  # fail CLOSED
    # Log the decision in Magenta color
    print('\033[95m', "Fail-closed decision: PROCEED (sandbox available)")
    return sandboxed_exec(code)


agent = create_react_agent(llm, tools = [run_python],
    prompt = "You are a data analysis assistant. Use run_python for calculations.")


if __name__ == "__main__":
    user_msg = sys.argv[1] if len(sys.argv) > 1 else \
        "What's the standard deviation of [4, 8, 15, 16, 23, 42]?"

    # Log this function call in Yellow color
    print('\033[33m', "=================================================================")
    print('\033[33m', "Running defenses-fail_closed with user_msg: " + user_msg)
    print('\033[33m', "=================================================================")

    result = agent.invoke({"messages": [("user", user_msg)]})

    # Print the output message in Cyan color
    print('\033[96m', result["messages"][-1].content)
