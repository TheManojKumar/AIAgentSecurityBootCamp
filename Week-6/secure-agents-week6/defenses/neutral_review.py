# defenses/neutral_review.py — strip persuasive framing before human review (ASI09)
#
# The HITL gate must show the human RAW FACTS (exact code, exact tool, exact
# args), not the agent's persuasive narration. An agent claiming "I already
# reviewed this, approving is routine" is manipulating the reviewer.
import re

PERSUASION_PATTERNS = [
    r"i have (already )?(security[- ])?reviewed.*",
    r"this is (a )?(routine|standard|pre-?approved|pre-?authorized).*",
    r"approving is (routine|standard|safe).*",
    r"no further review (is )?(required|needed).*",
    r"✅.*",
]


def neutral_review_payload(tool: str, args: dict, raw_code: str = "") -> dict:
    """Return only verifiable facts for the human to judge; drop all narration."""
    code = raw_code
    for pat in PERSUASION_PATTERNS:
        code = re.sub(pat, "", code, flags=re.IGNORECASE)
    return {
        "tool": tool,
        "args": args,
        "code_to_run": code.strip(),
        "note": "Framing/claims removed. Judge only the raw action above.",
    }
