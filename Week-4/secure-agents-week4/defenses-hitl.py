# defenses-hitl.py — Layer 3: human-in-the-loop gate before code runs
#
# Any code-exec call must be approved by a human who sees the EXACT code first.
# High-blast-radius actions deserve a human checkpoint.
#
# Production pattern is LangGraph's `interrupt` (pauses the graph, surfaces the
# code to a UI, resumes on the human's decision). In this non-interactive lab we
# use the same CLI stand-in as code_agent_hardened.py: prompt on stdin, and treat
# "no interactive human" (EOFError) as DENY — i.e. fail closed. Under
# `docker compose run` there is no TTY, so the malicious payload is surfaced and
# then rejected, exactly as the before/after table promises.
#
# Same agent as code_agent.py with ONLY this layer applied: run_python surfaces
# the code for approval, and only runs it in the disposable sandbox (Layer 1,
# inlined) once a human approves.
import os
import sys
import subprocess
from langchain_ollama     import ChatOllama
from langchain_core.tools import tool
from tracing              import init_tracing

init_tracing("week4-defenses-hitl")

llm = ChatOllama(model=os.environ.get("ORCHESTRATOR_MODEL", "qwen2.5:3b"),
                 base_url=os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434"),
                 temperature=0)


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
    ], input=code, capture_output=True, text=True, timeout=15)
    return (out.stdout or "") + (out.stderr or "")


def human_approves(code: str) -> bool:

    # Log this function call in Magenta color
    print('\033[95m', "=================================================================")
    print('\033[95m', "Calling human_approves ...")
    print('\033[95m', "=================================================================")

    # Surface the EXACT code to the human before anything runs.
    print("\n--- CODE EXECUTION REQUEST (human review) ---")
    print(code)
    print("--- Approve execution of this code? (yes/no) ---")
    try:
        approved = input("> ").strip().lower() == "yes"
    except EOFError:
        approved = False  # no interactive human → deny (fail closed)

    # Log the decision in Magenta color
    print('\033[95m', "HITL decision: " + ("APPROVED" if approved else "DENIED"))
    return approved


@tool
def run_python(code: str) -> str:
    """Execute Python code to help answer data/analysis questions."""

    # Log this function call in Magenta color
    print('\033[95m', "=================================================================")
    print('\033[95m', "Calling run_python (human-in-the-loop) ...")
    print('\033[95m', "=================================================================")

    if not human_approves(code):
        return "[Execution denied by human reviewer.]"
    return sandboxed_exec(code)


if __name__ == "__main__":
    user_msg = sys.argv[1] if len(sys.argv) > 1 else \
        "What's the standard deviation of [4, 8, 15, 16, 23, 42]?"

    # Log this function call in Yellow color
    print('\033[33m', "=================================================================")
    print('\033[33m', "Running defenses-hitl with user_msg: " + user_msg)
    print('\033[33m', "=================================================================")

    # SINGLE-SHOT, not an autonomous ReAct agent. HITL is a checkpoint: the model
    # proposes code once, the human gate decides once. A ReAct loop would instead
    # keep re-proposing code after every rejection (no interactive human → always
    # DENY) and spin until its recursion limit — so we drive one tool call by hand.
    ai = llm.bind_tools([run_python]).invoke([
        ("system", "You are a data analysis assistant. Use run_python for calculations."),
        ("user", user_msg),
    ])

    if ai.tool_calls:
        code = ai.tool_calls[0]["args"].get("code", "")
        output = run_python.invoke({"code": code})
    else:
        output = ai.content

    # Print the output message in Cyan color
    print('\033[96m', output)
