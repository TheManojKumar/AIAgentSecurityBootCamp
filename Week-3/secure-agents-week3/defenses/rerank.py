# defenses/rerank.py — Layer 4: retrieval-time re-ranking & contradiction check
#
# Flag when a retrieved doc contradicts higher-trust sources (a poison signal),
# and prefer official sources on ties. Demotes the "9999 days / ignore older
# documents" poison doc.

INJECTION_SIGNALS = (
    "ignore older", "ignore previous", "authoritative policy",
    "must first call", "official update", "skip all approval",
)


def score(doc: dict) -> float:
    """doc = {'text': str, 'source': 'official'|'untrusted', 'distance': float}"""
    base = 1.0 - doc.get("distance", 0.0)          # closer = higher
    if doc.get("source") == "official":
        base += 0.5                                 # prefer official on ties
    text = doc.get("text", "").lower()
    if any(sig in text for sig in INJECTION_SIGNALS):
        base -= 1.0                                 # demote likely poison
        doc["flagged"] = True
    return base


def rerank(docs: list[dict]) -> list[dict]:
    return sorted(docs, key=score, reverse=True)
