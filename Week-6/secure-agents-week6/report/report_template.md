# Agentic Security Red-Team Report — <SYSTEM NAME>

**Date:** <YYYY-MM-DD>  ·  **Tester:** <NAME>  ·  **Version/commit:** <HASH>
**Model tier(s) tested:** <Tier A/B/C, model strings>

---

## 1. Executive Summary
*(Audience: leadership. Business terms, no jargon.)*

- **Overall risk posture:** <one line — e.g. "Moderate; two high-severity findings remediated, one residual.">
- **Top risks found:** <bullet the 2–4 that matter to the business>
- **Business impact if unaddressed:** <data exposure, financial, compliance, reputational>
- **Residual risk after fixes:** <what remains and why>
- **Recommendations (one line each):** <fund X, adopt Y, monitor Z>

---

## 2. Methodology
*(Audience: engineering + audit. Make it reproducible.)*

- **Tools:** Garak (<probes>), DeepTeam (<ASI suite>), PyRIT (<orchestrators>).
- **Scope:** <which components — supervisor, RAG, code tool, MCP servers>.
- **Out of scope:** <what wasn't tested>.
- **Environment:** <local Ollama, tiers, generations/iterations>.
- **Success criteria:** <what counts as a "hit">.

---

## 3. Findings
*(One block per finding.)*

### Finding <N> — <short title>
- **ASI ID:** ASI<##> — <name>
- **Severity:** <Critical / High / Medium / Low>
- **Reproduction:** <exact prompt/probe + steps>
- **Observed behavior:** <what the system did, with Phoenix trace link>
- **Root cause:** <the missing/weak control>
- **Fix applied:** <defense module + change>
- **Re-test result:** <pass/fail after fix; probe re-run output>

---

## 4. Compliance Mapping

| Finding | OWASP ASI | NIST AI RMF | MITRE ATLAS |
|---------|-----------|-------------|-------------|
| <N>     | ASI<##>   | <function>  | <technique> |

---

## 5. Security Delta (before / after)

| Probe / attack | Baseline | After hardening |
|----------------|----------|-----------------|
| <probe>        | FAIL     | PASS            |

---

## Appendix
- Raw tool outputs: <paths>
- Phoenix trace links: <urls>
- Model/tier matrix: <table>
