# defenses/param_validation.py — Layer 4: parameter validation & no shell
#
# Never pass agent/model-supplied params into a shell. Validate the input and
# use a subprocess argv list (shell=False). The crafted "localhost; id" is then
# a literal argument, not a command.
import re
import subprocess

_HOST_RE = re.compile(r"^[A-Za-z0-9.\-]+$")   # hostnames/IPs only, no shell metachars


def safe_ping(host: str) -> str:
    if not _HOST_RE.match(host):
        return "DENIED: invalid host."
    # argv list, shell=False — the value can never be interpreted as a command
    out = subprocess.run(["echo", "pinging", host], capture_output=True, text=True)
    return out.stdout
