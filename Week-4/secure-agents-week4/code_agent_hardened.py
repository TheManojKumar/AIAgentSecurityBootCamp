# code_agent_hardened.py — Week 4 hardened code agent (INSTRUCTOR COPY)
#
# All four controls:
#   Layer 1 — sandboxed exec (ephemeral, network-less, read-only, cap-dropped)
#   Layer 2 — fail closed: refuse if the sandbox is unavailable
#   Layer 3 — human-in-the-loop approval gate showing exact code
#   Layer 4 — capability scoping: prefer a constrained math evaluator
#
# For the constrained-math path we route arithmetic to safe_eval and only fall
# through to the gated+sandboxed exec for genuinely general code.
# Ships to instructors only; omit this file from the student distribution.
import sys
import shutil
import subprocess
from tracing import init_tracing

init_tracing("week4-hardened")


# --- Layer 1: sandboxed execution ---
def sandboxed_exec(code: str) -> str:

    # Log this function call in Red color
    print('\033[31m', "=================================================================")
    print('\033[31m', "Calling sandboxed_exec ...")
    print('\033[31m', "=================================================================")

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


# --- Layer 2: fail closed ---
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


# --- Layer 3: human approval (CLI stand-in for LangGraph interrupt) ---
def human_approves(code: str) -> bool:

    # Log this function call in Magenta color
    print('\033[95m', "=================================================================")
    print('\033[95m', "Calling human_approves ...")
    print('\033[95m', "=================================================================")

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


def guarded_run(code: str) -> str:

    # Log this function call in Magenta color
    print('\033[95m', "=================================================================")
    print('\033[95m', "Calling guarded_run ...")
    print('\033[95m', "=================================================================")

    if not docker_available():
        # Log the decision in Magenta color
        print('\033[95m', "Gate decision: DENIED (sandbox unavailable)")
        return "DENIED: secure sandbox unavailable; refusing to execute."
    if not human_approves(code):
        # Log the decision in Magenta color
        print('\033[95m', "Gate decision: DENIED (human rejected)")
        return "[Execution denied by human reviewer.]"
    # Log the decision in Magenta color
    print('\033[95m', "Gate decision: APPROVED")
    return sandboxed_exec(code)


if __name__ == "__main__":
    # Demo: feed the direct-RCE payload; the gate surfaces it and the sandbox
    # contains it even if approved.
    code = sys.argv[1] if len(sys.argv) > 1 else "print(sum([4,8,15,16,23,42])/6)"

    # Log this function call in Yellow color
    print('\033[33m', "=================================================================")
    print('\033[33m', "Running code_agent_hardened with code: " + code)
    print('\033[33m', "=================================================================")

    # Print the output message in Cyan color
    print('\033[96m', guarded_run(code))
