# defenses-param_validation.py — Layer 4: parameter validation & no shell
#
# Never pass agent/model-supplied params into a shell. Validate the input and
# use a subprocess argv list (shell=False). The crafted "localhost; id" is then
# a literal argument, not a command.
import re
import subprocess
from tracing import init_tracing

init_tracing("week5-defenses-param_validation")

_HOST_RE = re.compile(r"^[A-Za-z0-9.\-]+$")   # hostnames/IPs only, no shell metachars


def safe_ping(host: str) -> str:

    # Log this function call in Magenta color
    print('\033[95m', "=================================================================")
    print('\033[95m', "Calling safe_ping ...")
    print('\033[95m', "=================================================================")

    if not _HOST_RE.match(host):

        # Log the verdict in Magenta color
        print('\033[95m', "Validation verdict: DENIED (invalid host)")

        return "DENIED: invalid host."

    # Log the verdict in Magenta color
    print('\033[95m', "Validation verdict: ALLOWED")

    # argv list, shell=False — the value can never be interpreted as a command
    out = subprocess.run(["echo", "pinging", host], capture_output=True, text=True)
    return out.stdout
