# defenses-docker_sandbox.py — Layer 1: real sandboxing
#
# Execute model code in a throwaway container with NO network, read-only FS,
# dropped capabilities, CPU/mem/pids limits, and a hard timeout — never
# in-process. Even successful "execution" is contained to a vanishing box:
# no exfiltration (SSRF dead), no persistence, no host access.
import subprocess
import tempfile
import os
from tracing import init_tracing

init_tracing("week4-defenses-docker_sandbox")


def run_python(code: str) -> str:

    # Log this function call in Red color
    print('\033[31m', "=================================================================")
    print('\033[31m', "Calling run_python ...")
    print('\033[31m', "=================================================================")

    with tempfile.NamedTemporaryFile("w", suffix=".py", dir="/sandbox_io", delete=False) as f:
        f.write(code)
        script = os.path.basename(f.name)
    try:
        out = subprocess.run([
            "docker", "run", "--rm",
            "--network", "none",            # no exfiltration / SSRF
            "--read-only",                  # immutable FS
            "--cap-drop", "ALL",            # no privileged syscalls
            "--pids-limit", "64",
            "--memory", "256m", "--cpus", "0.5",
            "--security-opt", "no-new-privileges",
            "-v", f"/sandbox_io/{script}:/run/{script}:ro",
            "python:3.12-slim", "timeout", "5", "python", f"/run/{script}"
        ], capture_output=True, text=True, timeout=15)
        return (out.stdout or "") + (out.stderr or "")
    finally:
        os.unlink(f"/sandbox_io/{script}")
