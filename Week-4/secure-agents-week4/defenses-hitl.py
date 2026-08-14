# defenses-hitl.py — Layer 3: human-in-the-loop gate before code runs
#
# Use LangGraph's interrupt to require human approval for any code-exec call,
# showing the EXACT code. High-blast-radius actions deserve a human checkpoint.
from langgraph.types import interrupt
from tracing         import init_tracing

from docker_sandbox import run_python as sandboxed_exec

init_tracing("week4-defenses-hitl")


def code_gate(state):

    # Log this function call in Magenta color
    print('\033[95m', "=================================================================")
    print('\033[95m', "Calling code_gate (human-in-the-loop) ...")
    print('\033[95m', "=================================================================")

    code = state["pending_code"]
    decision = interrupt({"action": "run_python", "code": code,
                          "prompt": "Approve execution of this code? (yes/no)"})

    # Log the decision in Magenta color
    print('\033[95m', "HITL decision: " + ("APPROVED" if decision == "yes" else "DENIED"))

    if decision != "yes":
        return {"messages": [("system", "[Execution denied by human reviewer.]")]}
    return {"messages": [("tool", sandboxed_exec(code))]}
