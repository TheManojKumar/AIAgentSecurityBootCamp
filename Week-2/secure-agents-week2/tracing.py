"""Phoenix tracing auto-configuration (shared across weeks)."""
import os


def init_tracing(project_name: str = "week2"):
    try:
        from phoenix.otel import register
        endpoint = os.environ.get("PHOENIX_COLLECTOR_ENDPOINT")
        kwargs = {"project_name": project_name, "auto_instrument": True}
        if endpoint:
            kwargs["endpoint"] = endpoint
        return register(**kwargs)
    except Exception as e:
        print(f"[tracing] Phoenix not initialised ({e}); continuing without traces.")
        return None
