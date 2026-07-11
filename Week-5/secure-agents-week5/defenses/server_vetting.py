# defenses/server_vetting.py — Layer 3: server vetting & pinning (supply-chain hygiene)
#
# Only connect to servers from a vetted manifest with pinned versions/hashes;
# reject unknown servers and unexpected tool sets (tool drift).

class Untrusted(Exception):
    pass


class ToolDrift(Exception):
    pass


MANIFEST = {
    "notes": {"sha256": "abc123...", "expected_tools": {"add_note", "search_notes"}},
}


def verify_server(name, advertised_tools):
    if name not in MANIFEST:
        raise Untrusted(name)
    advertised = {t.name for t in advertised_tools}
    if advertised - MANIFEST[name]["expected_tools"]:
        raise ToolDrift(name)   # server added unexpected tools → reject
    return True
