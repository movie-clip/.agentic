REPORT 2026-09-03-us43.3-trust-gate-module/05
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd C:\projects\investments\portfolio && python scripts/run_all_tests.py
  result:    PASS
  detail:    anchor = git blobs 04cd099 of both engine files; verified by char-diff of each moved helper body (ast.get_source_segment, normalized only for the def-name change). run_all_tests.py green: golden-regen no drift, 984 backend passed, 359 frontend passed, tsc clean, dead-code strict clean. git diff dashboardGoldens.ts empty.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - build_diagnostics_drawdown_summary moved per 02 § A though AC1's literal list omits it; audit confirms its body char-identical to the 04cd099 blob. Not a finding; review gate owns the AC1-scope call.
  - The relative-return output-admission twin stayed in diagnostics_engine.py, unchanged vs anchor — outside this slice's move list, not audited here.

---

## Orchestrator brief

Financial gate on the trust-gate relocation (US-43.3). VERDICT: PASS.

- Anchor = committed blobs at 04cd099 (US-43.1+43.2 in); working-tree trust_gate.py read directly.
- All 14 relocated functions + the constant DASHBOARD_EXACT_SLICE_EXCESS_RETURN_RUNTIME_ENABLED are char-identical to their anchor bodies. Only permitted deltas present: leading-underscore drop, and the one sanctioned rename _resolve_section_trust -> build_diagnostics_section_trust. Zero call-site renames inside any moved body (no moved body calls another moved helper).
- The merge: both former _has_any_symbol_price_history defs (dashboard + diagnostics) are byte-identical to each other and to the single merged has_any_symbol_price_history. Output-neutral.
- Both engine diffs vs anchor are pure: def deletions + import repoint + call-site name updates. No logic touched. Import trims verified genuinely orphaned (zero remaining refs); kept imports still used.
- Trust honesty intact: two distinct SectionTrust shapes preserved, both drawdown gates still return False, build_diagnostics_drawdown_summary still nulls exactly current+max_drawdown_pct on flag=False, two investor-economics builders keep distinct branching. No rung collapsed/reclassified/fabricated.
- Goldens byte-identical; dashboardGoldens.ts clean; run_all_tests.py green (984 backend / 359 frontend). Regression blocks in test_analytics.py / test_routes.py / test_ledger_replay_audit.py / test_exposure_engine.py unchanged and passing.
- RESEARCH-skip discharged: no non-mechanical change, no methodology edit implied, no body change required to relocate. All three false -> RESEARCH stays skipped.
- Sections below, named exactly: "§ 1 char-diff results", "§ 2 merge proof AC2 AC5", "§ 3 engine-diff review", "§ 4 trust-honesty checks", "§ 5 import trims", "§ 6 RESEARCH-skip discharge".

---

## § 1 char-diff results

Method: `ast.get_source_segment` extracts each function's exact source span from
the anchor blob (`git show 04cd099:...`) and from the working-tree
`trust_gate.py`. Compared after a single normalization: `def <old>(` -> `def
<new>(` (permitted delta (a)/(b)). Any other character delta would fail.

| trust_gate.py symbol | former name | anchor file | result |
|---|---|---|---|
| build_dashboard_section_trust | _build_dashboard_section_trust | dash 04cd099 | identical |
| classify_portfolio_return_basis | _classify_portfolio_return_basis | dash 04cd099 | identical (incl. docstring) |
| build_dashboard_return_basis_contract | _build_dashboard_return_basis_contract | dash 04cd099 | identical |
| build_dashboard_return_basis_evidence | _build_dashboard_return_basis_evidence | dash 04cd099 | identical |
| allow_dashboard_drawdown_outputs | _allow_dashboard_drawdown_outputs | dash 04cd099 | identical (incl. 20-line justification comment, em-dashes and `$125.72 / $107.79` figures intact) |
| build_dashboard_investor_economics_status | _build_dashboard_investor_economics_status | dash 04cd099 | identical |
| build_dashboard_investor_economics_partial_unlock | _build_dashboard_investor_economics_partial_unlock | dash 04cd099 | identical (all 3 scalar policies, withheld_families list of 8, client_derivation_rule) |
| has_replay_outputs | _has_replay_outputs | dash 04cd099 | identical |
| has_any_symbol_price_history | _has_any_symbol_price_history | dash 04cd099 | identical |
| build_diagnostics_section_trust | _resolve_section_trust **(sanctioned rename)** | diag 04cd099 | identical modulo the rename |
| allow_diagnostics_drawdown_outputs | _allow_diagnostics_drawdown_outputs | diag 04cd099 | identical |
| apply_diagnostics_drawdown_output_policy | _apply_diagnostics_drawdown_output_policy | diag 04cd099 | identical |
| build_diagnostics_drawdown_summary | _build_diagnostics_drawdown_summary **(02 § A ruling)** | diag 04cd099 | identical |
| build_diagnostics_investor_economics_status | _build_diagnostics_investor_economics_status | diag 04cd099 | identical |

Constant: `DASHBOARD_EXACT_SLICE_EXCESS_RETURN_RUNTIME_ENABLED = True` — anchor
string `'DASHBOARD_EXACT_SLICE_EXCESS_RETURN_RUNTIME_ENABLED = True'` ==
trust_gate string. Identical.

Call-site-rename-inside-a-moved-body check: NONE required. The dashboard
return-basis composition (`build_dashboard_return_basis_contract` +
`classify_portfolio_return_basis`) is assembled at the engine call site
(dashboard_history_engine.py L365-370), not inside either moved body. No moved
body references another moved def by any name — permitted delta (c) does not
arise.

