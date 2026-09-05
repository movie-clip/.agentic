REPORT 2026-09-02-us43.1-synthetic-history-module/05
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd C:\projects\investments\portfolio && python scripts/run_all_tests.py
  result:    PASS
  detail:    Full suite green: backend pytest 980 passed (50 warnings); frontend vitest 359 passed (40 files); tsc --noEmit clean; dead-code gate clean (ruff F401/F811/F841 + vulture + knip). git diff apps/desktop/src/test/dashboardGoldens.ts EMPTY. Anchor for the verbatim check: `git show HEAD:...diagnostics_engine.py` lines 761-924.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Slice is engineering-sound and behaviour-neutral. Reviewer (step 4) may proceed to AC1-AC5 against plan 02 § 5's gradeable reading; nothing engineering-side blocks it.
  - Docs lane (step 5, close-out) still owes T-43.1.3 per plan 02 § 6 — the symbol-path-text-only doc reconciliation. No methodology content change.

risks:
  - diagnostics_engine.py new import sits above the `exposure_engine` import rather than alphabetised; that block was already unsorted and ruff does not enforce order — cosmetic, not a change request.
  - Pre-existing uncommitted drift (CLAUDE.md, epic-roadmap.md, stories/README.md, tech-debt-register.md, CONTEXT.md, docs/agents/, epic-43 PRD + US-43.* stories) confirmed out of scope and not from this run.

## Orchestrator brief

Integration gate over the synthetic-history relocation (US-43.1, T-43.1.1 + T-43.1.2). Verdict: PASS. No change requests, no `cr/` files. No quant lane needed — the plan 02 § 7 condition is satisfied (see below).

Decisions / findings, one line each:
- § 7 verbatim condition HOLDS: the two moved bodies are byte-identical to pre-move `diagnostics_engine.py` L761-924 after exactly the three permitted renames — no other in-body character changed. Quant re-audit NOT triggered.
- Contract UNCROSSED: `app/schemas/**`, `app/api/**`, `analytics/**` untouched; no route response shape changed; no `docs/contracts/*` field changed; `apps/desktop/src/**` untouched.
- diagnostics_engine.py: 4 dead-import cleanups correct and complete (SYNTHETIC_COVERAGE_DE_MINIMIS_WEIGHT + DailyPortfolioState + DailyStatePosition + SyntheticHistoryCoverage); L731 self-call uses the public name; ruff F401 clean confirms no orphan.
- Five engines: import line + call site each rewired to `app.services.synthetic_history`, keyword args unchanged.
- Tests: name-only retargets + one AC2 pin test asserting object identity across the five engines and `not hasattr` on both old private diagnostics names; coverage-matrix cases unchanged in substance (behaviour-neutrality proof AC4 intact).
- Full suite run here: green. dashboardGoldens.ts diff EMPTY.

Sections below: `1. § 7 verbatim char-diff (this gate owns it)` · `2. Contract alignment` · `3. diagnostics_engine.py cleanup` · `4. Five engines` · `5. Test changes` · `6. Suite run`.

---

## 1. § 7 verbatim char-diff (this gate owns it)

Method: extracted pre-move body from `git show HEAD:services/quant-engine/app/services/diagnostics_engine.py` lines 761-924; extracted the new module's function region (`synthetic_history.py` L21-184); applied the three permitted renames to the pre-move copy; `diff` → **zero remaining differences**.

Permitted deltas observed, and only these:
1. `def _build_synthetic_snapshot_history_states` → `def build_synthetic_snapshot_history_states` (×2).
2. Thin wrapper's internal call `states, _coverage = _build_synthetic_snapshot_history_states_with_coverage(` → `... build_synthetic_snapshot_history_states_with_coverage(`.
3. New module docstring (L1-10) + 3-line import block (L12-18) — new to the module, not part of the moved bodies.

The `_weight` local closure, all comments, the L39-54 docstring, the coverage-rule branches, the `(states, coverage)` return shape, all rounding (`round(..., 2)` / `round(..., 6)`), and the `SYNTHETIC_COVERAGE_DE_MINIMIS_WEIGHT` comparison are character-for-character unchanged. The § 7 condition is met; the quant-audit gate is correctly skipped.

## 2. Contract alignment

