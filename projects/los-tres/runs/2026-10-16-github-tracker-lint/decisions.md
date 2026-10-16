# Decisions — 2026-10-16-github-tracker-lint

## D-1 · verify · 2026-10-16
- **Asked:** protocol-lint failed twice (01, 02); a third round on the F1/F2 lineage exceeds the two-round cap (gates.md § 4), and spent 2 reached twice the original budget 1. Run a third lint round after the F6/F7 fixes?
- **Ruling (owner's words):** "Go"
- **Effect:** budget raised 2 → 3 for one re-lint (03) of orchestrator.md § 7 and los-tres phases.md.

## D-2 · verify · 2026-10-16
- **Asked:** check_network_edit.py reports projects/los-tres/project.md has no passing protocol-lint artifact (03 judged only orchestrator.md § 7 and phases.md). Run a one-file lint (04), past budget 3?
- **Ruling (owner's words):** "Yes, do what needs to be done"
- **Effect:** budget raised 3 → 4 for one lint (04) of projects/los-tres/project.md.
