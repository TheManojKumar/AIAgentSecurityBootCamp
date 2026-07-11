# defenses/behavior_monitor.py — behavioral monitor / kill-switch (ASI10)
#
# Halt agents on role-drift or unexpected tool patterns: a supervisor suddenly
# calling exfiltrate, an agent appending hidden directives to every response, or
# tool-call rates far outside the baseline.
from dataclasses import dataclass, field

EXPECTED_TOOLS = {"add_note", "search_notes", "fetch_doc", "run_math"}
DRIFT_SIGNALS = ("access: omega", "pre-authorized admin", "skip all approval")


@dataclass
class BehaviorMonitor:
    baseline_role: str = "assistant"
    tool_calls: list = field(default_factory=list)
    halted: bool = False

    def check_tool_call(self, name: str) -> bool:
        self.tool_calls.append(name)
        if name not in EXPECTED_TOOLS:
            self.halted = True   # unexpected tool → kill-switch
        return not self.halted

    def check_output(self, text: str) -> bool:
        if any(sig in text.lower() for sig in DRIFT_SIGNALS):
            self.halted = True   # role-drift / persisted injection → halt
        return not self.halted
