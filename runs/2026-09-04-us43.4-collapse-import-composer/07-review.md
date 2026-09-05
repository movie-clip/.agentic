REPORT 2026-09-04-us43.4-collapse-import-composer/07
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd services/quant-engine && pytest -q app/tests/test_analytics.py
  result:    PASS
  detail:    218 passed, 1 warning in 24.14s (via mcp__project__run_tests scope=backend path=app/tests/test_analytics.py); full-suite corroboration via mcp__project__check_gates: dead-code (ruff/vulture/knip) clean, tsc --noEmit clean, goldens_drifted:false, commit-gate marker present.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - Story close-out and epic-roadmap.md cite the pin test under the wrong name; cosmetic, does not affect PASS — see § Docs close-out spot check, test-name note.
  - Two PRDs still name the deleted `import_engine_composer` symbol, left untouched by design — see § Docs close-out spot check, PRD note.

## Orchestrator brief

- Verdict PASS. All four ACs independently confirmed against code, not against lane claims. See § AC-by-AC.
- Test plan's single pin assertion verified present, correctly placed, correctly formed, and green — see § Test plan.
- Docs close-out (T-43.4.2) spot-checked across 6 touched files plus CONTEXT.md and both untouched PRDs; all consistent with reality except one cosmetic test-name citation (§ risks, non-blocking).
- No BLOCKING or SHOULD_FIX findings raised.

## AC-by-AC

**AC1 — compose body moved verbatim as `_compose_import_bootstrap_response`; composer file deleted.**
SATISFIED. Read `services/quant-engine/app/services/import_engine.py:25-47` directly: `_compose_import_bootstrap_response` is present, module-private, and its body (the `ImportedBootstrapResponse(...)` construction including the delegated `build_import_admission_summary(snapshot)` call) matches the composer's described shape. `test -f app/services/import_engine_composer.py` confirms the file does not exist on disk; `git status --porcelain` shows `D  services/quant-engine/app/services/import_engine_composer.py`.

**AC2 — three public entry functions unchanged; callers unchanged.**
SATISFIED. `import_engine.py:14-22,50-79` shows `build_import_bootstrap`, `build_import_bootstrap_from_portfolio_snapshot_request`, `build_import_bootstrap_from_snapshot` retain their exact prior names/signatures; the only body change is the single call-site line (`compose_import_bootstrap_response` → `_compose_import_bootstrap_response`) inside `build_import_bootstrap_from_snapshot`, every keyword argument unchanged. `app/api/routes/imports.py:10,66,96,109` (not in `git status --porcelain` — untouched) imports and calls `build_import_bootstrap` / `build_import_bootstrap_from_portfolio_snapshot_request` with unchanged signatures.

**AC3 — behaviour-neutral: goldens byte-identical, full suite green.**
SATISFIED. `git diff --stat HEAD -- apps/desktop/src/test/dashboardGoldens.ts` is empty. `mcp__project__check_gates` reports `goldens_drifted:false`, dead-code clean, `tsc --noEmit` clean, commit-gate marker present. `mcp__project__run_tests` on `app/tests/test_analytics.py` (the file carrying the new pin plus the exercised bootstrap coverage): 218 passed, 1 warning, 0 failures.

**AC4 — no dangling reference to `import_engine_composer` anywhere in `app/` or `app/tests/`; dead-code gate green.**
SATISFIED. `grep -rn "import_engine_composer|compose_import_bootstrap_response" app/` returns only the new helper's own name, its call site, and the pin test's intentional reference (test_analytics.py:781,783) — no other hit under `app/` or `app/tests/`. The only other matches are stale `.pyc` cache files in `__pycache__`, which the story's own Notes/decisions section explicitly rules out of scope ("Stale `import_analysis`/`import_analysis_composer` `.pyc` artifacts... are from a prior rename and are not in scope"). Dead-code gate (`mcp__project__check_gates`): ruff/vulture/knip all clean.

## Test plan

- The plan's single named deliverable — "1 assertion added ... pinning `app.services.import_engine_composer` no longer imports" — exists at `services/quant-engine/app/tests/test_analytics.py:781-783`, immediately after `test_build_import_bootstrap_from_snapshot_falls_back_to_ledger_and_position_dates_when_statement_period_missing` (line 778 ends that test; the pin starts line 781), exactly as the story specifies. Form matches: `with pytest.raises(ModuleNotFoundError): import app.services.import_engine_composer  # noqa: F401`.
- No new unit test for the private helper, as the plan stated — it is exercised end to end via `build_import_bootstrap_from_snapshot`'s existing coverage in the same file, which stays green.
- Regression suites (`test_analytics.py`, full `run_all_tests.py` per dispatch 04) stay green — corroborated independently in this gate via `mcp__project__run_tests` + `mcp__project__check_gates`, not merely re-read from prior lane claims.

## Docs close-out (T-43.4.2) spot check

- `docs/architecture/system-architecture.md:62` — import path list now reads `import_engine.py, statement_importer.py, import_admission.py, portfolio_snapshot_builder.py, history_context_builder.py`; no `import_engine_composer` mention. Confirmed by direct read.
- `CONTEXT.md:57-62` ("import bootstrap" section) — already named only `import_engine.py` and the private-helper shape pre-existing this story; confirmed accurate, correctly left unedited per the docs lane's own note.
- `docs/tech-debt-register.md:341` — US-43.4 row carries a `**RESOLVED (US-43.4, 2026-09-05):**` annotation naming the shipped shape; confirmed by direct read.
- `docs/product/epic-roadmap.md` — Epic 43 header now reads "Completed... US-43.4 Done 2026-09-05" (line 101-102); story-snapshot table row shows `Done` (line 154); slice-log row for 2026-09-05/US-43.4 present (line 166). Confirmed.
- `docs/product/stories/US-43.4-collapse-import-engine-composer.md` — Status: Done, Last updated 2026-09-05, all 4 ACs and both tickets checked, Close-out section present. Confirmed by direct read.
- `docs/contracts/exposure-fields.md:34` — field-forwarding call chain now names `_compose_import_bootstrap_response(...)` inside `import_engine.py`, correctly noting the fold from the now-deleted `import_engine_composer.py`. Confirmed. `ImportedBootstrapResponse` schema itself untouched (not in `git status --porcelain`), so no contract-shape drift.
- **PRD note.** Two PRDs left naming the old symbol: `epic-8-reset-to-analysis-core.md:72`, `epic-43-engine-seam-consolidation.md:35,48,80`. Acceptable — out of the DoD's named file list (system-architecture.md/CONTEXT.md/register/roadmap/story only), and the docs lane's inputs/02 scoping treats PRDs as historical planning snapshots, not living reference docs.
- **Test-name note.** `docs/product/stories/US-43.4-collapse-import-engine-composer.md:120` and `docs/product/epic-roadmap.md:166` both cite the pin test as `test_import_engine_composer_module_is_gone`. The actual test at `test_analytics.py:781` is named `test_import_engine_composer_module_no_longer_exists`. Cosmetic doc-narration mismatch only — the assertion (`pytest.raises(ModuleNotFoundError)` on the deleted module) is present, correctly placed after the intended test, and passes. Does not affect AC1/AC4 or the PASS verdict; a one-line docs edit would fix the citation.
