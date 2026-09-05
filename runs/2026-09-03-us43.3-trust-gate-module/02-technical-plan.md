REPORT 2026-09-03-us43.3-trust-gate-module/02
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    DESIGN order, verification field was NONE. Plan derived from 01-recon.md file:line reads plus first-hand reads of diagnostics_engine.py L200-505 and dashboard_history_engine.py import block.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - RULING (AC1 scope): `_build_diagnostics_drawdown_summary` (diagnostics_engine.py:234-248) MOVES to trust_gate.py. AC1's enumerated list is extended by one name — rationale for the reviewer in § A.
  - RULING: the "dashboard partial-unlock helper" = `_build_dashboard_investor_economics_partial_unlock` (already in AC1); it moves AND drags module constant `DASHBOARD_EXACT_SLICE_EXCESS_RETURN_RUNTIME_ENABLED` with it — see § A.
  - RULING: `_resolve_section_trust` is RENAMED to `build_diagnostics_section_trust` on the move (AC1 sanctions it: "e.g. build_dashboard_section_trust / build_diagnostics_section_trust"). Body verbatim. See § B.
  - Final module = 16 public symbols (15 functions + 1 constant), 0 module-private, 1 merged primitive. Full list, signatures, import block, layering proof in § B.
  - ONE-MERGE boundary confirmed from recon § byte comparison: only `has_any_symbol_price_history` merges. Two section-trust builders, two drawdown gates, two investor-economics builders, both return-basis paths stay separate — § C.
  - Contract: NO schema, NO run_metadata shape, NO docs/contracts field, NO dashboardGoldens.ts change. Schema hook does NOT fire (no app/schemas/ edit). Verbatim relocation, AC4 byte-identical — § D.
  - RESEARCH gate: CONFIRM SKIP. No formula/weighting/return-basis/trust-threshold change; the one merge is two byte-identical pure functions. Guardrail #1/#3 served by the retained AUDIT gate — § F.
  - AUDIT scope: anchor = pre-move source blob; char-diff every moved body; goldens byte-identical; every section_trust / output-admission / investor-economics / return-basis value identical on every route — § G.
  - Lane split: ONE backend order (T-43.3.1 → 43.3.2 → 43.3.3 sequential, dead-import cleanup only resolves after all three); then test (new test_trust_gate.py, 2 tests, no retarget); gates quant-audit FIRST then integration then review; docs (T-43.3.4) at close-out — § E, § H.
  - Test lane: NO import/monkeypatch retarget (recon § Import inventory: zero test references to any moving helper). Regression evidence is test_analytics.py + test_routes.py + test_ledger_replay_audit.py:686 + test_exposure_engine.py:608 — NOT the test_dashboard_history*/test_diagnostics* files the story names, which do not exist. See § E.

risks:
  - AC1 as written does not list `_build_diagnostics_drawdown_summary`. My ruling extends it. If the reviewer diffs strictly against the story's AC1 text, brief them with § A first — this plan is the authority the orchestrator carries to the review gate.
  - Story "Implementer must read" line ranges (~L182-330 / ~L952 diagnostics; ~L124-400 / ~L720-724 dashboard) are STALE after uncommitted US-43.1/43.2. Build and audit lanes use recon's numbers and this plan's, never the story's.
  - The relative-return output-admission pair (`_allow_diagnostics_relative_return_outputs` L251-252, `_apply_diagnostics_relative_return_output_policy` L270-283) is the structural twin of the drawdown pair AC1 moves, but AC1 names neither half. Left in diagnostics_engine.py — a follow-up story could relocate it for symmetry. Not this slice.
  - Dashboard has no `_build_dashboard_*_drawdown_summary` twin — `_allow_dashboard_drawdown_outputs` returns False and suppression happens elsewhere in the dashboard path. The asymmetry between the two engines is pre-existing; the relocation neither fixes nor worsens it.
  - Story ticket T-43.3.1 bundles "add test_trust_gate.py" into the module-creation ticket. In this network tests are a separate lane; the backend order creates the module, the test order writes the file. Ticket text and lane boundary differ — expected, not a conflict.

---

## Orchestrator brief

Technical plan for US-43.3 — relocate the trust gate into `app/services/trust_gate.py`. Verbatim relocation, one byte-identical merge, zero behaviour change.

