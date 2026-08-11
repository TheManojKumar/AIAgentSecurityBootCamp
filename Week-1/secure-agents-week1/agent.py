# agent.py — Week 1 vulnerable baseline
#
# A single tool-calling agent with two tools: a safe one (get_weather) and a
# deliberately sensitive one (read_file) with NO validation. This is the
# baseline students attack in Part B before hardening it in Part C.
import os
from langgraph.prebuilt     import create_react_agent
from langchain_ollama       import ChatOllama
from langchain_core.tools   import tool
from tracing                import init_tracing

init_tracing("week1")

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


@tool
def read_file(path: str) -> str:
    """Read a file from the agent's workspace."""   # the 'sensitive' tool

    # Log this function call in Red color
    print('\33[31m', "=================================================================")
    print('\33[31m', "Calling read_file with input: " + path)
    print('\33[31m', "=================================================================")

    with open(path) as f:                     # NOTE: no validation — that's the point
        return f.read()


SYSTEM = "You are a helpful weather assistant."

agent = create_react_agent(llm, tools=[get_weather, read_file], prompt=SYSTEM)


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