- `git diff --name-only HEAD` + untracked scan: no file under `services/quant-engine/app/schemas/`, `services/quant-engine/app/api/`, or `services/quant-engine/app/analytics/`. `app/api/main.py` untouched — no router change to miss.
- New module consumes `ImportedPortfolioSnapshot` (`app.schemas.imports`) and returns `list[DailyPortfolioState]` / `tuple[list[DailyPortfolioState], SyntheticHistoryCoverage]` (`app.schemas.reconciliation`) — all pre-existing, all unchanged.
- `apps/desktop/src/**` untouched; no `docs/contracts/<area>-fields.md` field added/removed/retyped. No frontend lane was needed and none ran.
- Truth-class (guardrail #3): Synthetic History is given a public home named for it; no trust label, trust rung, or `SyntheticHistoryCoverage` field changed. No truth classes mixed in any response.

## 3. diagnostics_engine.py cleanup

- L3: `from app.core.constants import DEFAULT_BENCHMARK_SYMBOL, SYNTHETIC_COVERAGE_DE_MINIMIS_WEIGHT` → drops the constant, keeps `DEFAULT_BENCHMARK_SYMBOL`. Correct.
- `app.schemas.reconciliation` import block: `DailyPortfolioState`, `DailyStatePosition`, `SyntheticHistoryCoverage` removed; every other name in that block retained. Correct — matches plan 02 § 6 exactly.
- Added `from app.services.synthetic_history import build_synthetic_snapshot_history_states`.
- Self-call (post-edit line ~731) in `_run_diagnostics_with_history`: `daily_states = build_synthetic_snapshot_history_states(snapshot=..., price_histories=..., valuation_dates=...)` — public name, keyword args unchanged, no unpacking (it calls the thin wrapper, as before).
- Both `def _build_synthetic_snapshot_history_states*` deleted; next `def` (`run_imported_diagnostics_engine`) now directly follows. `grep "def _build_synthetic"` → zero matches.
- No orphaned import: ruff `F401` clean in the full-suite dead-code gate. Nothing hand-asserted.

## 4. Five engines

`attribution_engine.py`, `correlation_engine.py`, `distribution_engine.py`, `drawdown_engine.py`, `stress_engine.py` — each a two-line change:
- import: `from app.services.diagnostics_engine import _build_synthetic_snapshot_history_states_with_coverage` → `from app.services.synthetic_history import build_synthetic_snapshot_history_states_with_coverage`.
- call site: `daily_states, coverage = build_synthetic_snapshot_history_states_with_coverage(snapshot=..., price_histories=..., valuation_dates=...)` — leading `_` dropped, keyword args and `(daily_states, coverage)` unpacking unchanged.

Layering: `synthetic_history.py` imports only `app.core.constants` + `app.schemas.*` (leaf); the six consumers import it back; acyclic. Confirmed against the recon 01 cycle check.

## 5. Test changes

- `test_synthetic_history_coverage.py`: import block retargeted to `app.services.synthetic_history`; 6 coverage-matrix call sites renamed (leading `_` dropped, explicit rename, no `as` alias — `grep "_build_synthetic" app/tests/` clean). No assertion, expected value, or fixture body changed → AC4 behaviour-neutrality proof intact.
- New test `test_all_engine_consumers_bind_to_the_shared_synthetic_history_symbol`: asserts `engine.build_synthetic_snapshot_history_states_with_coverage is synthetic_history.build_...` for all five engines, plus `not hasattr(diagnostics_engine, "_build_synthetic_snapshot_history_states")` and the `_with_coverage` variant. This tests the extraction contract — it would fail if any consumer re-implemented the builder or if diagnostics retained the private symbol. Not implementation-pinning.
- `test_correlation_engine.py:310`: `mocker.patch` string `app.services.correlation_engine._build_..._with_coverage` → `...build_..._with_coverage` — still patched on the consuming module, survives the re-home. Sole cause of the backend lane's transient failure, now resolved.

## 6. Suite run

`cd C:\projects\investments\portfolio && python scripts/run_all_tests.py` — run by this gate:
- backend pytest: 980 passed, 50 warnings.
- frontend vitest: 359 passed, 40 files.
- `tsc --noEmit`: clean.
- dead-code strict gate: ruff clean, vulture clean, knip clean.
- `git diff apps/desktop/src/test/dashboardGoldens.ts`: empty — no dashboard-output change, as AC3 requires.
