REPORT 2026-09-02-us43.2-factor-model-module/02
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Design pass — read-only; order verification field was NONE. No commands run, no files edited.

contract_notes:
  - schemas/return_basis.py gains a bare `ReturnBasis` Literal (T-43.2.1); the schema_edit_reminder hook fires but no types.ts or docs/contracts/<area>-fields.md mirror is owed — it is a function-parameter annotation, never a Pydantic model field. See § Contract.
  - docs/finance/financial-methodology.md §Statistical Factor Model must re-point moved-symbol "implemented in risk.py" / "top of risk.py" phrasing to analytics/factor_model.py (T-43.2.4). See § Docs edit list.
  - docs/tech-debt-register.md row US-43.2 (L339) under-lists cross-seam consumers (2 named, 4 actual) and must record the AC3 linalg disposition + the AC1 amendment, then mark Resolved (T-43.2.4). See § Docs edit list.
  - No route response shape, no docs/contracts/<area>-fields.md field, and no apps/desktop/src/test/dashboardGoldens.ts change is in play — verbatim relocation, outputs byte-identical (AC4). See § Contract.

pack_corrections:
  - none

handoff:
  - One backend implementation order covers T-43.2.1 + T-43.2.2 + T-43.2.3 source edits — see § Backend edit list.
  - One test order, dispatched after the backend order reports, covers all test retargets + the 2 new identity tests + test_attribution.py L416/L426 — see § Test edit list.
  - quant-audit (AUDIT mode) runs before integration and review because analytics/ is touched; anchor = pre-move git blob + char-diff of moved spans — see § Quant AUDIT scope.
  - quant RESEARCH mode is skipped for this slice; conditions in § RESEARCH ruling.
  - docs order T-43.2.4 runs after the reviewer PASS — see § Docs edit list.
  - Full dispatch order is in § Lane split and dispatch order.

risks:
  - I am reading the profile's "analytics/ -> quant lane in research mode before" routing rule as satisfied-by-AUDIT for this proven-verbatim relocation and ruling RESEARCH skippable. That softens a written routing rule (not one of the five numbered hard guardrails). The human should confirm. If the build lane cannot move a function without altering it, RESEARCH becomes required.
  - AC1's literal moving-list is amended: `selected_history_return_series` (and its private helper `_series_to_returns`) STAY in risk.py, renamed public, because moving them creates a risk.py <-> factor_model.py import cycle via `select_history_price_series`. The reviewer must grade AC1 against the amended list in § Cycle decision.
  - AC5 as written names only test_analytics.py; test_attribution.py L416/L426 also patch `_fit_factor_model` on the consumer module and must be retargeted. Folded into § Test edit list — flag for the reviewer that AC5's wording is under-inclusive.
  - `UcitsCandidateMapping` is added to the moving set (not named in AC1) to keep factor_model.py a zero-back-edge leaf. If the build lane leaves it in risk.py instead, module import ordering becomes load-bearing and fragile.
  - All line numbers are from the recon working tree; T-43.2.1 shifts risk.py lines before T-43.2.2/.3 run. The build lane must re-locate by symbol, not by line.

---

## Orchestrator brief

Design pass for US-43.2 — move the statistical-factor-model internals out of `analytics/risk.py` into a new `analytics/factor_model.py`, and the `ReturnBasis` execution-basis `Literal` into `schemas/return_basis.py`. Verbatim relocation, behaviour-neutral.

Decisions taken:
- **Cycle decision:** `selected_history_return_series` + `_series_to_returns` STAY in risk.py (renamed public); factor_model.py does not need them. AC1 moving-list is amended — see § Cycle decision. `UcitsCandidateMapping` is ADDED to the move so factor_model.py imports nothing from risk.py (a clean leaf). risk.py <-> factor_model.py ends acyclic.
- **AC3 linalg:** `_least_squares` / `_solve_linear_system` / `_dot` have zero non-factor callers — they MOVE to factor_model.py, stay underscore-private there, risk.py does not import them back.
- **AC2 / ReturnBasis:** new home is a top-level `ReturnBasis = Literal[...]` in schemas/return_basis.py; no name collision. Crosses no wire contract. Code importers to rewire: risk.py, attribution.py, diagnostics_engine.py (3).
- **RESEARCH ruling:** skipped for this slice (no formula / ridge-floor / factor-definition / member change), conditional on the AUDIT proving verbatim — see § RESEARCH ruling.
- **AUDIT scope:** planned; anchor = pre-move git blob; check goldens byte-identical + named factor-model/attribution/stress test blocks + char-diff — see § Quant AUDIT scope.
- **Lane split:** one backend order (T-43.2.1–.3 source), then one test order, then quant-audit -> integration -> review, then docs T-43.2.4 — see § Lane split and dispatch order.

