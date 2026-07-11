# code_agent.py — Week 4 vulnerable baseline
#
# An agent given a run_python tool that naively executes model-written code
# IN-PROCESS (the unsafe pattern frameworks shipped). Prompt injection plus this
# tool equals an unauthenticated shell inside the container. Students see the
# RCE happen in Part B, then contain it in Part C.
import os
import sys
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from tracing import init_tracing

init_tracing("week4")

llm = ChatOllama(model=os.environ.get("ORCHESTRATOR_MODEL", "qwen2.5:3b"),
                 base_url=os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434"),
                 temperature=0)


@tool
def run_python(code: str) -> str:
    """Execute Python code to help answer data/analysis questions."""
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(code, {})           # <-- the vulnerability: arbitrary exec, no isolation
    return buf.getvalue()


agent = create_react_agent(llm, tools=[run_python],
    prompt="You are a data analysis assistant. Use run_python for calculations.")


if __name__ == "__main__":
    user_msg = sys.argv[1] if len(sys.argv) > 1 else \
        "What's the standard deviation of [4, 8, 15, 16, 23, 42]?"
    print(agent.invoke({"messages": [("user", user_msg)]})["messages"][-1].content)
