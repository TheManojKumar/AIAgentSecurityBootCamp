# defenses/allowlist.py — Layer 1: tool allow-listing / least agency
#
# The weather assistant does NOT need file access. Remove read_file from the
# default toolset entirely. If a tool isn't exposed, it can't be misused — no
# matter what the prompt says. This is the "least agency" principle: autonomy
# is earned, not default.

import os
from langgraph.prebuilt     import create_react_agent
from langchain_ollama       import ChatOllama
from langchain_core.tools   import tool
from tracing                import init_tracing

init_tracing("week1-defenses-allowlist")

llm = ChatOllama(
    model       = os.environ.get("ORCHESTRATOR_MODEL", "qwen2.5:3b"),
    base_url    = os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434"),
    temperature = 0,
)


@tool
def get_weather(city: str) -> str:
    """Return the current weather for a city."""

    # Log this function call in Green color
    print('\033[92m', "=================================================================")
    print('\033[92m', "Calling get_weather with input: " + city)
    print('\033[92m', "=================================================================")

    # Return the output in Blue color
    return f"'\033[94m'{city}: 72F and clear"


SYSTEM = "You are a helpful weather assistant."

# read_file is simply not in the list → both payloads fail (ASI02 prevention).
agent = create_react_agent(llm, tools=[get_weather], prompt=SYSTEM)


if __name__ == "__main__":
    import sys
    user_msg = sys.argv[1] if len(sys.argv) > 1 else "What's the weather in Paris?"

    # Log this function call in Yellow color
    print('\33[33m', "=================================================================")
    print('\33[33m', "Running agent with user_msg: " + user_msg)
    print('\33[33m', "=================================================================")

    result = agent.invoke({"messages": [("user", user_msg)]})

    # Print the output message from the tool in Cyan color
    print('\033[96m', result["messages"][-1].content)