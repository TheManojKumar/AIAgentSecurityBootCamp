# defenses-server_vetting.py — Layer 3: server vetting & pinning (supply-chain hygiene)
#
# Only connect to servers from a vetted manifest with pinned versions/hashes;
# reject unknown servers and unexpected tool sets (tool drift).
from tracing import init_tracing

init_tracing("week5-defenses-server_vetting")


class Untrusted(Exception):
    pass


class ToolDrift(Exception):
    pass


MANIFEST = {
    "notes": {"sha256": "abc123...", "expected_tools": {"add_note", "search_notes"}},
}


def verify_server(name, advertised_tools):

    # Log this function call in Magenta color
    print('\033[95m', "=================================================================")
    print('\033[95m', "Calling verify_server ...")
    print('\033[95m', "=================================================================")

    if name not in MANIFEST:
        raise Untrusted(name)
    advertised = {t.name for t in advertised_tools}
    if advertised - MANIFEST[name]["expected_tools"]:
        raise ToolDrift(name)   # server added unexpected tools → reject

    # Log the verdict in Magenta color
    print('\033[95m', "Vetting verdict: SAFE")

    return True
