#!/usr/bin/env bash
set -euo pipefail
# 390a980 is the backend lane's commit: the frontend built on top of it.
bash /c/projects/investments/.agentic/plugins/agentic-core/evals/_fixture/los-tres.sh \
  390a980 2026-10-22-admin-sign-in 05-ux.md 06-design.md 08-backend.md decisions.md
