# defenses-capability_scope.py — Layer 4: capability scoping & allow-listed ops
#
# If the real need is "math," don't grant "arbitrary Python." Offer a
# constrained evaluator (no imports, no dunders, AST-allow-listed) instead of
# exec. os.popen won't even parse. Right tool for the job beats sandboxing the
# wrong tool.
import ast
import operator
from tracing import init_tracing

init_tracing("week4-defenses-capability_scope")

# Only these AST node types are permitted — no Import, Call to arbitrary names,
# Attribute access (dunders), etc.
_ALLOWED_NODES = (
    ast.Expression, ast.Module, ast.Expr,
    ast.BinOp, ast.UnaryOp, ast.Num, ast.Constant,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
    ast.USub, ast.UAdd,
    ast.List, ast.Tuple, ast.Load,
)

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

    # Log this function call in Magenta color
    print('\033[95m', "=================================================================")
    print('\033[95m', "Calling safe_eval ...")
    print('\033[95m', "=================================================================")

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


def run_math(expr: str) -> str:

    # Log this function call in Magenta color
    print('\033[95m', "=================================================================")
    print('\033[95m', "Calling run_math ...")
    print('\033[95m', "=================================================================")

    try:
        result = str(safe_eval(expr))
        # Log the verdict in Magenta color
        print('\033[95m', "Capability-scope verdict: ALLOWED")
        return result
    except Exception as e:
        # Log the verdict in Magenta color
        print('\033[95m', "Capability-scope verdict: DENIED")
        return f"DENIED: {e}"


if __name__ == "__main__":

    # Log this function call in Yellow color
    print('\033[33m', "=================================================================")
    print('\033[33m', "Running capability_scope demo ...")
    print('\033[33m', "=================================================================")

    # Print the output message in Cyan color
    print('\033[96m', run_math("sum([4,8,15,16,23,42]) / 6"))          # allowed
    print('\033[96m', run_math("__import__('os').popen('id').read()"))  # DENIED
