# team.py — Week 2 vulnerable baseline
#
# A LangGraph supervisor routing to a researcher (fetches "documents" from a
# local mock corpus) and a writer (summarizes for the user). The supervisor
# trusts research content IMPLICITLY — that unguarded trust boundary is the
# vulnerability students exploit in Part B.
import os
import sys
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from tracing import init_tracing

init_tracing("week2")

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434")

llm = ChatOllama(model=os.environ.get("ORCHESTRATOR_MODEL", "qwen2.5:3b"),
                 base_url=OLLAMA_HOST, temperature=0)
spec = ChatOllama(model=os.environ.get("SPECIALIST_MODEL", "llama3.2:3b"),
                  base_url=OLLAMA_HOST, temperature=0)


@tool
def fetch_doc(topic: str) -> str:
    """Fetch a document about a topic from the local corpus."""

    # Log this function call in Red color
    print('\033[31m', "=================================================================")
    print('\033[31m', "Calling fetch_doc with input: " + topic)
    print('\033[31m', "=================================================================")

    path = f"workspace/corpus/{topic}.txt"
    with open(path) as f:
        return f.read()        # returns whatever the doc says — including injected text


def researcher(state: MessagesState):

    # Log this function call in Green color
    print('\033[92m', "=================================================================")
    print('\033[92m', "Calling researcher")
    print('\033[92m', "=================================================================")

    # specialist reads the topic doc and returns the raw content upward
    out = spec.invoke(state["messages"] + [("system", "Research the topic; return what you find.")])
    return {"messages": [out]}


def supervisor(state: MessagesState):

    # Log this function call in Blue color
    print('\033[94m', "=================================================================")
    print('\033[94m', "Calling supervisor")
    print('\033[94m', "=================================================================")

    # VULNERABLE: trusts research content implicitly, may follow instructions inside it
    out = llm.invoke(state["messages"] + [("system",
          "You are the supervisor. Use the research to fulfill the user's request.")])
    return {"messages": [out]}


def writer(state: MessagesState):

    # Log this function call in Bright-Yellow color
    print('\033[93m', "=================================================================")
    print('\033[93m', "Calling writer")
    print('\033[93m', "=================================================================")

    out = llm.invoke(state["messages"] + [("system",
          "Write a concise summary for the user based on the research above.")])
    return {"messages": [out]}


g = StateGraph(MessagesState)
g.add_node("supervisor", supervisor)
g.add_node("researcher", researcher)
g.add_node("writer", writer)
g.add_edge(START, "researcher")
g.add_edge("researcher", "supervisor")
g.add_edge("supervisor", "writer")
g.add_edge("writer", END)
team = g.compile()


if __name__ == "__main__":
    user_msg = sys.argv[1] if len(sys.argv) > 1 else \
        "Summarize what the corpus says about solar power."

    # Log this function call in Yellow color
    print('\033[33m', "=================================================================")
    print('\033[33m', "Running team with user_msg: " + user_msg)
    print('\033[33m', "=================================================================")

    result = team.invoke({"messages": [("user", user_msg)]})

    # Print the output message in Cyan color
    print('\033[96m', result["messages"][-1].content)