Decisions taken:
- AC1 scope ruling: `_build_diagnostics_drawdown_summary` MOVES — it is the other half of the drawdown output-admission policy AC1 already relocates; single call site; verbatim. AC1's list extended by one name.
- The dashboard partial-unlock helper `_build_dashboard_investor_economics_partial_unlock` is already in AC1; it moves plus the `DASHBOARD_EXACT_SLICE_EXCESS_RETURN_RUNTIME_ENABLED` constant.
- `_resolve_section_trust` renamed `build_diagnostics_section_trust` (AC1 sanctions); all 15 moved names go PUBLIC, none stay module-private.
- One-merge boundary: only `has_any_symbol_price_history` merges. Two section-trust builders, two drawdown gates, two investor-economics builders, both return-basis paths stay separate.
- Contract: no schema / run_metadata / contracts-doc / goldens change; schema hook does not fire.
- RESEARCH gate ruling: CONFIRM SKIP. AUDIT gate runs first, char-diffs against the pre-move blob.
- Lane split: one backend order (3 sequential steps), then test, then quant-audit then integration then review, then docs.

Sections below: § A — AC1 scope ruling · § B — Final shape of trust_gate.py · § C — The one-merge boundary · § D — Contract section · § E — Per-lane ordered edit list · § F — RESEARCH gate ruling · § G — Quant AUDIT scope ruling · § H — Lane split and dispatch order.

---

## § A — AC1 scope ruling

### A.1 `_build_diagnostics_drawdown_summary` (diagnostics_engine.py:234-248) — RULING: MOVES

**What it is.** A pure output-admission gate:

```
def _build_diagnostics_drawdown_summary(volatility_regime, *, allow_drawdown_outputs: bool) -> DiagnosticsDrawdownSummary:
    if not allow_drawdown_outputs:
        return DiagnosticsDrawdownSummary(current_drawdown_pct=None, max_drawdown_pct=None)
    return DiagnosticsDrawdownSummary(
        current_drawdown_pct=volatility_regime.snapshot.current_drawdown_pct,
        max_drawdown_pct=volatility_regime.snapshot.max_drawdown_pct,
    )
```

**Why it moves.**
- It takes the identical `allow_drawdown_outputs` flag that `_allow_diagnostics_drawdown_outputs` produces and `_apply_diagnostics_drawdown_output_policy` consumes — and AC1 already relocates both of those.
- It is constructed one call after `_apply_diagnostics_drawdown_output_policy`: `_apply_…` at L419-422, `_build_diagnostics_drawdown_summary` at L484-487, both passed `allow_drawdown_outputs` from the same L418 computation.
- It nulls the same two snapshot fields (`current_drawdown_pct`, `max_drawdown_pct`) that `_apply_…` nulls on `volatility_regime.snapshot`. It is literally the second projection of one decision — "may diagnostics publish drawdown numbers".
- Leaving it in `diagnostics_engine.py` splits a single output-trust decision across the module boundary — the exact anti-pattern guardrail #3 and this story exist to remove.
- The move is verbatim: body unchanged, one call site (L484 only — `build_unavailable_diagnostics_result` at L565 constructs `DiagnosticsDrawdownSummary()` inline and does NOT call this helper), zero logic change. Risk is nil.

**Consequence for the reviewer.** AC1's enumerated list is extended by exactly one name: `_build_diagnostics_drawdown_summary` → `build_diagnostics_drawdown_summary`. This is recorded here as the design authority. AC5 ("a reviewer can diff each moved function against its pre-move body and see no logic change") holds for it unchanged. `trust_gate.py` gains one import: `DiagnosticsDrawdownSummary` from `app.schemas.diagnostics`.

**What does NOT move** (bounding the extension so it does not cascade): `_allow_diagnostics_relative_return_outputs` (L251-252) and `_apply_diagnostics_relative_return_output_policy` (L270-283) — the relative-return output-admission pair. AC1 names *neither* half of that pair, so relocating it is a scope decision the story did not make (unlike the drawdown summary, which is the tail of a pair AC1 half-moved). Also staying: `_build_diagnostics_source_status` (L85-120), `_resolve_diagnostics_confidence` (L163-176). See risks for the follow-up note.

