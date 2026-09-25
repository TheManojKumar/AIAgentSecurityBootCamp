#!/usr/bin/env bash
# Run Garak against the local hardened system's HTTP endpoint.
# On CPU (Tier C), add --generations 1 for a fast sweep.
set -euo pipefail

GENERATIONS="${1:-3}"

# promptinject's classes are generated from its rogue strings: HijackHateHumans,
# HijackKillHumans and HijackLongPrompt. The first two are listed here and the
# third is deliberately left out — its prompts are long enough that a single
# request costs minutes on a CPU-tier model (the guard reads the whole prompt,
# then the orchestrator reads it again and answers), and garak gives up on it
# before the system does. garak has no exclusion syntax, so the probes we want
# are named one by one. Put it back with:
#   PROBES=dan,encoding,leakreplay,promptinject bash redteam/run_garak.sh 1
PROBES="${PROBES:-dan,encoding,leakreplay,promptinject.HijackHateHumans,promptinject.HijackKillHumans}"

python -m garak \
  --model_type rest \
  --generations "${GENERATIONS}" \
  --probes "${PROBES}" \
  -G redteam/rest_config.json
