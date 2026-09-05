REPORT 2026-09-02-us43.2-factor-model-module/06
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd C:\projects\investments\portfolio && python scripts/run_all_tests.py
  result:    PASS
  detail:    "All tests passed." backend pytest 982 passed; desktop vitest 40 files / 359 passed; tsc --noEmit green; dead-code strict (ruff+vulture+knip) clean. git diff --exit-code apps/desktop/src/test/dashboardGoldens.ts EMPTY (exit 0). Independent structural checks: `python -c "import app.analytics.risk, app.analytics.factor_model, app.analytics.attribution"` -> "IMPORT OK" (no circular-import error at module load).

contract_notes:
  - docs/finance/financial-methodology.md §Statistical Factor Model still credits risk.py for the moved factor-model symbols; repoint to analytics/factor_model.py in T-43.2.4 (not an integration blocker).
  - docs/architecture/system-architecture.md analytics module inventory does not list analytics/factor_model.py (T-43.2.4, not an integration blocker).
  - .claude/skills/write-story/SKILL.md factor_model.py row was already added by the test lane; T-43.2.4 owns only finalising its wording (not a blocker).

pack_corrections:
  - none

handoff:
  - No change requests. Slice clears the engineering gate; proceed to review (acceptance gate) against AC1 (amended list) and AC2-AC6.

risks:
  - AC1 text lists selected_history_return_series as a symbol factor_model.py "defines"; the design amended this (it stays in risk.py, renamed public, to avoid an import cycle). Engineering is sound — the reviewer grades AC1 against 02 § Cycle decision's amended list.
  - AC5 text names only test_analytics.py:17-18, not test_attribution.py L416/L426; those retargets were done per 02 § Test edit list. AC5 wording is under-inclusive, not the work — flag for the reviewer.
  - Pre-existing stale docstring mentions of a deleted _orthogonalize_factor_series (attribution.py header, risk.py docstring) are untouched, out of scope per 02 — noted for docs-lane awareness only.

---

## Orchestrator brief

Engineering gate over the US-43.2 factor-model relocation. **Verdict: PASS.** No change requests.

