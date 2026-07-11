# defenses/hitl.py — Layer 3: human-in-the-loop gate before code runs
#
# Use LangGraph's interrupt to require human approval for any code-exec call,
# showing the EXACT code. High-blast-radius actions deserve a human checkpoint.
from langgraph.types import interrupt

from docker_sandbox import run_python as sandboxed_exec


def code_gate(state):
    code = state["pending_code"]
    decision = interrupt({"action": "run_python", "code": code,
                          "prompt": "Approve execution of this code? (yes/no)"})
    if decision != "yes":
        return {"messages": [("system", "[Execution denied by human reviewer.]")]}
    return {"messages": [("tool", sandboxed_exec(code))]}
