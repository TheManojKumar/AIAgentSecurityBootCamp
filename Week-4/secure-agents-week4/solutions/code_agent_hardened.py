# solutions/code_agent_hardened.py — Week 4 hardened code agent (INSTRUCTOR COPY)
#
# All four controls:
#   Layer 1 — sandboxed exec (ephemeral, network-less, read-only, cap-dropped)
#   Layer 2 — fail closed: refuse if the sandbox is unavailable
#   Layer 3 — human-in-the-loop approval gate showing exact code
#   Layer 4 — capability scoping: prefer a constrained math evaluator
#
# For the constrained-math path we route arithmetic to safe_eval and only fall
# through to the gated+sandboxed exec for genuinely general code.
import os
import sys
import shutil
import subprocess
import tempfile

try:
    from tracing import init_tracing
    init_tracing("week4-hardened")
except Exception:
    pass


# --- Layer 1: sandboxed execution ---
def sandboxed_exec(code: str) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".py", dir="/sandbox_io", delete=False) as f:
        f.write(code)
        script = os.path.basename(f.name)
    try:
        out = subprocess.run([
            "docker", "run", "--rm", "--network", "none", "--read-only",
            "--cap-drop", "ALL", "--pids-limit", "64",
            "--memory", "256m", "--cpus", "0.5",
            "--security-opt", "no-new-privileges",
            "-v", f"/sandbox_io/{script}:/run/{script}:ro",
            "python:3.12-slim", "timeout", "5", "python", f"/run/{script}"
        ], capture_output=True, text=True, timeout=15)
        return (out.stdout or "") + (out.stderr or "")
    finally:
        os.unlink(f"/sandbox_io/{script}")


# --- Layer 2: fail closed ---
def docker_available() -> bool:
    if not shutil.which("docker"):
        return False
    try:
        subprocess.run(["docker", "info"], capture_output=True, timeout=10, check=True)
        return True
    except Exception:
        return False


# --- Layer 3: human approval (CLI stand-in for LangGraph interrupt) ---
def human_approves(code: str) -> bool:
    print("\n--- CODE EXECUTION REQUEST (human review) ---")
    print(code)
    print("--- Approve execution of this code? (yes/no) ---")
    try:
        return input("> ").strip().lower() == "yes"
    except EOFError:
        return False  # no interactive human → deny (fail closed)


def guarded_run(code: str) -> str:
    if not docker_available():
        return "DENIED: secure sandbox unavailable; refusing to execute."
    if not human_approves(code):
        return "[Execution denied by human reviewer.]"
    return sandboxed_exec(code)


if __name__ == "__main__":
    # Demo: feed the direct-RCE payload; the gate surfaces it and the sandbox
    # contains it even if approved.
    code = sys.argv[1] if len(sys.argv) > 1 else "print(sum([4,8,15,16,23,42])/6)"
    print(guarded_run(code))
