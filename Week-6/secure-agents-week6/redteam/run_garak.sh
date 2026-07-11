#!/usr/bin/env bash
# Run Garak against the local hardened system's HTTP endpoint.
# On CPU (Tier C), add --generations 1 for a fast sweep.
set -euo pipefail

GENERATIONS="${1:-3}"

python -m garak \
  --model_type rest \
  --generations "${GENERATIONS}" \
  --probes promptinject,leakreplay,encoding,dan \
  -G redteam/rest_config.json
