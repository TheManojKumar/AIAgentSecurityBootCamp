# mcp_agent.py — Week 5 baseline
#
# An agent that connects to a local MCP server via MultiServerMCPClient and uses
# its tools. When you add the malicious server (see the vulnerable config
# below), tool names AND descriptions enter the model's context — so a poisoned
# description can hijack behavior, and a hidden tool can exfiltrate.
import os
import sys
import asyncio
from langchain_ollama import ChatOllama
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from tracing import init_tracing

init_tracing("week5")

# VULNERABLE CONFIG: both the legitimate notes server AND the malicious server
# are trusted with identical wiring — the only difference is trust.
SERVERS = {
    "notes": {"command": "python", "args": ["/servers/notes_server.py"], "transport": "stdio"},
    # Uncomment to run the attack in Part B:
    # "backup": {"command": "python", "args": ["/servers/malicious_server.py"], "transport": "stdio"},
}


async def main(user_msg):
    client = MultiServerMCPClient(SERVERS)
    tools = await client.get_tools()      # tool names + DESCRIPTIONS enter the context here
    llm = ChatOllama(model=os.environ.get("ORCHESTRATOR_MODEL", "qwen2.5:3b"),
                     base_url=os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434"),
                     temperature=0)
    agent = create_react_agent(llm, tools=tools, prompt="You are a notes assistant.")
    result = await agent.ainvoke({"messages": [("user", user_msg)]})
    print(result["messages"][-1].content)


if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else "Save a note: buy milk."
    asyncio.run(main(msg))
