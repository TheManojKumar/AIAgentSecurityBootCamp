"""Phoenix tracing auto-configuration.

Import init_tracing() at the top of any agent entrypoint to get automatic
LangChain/LangGraph instrumentation. No manual span code required.
"""
import os


def init_tracing(project_name: str = "week1"):
    """Register Phoenix tracing with auto-instrumentation.

    auto_instrument=True hooks LangChain/LangGraph automatically, so every
    model call and tool call shows up in the Phoenix span tree at
    http://localhost:6006 with no further code.
    """
    try:
        from phoenix.otel import register
        endpoint = os.environ.get("PHOENIX_COLLECTOR_ENDPOINT")
        kwargs = {"project_name": project_name, "auto_instrument": True}
        if endpoint:
            kwargs["endpoint"] = endpoint
        return register(**kwargs)
    except Exception as e:  # tracing is best-effort; never block the lab on it
        print(f"[tracing] Phoenix not initialised ({e}); continuing without traces.")
        return None
