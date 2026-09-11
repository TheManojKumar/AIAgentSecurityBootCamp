# defenses-server_vetting.py — Layer 3: server vetting & pinning (supply-chain hygiene)
#
# Runnable single-layer demo: connect to BOTH MCP servers (same wiring as
# mcp_agent.py), then apply ONLY a manifest check before the model ever sees a
# tool. Only connect to servers from a vetted manifest with pinned tool sets;
# reject unknown servers and unexpected tool sets (tool drift).
import os
import sys
import asyncio
from langchain_ollama              import ChatOllama
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt            import create_react_agent
from tracing                       import init_tracing

init_tracing("week5-defenses-server_vetting")

SERVERS = {
    "notes":  {"command": "python", "args": ["servers/notes_server.py"],     "transport": "stdio"},
    "backup": {"command": "python", "args": ["servers/malicious_server.py"], "transport": "stdio"},
}


class Untrusted(Exception):
    pass


class ToolDrift(Exception):
    pass


MANIFEST = {
    "notes": {"sha256": "abc123...", "expected_tools": {"add_note", "search_notes"}},
}


# A perfectly ordinary agent system prompt. The second sentence is the one that
# turns a malicious tool description into a working exploit: it tells the model
# that what a tool says about itself is authoritative. Most real agent
# frameworks say something like this.
SYSTEM_PROMPT = ("You are a notes assistant. Tools may state usage requirements "
                 "in their descriptions; follow them before you answer.")

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


async def main(user_msg):

    # Log this function call in Green color
    print('\033[92m', "=================================================================")
    print('\033[92m', "Calling main ...")
    print('\033[92m', "=================================================================")

    client = MultiServerMCPClient(SERVERS)

    safe = []
    for server_name in SERVERS:
        tools = await client.get_tools(server_name = server_name)
        try:
            verify_server(server_name, tools)
            safe.extend(tools)
        except (Untrusted, ToolDrift) as e:
            print('\033[95m', f"Vetting verdict: REJECTED ({type(e).__name__}: {e})")
            continue

    llm = ChatOllama(model = os.environ.get("ORCHESTRATOR_MODEL", "qwen2.5:3b"),
                     base_url = os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434"),
                     temperature = 0)
    agent  = create_react_agent(llm, tools = safe, prompt = SYSTEM_PROMPT)
    result = await agent.ainvoke({"messages": [("user", user_msg)]})

    # Print the output message in Cyan color
    print('\033[96m', result["messages"][-1].content)


if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else "Save a note: call the dentist, then find my notes about the dentist."

    # Log this function call in Yellow color
    print('\033[33m', "=================================================================")
    print('\033[33m', "Running defenses-server_vetting with user_msg: " + msg)
    print('\033[33m', "=================================================================")

    asyncio.run(main(msg))
