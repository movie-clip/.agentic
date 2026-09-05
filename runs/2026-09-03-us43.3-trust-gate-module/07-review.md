REPORT 2026-09-03-us43.3-trust-gate-module/07
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd C:\projects\investments\portfolio && python scripts/run_all_tests.py
  result:    PASS
  detail:    Re-ran run_all_tests.py: exit 0 — golden regen no drift, 984 backend passed (50 warnings), 359 frontend passed (40 files), tsc --noEmit clean, dead-code strict clean (ruff/vulture/knip). git diff dashboardGoldens.ts empty. AC5 anchor: git blob HEAD 04cd099 of both engine files; spot-diffed dashboard + diagnostics moved bodies char-identical.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - T-43.3.4 docs close-out still owed (explicitly next lane, not this gate): system-architecture.md services inventory + trust-rule section, tech-debt-register.md:340 -> Resolved, epic-roadmap.md slice log, CONTEXT.md:47-54 confirm, story Status Backlog -> Done.

risks:
  - Plan 02 prose says "15 functions" but its own § B.2 table and the shipped module both hold 14 functions + 1 constant. The delivered set is exactly AC1's 12 + has_any_symbol_price_history + build_diagnostics_drawdown_summary; nothing is missing. The "15" is a plan miscount, not a delivery gap.
  - AC1 extension (build_diagnostics_drawdown_summary + DASHBOARD_EXACT_SLICE_EXCESS_RETURN_RUNTIME_ENABLED): acceptable-as-built — 02 § A ruling, human-approved, body char-identical to anchor (05 § 1). Not a deviation.
  - Story test-plan "retarget test_dashboard_history*.py / test_diagnostics*.py": those files DO NOT EXIST (ls exit 1). Nothing to retarget — recon-surfaced, plan-ruled (02 § E). Acceptable-as-built. Regression evidence is test_analytics.py + test_routes.py + test_ledger_replay_audit.py + test_exposure_engine.py green and unmodified.

---

## Orchestrator brief

Acceptance gate on US-43.3 (relocate the trust gate into services/trust_gate.py). VERDICT: PASS.

- All six ACs (AC1 as extended per 02 § A) satisfied — evidence per AC in § AC verdicts.
- Suite re-run green here: 984 backend / 359 frontend / tsc / dead-code strict; goldens untouched.
- Two flagged items — AC1's one-name extension and the "test files don't exist" gap — are both acceptable-as-built: each was surfaced pre-build (recon / plan) and design-ruled, and the shipped code matches the ruling. Neither is a real deviation.
- One new observation: plan 02 prose miscounts the module at "15 functions" (it is 14 + 1 constant); the delivered symbol set is complete. Recorded in risks, does not affect the verdict.
- Nothing for review to block. T-43.3.4 docs close-out is the only outstanding work and is the next lane by design.

Sections below: § AC verdicts — per-criterion evidence with file:line · § Test plan delivery · § Trust-state spot checks · § Repo hygiene.

---

## § AC verdicts

### AC1 (EXTENDED, 02 § A) — SATISFIED

