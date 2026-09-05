REPORT 2026-09-03-us43.3-trust-gate-module/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE (read-only recon order)
  result:    NOT_RUN
  detail:    Order verification field was NONE; no command to run. Findings are file:line reads of the current working tree.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - All 14 named helpers located with exact def line, body span and signature — see § Symbol map: dashboard_history_engine.py (9 helpers + 1 module constant) and § Symbol map: diagnostics_engine.py (5 helpers).
  - CONFIRMED: the two `_has_any_symbol_price_history` defs are byte-for-byte identical — dashboard_history_engine.py:720-721 and diagnostics_engine.py:783-784, same signature, same single `return any(...)` line, no docstring, no comments. Safe single-copy merge for AC2. Bodies quoted side by side in § _has_any_symbol_price_history byte comparison.
  - Every call site mapped with its run_* path — see § Call sites. Dashboard: all 9 helpers are called from `run_imported_dashboard_history`; `_build_dashboard_return_basis_evidence` and `_build_dashboard_investor_economics_partial_unlock` are also called from `_build_unavailable_dashboard_history_result` (reached from `run_dashboard_history_engine` too). Diagnostics: helpers called from `build_historical_diagnostics_result` and `build_unavailable_diagnostics_result`; `_has_any_symbol_price_history` from `_run_diagnostics_with_history`.
  - Cross-engine coupling: `diagnostics_engine.py:59` `from app.services.dashboard_history_engine import _build_dashboard_investor_economics_partial_unlock` is the ONLY non-test `from...import` of any moving helper anywhere in app/. Used at diagnostics L475 and L560. After the move, both engines import it from `app.services.trust_gate`, which deletes this diagnostics->dashboard_history_engine dependency.
  - Module constant `DASHBOARD_EXACT_SLICE_EXCESS_RETURN_RUNTIME_ENABLED` (dashboard_history_engine.py:44) is referenced only inside `_build_dashboard_investor_economics_partial_unlock` (L296). It must move into `trust_gate.py` with that helper — leaving it in the engine and importing it back would create a dashboard_history_engine <-> trust_gate cycle.
  - Tests: NO test imports or monkeypatches any moving helper. `test_analytics.py:44-49` imports only `_compute_contribution_adjusted_monthly_returns` / `_compute_max_drawdown` / `run_*` from dashboard_history_engine (none moving); `test_analytics.py:50` imports only `run_*` from diagnostics_engine. Tests patch `app.services.<engine>.MarketDataService` (the class) — unaffected by the helper re-home. Test-lane retarget work for these helpers is effectively nil; only the 2 new `test_trust_gate.py` tests need writing.
  - Cycle check DEFINITIVE: `trust_gate.py` would import from `app.schemas.dashboard_history`, `app.schemas.diagnostics`, `app.schemas.reconciliation`, `app.services.market_data`, stdlib `typing` — full list per helper in § trust_gate.py import surface. `market_data.py` imports only `app.core` / `app.clients` / `app.schemas` / `app.services.holdings_history`; the three schema modules are leaves. Nothing trust_gate imports reaches back to either engine. Both engines importing trust_gate while trust_gate imports neither is acyclic.
  - Out-of-scope helpers CONFIRMED not entangled: `_admitted_exact_slice_scope` (dashboard_history_engine.py:329-340) and `_slice_matches_admitted_scope` (L343-374) are called only at L524 and L777 respectively, by non-moving code. No moving helper references either. `_classify_portfolio_return_basis` takes a plain `admitted_exact_slice: bool`; the caller derives it via `_admitted_exact_slice_scope` at the call site (L524/L531), so nothing moves with the helper. See § Out-of-scope entanglement check.
  - Prior art for the AC3 import-surface pin: `test_synthetic_history_coverage.py:338-367` (US-43.1: `assert engine.X is shared.X` + `assert not hasattr(module, "_old_name")`) and `test_analytics.py:8001-8034` (US-43.2: `assert module.ReturnBasis is ReturnBasis`, `assert risk_module.fit_factor_model is factor_model.fit_factor_model`). US-43.1 and US-43.2 are the direct structural template for this story.
  - Working tree: US-43.1 + US-43.2 uncommitted edits touch diagnostics_engine.py only at imports (L4, L5-24, L39, L57) and a now-deleted in-module synthetic-history builder — all >=110 lines above the first mapped span (`_resolve_section_trust` L179). No overlap and no adjacency inside any mapped span. dashboard_history_engine.py is not touched by US-43.1/43.2 and sits at committed HEAD; its line numbers are stable. See § Working-tree state.
  - Blast radius by lane: backend — create `services/quant-engine/app/services/trust_gate.py`, move 14 symbols + 1 constant verbatim, repoint imports in `dashboard_history_engine.py` and `diagnostics_engine.py` (incl. deleting the `_has_any_symbol_price_history` local copy in each and the L59 cross-engine import). test — add `test_trust_gate.py` (2 tests: the merged primitive + the AC3 import-surface identity pin); no existing test retarget needed. docs — T-43.3.4: `docs/architecture/system-architecture.md:65` services inventory + trust-rule section, `docs/tech-debt-register.md:340` row, `docs/product/epic-roadmap.md` slice log, story -> Done; `CONTEXT.md:47-54` already describes trust_gate in target state. No `docs/contracts/*.md` change (AC4 behaviour-neutral). No schema, no analytics/, no frontend, no quant lane.
  - Diagnostics has 3 further trust-gate-shaped helpers the story does NOT name and leaves in place: `_build_diagnostics_drawdown_summary` (L234-248), `_allow_diagnostics_relative_return_outputs` (L251-252), `_apply_diagnostics_relative_return_output_policy` (L270-283). Design lane should confirm these stay in diagnostics_engine.py.
  - Sources of truth and their currency — see § Sources of truth.

