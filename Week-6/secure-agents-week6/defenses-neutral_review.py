# defenses-neutral_review.py — strip persuasive framing before human review (ASI09)
#
# The HITL gate must show the human RAW FACTS (exact code, exact tool, exact
# args), not the agent's persuasive narration. An agent claiming "I already
# reviewed this, approving is routine" is manipulating the reviewer.
import re
from tracing import init_tracing

init_tracing("week6-defenses-neutral_review")

PERSUASION_PATTERNS = [
    r"i have (already )?(security[- ])?reviewed.*",
    r"this is (a )?(routine|standard|pre-?approved|pre-?authorized).*",
    r"approving is (routine|standard|safe).*",
    r"no further review (is )?(required|needed).*",
    r"✅.*",
]


def neutral_review_payload(tool: str, args: dict, raw_code: str = "") -> dict:
    """Return only verifiable facts for the human to judge; drop all narration."""

    # Log this function call in Magenta color
    print('\033[95m', "=================================================================")
    print('\033[95m', "Calling neutral_review_payload ...")
    print('\033[95m', "=================================================================")

    code = raw_code
    for pat in PERSUASION_PATTERNS:
        code = re.sub(pat, "", code, flags=re.IGNORECASE)

    # Log the verdict in Magenta color
    print('\033[95m', "Neutral review: persuasive framing stripped; judge the raw action only.")

    return {
        "tool": tool,
        "args": args,
        "code_to_run": code.strip(),
        "note": "Framing/claims removed. Judge only the raw action above.",
    }
