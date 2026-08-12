# defenses-fail_closed.py — Layer 2: no silent fallback (the CrewAI lesson)
#
# If the sandbox can't be created, REFUSE — never degrade to in-process exec.
# This one rule is the entire CrewAI CVE class (CVE-2026-2275/2287): a sandbox
# that silently degrades is not a sandbox. Fail CLOSED, not open.
import shutil
import subprocess
from tracing import init_tracing

from docker_sandbox import run_python as sandboxed_exec

init_tracing("week4-defenses-fail_closed")


def docker_available() -> bool:

    # Log this function call in Magenta color
    print('\033[95m', "=================================================================")
    print('\033[95m', "Calling docker_available ...")
    print('\033[95m', "=================================================================")

    if not shutil.which("docker"):
        return False
    try:
        subprocess.run(["docker", "info"], capture_output=True, timeout=10, check=True)
        return True
    except Exception:
        return False


def run_python(code: str) -> str:

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