risks:
  - Story line hints are stale after US-43.1/43.2. The story cites diagnostics helpers at "~L182-L330 and ~L952" but the working-tree file is 785 lines; the real spans are L179-267 and L783-784. Design and build must use this report's numbers, not the story's "Implementer must read" ranges.
  - `_build_dashboard_return_basis_contract` is only one of three ways a `ReturnBasisContract` is built in dashboard_history_engine.py — inline `DashboardHistoryRunMetadata.ReturnBasisContract(...)` constructions at L535-538 and L680-683 do not call the helper and are out of scope. Moving the helper does not centralise contract construction; a reviewer expecting "all contract building now in trust_gate" would be wrong.
  - `_build_dashboard_investor_economics_status` (no args) and `_build_diagnostics_investor_economics_status` (3 kwargs, branching body) are different functions, not a merge candidate — consistent with AC5's "no behavioural merge". They move as two separate functions.
  - No dedicated `test_dashboard_history*.py` / `test_diagnostics*.py` exists. Engine coverage lives in `test_analytics.py` (plus `test_routes.py`, `test_ledger_replay_audit.py:686`, `test_exposure_engine.py:608`). The story Test plan names files that do not exist; the behaviour-neutrality regression evidence is in `test_analytics.py`.
  - `_build_diagnostics_drawdown_summary` (L234-248) reads `volatility_regime.snapshot` fields and is invoked immediately after `_apply_diagnostics_drawdown_output_policy` (L419 and L484) with the same `allow_drawdown_outputs` flag. It is trust-gate-shaped but absent from AC1's list; if design decides it should also move, that is a scope addition to flag, not assume.

---

## Orchestrator brief

Read-only symbol-level map for US-43.3 (relocate the trust gate into `services/trust_gate.py`). All findings are file:line against the current working tree, which carries uncommitted US-43.1 + US-43.2 edits in `diagnostics_engine.py` (imports + a deleted synthetic-history function; none overlap the mapped spans).