## § 2 merge proof AC2 AC5

Anchor `_has_any_symbol_price_history`:
- dashboard blob 04cd099: `def _has_any_symbol_price_history(symbol_price_histories: dict[str, list[dict]]) -> bool:` / `    return any(rows for rows in symbol_price_histories.values())`
- diagnostics blob 04cd099: identical char-for-char (no docstring, no comment, no blank-line delta).

Merged `has_any_symbol_price_history` in trust_gate.py L39-40: identical body,
`_` dropped from the name. One def replaces two byte-identical predecessors ->
output-neutral by construction. Both former call sites now call the merged name
with the same guard expression
(`if not benchmark_rows or not has_any_symbol_price_history(symbol_price_histories):`
— dashboard L301, diagnostics L611).

## § 3 engine-diff review

`git diff 04cd099 -- dashboard_history_engine.py` and `... diagnostics_engine.py`
each contain only:
- deletion of the moved `def` blocks (verbatim, verified above),
- import-block edits: new `from app.services.trust_gate import (...)`, removal of
  now-orphaned schema/market_data names, and in diagnostics the removal of the
  `from app.services.dashboard_history_engine import _build_dashboard_investor_economics_partial_unlock`
  cross-engine edge (L59 anchor),
- call-site identifier updates to the de-underscored / renamed names.

No retained statement changed. No file under `analytics/` or `app/schemas/`
appears in `git status` (only the two engines + new `trust_gate.py` +
`test_trust_gate.py`). Schema hook did not fire — correct. `_admitted_exact_slice_scope`
and `_slice_matches_admitted_scope` remain in dashboard_history_engine.py.

## § 4 trust-honesty checks

- **Two SectionTrust builders, distinct shapes, NOT merged.**
  `build_dashboard_section_trust` -> `DashboardHistoryRunMetadata.SectionTrust`
  (`portfolio_path` / `benchmark_path` / `monthly_returns_path`).
  `build_diagnostics_section_trust` -> `DiagnosticsRunMetadata.SectionTrust`
  (`benchmark_relative_path` / `factor_model_path` / `risk_contribution_path`).
  Different inputs, different output type. Preserved.
- **Both drawdown gates still `return False`**, still two functions with
  different signatures (`allow_dashboard_drawdown_outputs(*, benchmark_rows,
  symbol_price_histories)` vs `allow_diagnostics_drawdown_outputs()`).
- **`build_diagnostics_drawdown_summary`** still returns
  `DiagnosticsDrawdownSummary(current_drawdown_pct=None, max_drawdown_pct=None)`
  — exactly those two fields nulled — when `allow_drawdown_outputs` is False,
  and the passthrough of `volatility_regime.snapshot.*` when True.
- **`apply_diagnostics_drawdown_output_policy`** still nulls `drawdown_pct` +
  `wealth_index` per rolling point and `current_drawdown_pct` +
  `max_drawdown_pct` on the snapshot when the flag is False.
- **Two investor-economics builders keep distinct branching.** Dashboard:
  unconditional `build_investor_economics_status(available=False)`. Diagnostics:
  three-way branch on `historical_sections_available` /
  `allow_drawdown_outputs && allow_relative_return_outputs`.
- No `verified` / `degraded` / `withheld` / `unavailable` rung was collapsed,
  reclassified or fabricated. Every value-producing path is a verbatim body.
- Behaviour-neutrality evidence (AC4): the pre-existing regression blocks —
  `section_trust` (9 asserts in test_analytics.py + test_routes.py),
  `investor_economics_status` / `_partial_unlock` (31), `return_basis_contract`
  / `_evidence` (70), `drawdown_summary` / `current_drawdown_pct` /
  `max_drawdown_pct is None` (39), `test_ledger_replay_audit.py:686`,
  `test_exposure_engine.py` — are UNCHANGED (not in `git status`) and pass.

## § 5 import trims

- dashboard_history_engine.py: removed `DashboardHistoryInvestorEconomicsPartialUnlock`,
  `DashboardHistoryInvestorEconomicsScalarPolicy`, `InvestorEconomicsStatus`
  (schemas.dashboard_history) and `build_histories_return_basis_evidence`,
  `build_history_return_basis_evidence`, `classify_history_return_basis_contract`
  (services.market_data). `grep` confirms zero remaining references to each in
  the file. Kept: `build_investor_economics_status` (still used L527),
  `detect_history_return_basis` (still used L130).
- diagnostics_engine.py: removed the whole
  `from app.schemas.dashboard_history import InvestorEconomicsStatus, build_investor_economics_status`
  line and the cross-engine import. `grep` confirms zero remaining references to
  `InvestorEconomicsStatus` / `build_investor_economics_status` /
  `_build_dashboard_investor_economics_partial_unlock` in the file.
- Every removed name was referenced only by a moved body. Nothing still-needed
  was removed. The ruff F401 gate inside `run_all_tests.py` is green, which is
  an independent confirmation.

## § 6 RESEARCH-skip discharge

- **Non-mechanical change in the char-diff?** NO. All 14 bodies + the constant
  are identical modulo permitted deltas (a) leading-underscore, (b) the single
  sanctioned rename. No (c) call-site rename was needed.
- **Any methodology formula / rule description need to change?** NO.
  `docs/finance/financial-methodology.md` § "Trust, Degradation, Withholding,
  and Unavailability" describes the ladder and consumer rules; none references
  an implementation location, and no formula moved. No edit implied.
- **Did any moved function require a body change to relocate?** NO.
- All three conditions false -> RESEARCH remains correctly skipped; no dispatch
  required.
