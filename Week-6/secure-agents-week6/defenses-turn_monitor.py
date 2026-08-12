# defenses-turn_monitor.py — conversation-level state monitoring
#
# PyRIT's multi-turn escalation gets further than any single prompt. Track state
# across turns and flag drift: repeated refusals being probed, escalating
# sensitivity, or a request that only becomes dangerous in the context of prior
# turns.
from dataclasses import dataclass, field
from tracing import init_tracing

init_tracing("week6-defenses-turn_monitor")

ESCALATION_MARKERS = ("ignore your", "for the audit", "pre-authorized",
                      "confirm you can ignore", "print the contents of any secrets")


@dataclass
class TurnMonitor:
    history: list = field(default_factory=list)
    suspicion: int = 0

    def observe(self, user_text: str) -> bool:
        """Return True if the conversation should be halted for review."""

        # Log this function call in Magenta color
        print('\033[95m', "=================================================================")
        print('\033[95m', "Calling TurnMonitor.observe ...")
        print('\033[95m', "=================================================================")

        self.history.append(user_text)
        lowered = user_text.lower()
        if any(m in lowered for m in ESCALATION_MARKERS):
            self.suspicion += 2
        # slow-boil: many turns nudging at boundaries
        if len(self.history) >= 3 and self.suspicion >= 1:
            self.suspicion += 1
        halt = self.suspicion >= 3

        # Log the verdict in Magenta color
        print('\033[95m', "Turn monitor verdict: " + ("HALT" if halt else "CONTINUE"))

        return halt