Verdicts on the DoD questions:
- 14 helpers + 1 module constant located with exact spans and signatures — § Symbol map: dashboard_history_engine.py, § Symbol map: diagnostics_engine.py.
- `_has_any_symbol_price_history` byte-identical in both engines: CONFIRMED — § _has_any_symbol_price_history byte comparison.
- All call sites with run_* path: § Call sites.
- trust_gate.py import surface + per-helper dependency list + cycle proof: § trust_gate.py import surface — acyclic, DEFINITIVE.
- Every import/monkeypatch of the helpers in app/ and app/tests/: § Import / monkeypatch inventory — one non-test cross-engine `from...import` (diagnostics_engine.py:59), zero test references.
- Out-of-scope `_admitted_exact_slice_scope` / `_slice_matches_admitted_scope`: CONFIRMED not entangled — § Out-of-scope entanglement check.
- Working-tree adjacency of US-43.1/43.2: § Working-tree state — no span overlap.
- Governing docs and currency: § Sources of truth.

Lane split for planning: backend (create module, move symbols, repoint two engines), test (new `test_trust_gate.py`, 2 tests, no retarget), docs (T-43.3.4). No schema / analytics / frontend / quant lane.

---

## Symbol map: dashboard_history_engine.py

Committed HEAD (not touched by US-43.1/43.2). File is 1067 lines.

| Symbol | def line | body span | signature / notes |
|---|---|---|---|
| `DASHBOARD_EXACT_SLICE_EXCESS_RETURN_RUNTIME_ENABLED` | 44 | 44 | module constant `= True`; sole use at L296 inside `_build_dashboard_investor_economics_partial_unlock` — moves with that helper |
| `_build_dashboard_section_trust` | 133 | 133-159 | `(*, benchmark_rows: list[dict], daily_states: list, monthly_returns_suppressed: bool) -> DashboardHistoryRunMetadata.SectionTrust` |
| `_classify_portfolio_return_basis` | 162 | 162-184 | `(*, daily_states: list, admitted_exact_slice: bool) -> str`; docstring L167-181; pure, no external refs |
| `_build_dashboard_return_basis_contract` | 187 | 187-196 | `(benchmark_rows: list[dict], *, portfolio_path: str = "unavailable") -> DashboardHistoryRunMetadata.ReturnBasisContract` |
| `_build_dashboard_return_basis_evidence` | 199 | 199-216 | `(*, benchmark_rows: list[dict], symbol_price_histories: dict[str, list[dict]] | None = None, verified_benchmark_scope: dict[str, str | bool | int | None] | None = None) -> DashboardHistoryRunMetadata.ReturnBasisEvidenceBundle` |
| `_allow_dashboard_drawdown_outputs` | 237 | 237-262 | `(*, benchmark_rows: list[dict], symbol_price_histories: dict[str, list[dict]]) -> bool`; returns `False`; 20-line justification comment L242-261; both params intentionally unread |
| `_build_dashboard_investor_economics_status` | 265 | 265-268 | `() -> InvestorEconomicsStatus` |
| `_build_dashboard_investor_economics_partial_unlock` | 271 | 271-312 | `() -> DashboardHistoryInvestorEconomicsPartialUnlock`; the "dashboard partial-unlock helper" of AC1; also imported by diagnostics_engine.py:59 |
| `_has_any_symbol_price_history` | 720 | 720-721 | `(symbol_price_histories: dict[str, list[dict]]) -> bool`; pure |
| `_has_replay_outputs` | 724 | 724-725 | `(daily_states, performance_series) -> bool`; pure |

Not moving (named in the DoD prompt only to bound scope): `_build_dashboard_benchmark_history_status` (L124-130 — not in the story list), `_build_dashboard_portfolio_proof_metadata` (L219-234), `_admitted_exact_slice_scope` (L329-340), `_slice_matches_admitted_scope` (L343-374), `_allow_benchmark_return_output` (L377-393), `_withhold_benchmark_return_series` (L396-397), `_build_range_metrics` and everything below it.

## Symbol map: diagnostics_engine.py

Working tree (post US-43.1/43.2, uncommitted). File is 785 lines.