### A.2 The dashboard partial-unlock helper — RULING: MOVES (already in AC1) + constant

The helper recon surfaced is `_build_dashboard_investor_economics_partial_unlock` (dashboard_history_engine.py:271-312). It is **already named in AC1** ("+ the dashboard partial-unlock helper"), so there is no scope question about the helper itself — it moves to `build_dashboard_investor_economics_partial_unlock`.

Two attached facts the build and review lanes must carry:
1. **Module constant rides along.** `DASHBOARD_EXACT_SLICE_EXCESS_RETURN_RUNTIME_ENABLED` (dashboard_history_engine.py:44, `= True`) is referenced only at L296 inside this helper. It must move into `trust_gate.py` with the helper. Leaving it in the engine and importing it back creates a `dashboard_history_engine ↔ trust_gate` cycle. This is an implicit AC1 addition (a constant, not a helper) — flagged for the reviewer.
2. **Resolves the one cross-engine leak.** `diagnostics_engine.py:59` (`from app.services.dashboard_history_engine import _build_dashboard_investor_economics_partial_unlock`, used at L475 and L560) is the only non-test cross-module import of any moving helper. After the move both engines import it from `app.services.trust_gate`; the diagnostics→dashboard_history_engine edge is deleted.

---

## § B — Final shape of trust_gate.py

Module path: `services/quant-engine/app/services/trust_gate.py`.

### B.1 Module docstring intent