- **Contract alignment — PASS.** The only schema-facing change is `schemas/return_basis.py` gaining `ReturnBasis = Literal[...]`. Confirmed by grep (not just the backend lane's assertion): bare `ReturnBasis` appears only at its new definition and one prose comment in `reconciliation.py:569`; zero refs in `apps/desktop/src/`, zero in `docs/contracts/`. It is a function-parameter annotation, never a Pydantic model field — no `types.ts` / contract-doc mirror owed. No route response shape changed; `dashboardGoldens.ts` diff empty.
- **Import structure — PASS.** `factor_model.py` imports only `{__future__, dataclasses}` — nothing from `risk.py`. `risk.py` imports 7 names back; `FACTOR_KEY_MAP` correctly not re-imported (no consumer). `return_basis.py` imports only `typing` + `pydantic`. Live `import` of all three modules from `services/quant-engine` succeeds — acyclic proven at load, not just on paper.
- **No leaked private names — PASS.** `grep "from app.analytics.risk import _"` over non-test `app/` returns only pre-existing unrelated symbols (`_build_wealth_index`, `_build_drawdown_from_return_index`). Zero factor-model private names imported anywhere. `_least_squares` / `_solve_linear_system` / `_dot` exist only in `factor_model.py`, not re-exported.
- **No duplicated formula — PASS.** risk.py diff shows the 12 moved symbols *deleted*, not copied. Each moved symbol has exactly one `def`/assignment site (in `factor_model.py`). `selected_history_return_series` / `_series_to_returns` exist only in `risk.py`.
- **Full suite — PASS.** 982 backend + 359 frontend, tsc + dead-code strict green, golden diff empty. Ran it myself.
- **Scope containment — PASS.** `git diff` touches exactly the 10 listed files and nothing else. No US-43.1 / Epic 43 drift present in the tree.
- Sections below: Findings by DoD item.

---

## Findings by DoD item

### 1. Contract alignment — PASS

`git diff services/quant-engine/app/schemas/return_basis.py`: adds a top-level
`ReturnBasis = Literal["portfolio_value", "market_value", "market_value_trade_neutral"]`
after the existing Literal family, with the risk.py explanatory comment ported
verbatim. No `class` added, no `BaseModel` field.

Verified the backend lane's contract_note ("schema hook fired, no mirror owed")
is **correct, not merely asserted**:

- `grep -rn "\bReturnBasis\b" services/quant-engine/app/schemas/` → only the new
  definition (`return_basis.py:28`) and a prose comment (`reconciliation.py:569`,
  no code).
- `grep -rn "\bReturnBasis\b" docs/contracts/` → nothing.
- `grep -rn "\bReturnBasis\b" apps/desktop/src/` → nothing.

`ReturnBasis` is only ever used as `return_basis: ReturnBasis = "portfolio_value"`
parameter annotations in `build_*` / `_build_*` signatures. It is never
serialized. No `types.ts` mirror, no `docs/contracts/<area>-fields.md` field is
owed. `dashboardGoldens.ts` diff is empty (exit 0). No route response shape
changed — `api/main.py` and `api/routes/**` are not in the diff.

### 2. Import structure — PASS

`factor_model.py` import block (lines 15-17): `from __future__ import annotations`
+ `from dataclasses import dataclass`. Nothing from `risk.py`, nothing from
`schemas/`. It is a pure leaf.

`risk.py` adds `from app.analytics.factor_model import (DEFAULT_FACTOR_DEFINITIONS,
FACTOR_PROXY_MAP, FactorDefinition, ROLLING_RIDGE_FLOOR, UcitsCandidateMapping,
fit_factor_model, orthogonalize_factors_window)` and `from app.schemas.return_basis
import ReturnBasis`. `FACTOR_KEY_MAP` is deliberately not re-imported (grep
confirms no residual `risk.py` reference; ruff would flag it if unused).

`schemas/return_basis.py` imports `from typing import Literal` +
`from pydantic import BaseModel, Field` only.

`cd services/quant-engine && python -c "import app.analytics.risk,
app.analytics.factor_model, app.analytics.attribution"` → `IMPORT OK`. No
circular-import error at module load. `risk.py <-> factor_model.py` is acyclic
because the back-edge does not exist.

### 3. No leaked private names — PASS

`grep -rn "from app\.analytics\.risk import _"` over `app/` (non-test):
`drawdown_engine.py` (`_build_wealth_index`), `drawdown.py`
(`_build_drawdown_from_return_index`) — both pre-existing, both symbols that
stay in `risk.py`, neither factor-model-related. Zero factor-model private
names imported anywhere. `attribution.py` now imports `fit_factor_model` /
`orthogonalize_factors_window` (public) from `factor_model.py` and
`selected_history_return_series` (public) from `risk.py` — no `_`-prefixed
cross-seam import remains (AC3 satisfied).

`_least_squares` / `_solve_linear_system` / `_dot`: single `def` site each, all
in `factor_model.py`, underscore kept, not in `risk.py`'s import-back list, not
referenced by any other module.

### 4. No duplicated formula — PASS

`git diff risk.py` shows the moved spans as pure deletions:
`UcitsCandidateMapping`, `FactorDefinition`, `DEFAULT_FACTOR_DEFINITIONS`,
`FACTOR_PROXY_MAP`, `FACTOR_KEY_MAP`, `ROLLING_RIDGE_FLOOR`,
`ORTHOGONALIZATION_ZERO_RESIDUAL_THRESHOLD`, `_orthogonalize_factors_window`,
`_fit_factor_model`, `_least_squares`, `_solve_linear_system`, `_dot` — all
removed, none left behind. `FACTOR_BY_LABEL` (line 134, stays) is correctly
re-derived from the imported `DEFAULT_FACTOR_DEFINITIONS`.

`grep "^def (_least_squares|_solve_linear_system|_dot|fit_factor_model|
orthogonalize_factors_window|_series_to_returns|selected_history_return_series)"`
over `app/`: each name has exactly one definition site. The linalg trio and the
two fit functions are only in `factor_model.py`; `selected_history_return_series`
and `_series_to_returns` are only in `risk.py`. No copy exists in the other
module.

### 5. Full suite + goldens — PASS

Ran `python scripts/run_all_tests.py` end to end: golden regen (no drift) →
backend pytest **982 passed** → desktop vitest **40 files / 359 passed** →
`tsc --noEmit` green → dead-code strict (ruff + vulture + knip) clean → final
line `All tests passed.`

`git diff --exit-code apps/desktop/src/test/dashboardGoldens.ts` → exit 0,
empty.

Two new tests reviewed for quality (test the contract, not the implementation):
`test_return_basis_literal_lives_in_schemas_and_is_shared_by_reference`
(test_analytics.py:8001) pins the three members and single-object identity
across `risk` / `attribution` / `diagnostics_engine`;
`test_factor_model_fit_symbols_are_shared_by_reference_across_the_seam`
(test_analytics.py:8024) pins `risk_module.fit_factor_model is
factor_model.fit_factor_model` (and `orthogonalize_factors_window`, and
`attribution.fit_factor_model`). Both would fail if a lane re-added a local
definition or the seam stopped sharing one object — real coverage.

### 6. Scope containment — PASS

`git status --porcelain` + `git diff --stat`: modified —
`analytics/risk.py`, `analytics/attribution.py`, `schemas/return_basis.py`,
`services/{attribution_engine,diagnostics_engine,stress_engine}.py`,
`tests/test_analytics.py`, `tests/test_attribution.py`,
`.claude/skills/write-story/SKILL.md`; untracked — `analytics/factor_model.py`.
That is exactly the DoD's listed set. No file outside it. The US-43.1 and
Epic 43 doc drift the order told me to ignore is not present in the working
tree (already committed), so there is nothing to exclude.

### 7. Deferred docs contract_notes — correctly not blockers

The methodology repoint, the system-architecture inventory line, and the
SKILL.md row wording are documentation lagging correct code — each is
`T-43.2.4` work, none blocks the engineering gate. The SKILL.md row itself was
already added by the test lane (its work order scoped it, and
`test_docs_paths.py::test_write_story_table_covers_every_analytics_module`
passes); only the wording finalisation is deferred.