| Symbol | def line | body span | signature / notes |
|---|---|---|---|
| `_resolve_section_trust` | 179 | 179-203 | `(*, benchmark_return_basis: Literal["verified_adjusted_close", "unverified_close_only", "unavailable"], factor_return_basis: Literal["verified_adjusted_close", "unverified_close_only", "unavailable"], historical_sections_available: bool) -> DiagnosticsRunMetadata.SectionTrust` |
| `_allow_diagnostics_drawdown_outputs` | 206 | 206-207 | `() -> bool`; returns `False` |
| `_apply_diagnostics_drawdown_output_policy` | 210 | 210-231 | `(volatility_regime: VolatilityRegimePayload, *, allow_drawdown_outputs: bool) -> VolatilityRegimePayload` |
| `_build_diagnostics_investor_economics_status` | 255 | 255-267 | `(*, historical_sections_available: bool, allow_drawdown_outputs: bool, allow_relative_return_outputs: bool) -> InvestorEconomicsStatus` |
| `_has_any_symbol_price_history` | 783 | 783-784 | `(symbol_price_histories: dict[str, list[dict]]) -> bool`; pure; byte-identical to the dashboard copy |

Trust-gate-shaped, NOT in the story's move list, stay in diagnostics_engine.py: `_build_diagnostics_source_status` (L85-120), `_resolve_diagnostics_confidence` (L163-176), `_build_diagnostics_drawdown_summary` (L234-248), `_allow_diagnostics_relative_return_outputs` (L251-252), `_apply_diagnostics_relative_return_output_policy` (L270-283).

## _has_any_symbol_price_history byte comparison

dashboard_history_engine.py:720-721
```
def _has_any_symbol_price_history(symbol_price_histories: dict[str, list[dict]]) -> bool:
    return any(rows for rows in symbol_price_histories.values())
```

diagnostics_engine.py:783-784
```
def _has_any_symbol_price_history(symbol_price_histories: dict[str, list[dict]]) -> bool:
    return any(rows for rows in symbol_price_histories.values())
```

Identical in every character: same signature, same single return statement, no docstring, no comments, no blank-line differences inside the body. AC2's "byte-for-byte identical today" holds. In both engines the call is guarded identically: `if not benchmark_rows or not _has_any_symbol_price_history(symbol_price_histories):` (dashboard L463, diagnostics L694).

## Call sites

### dashboard_history_engine.py

Inside `run_imported_dashboard_history` (def L422):
- L463 — `_has_any_symbol_price_history(symbol_price_histories)` — early-return guard
- L527 — `_build_dashboard_return_basis_contract(benchmark_rows, portfolio_path=...)`
- L529-532 — `_classify_portfolio_return_basis(daily_states=..., admitted_exact_slice=admitted_portfolio_twr_scope is not None)` — nested as the `portfolio_path=` argument to the L527 call; `admitted_portfolio_twr_scope` comes from `_admitted_exact_slice_scope(portfolio_proof)` at L524
- L545 — `_has_replay_outputs(daily_states, raw_performance_series)` — early-return guard
- L556-559 — `_allow_dashboard_drawdown_outputs(benchmark_rows=..., symbol_price_histories=...)`
- L576-580 — `_build_dashboard_section_trust(benchmark_rows=..., daily_states=..., monthly_returns_suppressed=...)`
- L582-586 — `_build_dashboard_return_basis_evidence(benchmark_rows=..., symbol_price_histories=..., verified_benchmark_scope=...)`
- L588 — `_build_dashboard_investor_economics_status()`
- L589 — `_build_dashboard_investor_economics_partial_unlock()`

Inside `_build_unavailable_dashboard_history_result` (def L655; reached from `run_dashboard_history_engine` at L405/L413 and from `run_imported_dashboard_history` early returns at L435, L464, L546):
- L684 — `_build_dashboard_return_basis_evidence(benchmark_rows=[])`
- L687 — `_build_dashboard_investor_economics_partial_unlock()`

### diagnostics_engine.py

Inside `build_historical_diagnostics_result` (def L327):
- L384-388 — `_resolve_section_trust(benchmark_return_basis=..., factor_return_basis=..., historical_sections_available=True)`
- L418 — `_allow_diagnostics_drawdown_outputs()`
- L419-422 — `_apply_diagnostics_drawdown_output_policy(build_volatility_regime_payload(...), allow_drawdown_outputs=...)`
- L470-474 — `_build_diagnostics_investor_economics_status(historical_sections_available=True, allow_drawdown_outputs=..., allow_relative_return_outputs=...)`
- L475 — `_build_dashboard_investor_economics_partial_unlock()` (imported from dashboard_history_engine at L59)