Sections below, by name: TECHNICAL PLAN (summary); Cycle decision; AC3 linalg ruling; AC2 / ReturnBasis contract; Contract; Final shape of `analytics/factor_model.py`; Backend edit list; Test edit list; Docs edit list; RESEARCH ruling; Quant AUDIT scope; Lane split and dispatch order.

---

## TECHNICAL PLAN (summary)

```
contract:   schemas/return_basis.py gains  ReturnBasis = Literal["portfolio_value",
            "market_value", "market_value_trade_neutral"]  (+ the porting of risk.py's
            L52-61 explanatory comment). It is a param annotation, never serialized —
            no types.ts, no docs/contracts field, dashboardGoldens.ts untouched. This
            is the ONLY thing that crosses. All engine outputs (factor model,
            attribution, stress) and all backend goldens stay byte-identical (AC4).

reuse:      New module analytics/factor_model.py is a LEAF — imports only
            `from __future__ import annotations` + `from dataclasses import dataclass`.
            It imports nothing from risk.py. risk.py imports the moved names back.
            attribution.py / attribution_engine.py / stress_engine.py /
            diagnostics_engine.py repoint their factor-symbol imports to
            analytics.factor_model. No new helper is written; every moved body is
            copied verbatim (only the two leading-underscore renames below).

lanes:      backend (T-43.2.1 + T-43.2.2 + T-43.2.3 source) ->
            test (T-43.2.3 test retargets + 2 new identity tests) ->
            quant-audit (AUDIT) -> integration -> review -> docs (T-43.2.4).
            Verification for the impl lanes: `python scripts/run_all_tests.py` green,
            `git diff --exit-code apps/desktop/src/test/dashboardGoldens.ts`,
            `python scripts/detect_deadcode.py --strict`.

decisions:  1. selected_history_return_series + _series_to_returns STAY in risk.py
               (renamed public) — AC1 list amended (cycle via select_history_price_series).
            2. UcitsCandidateMapping is ADDED to the move (keeps factor_model.py a leaf).
            3. _least_squares / _solve_linear_system / _dot MOVE, stay private in
               factor_model.py, not re-imported by risk.py (AC3).
            4. _fit_factor_model -> fit_factor_model, _orthogonalize_factors_window ->
               orthogonalize_factors_window (public: imported cross-module).
            5. FACTOR_BY_LABEL and FACTOR_MODEL_MIN_SHARED_OBSERVATIONS STAY in risk.py
               (re-derived from the imported DEFAULT_FACTOR_DEFINITIONS).
            6. No private alias kept in risk.py for the two renamed fns — the retargeted
               monkeypatches + the AC5 identity test cover it; an unused alias would
               fail the dead-code gate (AC6).
            7. RESEARCH mode skipped; AUDIT mode is the financial gate for the move.

risks:      See the report block's `risks:` — the RESEARCH-rule softening and the
            AC1/AC5 wording amendments are the ones the human/reviewer must sign off.
```

---

## Cycle decision

**Finding (from recon § Cycle check, confirmed against risk.py):**
`_selected_history_return_series` (risk.py:871-873) calls the PUBLIC
`select_history_price_series` (risk.py:839). `select_history_price_series` must
stay in risk.py — it is consumed by `is_history_series_verified_adjusted`
(L88), `selected_history_price_map` (L92), and tests (test_analytics.py L15,
L5671, L5682). If `_selected_history_return_series` moved to factor_model.py,
that module would need `from app.analytics.risk import select_history_price_series`
while risk.py does `from app.analytics.factor_model import ...` — a module-load
import cycle.

**Ruling — option (b) from the recon menu: it does NOT move.**

- `_selected_history_return_series` and `_series_to_returns` **stay in
  `analytics/risk.py`**.
- `_selected_history_return_series` is **renamed to `selected_history_return_series`**
  (public), because `attribution.py` imports it across the seam and AC3 forbids
  importing a `_`-prefixed name from `risk.py`. Making it public resolves the
  leak without moving it.
- `_series_to_returns` **keeps its underscore** — its only caller is
  `selected_history_return_series`, both in risk.py, so it never crosses the
  seam.
- `factor_model.py` does **not** import either. It does not need them: neither
  `_fit_factor_model` nor `_orthogonalize_factors_window` calls
  `_selected_history_return_series` (verified — their only private refs are the
  linalg trio + `ORTHOGONALIZATION_ZERO_RESIDUAL_THRESHOLD`).
- `attribution.py` keeps `from app.analytics.risk import selected_history_return_series`
  (public name, still sourced from risk.py). Its other factor imports move to
  `analytics.factor_model`.

