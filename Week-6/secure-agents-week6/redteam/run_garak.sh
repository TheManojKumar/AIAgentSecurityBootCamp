#!/usr/bin/env bash
# Run Garak against the local hardened system's HTTP endpoint.
#
# Usage (all forms work, mix as you like):
#   bash redteam/run_garak.sh                          # default probes, 3 generations
#   bash redteam/run_garak.sh 1                        # generations as a bare number
#   bash redteam/run_garak.sh --generations 1          # ...or as a flag
#   bash redteam/run_garak.sh --probes encoding        # one probe family only
#   PROBES=encoding bash redteam/run_garak.sh 1        # ...or via the environment
# On CPU (Tier C), use 1 generation for a fast sweep.
set -euo pipefail

# promptinject's classes are generated from its rogue strings: HijackHateHumans,
# HijackKillHumans and HijackLongPrompt. The first two are listed here and the
# third is deliberately left out — its prompts are long enough that a single
# request costs minutes on a CPU-tier model (the guard reads the whole prompt,
# then the orchestrator reads it again and answers), and garak gives up on it
# before the system does. garak has no exclusion syntax, so the probes we want
# are named one by one. Put it back with:
#   PROBES=dan,encoding,leakreplay,promptinject bash redteam/run_garak.sh 1
GENERATIONS="${GENERATIONS:-3}"
PROBES="${PROBES:-dan,encoding,leakreplay,promptinject.HijackHateHumans,promptinject.HijackKillHumans}"

while [ $# -gt 0 ]; do
  case "$1" in
    --generations|-g) GENERATIONS="$2"; shift 2 ;;
    --probes|-p)      PROBES="$2";      shift 2 ;;
    [0-9]*)           GENERATIONS="$1"; shift ;;
    *) echo "run_garak.sh: unknown argument '$1' (want: [N] [--generations N] [--probes LIST])" >&2
       exit 2 ;;
  esac
done

python -m garak \
  --model_type rest \
  --generations "${GENERATIONS}" \
  --probes "${PROBES}" \
  -G redteam/rest_config.json
