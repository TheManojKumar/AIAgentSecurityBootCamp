"""Phoenix tracing auto-configuration.

Import init_tracing() at the top of any agent entrypoint to get automatic
LangChain/LangGraph instrumentation. No manual span code required.
"""


def init_tracing(project_name: str = "week6"):
    try:
        from phoenix.otel import register
        from openinference.instrumentation.langchain import LangChainInstrumentor

        tracer_provider = register(project_name = project_name)
        LangChainInstrumentor().instrument(tracer_provider = tracer_provider)
        return tracer_provider
    except Exception as e:
        import traceback
        print(f"[tracing] Phoenix not initialised ({e}); continuing without traces.")
        traceback.print_exc()
        return None
