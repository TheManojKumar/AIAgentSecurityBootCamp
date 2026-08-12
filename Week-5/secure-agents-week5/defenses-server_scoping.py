# defenses-server_scoping.py — Layer 2: least-privilege per server
#
# Each server gets an explicit allow-list of tools the agent may use from it;
# everything else is invisible. 'exfiltrate' is not on the list → never callable,
# even if a description tries to coerce it. This is the durable control.
from tracing import init_tracing

init_tracing("week5-defenses-server_scoping")

ALLOWED = {"notes": {"add_note", "search_notes"}}   # 'exfiltrate' absent → uncallable


def scope_tools(all_tools):

    # Log this function call in Magenta color
    print('\033[95m', "=================================================================")
    print('\033[95m', "Calling scope_tools ...")
    print('\033[95m', "=================================================================")

    # each tool is expected to carry a `.server` attribute naming its origin
    return [t for t in all_tools
            if t.name in ALLOWED.get(getattr(t, "server", ""), set())]
