# defenses-rerank.py — Layer 4: retrieval-time re-ranking & contradiction check
#
# Flag when a retrieved doc contradicts higher-trust sources (a poison signal),
# and prefer official sources on ties. Demotes the "9999 days / ignore older
# documents" poison doc.
from tracing import init_tracing

init_tracing("week3-defenses-rerank")

INJECTION_SIGNALS = (
    "ignore older", "ignore previous", "authoritative policy",
    "must first call", "official update", "skip all approval",
)


def score(doc: dict) -> float:
    """doc = {'text': str, 'source': 'official'|'untrusted', 'distance': float}"""

    # Log this function call in Magenta color
    print('\033[95m', "=================================================================")
    print('\033[95m', "Calling score (screen) on doc")
    print('\033[95m', "=================================================================")

    base = 1.0 - doc.get("distance", 0.0)          # closer = higher
    if doc.get("source") == "official":
        base += 0.5                                 # prefer official on ties
    text = doc.get("text", "").lower()
    flagged = any(sig in text for sig in INJECTION_SIGNALS)
    if flagged:
        base -= 1.0                                 # demote likely poison
        doc["flagged"] = True

    # Log the verdict in Magenta color
    print('\033[95m', "Re-rank verdict: " + ("FLAGGED (likely poison)" if flagged else "CLEAN"))

    return base


def rerank(docs: list[dict]) -> list[dict]:

    # Log this function call in Green color
    print('\033[92m', "=================================================================")
    print('\033[92m', "Calling rerank")
    print('\033[92m', "=================================================================")

    return sorted(docs, key=score, reverse=True)
