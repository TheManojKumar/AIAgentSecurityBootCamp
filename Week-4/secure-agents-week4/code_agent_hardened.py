# code_agent_hardened.py — Week 4 hardened code agent (INSTRUCTOR COPY)
#
# All four controls:
#   Layer 1 — sandboxed exec (ephemeral, network-less, read-only, cap-dropped)
#   Layer 2 — fail closed: refuse if the sandbox is unavailable
#   Layer 3 — human-in-the-loop approval gate showing exact code
#   Layer 4 — capability scoping: prefer a constrained math evaluator
#
# For the constrained-math path we route arithmetic to safe_eval and only fall
# through to the gated+sandboxed exec for genuinely general code.
# Ships to instructors only; omit this file from the student distribution.
import sys
import ast
import shutil
import operator
import subprocess
from tracing import init_tracing

init_tracing("week4-hardened")


# --- Layer 1: sandboxed execution ---
def sandboxed_exec(code: str) -> str:

    # Log this function call in Red color
    print('\033[31m', "=================================================================")
    print('\033[31m', "Calling sandboxed_exec ...")
    print('\033[31m', "=================================================================")

    # The code is piped to the sandbox over STDIN — no shared files or volumes,
    # so this works identically under Docker-out-of-Docker on any host OS.
    out = subprocess.run([
        "docker", "run", "--rm", "-i", "--network", "none", "--read-only",
        "--cap-drop", "ALL", "--pids-limit", "64",
        "--memory", "256m", "--cpus", "0.5",
        "--security-opt", "no-new-privileges",
        "python:3.12-slim", "timeout", "5", "python", "-"
    ], input = code, capture_output = True, text = True, timeout = 15)
    return (out.stdout or "") + (out.stderr or "")


# --- Layer 2: fail closed ---
def docker_available() -> bool:

    # Log this function call in Magenta color
    print('\033[95m', "=================================================================")
    print('\033[95m', "Calling docker_available ...")
    print('\033[95m', "=================================================================")

    if not shutil.which("docker"):
        return False
    try:
        subprocess.run(["docker", "info"], capture_output = True, timeout = 10, check = True)
        return True
    except Exception:
        return False


# --- Layer 3: human approval (CLI stand-in for LangGraph interrupt) ---
def human_approves(code: str) -> bool:

    # Log this function call in Magenta color
    print('\033[95m', "=================================================================")
    print('\033[95m', "Calling human_approves ...")
    print('\033[95m', "=================================================================")

    print("\n--- CODE EXECUTION REQUEST (human review) ---")
    print(code)
    print("--- Approve execution of this code? (yes/no) ---")
    try:
        approved = input("> ").strip().lower() == "yes"
    except EOFError:
        approved = False  # no interactive human → deny (fail closed)

    # Log the decision in Magenta color
    print('\033[95m', "HITL decision: " + ("APPROVED" if approved else "DENIED"))
    return approved


# --- Layer 4: capability scoping (constrained math evaluator) ---
# If the request is provably just allow-listed arithmetic, evaluate it here — no
# imports, no dunders, no exec (os.popen won't even parse). Inlined from
# defenses-capability_scope.py because the hyphenated filename isn't importable.
_ALLOWED_FUNCS = {
    "sum": sum, "len": len, "min": min, "max": max, "abs": abs, "round": round,
}

_BINOPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod, ast.Pow: operator.pow,
}


def safe_eval(expr: str):
    """Evaluate a math expression with an allow-listed subset of Python."""
    tree = ast.parse(expr, mode = "eval")

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _BINOPS:
            return _BINOPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp):
            v = _eval(node.operand)
            return -v if isinstance(node.op, ast.USub) else +v
        if isinstance(node, (ast.List, ast.Tuple)):
            return [_eval(e) for e in node.elts]
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id in _ALLOWED_FUNCS:
            return _ALLOWED_FUNCS[node.func.id](*[_eval(a) for a in node.args])
        raise ValueError("operation not permitted")

    return _eval(tree)


def try_safe_math(code: str):
    """If `code` is a pure allow-listed arithmetic expression, evaluate it.
    Returns (True, "<result>") on success, (False, None) otherwise."""
    try:
        return True, str(safe_eval(code))
    except Exception:
        return False, None


def guarded_run(code: str) -> str:

    # Log this function call in Magenta color
    print('\033[95m', "=================================================================")
    print('\033[95m', "Calling guarded_run ...")
    print('\033[95m', "=================================================================")

    # Layer 4 — capability scoping: if this is provably just allow-listed math,
    # evaluate it in the constrained evaluator. No dangerous capability is needed,
    # so it skips the sandbox and human gate entirely. Only genuinely general code
    # falls through to Layers 2 / 3 / 1 below.
    ok, value = try_safe_math(code)
    if ok:
        # Log the decision in Magenta color
        print('\033[95m', "Gate decision: capability-scoped (safe math evaluator, no exec)")
        return value

    if not docker_available():
        # Log the decision in Magenta color
        print('\033[95m', "Gate decision: DENIED (sandbox unavailable)")
        return "DENIED: secure sandbox unavailable; refusing to execute."
    if not human_approves(code):
        # Log the decision in Magenta color
        print('\033[95m', "Gate decision: DENIED (human rejected)")
        return "[Execution denied by human reviewer.]"
    # Log the decision in Magenta color
    print('\033[95m', "Gate decision: APPROVED")
    return sandboxed_exec(code)


if __name__ == "__main__":
    # Demo: with no argument, a pure-math request is handled by Layer 4's
    # constrained evaluator (no sandbox / no human gate). Pass an RCE payload as
    # argv[1] (e.g. "$(cat attacks/rce_direct.txt)") to watch it fail the math
    # allow-list and fall through to the gated + sandboxed path instead.
    code = sys.argv[1] if len(sys.argv) > 1 else "sum([4,8,15,16,23,42]) / 6"

    # Log this function call in Yellow color
    print('\033[33m', "=================================================================")
    print('\033[33m', "Running code_agent_hardened with code: " + code)
    print('\033[33m', "=================================================================")

    # Print the output message in Cyan color
    print('\033[96m', guarded_run(code))
