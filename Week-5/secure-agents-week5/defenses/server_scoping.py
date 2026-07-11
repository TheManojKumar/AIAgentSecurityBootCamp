# defenses/server_scoping.py — Layer 2: least-privilege per server
#
# Each server gets an explicit allow-list of tools the agent may use from it;
# everything else is invisible. 'exfiltrate' is not on the list → never callable,
# even if a description tries to coerce it. This is the durable control.
ALLOWED = {"notes": {"add_note", "search_notes"}}   # 'exfiltrate' absent → uncallable


def scope_tools(all_tools):
    # each tool is expected to carry a `.server` attribute naming its origin
    return [t for t in all_tools
            if t.name in ALLOWED.get(getattr(t, "server", ""), set())]
