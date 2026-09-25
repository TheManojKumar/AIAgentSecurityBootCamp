# redteam/run_deepteam.py — DeepTeam agentic attack suite, run fully locally
#
# Points DeepTeam's red-teaming at the local HTTP endpoint. DeepTeam needs two
# models of its own besides the target: a SIMULATOR that writes the attacks and
# an EVALUATOR that judges the answers. Both default to OpenAI, which would send
# this lab's traffic off the machine and fail without an API key — so both are
# pointed at the same local Ollama the system under test uses.
import json
import os
import urllib.request

# Opt out of the telemetry both packages ship, before importing either of them.
os.environ.setdefault("DEEPTEAM_TELEMETRY_OPT_OUT", "YES")
os.environ.setdefault("DEEPEVAL_TELEMETRY_OPT_OUT", "YES")

# The compose service name, not localhost: this script runs in its own container
# (`docker compose run`), where localhost is that container and nothing is
# listening on it. Override with TARGET_URL to point somewhere else.
TARGET       = os.environ.get("TARGET_URL", "http://agent:8000/")
OLLAMA_HOST  = os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434")
ATTACK_MODEL = os.environ.get("ATTACK_MODEL", "llama3.2:1b")
JUDGE_MODEL  = os.environ.get("GUARD_MODEL", "qwen2.5:3b")


def model_callback(prompt: str) -> str:
    payload = json.dumps({"prompt": prompt}).encode()
    req = urllib.request.Request(TARGET, data = payload,
                                 headers = {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout = 300) as r:
        return json.loads(r.read()).get("response", "")


def main():

    # Log this function call in Yellow color
    print('\033[33m', "=================================================================")
    print('\033[33m', f"Running DeepTeam against {TARGET}")
    print('\033[33m', f"attacker: {ATTACK_MODEL}   judge: {JUDGE_MODEL}   via {OLLAMA_HOST}")
    print('\033[33m', "=================================================================")

    from deepeval.models import OllamaModel
    from deepteam import red_team
    from deepteam.vulnerabilities import PromptLeakage, ExcessiveAgency
    from deepteam.attacks.single_turn import PromptInjection

    simulator = OllamaModel(model = ATTACK_MODEL, base_url = OLLAMA_HOST, temperature = 0)
    evaluator = OllamaModel(model = JUDGE_MODEL,  base_url = OLLAMA_HOST, temperature = 0)

    risk = red_team(
        model_callback   = model_callback,
        vulnerabilities  = [PromptLeakage(), ExcessiveAgency()],
        attacks          = [PromptInjection()],
        simulator_model  = simulator,
        evaluation_model = evaluator,
        # Sequential: one small local model serves the attacker, the judge AND the
        # system under test. Ten concurrent attacks would queue behind each other
        # at best, and take the Ollama runner down at worst.
        async_mode       = False,
        max_concurrent   = 1,
    )

    # Print the output message in Cyan color
    print('\033[96m', risk)


if __name__ == "__main__":
    main()
