# defenses-scoped_tools.py — Layer 4: provenance / least privilege on tools
#
# The supervisor shouldn't even HAVE fetch_doc; only the researcher does, and
# fetch_doc is path-restricted (the Week 1 validation pattern). Even a followed
# instruction can't reach secrets.
import os
from langchain_core.tools import tool
from tracing import init_tracing

init_tracing("week2-defenses-scoped_tools")

CORPUS_ROOT = os.path.realpath("workspace/corpus")


@tool
def fetch_doc(topic: str) -> str:
    """Fetch a document about a topic from the local corpus (path-restricted)."""

    # Log this function call in Red color
    print('\033[31m', "=================================================================")
    print('\033[31m', "Calling fetch_doc (scoped) with input: " + topic)
    print('\033[31m', "=================================================================")

    # Reject traversal like "../secrets/api_keys" before it resolves.
    path = os.path.realpath(f"{CORPUS_ROOT}/{topic}.txt")
    if not path.startswith(CORPUS_ROOT + os.sep):
        return "DENIED: requested document is outside the corpus."
    if not os.path.exists(path):
        return f"NOT FOUND: no corpus document for topic '{topic}'."
    with open(path) as f:
        return f.read()


# Wiring principle: bind fetch_doc ONLY to the researcher agent. The supervisor
# is constructed with no tools, so it cannot fetch anything even if instructed.