Inside `build_unavailable_diagnostics_result` (def L517; called directly from `run_diagnostics_engine` L653, `run_imported_diagnostics_engine` L762, `_run_diagnostics_with_history` L695):
- L544-548 — `_resolve_section_trust(benchmark_return_basis="unavailable", factor_return_basis="unavailable", historical_sections_available=False)`
- L555-559 — `_build_diagnostics_investor_economics_status(historical_sections_available=False, allow_drawdown_outputs=False, allow_relative_return_outputs=False)`
- L560 — `_build_dashboard_investor_economics_partial_unlock()`

Inside `_run_diagnostics_with_history` (def L671):
- L694 — `_has_any_symbol_price_history(symbol_price_histories)` — early-return guard

Diagnostics run_* call-flow: `run_diagnostics_engine` (L649) -> `build_unavailable_diagnostics_result` (L653) OR `_run_diagnostics_with_history` (L660). `run_imported_diagnostics_engine` (L758) -> `build_unavailable_diagnostics_result` (L762) OR `_run_diagnostics_with_history` (L772). `_run_diagnostics_with_history` -> `build_unavailable_diagnostics_result` (L695) OR `build_historical_diagnostics_result` (L739).

## trust_gate.py import surface

### What trust_gate.py must import

From `app.schemas.dashboard_history`: `DashboardHistoryRunMetadata` (with nested `.SectionTrust`, `.ReturnBasisContract`, `.ReturnBasisEvidenceBundle`), `InvestorEconomicsStatus`, `build_investor_economics_status`, `DashboardHistoryInvestorEconomicsPartialUnlock`, `DashboardHistoryInvestorEconomicsScalarPolicy`.
From `app.schemas.diagnostics`: `DiagnosticsRunMetadata` (with nested `.SectionTrust`).
From `app.schemas.reconciliation`: `VolatilityRegimePayload`.
From `app.services.market_data`: `detect_history_return_basis`, `classify_history_return_basis_contract`, `build_histories_return_basis_evidence`, `build_history_return_basis_evidence`.
Stdlib: `from typing import Literal`.
Moves into the module (not an import): constant `DASHBOARD_EXACT_SLICE_EXCESS_RETURN_RUNTIME_ENABLED`.

### Per-helper dependency

| helper | private/shared symbols it references |
|---|---|
| `_build_dashboard_section_trust` | `detect_history_return_basis` (market_data), `DashboardHistoryRunMetadata.SectionTrust` |
| `_classify_portfolio_return_basis` | none (pure; docstring only) |
| `_build_dashboard_return_basis_contract` | `classify_history_return_basis_contract` (market_data), `DashboardHistoryRunMetadata.ReturnBasisContract` |
| `_build_dashboard_return_basis_evidence` | `build_histories_return_basis_evidence`, `build_history_return_basis_evidence` (market_data), `DashboardHistoryRunMetadata.ReturnBasisEvidenceBundle` |
| `_allow_dashboard_drawdown_outputs` | none (returns `False`) |
| `_build_dashboard_investor_economics_status` | `build_investor_economics_status`, `InvestorEconomicsStatus` (schemas.dashboard_history) |
| `_build_dashboard_investor_economics_partial_unlock` | `DashboardHistoryInvestorEconomicsPartialUnlock`, `DashboardHistoryInvestorEconomicsScalarPolicy` (schemas.dashboard_history), `DASHBOARD_EXACT_SLICE_EXCESS_RETURN_RUNTIME_ENABLED` (module constant, moves in) |
| `_has_any_symbol_price_history` | none (pure) |
| `_has_replay_outputs` | none (pure) |
| `_resolve_section_trust` | `Literal` (stdlib), `DiagnosticsRunMetadata.SectionTrust` |
| `_allow_diagnostics_drawdown_outputs` | none (returns `False`) |
| `_apply_diagnostics_drawdown_output_policy` | `VolatilityRegimePayload` (schemas.reconciliation) |
| `_build_diagnostics_investor_economics_status` | `build_investor_economics_status`, `InvestorEconomicsStatus` (schemas.dashboard_history) |