State: this module is the single home for the "is this output trustworthy enough to publish, and at what level" decision for the Dashboard-history and Diagnostics engines — section-trust rollups, per-section output-admission policy, the price-history / replay-output presence primitives, and the dashboard return-basis classification. It is a **relocation, not a unification** (per guardrail #3 / Epic 43): each engine keeps its own section-trust builder and its own output-admission gates as separate engine-qualified functions; only `has_any_symbol_price_history` is merged, because the two former copies were byte-identical. No formula lives here — every function body is verbatim from its former engine home.

### B.2 Symbol list — 15 functions (all PUBLIC), 1 constant, 0 module-private

Every listed function is imported by at least one engine, so per AC3 every one drops its leading underscore and none stays module-private. No moved helper calls another moved helper (the engines compose them at the call site), so there is no internal-only symbol.

| new name (in trust_gate.py) | former name | former location | body span | signature (unchanged) |
|---|---|---|---|---|
| `has_any_symbol_price_history` | `_has_any_symbol_price_history` | dashboard L720-721 **and** diagnostics L783-784 (byte-identical) | 2 lines | `(symbol_price_histories: dict[str, list[dict]]) -> bool` |
| `has_replay_outputs` | `_has_replay_outputs` | dashboard L724-725 | 2 lines | `(daily_states, performance_series) -> bool` |
| `build_dashboard_section_trust` | `_build_dashboard_section_trust` | dashboard L133-159 | 27 | `(*, benchmark_rows: list[dict], daily_states: list, monthly_returns_suppressed: bool) -> DashboardHistoryRunMetadata.SectionTrust` |
| `classify_portfolio_return_basis` | `_classify_portfolio_return_basis` | dashboard L162-184 | 23 | `(*, daily_states: list, admitted_exact_slice: bool) -> str` |
| `build_dashboard_return_basis_contract` | `_build_dashboard_return_basis_contract` | dashboard L187-196 | 10 | `(benchmark_rows: list[dict], *, portfolio_path: str = "unavailable") -> DashboardHistoryRunMetadata.ReturnBasisContract` |
| `build_dashboard_return_basis_evidence` | `_build_dashboard_return_basis_evidence` | dashboard L199-216 | 18 | `(*, benchmark_rows: list[dict], symbol_price_histories: dict[str, list[dict]] \| None = None, verified_benchmark_scope: dict \| None = None) -> DashboardHistoryRunMetadata.ReturnBasisEvidenceBundle` |
| `allow_dashboard_drawdown_outputs` | `_allow_dashboard_drawdown_outputs` | dashboard L237-262 | 26 (incl. 20-line justification comment) | `(*, benchmark_rows: list[dict], symbol_price_histories: dict[str, list[dict]]) -> bool` |
| `build_dashboard_investor_economics_status` | `_build_dashboard_investor_economics_status` | dashboard L265-268 | 4 | `() -> InvestorEconomicsStatus` |
| `build_dashboard_investor_economics_partial_unlock` | `_build_dashboard_investor_economics_partial_unlock` | dashboard L271-312 | 42 | `() -> DashboardHistoryInvestorEconomicsPartialUnlock` |
| `build_diagnostics_section_trust` | `_resolve_section_trust` **(RENAMED)** | diagnostics L179-203 | 25 | `(*, benchmark_return_basis: Literal[...], factor_return_basis: Literal[...], historical_sections_available: bool) -> DiagnosticsRunMetadata.SectionTrust` |
| `allow_diagnostics_drawdown_outputs` | `_allow_diagnostics_drawdown_outputs` | diagnostics L206-207 | 2 | `() -> bool` |
| `apply_diagnostics_drawdown_output_policy` | `_apply_diagnostics_drawdown_output_policy` | diagnostics L210-231 | 22 | `(volatility_regime: VolatilityRegimePayload, *, allow_drawdown_outputs: bool) -> VolatilityRegimePayload` |
| `build_diagnostics_drawdown_summary` | `_build_diagnostics_drawdown_summary` **(§ A ruling)** | diagnostics L234-248 | 15 | `(volatility_regime: VolatilityRegimePayload, *, allow_drawdown_outputs: bool) -> DiagnosticsDrawdownSummary` |
| `build_diagnostics_investor_economics_status` | `_build_diagnostics_investor_economics_status` | diagnostics L255-267 | 13 | `(*, historical_sections_available: bool, allow_drawdown_outputs: bool, allow_relative_return_outputs: bool) -> InvestorEconomicsStatus` |

Constant (moves in, not an import): `DASHBOARD_EXACT_SLICE_EXCESS_RETURN_RUNTIME_ENABLED = True` (from dashboard L44; sole use at L296 inside `build_dashboard_investor_economics_partial_unlock`).

Renames beyond dropping `_`: exactly one — `_resolve_section_trust` → `build_diagnostics_section_trust`, sanctioned by AC1's own worked example and giving the module two parallel `build_*_section_trust` names. Body verbatim. Both diagnostics call sites (L384, L544) update to the new name.

### B.3 Import block for `trust_gate.py` (from recon § import surface, plus the § A addition)

```python
from typing import Literal

from app.schemas.dashboard_history import (
    DashboardHistoryInvestorEconomicsPartialUnlock,
    DashboardHistoryInvestorEconomicsScalarPolicy,
    DashboardHistoryRunMetadata,
    InvestorEconomicsStatus,
    build_investor_economics_status,
)
from app.schemas.diagnostics import DiagnosticsDrawdownSummary, DiagnosticsRunMetadata
from app.schemas.reconciliation import VolatilityRegimePayload
from app.services.market_data import (
    build_histories_return_basis_evidence,
    build_history_return_basis_evidence,
    classify_history_return_basis_contract,
    detect_history_return_basis,
)
```

`DiagnosticsDrawdownSummary` is the only addition beyond recon's surface — required by the § A ruling. Exact member set is the build lane's to finalise against the moved bodies; the dead-code gate (AC6: ruff/vulture) fails on any unused import, so an over-broad block cannot ship.

### B.4 Cycle-free layering statement

`trust_gate.py` sits in the `services/` layer and imports only **downward**: stdlib `typing`; three schema leaves (`dashboard_history`, `diagnostics`, `reconciliation` — none import any engine, recon § cycle check); and `app.services.market_data` (imports only `app.core`, `app.clients`, `app.schemas.return_basis`, `app.services.holdings_history` — no engine, recon market_data.py:1-12). Nothing on that list transitively reaches `dashboard_history_engine.py` or `diagnostics_engine.py`. Both engines will `from app.services.trust_gate import …`; `trust_gate` imports neither. Graph stays acyclic, and the current `diagnostics_engine → dashboard_history_engine` edge (L59) is removed.

---

## § C — The one-merge boundary

Governs AC2 and AC5.

**The merge is `has_any_symbol_price_history`, and only that.** Recon § "_has_any_symbol_price_history byte comparison" confirms the two former defs (dashboard L720-721, diagnostics L783-784) are identical in every character — same signature, same single `return any(rows for rows in symbol_price_histories.values())`, no docstring, no comments, no blank-line difference. Both former call sites guard identically (`if not benchmark_rows or not _has_any_symbol_price_history(symbol_price_histories):` at dashboard L463, diagnostics L694). The merge is **output-neutral by inspection**: one def, character-identical to both predecessors, replaces two.

**Nothing else merges. Explicitly staying as separate engine-qualified functions:**
- **Section-trust builders** — `build_dashboard_section_trust` (keyword args: `benchmark_rows`, `daily_states`, `monthly_returns_suppressed`; returns `DashboardHistoryRunMetadata.SectionTrust` with `portfolio_path` / `benchmark_path` / `monthly_returns_path`) vs `build_diagnostics_section_trust` (keyword args: two `Literal` return-basis params + `historical_sections_available`; returns `DiagnosticsRunMetadata.SectionTrust` with `benchmark_relative_path` / `factor_model_path` / `risk_contribution_path`). Different inputs, different section shapes, different output type. No common interface designed (US-40.1 territory, explicitly out of scope).
- **Drawdown gates** — `allow_dashboard_drawdown_outputs(*, benchmark_rows, symbol_price_histories) -> bool` vs `allow_diagnostics_drawdown_outputs() -> bool`. Both currently `return False`, but they have different signatures and different justification comments; they remain two functions (AC5).
- **Investor-economics status builders** — `build_dashboard_investor_economics_status()` (no args) vs `build_diagnostics_investor_economics_status(*, historical_sections_available, allow_drawdown_outputs, allow_relative_return_outputs)` (branching body). Different functions, not a merge candidate.
- **Return-basis paths** — the dashboard path is three helpers (`classify_portfolio_return_basis`, `build_dashboard_return_basis_contract`, `build_dashboard_return_basis_evidence`); the diagnostics path builds `ReturnBasisEvidence` inline in `build_historical_diagnostics_result` and moves nothing. They stay distinct; the dashboard helpers are not generalised to serve diagnostics.
- **Drawdown output-admission projections** — `apply_diagnostics_drawdown_output_policy` (nulls `volatility_regime` rolling series + snapshot) and `build_diagnostics_drawdown_summary` (builds the `DiagnosticsDrawdownSummary` model) stay as two functions even though both consume the same flag.

---

## § D — Contract section

Every build lane reads this.

**No boundary is crossed. This is a verbatim relocation.**

- **No schema change.** `trust_gate.py` lives under `app/services/`, not `app/schemas/`. It *imports* existing Pydantic models (`DashboardHistoryRunMetadata`, `DiagnosticsRunMetadata`, `DiagnosticsDrawdownSummary`, `VolatilityRegimePayload`, `InvestorEconomicsStatus`, `DashboardHistoryInvestorEconomicsPartialUnlock`, `DashboardHistoryInvestorEconomicsScalarPolicy`) and defines no new model and no new field.
- **The schema-edit hook does NOT fire.** `scripts/hooks/schema_edit_reminder.py` matches edits under `app/schemas/`; there are none in this slice.
- **No `run_metadata` response-shape change.** Every `run_metadata.section_trust`, output-admission decision, investor-economics status / partial-unlock, and return-basis contract/evidence is produced by the same function body, now imported instead of locally defined. AC4: byte-identical on every route.
- **No `docs/contracts/<area>-fields.md` change.** No field is added, removed, renamed or re-nullabled. `risk-fields.md`, the dashboard-history contract doc, `currency-risk-fields.md` — untouched.
- **No `apps/desktop/src/test/dashboardGoldens.ts` change.** AC4 requires it untouched; `git diff` on it must be empty. Backend goldens byte-identical.
- **No frontend change.** No `types.ts`, no adapter, no card.
- **No `analytics/` change.** No formula, no weighting, no return-basis rule.

If the backend lane finds itself editing anything under `app/schemas/`, adding a field, or changing a response shape — **stop and report**; that is outside this slice and contradicts AC4/AC5.

---

## § E — Per-lane ordered edit list

All line numbers: `dashboard_history_engine.py` at committed HEAD `20f687b` (not touched by US-43.1/43.2, stable); `diagnostics_engine.py` at current working tree (carries uncommitted US-43.1/43.2 import edits, all ≥110 lines clear of every span below — recon § Working-tree state). **Relocate by symbol, not by line.**

### Backend — ONE work order, three sequential steps (T-43.3.1 → T-43.3.2 → T-43.3.3)

Rationale for one order: all three tickets touch the same new module and the same two engines; the dead-import cleanup in each engine can only be finalised once all moves are done. Splitting into three dispatches triples the context cost for no isolation benefit.

**Step 1 (T-43.3.1) — create the module + merge the primitive + move `has_replay_outputs`:**
1. Create `services/quant-engine/app/services/trust_gate.py` with the docstring (§ B.1) and import block (§ B.3, minus symbols not yet needed).
2. Add `DASHBOARD_EXACT_SLICE_EXCESS_RETURN_RUNTIME_ENABLED = True`.
3. Define `has_any_symbol_price_history` — single copy, body verbatim from dashboard L720-721 / diagnostics L783-784.
4. Define `has_replay_outputs` — body verbatim from dashboard L724-725.
5. `dashboard_history_engine.py`: delete `_has_any_symbol_price_history` (L720-721), `_has_replay_outputs` (L724-725), and the `DASHBOARD_EXACT_SLICE_EXCESS_RETURN_RUNTIME_ENABLED` constant (L44). Add `from app.services.trust_gate import has_any_symbol_price_history, has_replay_outputs`. Repoint call sites: L463 (`has_any_symbol_price_history`), L545 (`has_replay_outputs`).
6. `diagnostics_engine.py`: delete `_has_any_symbol_price_history` (L783-784). Add `has_any_symbol_price_history` to the `from app.services.trust_gate import …` line. Repoint call site L694.

**Step 2 (T-43.3.2) — section-trust builders + output-admission gates + investor-economics + partial-unlock:**
7. Move into `trust_gate.py`, bodies verbatim: `build_dashboard_section_trust` (from dashboard L133-159), `allow_dashboard_drawdown_outputs` (L237-262), `build_dashboard_investor_economics_status` (L265-268), `build_dashboard_investor_economics_partial_unlock` (L271-312).
8. Move into `trust_gate.py`, bodies verbatim: `build_diagnostics_section_trust` (from diagnostics L179-203 `_resolve_section_trust`, **renamed**), `allow_diagnostics_drawdown_outputs` (L206-207), `apply_diagnostics_drawdown_output_policy` (L210-231), `build_diagnostics_drawdown_summary` (L234-248 — **§ A ruling**), `build_diagnostics_investor_economics_status` (L255-267).
9. `dashboard_history_engine.py`: delete the four moved defs; extend the `trust_gate` import; repoint call sites — L576-580 (`build_dashboard_section_trust`), L556-559 (`allow_dashboard_drawdown_outputs`), L588 (`build_dashboard_investor_economics_status`), L589 + L687 (`build_dashboard_investor_economics_partial_unlock`).
10. `diagnostics_engine.py`: delete the five moved defs; **delete the L59 cross-engine import** and fold `build_dashboard_investor_economics_partial_unlock` into the `trust_gate` import; repoint call sites — L384-388 + L544-548 (`build_diagnostics_section_trust`), L418 (`allow_diagnostics_drawdown_outputs`), L419-422 (`apply_diagnostics_drawdown_output_policy`), L484-487 (`build_diagnostics_drawdown_summary`), L470-474 + L555-559 (`build_diagnostics_investor_economics_status`), L475 + L560 (`build_dashboard_investor_economics_partial_unlock`).

**Step 3 (T-43.3.3) — dashboard return-basis classification:**
11. Move into `trust_gate.py`, bodies verbatim: `classify_portfolio_return_basis` (dashboard L162-184), `build_dashboard_return_basis_contract` (L187-196), `build_dashboard_return_basis_evidence` (L199-216).
12. `dashboard_history_engine.py`: delete the three moved defs; extend the `trust_gate` import; repoint call sites — L527 (`build_dashboard_return_basis_contract`), L529-532 (`classify_portfolio_return_basis`, nested as the `portfolio_path=` arg), L582-586 + L684 (`build_dashboard_return_basis_evidence`).
13. **Dead-import cleanup, both engines:** in `dashboard_history_engine.py` remove now-unused `classify_history_return_basis_contract`, `build_histories_return_basis_evidence`, `build_history_return_basis_evidence` from the `app.services.market_data` import (used only by the three moved helpers); **keep `detect_history_return_basis`** — still used at L125 by `_build_dashboard_benchmark_history_status`, which is not moving. Check `diagnostics_engine.py` for any import left unused after the moves (`Literal` stays — used widely elsewhere; `VolatilityRegimePayload` stays — L587; `DiagnosticsDrawdownSummary` stays — inline at L565). The AC6 gate (ruff/vulture/knip + `tsc`) is the backstop; the build lane must land it clean, not rely on the gate to find leftovers.

Backend verification (lane runs it): `python scripts/run_all_tests.py` green; `git diff apps/desktop/src/test/dashboardGoldens.ts` empty; `python scripts/detect_deadcode.py --strict` clean.

### Test — ONE work order, new file only

New file `services/quant-engine/app/tests/test_trust_gate.py` with **exactly two tests**:
1. **Merge-primitive** (`has_any_symbol_price_history`): `{}` → `False`; `{"AAPL": []}` → `False`; `{"AAPL": [{"date": "..."}]}` → `True`. Pins the one merge (AC2).
2. **AC3 import-surface pin**: for every relocated name, assert the engine module references `trust_gate.<name>` by identity (`dashboard_history_engine.<name> is trust_gate.<name>` / `diagnostics_engine.<name> is trust_gate.<name>` where imported) and `not hasattr(<engine_module>, "_<old_name>")` for each former private name (including `_resolve_section_trust`, `_has_any_symbol_price_history`, `_has_replay_outputs`, `DASHBOARD_EXACT_SLICE_EXCESS_RETURN_RUNTIME_ENABLED`). Template: `test_synthetic_history_coverage.py:338-367` (US-43.1), `test_analytics.py:8001-8034` (US-43.2).

**No retarget work.** Recon § Import / monkeypatch inventory: zero test references to any moving helper; tests patch `app.services.<engine>.MarketDataService` (the class), unaffected by the re-home. The story Test-plan instruction to "retarget imports/monkeypatches in test_dashboard_history*.py / test_diagnostics*.py" is moot — **those files do not exist.** Engine coverage lives in `test_analytics.py` (+ `test_routes.py`, `test_ledger_replay_audit.py:686`, `test_exposure_engine.py:608`); those suites staying green unchanged in substance IS the behaviour-neutrality proof (AC4). The test lane does not edit them.

Test verification: `cd services/quant-engine && pytest` green (or the full suite).

### Docs — ONE work order at close-out (T-43.3.4)

- `docs/architecture/system-architecture.md` — add `trust_gate.py` to the shared/supporting services inventory (~L65, where `synthetic_history.py` was added for US-43.1) and add/extend the trust-rule section to point at it, cross-referencing guardrail #3.
- `CONTEXT.md:47-54` — the "### trust gate" section already describes the target state ("Lives in `services/trust_gate.py`…"); **confirm** it matches what shipped, correct only if the final symbol names differ.
- `docs/tech-debt-register.md:340` — mark row US-43.3 **Resolved**.
- `docs/product/epic-roadmap.md` — slice-log line (~L128, the `_has_any_symbol_price_history` merge reference); wording is the docs lane's call, not this plan's.
- `docs/product/stories/US-43.3-relocate-the-trust-gate.md` — Status → **Done**.
- No `docs/contracts/*.md` edit (§ D).

---

## § F — RESEARCH gate ruling

The orchestrator proposes skipping the quant RESEARCH pass. **Confirmed — SKIP.**

Checked against guardrail #1 (financial accuracy first), guardrail #3 (truth-class separation), and the profile rule "any change touching a return basis or a trust classification goes through the quant lane — research mode before, audit mode after":

- **Nothing is derived differently.** Every function body moves character-for-character. AC5 requires exactly this and makes it checkable: "a reviewer can diff each moved function against its pre-move body and see no logic change." The § A extension (`build_diagnostics_drawdown_summary`) is held to the same standard.
- **The one merge changes no logic.** `has_any_symbol_price_history` is `return any(rows for rows in symbol_price_histories.values())` — a presence check, not a classification. Both former copies are byte-identical (recon § byte comparison), so the merged def is provably output-neutral by inspection.
- **No formula, weighting, return-basis rule, or trust-ladder threshold is touched.** `analytics/` is not in scope. No `app/schemas/` edit. No methodology-doc section is added or changed — `docs/finance/financial-methodology.md` needs no edit.
- **The profile rule's "before" half has nothing to establish.** RESEARCH produces a concept definition, formulas with citations, a trust-class analysis, a visualization design. There is no new concept here. The rule's "after" half — the quant AUDIT gate — is retained and runs first among the gates (§ G), which is the correct guardrail-#3 control for a relocation: prove the derivation is unchanged rather than re-derive it.

If this ruling is rejected, the only thing RESEARCH could be asked to establish is "does merging two byte-identical two-line pure functions change any trust output" — which is answerable by inspection and does not need the RESEARCH apparatus.

---

## § G — Quant AUDIT scope ruling

The gate is PLANNED and runs first among the three gates (guardrail #3).

The auditor checks a **relocation**, not a computation. What it checks against:

1. **Anchor = the pre-move source blob.** For `dashboard_history_engine.py`, the committed `20f687b` version. For `diagnostics_engine.py`, the working-tree state *before* this slice's edits (its trust-helper spans L179-267 and L783-784 sit clear of the uncommitted US-43.1/43.2 edits — recon § Working-tree state — so the pre-slice body is unambiguous). This is the external anchor required by `gates.md` § 2: the audit is a diff against known-good source, not a recompute from the methodology doc.
2. **Char-diff every moved body** against its pre-move body. Must be identical except for: (a) the symbol name losing its leading `_`; (b) the single rename `_resolve_section_trust` → `build_diagnostics_section_trust`. Zero token changes inside any body — including the § A helper `build_diagnostics_drawdown_summary` and the 20-line justification comment inside `allow_dashboard_drawdown_outputs`.
3. **The merge is output-neutral.** Both pre-move `_has_any_symbol_price_history` bodies (dashboard L720-721, diagnostics L783-784) char-identical to the single merged `has_any_symbol_price_history`.
4. **Goldens byte-identical.** `git diff apps/desktop/src/test/dashboardGoldens.ts` empty; backend golden artifacts unchanged.
5. **Every trust decision identical on every route.** For the diagnostics and dashboard-history routes: `run_metadata.section_trust` (both section shapes), every output-admission decision (drawdown suppression on `volatility_regime` *and* on `drawdown_summary`, investor-economics status, relative-return suppression), investor-economics status + partial-unlock, and the return-basis contract + evidence bundle — identical value-for-value pre vs post. The evidence is `test_analytics.py` + `test_routes.py` passing unchanged in substance (they already assert on all of these).
6. **No scope leak.** Confirm no file under `analytics/` changed; confirm no file under `app/schemas/` changed (schema hook did not fire); confirm the `portfolio_proof` slice-scope helpers (`_admitted_exact_slice_scope`, `_slice_matches_admitted_scope`) stayed in `dashboard_history_engine.py`.

`verification.detail` for the audit must name anchor (2) — the pre-move blob — explicitly, per `gates.md` § 2.

---

## § H — Lane split and dispatch order

| # | Lane | Order | Depends on | Parallel? |
|---|---|---|---|---|
| 1 | backend (`backend-engineer`) | one order, 3 sequential steps T-43.3.1→2→3, ending with dead-import cleanup | — | no |
| 2 | test (`test-engineer`) | new `test_trust_gate.py`, 2 tests, no retarget | backend step 3 landed (needs final module + all renames) | no |
| 3 | quant-audit (`quant-analyst` AUDIT) | financial gate — **runs first among gates** (guardrail #3) | 1, 2 | — |
| 4 | integration (`tech-lead` INTEGRATION) | engineering gate | 3 PASS | — |
| 5 | review (`reviewer`) | acceptance gate — brief with § A (AC1 extension) | 4 PASS | — |
| 6 | docs (`docs-engineer`) | T-43.3.4 close-out | 5 PASS | — |

- **RESEARCH gate: skipped** (§ F).
- No contract/consumer ordering issue (no contract change), but module-before-rewire-before-tests-before-gates-before-docs holds.
- The review gate must receive this plan (or at least § A) as an `input` — AC1's written list does not include `_build_diagnostics_drawdown_summary`, and this plan is the authority that extends it.
- Two-rounds-max on any integration change request (`gates.md` § 4).
