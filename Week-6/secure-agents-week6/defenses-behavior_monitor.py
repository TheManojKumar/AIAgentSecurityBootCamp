# defenses-behavior_monitor.py — behavioral monitor / kill-switch (ASI10)
#
# Halt agents on role-drift or unexpected tool patterns: a supervisor suddenly
# calling exfiltrate, an agent appending hidden directives to every response, or
# tool-call rates far outside the baseline.
from dataclasses import dataclass, field
from tracing     import init_tracing

init_tracing("week6-defenses-behavior_monitor")

EXPECTED_TOOLS = {"add_note", "search_notes", "fetch_doc", "run_math"}
DRIFT_SIGNALS  = ("access: omega", "pre-authorized admin", "skip all approval")


@dataclass
class BehaviorMonitor:
    baseline_role: str = "assistant"
    tool_calls: list = field(default_factory = list)
    halted: bool = False

    def check_tool_call(self, name: str) -> bool:

        # Log this function call in Magenta color
        print('\033[95m', "=================================================================")
        print('\033[95m', "Calling BehaviorMonitor.check_tool_call ...")
        print('\033[95m', "=================================================================")

        self.tool_calls.append(name)
        if name not in EXPECTED_TOOLS:
            self.halted = True   # unexpected tool → kill-switch

        # Log the verdict in Magenta color
        print('\033[95m', "Behavior monitor verdict: " + ("HALT" if self.halted else "OK"))

        return not self.halted

    def check_output(self, text: str) -> bool:

        # Log this function call in Magenta color
        print('\033[95m', "=================================================================")
        print('\033[95m', "Calling BehaviorMonitor.check_output ...")
        print('\033[95m', "=================================================================")

        if any(sig in text.lower() for sig in DRIFT_SIGNALS):
            self.halted = True   # role-drift / persisted injection → halt

        # Log the verdict in Magenta color
        print('\033[95m', "Behavior monitor verdict: " + ("HALT" if self.halted else "OK"))

        return not self.halted