### Cycle check — DEFINITIVE: acyclic

- `app.services.market_data` imports: `app.core.symbols`, `app.clients.fmp`, `app.clients.yfinance_client`, `app.schemas.return_basis`, `app.services.holdings_history`. No engine module. (market_data.py:1-12.)
- `app.schemas.dashboard_history` imports: stdlib `typing`, `pydantic`, `app.schemas.portfolio_engine`, `app.schemas.return_basis`, `app.schemas.reconciliation`. Leaf. (dashboard_history.py:1-7.)
- `app.schemas.diagnostics` imports: stdlib `typing`, `pydantic`, `app.schemas.dashboard_history`, `app.schemas.imports`, `app.schemas.portfolio_engine`, `app.schemas.return_basis`, `app.schemas.reconciliation`. Leaf. (diagnostics.py:1-9.)
- `app.schemas.reconciliation` is a schema leaf.

Nothing on trust_gate.py's import list transitively reaches `dashboard_history_engine.py` or `diagnostics_engine.py`. Both engines would `from app.services.trust_gate import ...`; trust_gate would import nothing from either. The graph stays acyclic. This also removes the current diagnostics_engine -> dashboard_history_engine edge (diagnostics_engine.py:59).

## Import / monkeypatch inventory

### Non-test app/ (only one)
- `services/quant-engine/app/services/diagnostics_engine.py:59` — `from app.services.dashboard_history_engine import _build_dashboard_investor_economics_partial_unlock`. Real `from...import` (bound into the diagnostics module namespace; used at L475, L560). Must be repointed to `app.services.trust_gate`. This is the only cross-module import of any moving helper anywhere in the non-test tree.

### app/tests/ (none reference a moving helper)
- `test_analytics.py:44-49` — `from app.services.dashboard_history_engine import _compute_contribution_adjusted_monthly_returns, _compute_max_drawdown, run_dashboard_history_engine, run_imported_dashboard_history`. None of these move (`_compute_*` stay in the engine).
- `test_analytics.py:50` — `from app.services.diagnostics_engine import run_diagnostics_engine, run_imported_diagnostics_engine`. Neither moves.
- `test_analytics.py:8017-8021` — `import app.services.diagnostics_engine as diagnostics_engine_module` then `assert diagnostics_engine_module.ReturnBasis is ReturnBasis` (US-43.2 identity pin; a `trust_gate` analog is the AC3 test).
- `test_ledger_replay_audit.py:686` — `from app.services.dashboard_history_engine import run_imported_dashboard_history`. Not a moving helper.
- `test_exposure_engine.py:11` — `from app.services.diagnostics_engine import run_imported_diagnostics_engine`. Not a moving helper.

### Monkeypatch / mocker.patch
- Tests patch `app.services.dashboard_history_engine.MarketDataService` and `app.services.diagnostics_engine.MarketDataService` (the class) — many sites in `test_analytics.py` and `test_routes.py`, plus `conftest.py:251` and `conftest.py:274` `monkeypatch.setattr("app.services.<engine>.MarketDataService", ...)`. None target a trust-gate helper; the re-home does not affect them.
- No `monkeypatch.setattr(<engine_module>, "<moving helper>", ...)` exists anywhere.

### Prior-art pins for AC3 (import-surface identity check)
- `test_synthetic_history_coverage.py:338-367` (US-43.1) — `assert engine.build_synthetic_snapshot_history_states_with_coverage is synthetic_history.build_...` plus `assert not hasattr(diagnostics_engine, "_build_synthetic_snapshot_history_states")`.
- `test_analytics.py:8001-8034` (US-43.2) — `assert risk_mod.ReturnBasis is ReturnBasis`, `assert risk_module.fit_factor_model is factor_model.fit_factor_model`.

## Out-of-scope entanglement check

