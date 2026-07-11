# defenses/allowlist.py — Layer 1: tool allow-listing / least agency
#
# The weather assistant does NOT need file access. Remove read_file from the
# default toolset entirely. If a tool isn't exposed, it can't be misused — no
# matter what the prompt says. This is the "least agency" principle: autonomy
# is earned, not default.
import os
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from langchain_core.tools import tool

llm = ChatOllama(
    model=os.environ.get("ORCHESTRATOR_MODEL", "qwen2.5:3b"),
    base_url=os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434"),
    temperature=0,
)


@tool
def get_weather(city: str) -> str:
    """Return the current weather for a city."""
    return f"{city}: 72F and clear"


SYSTEM = "You are a helpful weather assistant."

# read_file is simply not in the list → both payloads fail (ASI02 prevention).
agent = create_react_agent(llm, tools=[get_weather], prompt=SYSTEM)


if __name__ == "__main__":
    import sys
    user_msg = sys.argv[1] if len(sys.argv) > 1 else "What's the weather in Seattle?"
    print(agent.invoke({"messages": [("user", user_msg)]})["messages"][-1].content)
