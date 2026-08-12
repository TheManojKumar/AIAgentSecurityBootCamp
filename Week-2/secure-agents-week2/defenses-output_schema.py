# defenses-output_schema.py — Layer 3: structured output contracts
#
# Force specialists to return TYPED data, not free text, so instructions have
# nowhere to hide. The supervisor consumes fields (topic, findings, source),
# never a raw prose channel — the exact channel that carried the attack.
from pydantic import BaseModel
from tracing import init_tracing

init_tracing("week2-defenses-output_schema")


class Research(BaseModel):
    topic: str
    findings: list[str]     # bullet facts only — no prose channel for injected commands
    source: str


# Usage sketch: bind the schema to the specialist so it must populate it, then
# the supervisor reads research.findings rather than free text.
#
#   structured_spec = spec.with_structured_output(Research)
#   research: Research = structured_spec.invoke(...)
#   for fact in research.findings:
#       ...  # consume typed facts only
