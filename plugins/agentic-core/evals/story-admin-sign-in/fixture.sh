#!/usr/bin/env bash
set -euo pipefail
bash /c/projects/investments/.agentic/plugins/agentic-core/evals/_fixture/los-tres.sh \
  46fc5a5 2026-10-22-admin-sign-in 01-recon.md 02-delivery-brief.md decisions.md
# Only the framing rulings existed when the story was first drafted.
d=agentic/runs/eval-2026-10-22-admin-sign-in/decisions.md
awk '/· specification ·/{exit} {print}' "$d" > "$d.tmp" && mv "$d.tmp" "$d"
