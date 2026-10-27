#!/usr/bin/env bash
set -euo pipefail
# b06aa51 adds the approved story; nothing of the build exists yet.
bash /c/projects/investments/.agentic/plugins/agentic-core/evals/_fixture/los-tres.sh \
  b06aa51 2026-10-22-admin-sign-in 05-ux.md 06-design.md 07-recon.md decisions.md
