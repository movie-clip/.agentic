#!/usr/bin/env bash
set -euo pipefail
bash /c/projects/investments/.agentic/plugins/agentic-core/evals/_fixture/corpus-run.sh \
  68cd7fb \
  2026-10-29-s5-5-vehicle-fitment-model/01-recon.md \
  2026-10-29-s5-5-vehicle-fitment-model/02-story.md \
  2026-10-29-s5-5-vehicle-fitment-model/03-design.md \
  2026-10-29-s5-5-vehicle-fitment-model/decisions.md
# Only the specification rulings existed at the build go.
d=agentic/runs/2026-10-29-s5-5-vehicle-fitment-model/decisions.md
awk '/· build go ·/{exit} {print}' "$d" > "$d.tmp" && mv "$d.tmp" "$d"
