# defenses-neutral_review.py — Layer 3: strip persuasive framing before human review (ASI09)
#
# The HITL gate must show the human RAW FACTS (exact code, exact tool, exact
# args), not the agent's persuasive narration. An agent claiming "I already
# reviewed this, approving is routine" is manipulating the reviewer.
#
# Runnable single-layer demo: take the agent's submission as the human would
# receive it, then show what the gate should have put in front of them instead.
# Pass a file path (preferred — newlines survive) or the text itself; with no
# argument it reads attacks/asi09_trust_exploit.txt.
import os
import re
import sys
from tracing import init_tracing

init_tracing("week6-defenses-neutral_review")

PERSUASION_PATTERNS = [
    r"i have (already )?(security[- ])?reviewed.*",
    r"this is (a )?(routine|standard|pre-?approved|pre-?authorized).*",
    r"approving is (routine|standard|safe).*",
    r"no further review (is )?(required|needed).*",
    r"✅.*",
]

ATTACK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "attacks", "asi09_trust_exploit.txt")

# What the agent says it wants to do. The human is judging this, not the prose.
REQUESTED_TOOL = "run_code"
REQUESTED_ARGS = {"language": "python", "timeout_s": 30}


def neutral_review_payload(tool: str, args: dict, raw_code: str = "") -> dict:
    """Return only verifiable facts for the human to judge; drop all narration."""

    # Log this function call in Magenta color
    print('\033[95m', "=================================================================")
    print('\033[95m', "Calling neutral_review_payload ...")
    print('\033[95m', "=================================================================")

    code = raw_code
    for pat in PERSUASION_PATTERNS:
        code = re.sub(pat, "", code, flags = re.IGNORECASE)

    # Log the verdict in Magenta color
    print('\033[95m', "Neutral review: persuasive framing stripped; judge the raw action only.")

    return {
        "tool": tool,
        "args": args,
        "code_to_run": code.strip(),
        "note": "Framing/claims removed. Judge only the raw action above.",
    }


def load_submission(argument: str = "") -> str:
    """The agent's submission: a file path, literal text, or the shipped attack."""

    if argument and os.path.isfile(argument):
        text = open(argument, encoding = "utf-8").read()
    elif argument:
        return argument
    else:
        text = open(ATTACK_FILE, encoding = "utf-8").read()

    # '#' lines are the lab's annotation of the attack, not part of the submission
    return "\n".join(line for line in text.splitlines() if not line.startswith("#")).strip()


def main(submission: str):

    # Log this function call in Green color
    print('\033[92m', "=================================================================")
    print('\033[92m', "Calling main ...")
    print('\033[92m', "=================================================================")

    # Log what the agent submitted, verbatim, in Red color
    print('\033[91m', "What the agent put in front of the human:")
    print('\033[91m', submission)

    payload = neutral_review_payload(REQUESTED_TOOL, REQUESTED_ARGS, submission)

    # Print the output message in Cyan color
    print('\033[96m', "What the gate should show instead:")
    for key, value in payload.items():
        print('\033[96m', f"  {key}: {value}")


if __name__ == "__main__":
    argument   = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].strip() else ""
    submission = load_submission(argument)

    # Log this function call in Yellow color
    print('\033[33m', "=================================================================")
    print('\033[33m', "Running defenses-neutral_review on " + (argument or ATTACK_FILE))
    print('\033[33m', "=================================================================")

    main(submission)
