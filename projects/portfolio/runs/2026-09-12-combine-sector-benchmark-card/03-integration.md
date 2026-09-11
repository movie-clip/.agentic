REPORT 2026-09-12-combine-sector-benchmark-card/03
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd apps/desktop && npx vitest run ; cd apps/desktop && npx tsc --noEmit ; python scripts/detect_deadcode.py --strict
  result:    PASS
  detail:    vitest: 43 files / 390 tests passed, 0 failed. tsc --noEmit: exited clean, no output. detect_deadcode.py --strict: ruff clean, vulture clean, knip clean, "STRICT: no dead-code findings — clean." No drift in apps/desktop/src/test/dashboardGoldens.ts (git diff empty).

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - The fold choice (Benchmark Positioning folds, Sector Composition does not) is accepted: it carries the variable-length detail (2 metrics + 2 lists) that benefits from collapsing, while Sector Composition is a single fixed chart+legend view with nothing to hide.
  - The rename-vs-net-new question over SectorPieCard.test.tsx is resolved by 02-test.md's own investigation (net-new, confirmed by git history).
  - The pack/handoff wording correction 02-test.md requests is a docs-lane matter at close-out, not something this gate blocks on.