**AC1 amendment (state plainly for the reviewer):** AC1 lists
`selected_history_return_series` among the symbols `factor_model.py` "defines
(moved verbatim from risk.py)". That is amended: it stays in `risk.py`, renamed
public. Rationale: (1) the import cycle above; (2) it is not a factor-model
internal — it is a generic price-history-to-returns utility whose in-risk.py
callers are `_benchmark_return_series` (L1622, feeds every risk/vol summary) and
`_build_position_risk_contributions` (L2043), both non-factor. Moving it would
force risk.py to import it back at 4 sites AND break acyclicity. Grade AC1
against: `FactorDefinition`, `UcitsCandidateMapping` (added), `DEFAULT_FACTOR_DEFINITIONS`,
`FACTOR_PROXY_MAP`, `FACTOR_KEY_MAP`, `ROLLING_RIDGE_FLOOR`,
`ORTHOGONALIZATION_ZERO_RESIDUAL_THRESHOLD`, `fit_factor_model`,
`orthogonalize_factors_window`, `_least_squares`, `_solve_linear_system`, `_dot`.

**`UcitsCandidateMapping` (recon's fourth back-edge concern) — ruling: it moves
too.** It is a field type inside `FactorDefinition` and is used to construct
`DEFAULT_FACTOR_DEFINITIONS` (both moving). It also feeds risk.py's UCITS-scoring
helpers (L234-548, staying) — those will `from app.analytics.factor_model import
UcitsCandidateMapping`. It imports only stdlib `dataclasses`. Moving it makes
`factor_model.py` a pure leaf with **zero** imports from `risk.py`, which is the
only shape that is unconditionally acyclic (leaving it in risk.py would make
risk.py's import of factor-model symbols have to sit below L77 in the file — a
fragile mid-file import future edits can silently break).

**Acyclic proof:** after the move, `factor_model.py` imports `{__future__,
dataclasses}` only. `risk.py` imports factor-model names from `factor_model.py`.
No edge from `factor_model.py` back to `risk.py`. `schemas/return_basis.py`
imports `{typing, pydantic}` only; `analytics -> schemas` is the sanctioned
direction. Both new edges are one-way.

---

## AC3 linalg ruling

**Confirmed from recon § Linalg trio callers (exhaustive grep of
`_least_squares` / `_solve_linear_system` / `_dot(` over all `app/**/*.py`,
test and non-test):**

| Callee | Call site | Enclosing fn | Class |
|---|---|---|---|
| `_least_squares` | risk.py:1731 | `_orthogonalize_factors_window` | factor-model (moving) |
| `_least_squares` | risk.py:1743 | `_fit_factor_model` | factor-model (moving) |
| `_dot` | risk.py:1732 | `_orthogonalize_factors_window` | factor-model (moving) |
| `_dot` | risk.py:1744 | `_fit_factor_model` | factor-model (moving) |
| `_solve_linear_system` | risk.py:2220 | `_least_squares` | factor-model (transitive) |

No other file references any of the three. **Zero non-factor callers remain in
`risk.py`.**

**Ruling:** `_least_squares`, `_solve_linear_system`, `_dot` **MOVE to
`analytics/factor_model.py`**. They stay module-private (underscore kept) — no
module outside `factor_model.py` references them. `risk.py` does **not** import
them back. This is recorded here per AC3's "The story records which".

---

## AC2 / ReturnBasis contract

**Crosses no wire contract.** `ReturnBasis` is a Python `Literal` used only as a
function-parameter annotation in `build_*` / `_build_*` signatures. It is never
a Pydantic model field, never serialized. `apps/desktop/src/test/dashboardGoldens.ts`
and every route response are byte-identical (recon contract_note; AC4).

**Exact new home:** `services/quant-engine/app/schemas/return_basis.py`, appended
as a new top-level alias alongside the existing `ReturnBasis*` family (which is
`ReturnBasisContract` L6, `ReturnBasisPathTrust` L7, `ReturnBasisVerificationStatus`
L8, `ReturnBasisEconomicBasis` L9, `ReturnBasisConstructionMethod` L10-16). There
is **no bare `ReturnBasis` name in that file today — no collision** (recon
confirmed). Place it after the Literal family, before `ReturnBasisEvidence` (L19),
and port risk.py's L52-61 explanatory comment with it:

```python
ReturnBasis = Literal["portfolio_value", "market_value", "market_value_trade_neutral"]
```

**Full importer list to rewire (bare `ReturnBasis` name, code only):**

| Module | Line today | Action |
|---|---|---|
| `analytics/risk.py` | def L62 (+comment L52-61) | delete def; add `from app.schemas.return_basis import ReturnBasis`. 8 annotation sites (L551, 572, 804, 876, 1206, 1381, 1542, 1552) unchanged. |
| `analytics/attribution.py` | import L33 (inside the risk block) | remove from risk block; add `from app.schemas.return_basis import ReturnBasis`. Uses L62, L107 unchanged. |
| `services/diagnostics_engine.py` | import L9 (inside the risk block) | remove from risk block; add `ReturnBasis` to the existing `from app.schemas.return_basis import ReturnBasisEvidence` line (L40). Use L403 unchanged. |

`schemas/reconciliation.py:569` mentions `ReturnBasis` in a prose comment only —
**no edit**. No test file imports the bare name (recon). The AC2 pin test is new
(see § Test edit list).

Note the work order's "5 app/ modules" for ReturnBasis: that count is the
*factor-symbol* rewire set (risk.py import-back + attribution.py + stress_engine.py
+ diagnostics_engine.py + attribution_engine.py). The bare-`ReturnBasis` code
rewire set is **3** (risk.py, attribution.py, diagnostics_engine.py).

---

## Contract

**What crosses (one thing):** the `schemas/return_basis.py` edit above (T-43.2.1).

**Schema-hook implication:** `scripts/hooks/schema_edit_reminder.py` (PostToolUse)
fires on any edit under `app/schemas/`. It will fire here. There is **nothing to
mirror** — no `types.ts` change, no `docs/contracts/<area>-fields.md` field
change — because `ReturnBasis` is a param annotation, not a model field. The
backend lane MUST state this explicitly in its own `contract_notes`
("schema hook fired on return_basis.py; no TS / contract-doc mirror owed —
`ReturnBasis` is a `Literal` param annotation, not a serialized field") so the
integration gate does not flag a missing mirror. This also makes T-43.2.1
schema-touching, which is correctly routed through full planning (the profile's
express lane explicitly excludes anything under `app/schemas/`).

**What does NOT cross:**
- No route response shape. `build_statistical_factor_model`,
  `build_factor_attribution`, the stress engine responses — all unchanged
  (verbatim move; `build_statistical_factor_model` stays in risk.py per the
  story Notes).
- No `docs/contracts/<area>-fields.md` field. recon confirmed `risk-fields.md`
  (L34/L88), `exposure-fields.md` (L107-315), `factor-drift-fields.md`,
  `diagnostics-fields.md` reference `risk.py` only for symbols that STAY
  (`build_stress_scenarios`, `STRESS_SCENARIOS`, `build_lookthrough_*`,
  `build_market_overlap_summary`, `build_rolling_risk_series`) or reference
  response field names only.
- No frontend / TS change of any kind.
- `apps/desktop/src/test/dashboardGoldens.ts` untouched; backend goldens
  byte-identical (AC4).

**Truth class:** unchanged. The move reclassifies nothing.
`apply_return_basis_status_to_factor_model` / `apply_return_basis_status_to_model_reliability`
(risk.py L1000, L1014) stay in risk.py, untouched — verified they reference no
moving symbol (only `detect_*`, `_degrade_status_for_unverified_return_basis`
which stays at L833, and schema models).

---

## Final shape of `analytics/factor_model.py`

**Module docstring intent:**
> Statistical factor-model internals extracted from `analytics/risk.py` (US-43.2):
> the factor-definition vocabulary (`UcitsCandidateMapping`, `FactorDefinition`,
> `DEFAULT_FACTOR_DEFINITIONS`, and the proxy/key maps), the per-window
> Gram-Schmidt orthogonalisation and ridge-OLS fit, and their linear-algebra
> primitives. Behaviour-neutral relocation — formulas, ridge floors and factor
> definitions are unchanged; see `docs/finance/financial-methodology.md`
> §Statistical Factor Model. This module is a leaf: it imports nothing from
> `risk.py`, so `risk.py` imports these names back.

**Import block:**
```python
from __future__ import annotations

from dataclasses import dataclass
```
(The build lane adds `from typing import ...` only if a moved body needs it —
none of the listed bodies do under `from __future__ import annotations`. The
dead-code gate catches any unused import.)

**Symbol list (all copied verbatim from `risk.py`; source spans from recon
§ Moving symbols):**

| Symbol | risk.py span | Visibility in factor_model.py | Why |
|---|---|---|---|
| `UcitsCandidateMapping` (frozen dataclass) | 65-77 | public (name unchanged) | imported back by risk.py UCITS helpers |
| `FactorDefinition` (frozen dataclass) | 97-111 | public | imported by risk.py, attribution.py |
| `DEFAULT_FACTOR_DEFINITIONS` (17-tuple) | 113-130 | public | imported by risk.py, attribution.py, tests |
| `FACTOR_PROXY_MAP` | 132 | public | imported by 4 modules |
| `FACTOR_KEY_MAP` | 133 | public | imported by attribution.py |
| `ROLLING_RIDGE_FLOOR` | 143 (+comment 139-142) | public | imported by risk.py, attribution.py |
| `ORTHOGONALIZATION_ZERO_RESIDUAL_THRESHOLD` | 1695 (+comment 1685-1694) | module-const (name unchanged) | used only inside `orthogonalize_factors_window` |
| `orthogonalize_factors_window` (was `_orthogonalize_factors_window`) | 1698-1738 | **public — rename, drop `_`** | imported by attribution.py; patched via `risk_module` in tests |
| `fit_factor_model` (was `_fit_factor_model`) | 1741-1750 | **public — rename, drop `_`** | imported by attribution.py; patched via `risk_module` in tests |
| `_least_squares` | 2211-2220 | **private — keep `_`** | no caller outside factor_model.py |
| `_solve_linear_system` | 2223-2240 | private — keep `_` | called only by `_least_squares` |
| `_dot` | 2243-2244 | private — keep `_` | called only inside factor_model.py |

Internal references inside the moved bodies (`_least_squares`, `_dot`,
`ORTHOGONALIZATION_ZERO_RESIDUAL_THRESHOLD`) resolve within `factor_model.py`
unchanged — only the two top-level `def` names lose their underscore.

**Stays in `risk.py`** (do not move): `select_history_price_series` (839),
`SelectedHistoryPriceSeries` (81-86), `is_history_series_verified_adjusted` (88),
`selected_history_price_map` (92), `selected_history_return_series` (renamed from
`_selected_history_return_series`, 871-873), `_series_to_returns` (2247-2255),
`FACTOR_BY_LABEL` (134), `FACTOR_MODEL_MIN_SHARED_OBSERVATIONS` (226),
`_build_rolling_factor_loadings` (1753-1803), `build_statistical_factor_model`,
`_build_factor_risk_contributions`, `STRESS_SCENARIOS` (152-156),
`WINDOW_MIN_OBSERVATIONS` (138), `ROLLING_WINDOWS` (136).

---

## Backend edit list

One backend order, three ticket-scoped stages, in this sequence (each stage ends
with a green `python scripts/run_all_tests.py`).

### Stage T-43.2.1 — move `ReturnBasis`
1. `app/schemas/return_basis.py` — after the Literal family (after L16, before
   `ReturnBasisEvidence` L19): port risk.py's L52-61 comment, then add
   `ReturnBasis = Literal["portfolio_value", "market_value", "market_value_trade_neutral"]`.
2. `app/analytics/risk.py` — delete L52-62 (comment + `ReturnBasis` def); add
   `from app.schemas.return_basis import ReturnBasis` to the `app.schemas`
   import group (near L12-13). 8 annotation sites unchanged.
3. `app/analytics/attribution.py` — remove `ReturnBasis` from the
   `from app.analytics.risk import (...)` block (L33); add
   `from app.schemas.return_basis import ReturnBasis`.
4. `app/services/diagnostics_engine.py` — remove `ReturnBasis` from the risk
   import block (L9); add it to the existing
   `from app.schemas.return_basis import ReturnBasisEvidence` line (L40).
5. Emit the "schema hook fired, no mirror owed" contract note (see § Contract).

### Stage T-43.2.2 — create `analytics/factor_model.py`, move internals
1. New file `app/analytics/factor_model.py` — docstring + import block + the 12
   symbols from § Final shape, each body copied verbatim, only the two
   top-level renames (`_fit_factor_model` -> `fit_factor_model`,
   `_orthogonalize_factors_window` -> `orthogonalize_factors_window`).
2. `app/analytics/risk.py` — delete the moved spans: L65-77
   (`UcitsCandidateMapping`), L97-133 (`FactorDefinition`,
   `DEFAULT_FACTOR_DEFINITIONS`, `FACTOR_PROXY_MAP`, `FACTOR_KEY_MAP`) — **keep
   L134 `FACTOR_BY_LABEL`**, L139-143 (`ROLLING_RIDGE_FLOOR` + comment),
   L1685-1695 (threshold + comment), L1698-1750 (orthogonalize + fit),
   L2211-2244 (linalg trio) — **keep L2247-2255 `_series_to_returns`**.
3. `app/analytics/risk.py` — add, in the import block (must sit above L134 where
   `FACTOR_BY_LABEL` is derived):
   `from app.analytics.factor_model import (UcitsCandidateMapping, FactorDefinition,
   DEFAULT_FACTOR_DEFINITIONS, FACTOR_PROXY_MAP, ROLLING_RIDGE_FLOOR,
   fit_factor_model, orthogonalize_factors_window)`. Add `FACTOR_KEY_MAP` to that
   list **only if** a residual risk.py reference exists (the dead-code gate will
   flag an unused import — recon found none).
4. `app/analytics/risk.py` — `_build_rolling_factor_loadings` L1781-1782: update
   the two call sites to the un-prefixed `orthogonalize_factors_window` /
   `fit_factor_model` (now module-level imported names).
5. `app/analytics/risk.py` — rename `_selected_history_return_series` ->
   `selected_history_return_series` at the def (L871) and its 4 internal call
   sites (L1384, L1622, L1994, L2043). `_series_to_returns` unchanged.
6. Record the AC3 disposition in the T-43.2.2 ticket / story Notes: "linalg trio
   moved to factor_model.py, no non-factor caller remained".
7. Run `python scripts/detect_deadcode.py --strict` — no orphaned import in
   risk.py (`dataclass` still used by `SelectedHistoryPriceSeries`; `Literal`
   still used widely).

### Stage T-43.2.3 — rewire the 4 consumers
1. `app/analytics/attribution.py` L28-37 — split the risk import: keep
   `from app.analytics.risk import selected_history_return_series`; add
   `from app.analytics.factor_model import (DEFAULT_FACTOR_DEFINITIONS,
   FACTOR_KEY_MAP, FACTOR_PROXY_MAP, ROLLING_RIDGE_FLOOR, fit_factor_model,
   orthogonalize_factors_window)`. Call-site renames: L133
   `_selected_history_return_series` -> `selected_history_return_series`; L198
   `_orthogonalize_factors_window` -> `orthogonalize_factors_window`; L205
   `_fit_factor_model` -> `fit_factor_model`. L55-56, L140, L178, L215 unchanged
   (names identical, module differs). AC3 check: attribution.py now imports zero
   `_`-prefixed names from risk.py.
2. `app/services/stress_engine.py` L18-23 — move `FACTOR_PROXY_MAP` to
   `from app.analytics.factor_model import FACTOR_PROXY_MAP`; keep
   `STRESS_SCENARIOS`, `build_statistical_factor_model`, `build_stress_scenarios`
   from `app.analytics.risk`.
3. `app/services/attribution_engine.py` L21 —
   `from app.analytics.risk import FACTOR_PROXY_MAP` becomes
   `from app.analytics.factor_model import FACTOR_PROXY_MAP`. Use L90 unchanged.
4. `app/services/diagnostics_engine.py` L4-25 — move `FACTOR_PROXY_MAP` (L6) to
   `from app.analytics.factor_model import FACTOR_PROXY_MAP`; keep everything
   else in the risk block.
5. Pre-existing stale docstring: `attribution.py` L1-22 and `risk.py:1703`
   mention a deleted `_orthogonalize_factor_series` — **out of scope**, do not
   act (recon; noted for docs lane awareness only).

---

## Test edit list

One test order, dispatched **after** the backend order reports (the retargets
need the final imported names). Owner: test lane. File:
`services/quant-engine/app/tests/test_analytics.py` unless noted.

**Retargets (the "~4 monkeypatch targets"):**
1. L15 — `from app.analytics.risk import DEFAULT_FACTOR_DEFINITIONS, ...`: move
   `DEFAULT_FACTOR_DEFINITIONS` to `from app.analytics.factor_model import
   DEFAULT_FACTOR_DEFINITIONS` (own line, or merged with L6's
   `from app.analytics import risk as risk_module` companion). This fixes 23 of
   the 25 `DEFAULT_FACTOR_DEFINITIONS` use sites in one edit
   (L1050, L1533, L2283, L4795, L4826, L4879, L5270, L5376, L5436, L5506, L5604,
   L5630, L5656, L5876, L5926, L5952, L6161, L6274, L7810, L7867, L8247, L8288).
   `build_statistical_factor_model` / `build_stress_scenarios` stay on the risk
   import line.
2. L5298, L7907 — `monkeypatch.setattr(risk_module, "DEFAULT_FACTOR_DEFINITIONS", ...)`:
   **UNCHANGED**. risk.py holds `DEFAULT_FACTOR_DEFINITIONS` as a re-imported
   module global that `_build_rolling_factor_loadings` (stays in risk.py) reads
   live at L1767 — the patch still binds.
3. L7914 — `real_fit = risk_module._fit_factor_model` -> `risk_module.fit_factor_model`.
4. L7924 — `monkeypatch.setattr(risk_module, "_fit_factor_model", nan_first_fit)`
   -> `"fit_factor_model"`. Still targets the `risk_module` binding (the consumer
   `_build_rolling_factor_loadings` resolves the name against risk.py's module
   global at call time — patch bites).
5. L7992 — `risk_module._orthogonalize_factors_window(...)` ->
   `risk_module.orthogonalize_factors_window(...)`.
6. L17-18 — **UNCHANGED**. recon confirms no symbol on L17 (`_apply_mapping_hard_caps`,
   `_build_factor_risk_contributions`, `_build_shared_sector_overlap`,
   `_classify_volatility_regime`, `_compute_covariance_matrix`,
   `_fund_category_proxy_sector`, `_mapping_match_label`) or L18
   (`_portfolio_time_weighted_return_series`) is in the moving set. **Flag for
   the reviewer:** AC5's "The test_analytics.py:17-18 private-symbol imports are
   updated to the new module" is a mis-statement — there is nothing to update
   there.

**`test_attribution.py` (AC5 gap — recon; not named in AC5):**
7. L416 — `real_fit = attr_mod._fit_factor_model` -> `attr_mod.fit_factor_model`.
8. L426 — `monkeypatch.setattr(attr_mod, "_fit_factor_model", fake_fit)` ->
   `"fit_factor_model"`.

**`test_stress_engine.py` L13** — `from app.analytics.risk import STRESS_SCENARIOS`:
**UNCHANGED** (STRESS_SCENARIOS stays in risk.py).

**Two new tests in `test_analytics.py`:**
9. **AC2 pin** — import `ReturnBasis` from `app.schemas.return_basis`; assert
   `typing.get_args(ReturnBasis) == ("portfolio_value", "market_value",
   "market_value_trade_neutral")`; assert it is the same object that
   `app.analytics.risk`, `app.analytics.attribution`, and
   `app.services.diagnostics_engine` bind (identity checks). (factor_model.py
   does not import `ReturnBasis` — do not assert on it there.)
10. **AC5 identity** — assert `risk_module.fit_factor_model is
    factor_model.fit_factor_model` and `risk_module.orthogonalize_factors_window
    is factor_model.orthogonalize_factors_window` (and, optionally,
    `attribution.fit_factor_model is factor_model.fit_factor_model`). This proves
    the retargeted monkeypatch in #4 lands on the object
    `_build_rolling_factor_loadings` actually calls.

**Behaviour-neutrality proof (must stay green in substance, not just pass):**
the factor-model, factor-shift, model-reliability and rolling-factor-loadings
blocks of `test_analytics.py` (incl. `test_orthogonalize_factors_window_reports_dropped_duplicate`,
def L7988); all of `test_attribution.py`; all `test_stress*.py`.

---

## Docs edit list (T-43.2.4)

Docs lane, after the reviewer PASS. Driven by recon's four contract_notes.

1. `docs/finance/financial-methodology.md` §Statistical Factor Model
   (~L1117-1129) — re-point "implemented in `risk.py`" / "the top of `risk.py`"
   phrasing for the moved symbols (`fit_factor_model`,
   `orthogonalize_factors_window`, `FactorDefinition`,
   `DEFAULT_FACTOR_DEFINITIONS`, `FACTOR_PROXY_MAP`/`FACTOR_KEY_MAP`,
   `ROLLING_RIDGE_FLOOR`) to `analytics/factor_model.py`. **Leave** the
   §Portfolio Return Methodology references (L468-470) to
   `_portfolio_time_weighted_return_series` and `factor_model_methodology()` —
   those symbols stay in `risk.py`.
2. `docs/architecture/system-architecture.md` — add `analytics/factor_model.py`
   to the analytics module inventory; note the transitional shape (`risk.py`
   imports it back; `build_statistical_factor_model` still owned by `risk.py`).
3. `CONTEXT.md` (repo root — a live file, exists) — add `analytics/factor_model.py`
   if it enumerates analytics modules.
4. `docs/tech-debt-register.md` row US-43.2 (L339) — correct the consumer list
   (4 cross-seam modules: attribution.py, stress_engine.py, diagnostics_engine.py,
   attribution_engine.py — not the 2 currently named); record the AC3 disposition
   (linalg trio moved) and the AC1 amendment (`selected_history_return_series`
   stayed, renamed public); mark the row **Resolved**. The L345-362
   methodology-divergence note on `attribution.py::_portfolio_return_series`
   stays **Open** — separate methodology-reviewed story (story Out-of-scope).
5. `docs/product/epic-roadmap.md` — slice-log entry for US-43.2.
6. `docs/product/stories/US-43.2-extract-factor-model-internals.md` — Status ->
   Done; record the AC1 amendment + AC3 disposition + AC5 wording note in Notes.
7. `docs/product/current-product-state.md` — confirm no edit needed (verbatim
   refactor, no user-visible change).

---

## RESEARCH ruling

**The orchestrator proposes skipping quant RESEARCH mode. Confirmed — skip it —
for this slice, with conditions.**

Reasoning:
- **Guardrail #1** ("financial accuracy first; any change to analytics, a factor
  formula or trust-state logic requires reading `financial-methodology.md` first
  and updating its tests in the same pass") is not breached by a skip: this
  slice changes **no** formula, no ridge floor (`{20:1e-5, 60:1e-5, 252:1e-5}`
  moves verbatim), no factor definition, no factor member, no orthogonalisation
  order, no trust classification. It is a file move. The methodology sections it
  needs already exist (§Statistical Factor Model, §Per-window orthogonalization).
  There is nothing for RESEARCH to establish.
- **The profile's routing rule** ("any change touching `analytics/` ... must go
  through the quant lane — in research mode before, audit mode after") is a
  written convention in `project.md`, phrased as operational routing — not one
  of the five numbered hard guardrails. Per PROTOCOL core, a numbered guardrail
  blocks; a pack/profile convention does not, but the softening must be
  surfaced. It is surfaced in the report block's `risks:`.
- The **AUDIT** half of that rule **is** honoured — quant-audit runs as the
  financial gate (see next section) and is the mechanism that proves the move
  was verbatim.

**Conditions on the skip:**
1. The quant-audit MUST perform a char-level diff of every moved region against
   the pre-move git blob and confirm byte-identical logic (see § Quant AUDIT
   scope). If that diff shows any non-mechanical change, the slice stops and
   RESEARCH is dispatched.
2. No methodology-doc edit beyond re-pointing implementation-location strings
   (T-43.2.4 item 1). Any change to a *formula description* triggers RESEARCH.
3. If the build lane finds a moved function cannot be relocated without a
   signature or body change (e.g. a shared helper needs adjusting), it stops and
   RESEARCH is dispatched before proceeding.

---

## Quant AUDIT scope

quant-audit (AUDIT mode) is **planned and runs first among the gates** (analytics/
touched; gates.md §1 — "where a change touches analytics the quant gate runs
first, because the others are meaningless if it fails").

**External anchor (gates.md §2):** the pre-move committed source —
`git show <merge-base>:services/quant-engine/app/analytics/risk.py`. A
verbatim-relocation audit's independent reference is the prior blob, char-compared.
State in `verification.detail`: "anchor = pre-move git blob of risk.py; verified
by char-diff of each moved span".

**The auditor must check:**
1. **Verbatim char-diff** of every moved region: `UcitsCandidateMapping` (was
   risk.py 65-77), `FactorDefinition` (97-111), `DEFAULT_FACTOR_DEFINITIONS`
   (113-130 — all 17 tuples, every proxy string, every `orthogonalization_order`
   int), `FACTOR_PROXY_MAP`/`FACTOR_KEY_MAP` (132-133), `ROLLING_RIDGE_FLOOR`
   (143 — `{20:1e-5, 60:1e-5, 252:1e-5}`),
   `ORTHOGONALIZATION_ZERO_RESIDUAL_THRESHOLD` (1695 — `1e-12`),
   `orthogonalize_factors_window` (1698-1738), `fit_factor_model` (1741-1750),
   `_least_squares` / `_solve_linear_system` / `_dot` (2211-2244). Bodies
   identical modulo (a) the two `def`-name underscore drops, (b) nothing else —
   no whitespace-only "cleanup", no numeric literal touched.
2. **Backend goldens byte-identical** — `python scripts/run_all_tests.py` green
   including the golden-regeneration step reporting no drift.
3. **`git diff --exit-code apps/desktop/src/test/dashboardGoldens.ts`** — clean.
4. **Behaviour-neutral proof blocks green in substance** (same assertions, not
   just passing): `test_analytics.py` factor-model / factor-shift /
   model-reliability / rolling-factor-loadings blocks +
   `test_orthogonalize_factors_window_reports_dropped_duplicate`;
   `test_attribution.py` in full; `test_stress*.py` in full.
5. **Trust honesty** — `apply_return_basis_status_to_factor_model` /
   `apply_return_basis_status_to_model_reliability` unchanged and still in
   `risk.py`; no rung collapsed or reclassified by the move.
6. **`selected_history_return_series`** rename is name-only — body (L871-873) and
   `_series_to_returns` (L2247-2255) byte-identical to pre-move.

---

## Lane split and dispatch order

| # | Lane / mode | Order | Depends on |
|---|---|---|---|
| 1 | backend (`backend-engineer`) | T-43.2.1 + T-43.2.2 + T-43.2.3 source edits, in that stage order — § Backend edit list | — |
| 2 | test (`test-engineer`) | T-43.2.3 test retargets + 2 new tests + test_attribution.py L416/L426 — § Test edit list | 1 reported |
| 3 | quant-audit (`quant-analyst` AUDIT) | financial gate — § Quant AUDIT scope | 1, 2 green |
| 4 | integration (`tech-lead` INTEGRATION) | engineering gate — contract alignment, no duplicated formula, router unaffected | 3 PASS |
| 5 | review (`reviewer`) | acceptance gate — AC1 (amended list), AC2-AC6 | 4 PASS |
| 6 | docs (`docs-engineer`) | T-43.2.4 close-out — § Docs edit list | 5 PASS |
| 7 | human | `python scripts/run_all_tests.py`, then commit | 6 |

**Granularity note:** stages T-43.2.1/.2/.3 are given as one backend order
because they are one engineer's coherent refactor of `risk.py` + its consumers,
and splitting them across three orders multiplies line-shift reconciliation. If
the orchestrator wants finer checkpoints, split at the ticket boundaries — each
stage is written to end on a green suite. The AC2 pin test (story T-43.2.1
"Add the AC2 test") is assigned to the **test** order (item 9), not backend.

**Verification each impl lane runs:** `python scripts/run_all_tests.py` (green,
incl. dead-code strict + `tsc --noEmit`); `git diff --exit-code
apps/desktop/src/test/dashboardGoldens.ts`.
