REPORT 2026-09-03-us43.3-trust-gate-module/03
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/services/trust_gate.py — NEW leaf module; 15 relocated functions, bodies verbatim, plus constant DASHBOARD_EXACT_SLICE_EXCESS_RETURN_RUNTIME_ENABLED = True
  - services/quant-engine/app/services/trust_gate.py — imports only `typing`, three schema leaves (dashboard_history, diagnostics, reconciliation) and app.services.market_data; imports nothing from either engine
  - services/quant-engine/app/services/dashboard_history_engine.py — deleted 9 helper defs + the constant; added trust_gate import (9 names); repointed 11 call sites to de-underscored names
  - services/quant-engine/app/services/dashboard_history_engine.py — trimmed schema + market_data imports orphaned by the move (see § Import trims)
  - services/quant-engine/app/services/diagnostics_engine.py — deleted 5 helper defs; deleted the L59 cross-engine import; added trust_gate import (7 names); repointed 10 call sites
  - services/quant-engine/app/services/diagnostics_engine.py — _resolve_section_trust renamed build_diagnostics_section_trust at its 2 call sites; dropped orphaned InvestorEconomicsStatus/build_investor_economics_status import

verification:
  command:   cd C:\projects\investments\portfolio && python scripts/run_all_tests.py
  result:    PASS
  detail:    run_all_tests.py: All tests passed — golden regen + backend pytest (-n auto) + desktop vitest + tsc --noEmit + dead-code strict gate (ruff/vulture/knip) all green. git diff apps/desktop/src/test/dashboardGoldens.ts empty. test_analytics.py alone: 217 passed.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Test lane creates services/quant-engine/app/tests/test_trust_gate.py per 02 § E — exactly 2 tests (merge-primitive + AC3 import-surface identity pin). No existing test needs retargeting.
  - AC3 pin lists — the exact trust_gate names each engine now imports, and the former private names now absent from each engine, are in § AC3 import surface below.
  - Docs close-out T-43.3.4 still owed: system-architecture.md shared-services inventory + trust-rule section, tech-debt-register.md:340 -> Resolved, epic-roadmap.md slice log, CONTEXT.md:47-54 confirm, story Status -> Done.
  - Diagnostics still uses DiagnosticsDrawdownSummary (L565 inline), VolatilityRegimePayload (L587 inline) and Literal — those imports were kept, matching 02 § E step 13.

risks:
  - 02 § A extension applied as ruled: build_diagnostics_drawdown_summary moved even though the story's literal AC1 list omits it. Review gate must diff against 02 § A, not raw story text.
  - Dead-import cleanup went past 02 § E step 13's named symbols — moving the two investor-economics status builders orphaned their schema imports in both engines. Details in § Import trims. Behaviour-neutral; full suite + dead-code gate green.
  - trust_gate.py puts the moved constant before the function block; its only consumer now lives in the same module, so nothing imports it back into an engine. Both engine<->trust_gate edges acyclic; the former diagnostics->dashboard_history_engine edge is deleted.

---

## Orchestrator brief

Backend lane for US-43.3 — verbatim relocation of the trust gate into
services/quant-engine/app/services/trust_gate.py. All three DoD verification
gates pass; goldens byte-identical. Two reference sections below: § AC3 import
surface (the pin lists the test lane needs) and § Import trims (the dead-import
cleanup that went beyond 02 § E step 13, for the audit lane).

## AC3 import surface

dashboard_history_engine.py imports from app.services.trust_gate:
`allow_dashboard_drawdown_outputs`, `build_dashboard_investor_economics_partial_unlock`,
`build_dashboard_investor_economics_status`, `build_dashboard_return_basis_contract`,
`build_dashboard_return_basis_evidence`, `build_dashboard_section_trust`,
`classify_portfolio_return_basis`, `has_any_symbol_price_history`, `has_replay_outputs`.

diagnostics_engine.py imports from app.services.trust_gate:
`allow_diagnostics_drawdown_outputs`, `apply_diagnostics_drawdown_output_policy`,
`build_dashboard_investor_economics_partial_unlock`, `build_diagnostics_drawdown_summary`,
`build_diagnostics_investor_economics_status`, `build_diagnostics_section_trust`,
`has_any_symbol_price_history`.

Former private names now absent from dashboard_history_engine.py:
`_build_dashboard_section_trust`, `_classify_portfolio_return_basis`,
`_build_dashboard_return_basis_contract`, `_build_dashboard_return_basis_evidence`,
`_allow_dashboard_drawdown_outputs`, `_build_dashboard_investor_economics_status`,
`_build_dashboard_investor_economics_partial_unlock`, `_has_any_symbol_price_history`,
`_has_replay_outputs`, `DASHBOARD_EXACT_SLICE_EXCESS_RETURN_RUNTIME_ENABLED`.

Former private names now absent from diagnostics_engine.py:
`_resolve_section_trust`, `_allow_diagnostics_drawdown_outputs`,
`_apply_diagnostics_drawdown_output_policy`, `_build_diagnostics_drawdown_summary`,
`_build_diagnostics_investor_economics_status`, `_has_any_symbol_price_history`.

## Import trims

dashboard_history_engine.py — removed from `app.schemas.dashboard_history`:
`DashboardHistoryInvestorEconomicsPartialUnlock`, `DashboardHistoryInvestorEconomicsScalarPolicy`,
`InvestorEconomicsStatus` (each used only by a moved helper). Removed from
`app.services.market_data`: `build_histories_return_basis_evidence`,
`build_history_return_basis_evidence`, `classify_history_return_basis_contract`
(02 § E step 13). Kept: `build_investor_economics_status` (still used at the
unavailable-result path), `detect_history_return_basis` (L130,
`_build_dashboard_benchmark_history_status`, not moving).

diagnostics_engine.py — removed the whole line
`from app.schemas.dashboard_history import InvestorEconomicsStatus, build_investor_economics_status`
(both became unused once `_build_diagnostics_investor_economics_status` moved).
Removed `from app.services.dashboard_history_engine import _build_dashboard_investor_economics_partial_unlock`
(02 § A.2). market_data import block left untouched — none of its names were
tied to a moved helper.

Both trims are forced by the ruff F401 gate inside `run_all_tests.py`; they add
no behaviour change. detect_deadcode.py --strict is clean.