- `services/quant-engine/app/services/trust_gate.py` exists; module docstring states "relocation, not a unification" (guardrail #3).
- 14 relocated functions present, all public, bodies verbatim:
  - section-trust: `build_dashboard_section_trust` (trust_gate.py:50), `build_diagnostics_section_trust` (:217, renamed from `_resolve_section_trust` per AC1's own worked example).
  - drawdown admission: `allow_dashboard_drawdown_outputs` (:136), `allow_diagnostics_drawdown_outputs` (:244), `apply_diagnostics_drawdown_output_policy` (:248), plus the § A extension `build_diagnostics_drawdown_summary` (:272).
  - investor-economics: `build_dashboard_investor_economics_status` (:164), `build_diagnostics_investor_economics_status` (:289), `build_dashboard_investor_economics_partial_unlock` (:170).
  - `has_replay_outputs` (:43); return-basis `classify_portfolio_return_basis` (:79), `build_dashboard_return_basis_contract` (:104), `build_dashboard_return_basis_evidence` (:116).
- Constant `DASHBOARD_EXACT_SLICE_EXCESS_RETURN_RUNTIME_ENABLED = True` at trust_gate.py:33 (sole consumer at :195, same module — no import-back cycle).
- Verbatim confirmed: I spot-diffed the dashboard bodies (HEAD 04cd099 L133-216) and diagnostics bodies (L179-267) against trust_gate.py — char-identical modulo `_` drop and the one sanctioned rename. 05 quant-audit ran an independent `ast.get_source_segment` char-diff over all 14 + the constant: identical.
- No `def` of any moved helper left in either engine: `grep -rn "def _<name>"` over `app/` → zero matches for all 14 former names.
- Both engines import from `app.services.trust_gate`: dashboard_history_engine.py:34-44 (9 names), diagnostics_engine.py:66-74 (7 names).

### AC2 — SATISFIED

- `has_any_symbol_price_history` defined once (trust_gate.py:39); `grep -rn "def _has_any_symbol_price_history\|def has_any_symbol_price_history" app/` → exactly one definition.
- Imported by both engines (dashboard :42, diagnostics :73); neither keeps a copy.
- Merge-primitive test `test_has_any_symbol_price_history_is_a_presence_check_over_values` (test_trust_gate.py:24): `{}` → False, `{"AAPL": []}` → False, non-empty row list → True. Passes (narrow run 2 passed; full suite green).

### AC3 — SATISFIED

- Both engines import every relocated helper from `app.services.trust_gate` and define none locally (grep above).
- No `_`-prefixed moved name imported from either engine: `grep -rn "from app.services.dashboard_history_engine import _\|from app.services.diagnostics_engine import _" app/` → zero.
- Former cross-engine edge (`diagnostics_engine.py:59 import _build_dashboard_investor_economics_partial_unlock`) removed.
- AC3 import-surface pin `test_engines_bind_the_relocated_trust_gate_symbols_by_reference` (test_trust_gate.py:39) encodes it: `getattr(engine, name) is getattr(trust_gate, name)` for every imported name in each engine, plus `not hasattr(engine, former_name)` for all 10 dashboard + 6 diagnostics former private names and the constant. Passes. Falsifiable: a re-implemented copy or a leftover private def fails the identity / hasattr assertion.

### AC4 — SATISFIED

- `git diff --stat apps/desktop/src/test/dashboardGoldens.ts` → empty.
- `run_all_tests.py` re-run here: golden regen reports no drift; 984 backend + 359 frontend passed; tsc clean; dead-code strict clean; exit 0.
- run_metadata contracts identical on every route: 67 lines in test_analytics.py + 25 in test_routes.py assert on `section_trust` / `drawdown_summary` / investor-economics status / `return_basis_contract`; both files unmodified (`git status` clean) and green. A logic change in any moved body would shift one of those pinned values and fail — it did not.

### AC5 — SATISFIED

- Two SectionTrust builders remain distinct: dashboard takes `benchmark_rows` / `daily_states` / `monthly_returns_suppressed` → `portfolio_path`/`benchmark_path`/`monthly_returns_path`; diagnostics takes two `Literal` return-basis params + `historical_sections_available` → `benchmark_relative_path`/`factor_model_path`/`risk_contribution_path`. Different inputs, different output type. Not merged.
- Return-basis paths distinct: diagnostics moves no return-basis helper (builds `ReturnBasisEvidence` inline); the 3 dashboard helpers are not generalised. Confirmed against 02 § C.
- No unification anywhere: my spot-diff + 05 ast char-diff show every moved body char-identical to its pre-move form.

### AC6 — SATISFIED

- Dead-code gate green: ruff / vulture / knip all "clean", strict mode "no dead-code findings"; tsc --noEmit clean.
- No orphan in either engine. Import trims removed names orphaned by the moved bodies — in dashboard_history_engine.py three `app.schemas.dashboard_history` names + three `app.services.market_data` names; in diagnostics_engine.py the `InvestorEconomicsStatus, build_investor_economics_status` line + the cross-engine import.
- The trims went one step past 02 § E step 13's named list (which named only the 3 market_data symbols) to also drop the orphaned schema imports from the moved investor-economics builders. 05 § 5 and 06 § "Import trims" both verified each removed name has zero remaining refs (`grep -c` = 0) and each kept name (`build_investor_economics_status`, `detect_history_return_basis`) is still used — behaviour-neutral, forced by the ruff F401 gate.
- `_admitted_exact_slice_scope` / `_slice_matches_admitted_scope` (out of scope) stayed in dashboard_history_engine.py.

---

## § Test plan delivery

- **2 new tests in `test_trust_gate.py`** — both exist and pin what they claim: the merged primitive (AC2, presence-check semantics) and the AC3 import-surface identity + former-name-absence pin. Both pass; full suite green.
- **"Retarget test_dashboard_history*.py / test_diagnostics*.py"** — those files DO NOT EXIST (`ls services/quant-engine/app/tests/ | grep dashboard_history\|diagnostic` → exit 1). Nothing to retarget. Recon surfaced this; 02 § E design-ruled it. Only `test_trust_gate.py` references any moved helper name.
- **Regression evidence** (the behaviour-neutrality proof): `test_analytics.py`, `test_routes.py`, `test_ledger_replay_audit.py`, `test_exposure_engine.py` — all present, all unmodified (`git status` clean), all green in the 984-pass backend run. They already assert on `section_trust`, drawdown-output admission, investor-economics status and the return-basis contract, so identical values keep them green.

---

## § Trust-state spot checks

- **Nullable → dash, not zero:** `build_diagnostics_drawdown_summary` still returns `DiagnosticsDrawdownSummary(current_drawdown_pct=None, max_drawdown_pct=None)` when `allow_drawdown_outputs` is False (trust_gate.py:277-281); `apply_diagnostics_drawdown_output_policy` still nulls `drawdown_pct`/`wealth_index` per rolling point and `current_drawdown_pct`/`max_drawdown_pct` on the snapshot (:256-268). Verbatim from anchor.
- **Trust ladder not collapsed:** two SectionTrust builders keep their distinct `verified_adjusted_close` / `degraded_unverified_return_basis` / `unavailable` branching; `classify_portfolio_return_basis` keeps the `verified_total_return` → `replay_derived` → `unavailable` ladder (:99-101). No rung merged or reclassified.
- **Synthetic-field badges:** no schema change, no new synthetic field, no UI change — N/A this slice.
- **New market-data caller mock:** no new market-data caller. `trust_gate.py` imports only pure classification helpers from `app.services.market_data` (no FMP client, no network path); the 984-pass backend suite exercises them.

---

## § Repo hygiene

- `git status --porcelain` → exactly the 4 in-scope files: `trust_gate.py` (new), `test_trust_gate.py` (new), `dashboard_history_engine.py` (M), `diagnostics_engine.py` (M). No stray files, nothing outside scope.
- Goldens: `dashboardGoldens.ts` untouched (git diff empty); backend golden regen reports no drift.
- Story status: still "Backlog". T-43.3.4 owns the flip to Done and is the next lane — the work order explicitly excludes failing on unreconciled docs. Consistent with reality.
