# redteam/run_deepteam.py — DeepTeam OWASP-ASI-aligned attack suite
#
# Points DeepTeam's agentic red-teaming at the local HTTP endpoint. DeepTeam
# maps findings to ASI IDs automatically; this script prints which ASIs come
# back green vs weak. (API surface is illustrative — adjust to the installed
# deepteam version.)
import json
import urllib.request

TARGET = "http://localhost:8000/"


def model_callback(prompt: str) -> str:
    payload = json.dumps({"prompt": prompt}).encode()
    req = urllib.request.Request(TARGET, data=payload,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read()).get("response", "")


def main():
    try:
        from deepteam import red_team
        from deepteam.vulnerabilities import PromptLeakage, ExcessiveAgency
        from deepteam.attacks import PromptInjection
    except Exception as e:
        print(f"[deepteam] import/version mismatch: {e}")
        print("Adjust imports to your installed deepteam version; concept is unchanged.")
        return

    risk = red_team(
        model_callback=model_callback,
        vulnerabilities=[PromptLeakage(), ExcessiveAgency()],
        attacks=[PromptInjection()],
    )
    print(risk)


if __name__ == "__main__":
    main()