- `_admitted_exact_slice_scope` — def dashboard_history_engine.py:329-340. Only caller: L524 (`admitted_portfolio_twr_scope = _admitted_exact_slice_scope(portfolio_proof)`), inside `run_imported_dashboard_history`.
- `_slice_matches_admitted_scope` — def L343-374. Only caller: L777 (`verified_twr_slice = _slice_matches_admitted_scope(...)`), inside `_build_range_metrics`.
- Neither is referenced by any of the 9 moving dashboard helpers or the 5 moving diagnostics helpers.
- `_classify_portfolio_return_basis` receives `admitted_exact_slice: bool` as a parameter; the boolean is computed at the call site (L531: `admitted_exact_slice=admitted_portfolio_twr_scope is not None`) from `_admitted_exact_slice_scope`'s tuple/None result. So the `portfolio_proof` / slice-scope coupling stays entirely in `dashboard_history_engine.py`; nothing about it moves with the helper.
- CONFIRMED: `_admitted_exact_slice_scope` and `_slice_matches_admitted_scope` stay in `dashboard_history_engine.py`, zero entanglement with the relocation.

## Working-tree state

Uncommitted (US-43.1 + US-43.2), all in `diagnostics_engine.py`:
- L4 — `from app.analytics.factor_model import FACTOR_PROXY_MAP` (US-43.2; `FACTOR_PROXY_MAP` no longer imported from `app.analytics.risk`).
- L5-24 — the `app.analytics.risk` import block, with the factor-model symbols removed (US-43.2).
- L39 — `from app.schemas.return_basis import ReturnBasis, ReturnBasisEvidence` (US-43.2 "moved ReturnBasis import"; `test_analytics.py:8017-8021` pins it).
- L57 — `from app.services.synthetic_history import build_synthetic_snapshot_history_states` (US-43.1).
- Deletion of the former in-module synthetic-history builder function (US-43.1; `test_synthetic_history_coverage.py:364-367` pins its absence). This deletion is what shrank the file and shifted the story's "~L182-L330 / ~L952" hints down to the actual L179-267 / L783-784.

Adjacency: the nearest mapped span, `_resolve_section_trust` at L179, is ~110 lines below the L57-67 import edits. No mapped span (L179-267, L783-784) overlaps or abuts a US-43.1/43.2 edit.

New sibling files from those stories, same layer as the proposed module: `services/quant-engine/app/services/synthetic_history.py`, `services/quant-engine/app/analytics/factor_model.py`.

`dashboard_history_engine.py`: not in the US-43.1/43.2 change set (the work order confirms both stories edited only diagnostics_engine.py). It is at committed HEAD `20f687b`; its mapped line numbers (L44, L133-312, L720-725) are stable.

## Sources of truth

- `docs/product/stories/US-43.3-relocate-the-trust-gate.md` — the story; "Last updated 2026-09-02"; Backlog. Its "Implementer must read" line ranges are stale (see risks); the Context table and ACs name the right symbols.
- `docs/product/prd/epic-43-engine-seam-consolidation.md` — PRD; US-43.3 row at L79, `_has_any_symbol_price_history` byte-copy noted at L33. Current, 3rd slice.
- `docs/tech-debt-register.md:340` — the US-43.3 register row (T-43.3.4 marks it Resolved).
- `docs/architecture/system-architecture.md:61` (per-engine services) and `:65` ("Shared / supporting" list) — T-43.3.4 adds `trust_gate.py` to the shared list and a trust-rule section cross-referencing guardrail #3. L65 was already updated for US-43.1's `synthetic_history.py`; `trust_gate.py` is not yet listed.
- `docs/product/epic-roadmap.md:128` — slice-log line referencing the `_has_any_symbol_price_history` merge.
- `CONTEXT.md:47-54` — "### trust gate" section already written in the target state ("Lives in `services/trust_gate.py`; the Dashboard history engine and the Diagnostics engine both call it. Each engine keeps its own `SectionTrust` builder function ... only the [price-history primitive is merged]"). T-43.3.4's "confirm `CONTEXT.md`" is essentially pre-satisfied.
- `docs/contracts/*.md` — no change. AC4 is behaviour-neutral (every `run_metadata.section_trust` / return-basis / investor-economics value byte-identical), so `risk-fields.md` and the dashboard contract docs do not move.
