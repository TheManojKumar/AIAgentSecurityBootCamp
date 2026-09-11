# defenses-param_validation.py — Layer 4: parameter validation & no shell
#
# Never pass agent/model-supplied params into a shell. Validate the input and
# use a subprocess argv list (shell=False). The crafted "localhost; id" is then
# a literal argument, not a command.
import re
import sys
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
    out = subprocess.run(["echo", "pinging", host], capture_output = True, text = True)
    return out.stdout


if __name__ == "__main__":
    # An empty argument means the caller's payload extraction produced nothing —
    # fall back to the payload rather than "validating" an empty string and
    # reporting DENIED, which reads like a pass but tests nothing.
    host = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].strip() else "localhost; id"

    # Log this function call in Yellow color
    print('\033[33m', "=================================================================")
    print('\033[33m', "Running defenses-param_validation with host: " + host)
    print('\033[33m', "=================================================================")

    result = safe_ping(host)

    # Print the output message in Cyan color
    print('\033[96m', result)
