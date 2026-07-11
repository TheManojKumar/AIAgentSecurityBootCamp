# defenses/fail_closed.py — Layer 2: no silent fallback (the CrewAI lesson)
#
# If the sandbox can't be created, REFUSE — never degrade to in-process exec.
# This one rule is the entire CrewAI CVE class (CVE-2026-2275/2287): a sandbox
# that silently degrades is not a sandbox. Fail CLOSED, not open.
import shutil
import subprocess

from docker_sandbox import run_python as sandboxed_exec


def docker_available() -> bool:
    if not shutil.which("docker"):
        return False
    try:
        subprocess.run(["docker", "info"], capture_output=True, timeout=10, check=True)
        return True
    except Exception:
        return False


def run_python(code: str) -> str:
    if not docker_available():
        return "DENIED: secure sandbox unavailable; refusing to execute."  # fail CLOSED
    return sandboxed_exec(code)
