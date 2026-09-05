REPORT 2026-09-04-us43.4-collapse-import-composer/06
status:      DONE
verdict:     NONE

changed:
  - docs/architecture/system-architecture.md:62 — removed `import_engine_composer.py` from the import-path service list.
  - docs/contracts/exposure-fields.md:34 — repointed the field-forwarding call chain from `compose_import_bootstrap_response(...)` / `import_engine_composer.py` to `_compose_import_bootstrap_response(...)` inside `import_engine.py`, noting the fold.
  - docs/tech-debt-register.md — US-43.4 row marked RESOLVED (2026-09-05) with the shipped shape, mirroring the US-43.1/43.2/43.3 row style.
  - docs/product/epic-roadmap.md — epic header/status flipped Active → Completed (all 4 stories now Done); epic-summary bullet for US-43.4 updated with shipped detail; story-snapshot table status Backlog → Done; new slice-log row added for US-43.4 (2026-09-05).
  - docs/product/stories/README.md — Epic 43 header flipped `(active)` → `(complete)`, PRD status note flipped Active → Completed, and US-43.4 status column flipped Backlog → Done.
  - docs/product/stories/US-43.4-collapse-import-engine-composer.md — Status header flipped Backlog → Done, `Last updated:` → 2026-09-05, all 4 ACs and both tickets (T-43.4.1, T-43.4.2) checked, and a "Close-out (2026-09-05) — as-built" section added naming the fold location, the human `git rm` step, the pin-test location, and the quant-audit-skip ruling.

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only doc-reconciliation order; verification field was NONE

contract_notes:
  - none — `ImportedBootstrapResponse` schema is unchanged (confirmed by inputs/02 § Contract disposition and inputs/03); the one code-pointer correction in exposure-fields.md is a traceability-doc fix, not a contract-shape change, and is already landed above.

pack_corrections:
  - none

handoff:
  - none

risks:
  - CONTEXT.md's "import bootstrap" section (lines 57-62) was confirmed accurate as-is by direct read — it already says "the response-assembly step is a private helper, not its own module," which matches the shipped fold. No edit made, per the order's own instruction to confirm-only if accurate.
  - Two PRDs (`docs/product/prd/epic-8-reset-to-analysis-core.md:72` and `docs/product/prd/epic-43-engine-seam-consolidation.md:35,48,80`) still name `import_engine_composer` — left untouched per the order's explicit exclusion (design-ruled out of scope, human-confirmed 2026-09-05). Confirmed by grep after all other edits: no other stale mention of `import_engine_composer` / `compose_import_bootstrap_response` remains anywhere under `docs/` outside those two PRDs and the story/roadmap's own historical/as-built narration (which correctly names the old symbol only when describing what was folded).
  - In `docs/product/stories/README.md` I also flipped the Epic 43 section header from `(active)` to `(complete)` and its PRD status note from Active to Completed, beyond the DoD's literal "flip the US-43.4 status column" instruction — this follows the same file's own established convention (every other completed epic in this README uses the `(complete)` suffix) and the docs-lane pack's auto-rule "epic Active → Completed when every story is done." Flagging it here since it was not itself named in `definition_of_done` for this file.
  - Ticked all 4 ACs and both tickets on the story file. No reviewer report exists yet for this run (the lane sequence in inputs/02 dispatches docs *before* review), so the tick is based on the integration (tech-lead) gate's own independent verification in inputs/05, which directly confirmed all four ACs (verbatim fold, call-site-only behavioural change, goldens byte-identical + full suite green, no dangling reference anywhere under `app/`) — not on an unverified claim.

## Orchestrator brief

- All 6 in-scope files from § Docs blast radius (inputs/02) reconciled; the two excluded PRDs correctly left untouched.
- CONTEXT.md confirmed already accurate, zero edit — per § Docs blast radius "No edit needed" disposition.
- Epic 43 is now fully Completed (all 4 stories Done) — flipped consistently across epic-roadmap.md and stories/README.md.
- No contract_notes, no pack_corrections outstanding.
