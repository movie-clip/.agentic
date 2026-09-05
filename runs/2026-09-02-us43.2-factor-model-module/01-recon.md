REPORT 2026-09-02-us43.2-factor-model-module/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE (read-only recon)
  result:    NOT_RUN
  detail:    Order verification field was NONE. No commands run; no files edited.

contract_notes:
  - docs/finance/financial-methodology.md §Statistical Factor Model L1117-1119 and §Portfolio Return Methodology L468-470 name `analytics/risk.py` as the implementation site for `factor_model_methodology()` and `_portfolio_time_weighted_return_series`; the §Statistical Factor Model prose (L1121-1129) attributes `FACTOR_MODEL_MIN_SHARED_OBSERVATIONS` and the rubric constants to "the top of `risk.py`". T-43.2.4 must re-point the moved symbols (fit / orthogonalize / return-series / FactorDefinition / the four constants) at `analytics/factor_model.py`. `_portfolio_time_weighted_return_series` and `factor_model_methodology()` do NOT move, so those two references stay correct.
  - docs/tech-debt-register.md row US-43.2 (L339) under-lists consumers: it names only `attribution.py:28` and `stress_engine.py:18`. Actual cross-seam importers of in-scope symbols are five modules — add `services/diagnostics_engine.py` (`FACTOR_PROXY_MAP`, `ReturnBasis`) and `services/attribution_engine.py` (`FACTOR_PROXY_MAP`). T-43.2.4 should correct the row and mark it Resolved.
  - docs/contracts/risk-fields.md L34/L88 and docs/contracts/exposure-fields.md L107-315 reference `analytics/risk.py` only for symbols that STAY (`build_stress_scenarios`, `STRESS_SCENARIOS` tuple, `build_lookthrough_*`, `build_market_overlap_summary`, `build_rolling_risk_series`). No contract-doc edit required for those. `docs/contracts/factor-drift-fields.md` / `diagnostics-fields.md` reference response field names only — unaffected.
  - No TS type / frontend change: `ReturnBasis` is a Python `Literal` used only as a function-parameter annotation (never a Pydantic model field), so serialized output is byte-identical and `apps/desktop/src/test/dashboardGoldens.ts` is untouched (AC4).

pack_corrections:
  - none

handoff:
  - Full line-level map is in the sections below; see § Moving symbols — exact spans, § Linalg trio callers (AC3), § Private refs of the moving functions, § Cross-seam importers, § ReturnBasis, § schemas/return_basis.py, § test_analytics.py sites, § Other test files, § Cycle check, § attribution.py structure.
  - AC3 DECISION INPUT: `_least_squares` / `_solve_linear_system` / `_dot` have ZERO non-factor callers anywhere. Every call site is inside `_orthogonalize_factors_window` or `_fit_factor_model` (both moving), and `_solve_linear_system` is called only by `_least_squares`. Per AC3 they MOVE to `factor_model.py`. See § Linalg trio callers.
  - CYCLE RISK: `_selected_history_return_series` (risk.py:871-873) calls the PUBLIC `select_history_price_series` (risk.py:839, stays — consumed by tests L15/L5671/L5682 and by `is_history_series_verified_adjusted` / `selected_history_price_map`). If `_selected_history_return_series` moves to `factor_model.py`, that module must import `select_history_price_series` back from `risk.py`, while `risk.py` imports `fit_factor_model` / `orthogonalize_factors_window` / `_selected_history_return_series` from `factor_model.py` → a real module-load import cycle. See § Cycle check for the three resolution shapes; design must choose.
  - `_selected_history_return_series` has NON-factor callers in risk.py that also force `risk.py` to import it back: `_benchmark_return_series` (risk.py:1622, feeds every risk/vol summary via `_paired_portfolio_and_benchmark_returns`) and `_build_position_risk_contributions` (risk.py:2043). Factor callers: `build_statistical_factor_model` (1384, stays), `_build_factor_risk_contributions` (1994, stays), `attribution.py` (133).
  - `_series_to_returns` (risk.py:2247-2255) is private and has exactly ONE caller — `_selected_history_return_series` (risk.py:873). It can travel with `_selected_history_return_series` wherever that lands.
  - `_orthogonalize_factors_window` also needs helper const `ORTHOGONALIZATION_ZERO_RESIDUAL_THRESHOLD` (risk.py:1695, sole user) to move with it.
  - `_build_rolling_factor_loadings` (risk.py:1753-1803) is NOT in the moving set (story omits it) yet it is the sole in-risk.py caller of BOTH `_orthogonalize_factors_window` (1781) and `_fit_factor_model` (1782), and it reads `DEFAULT_FACTOR_DEFINITIONS` (1767), `WINDOW_MIN_OBSERVATIONS` (1768), `ROLLING_RIDGE_FLOOR` (1769). It stays in risk.py and must import the moved names back at module level so the L7924 monkeypatch still bites (AC5). Tests call it directly as `risk_module._build_rolling_factor_loadings` at L5316, L7926, L7958, L7979.
  - CONFIRM/CORRECT story's attribution.py:28 claim: the import block is `analytics/attribution.py` L28-37 (`from app.analytics.risk import (`). Imported names (exactly): `DEFAULT_FACTOR_DEFINITIONS` (L29), `FACTOR_KEY_MAP` (L30), `FACTOR_PROXY_MAP` (L31), `ROLLING_RIDGE_FLOOR` (L32), `ReturnBasis` (L33), `_fit_factor_model` (L34), `_orthogonalize_factors_window` (L35), `_selected_history_return_series` (L36). Matches the story exactly. Use sites: L55-56 (`DEFAULT_FACTOR_DEFINITIONS`), L62 & L107 (`ReturnBasis` annotations), L133 (`_selected_history_return_series`), L140 (`FACTOR_PROXY_MAP`), L178 (`ROLLING_RIDGE_FLOOR`), L198 (`_orthogonalize_factors_window`), L205 (`_fit_factor_model`), L215 (`FACTOR_KEY_MAP`).
  - CONFIRM/CORRECT story's stress_engine.py:18 claim: block is `services/stress_engine.py` L18-23. It imports FOUR names, not two: `FACTOR_PROXY_MAP` (L19, IN SCOPE to move), `STRESS_SCENARIOS` (L20, STAYS in risk.py), `build_statistical_factor_model` (L21, STAYS), `build_stress_scenarios` (L22, STAYS). Only `FACTOR_PROXY_MAP` needs retargeting to `analytics.factor_model`. `STRESS_SCENARIOS` (risk.py:152-156) and `build_statistical_factor_model` are NOT in scope to move — story Notes L152-156 confirm risk.py keeps `build_statistical_factor_model`.
  - EXTRA consumer the story misses — `services/diagnostics_engine.py` L4-25 `from app.analytics.risk import (...)`: in-scope names are `FACTOR_PROXY_MAP` (L6) and `ReturnBasis` (L9, used at L403); everything else it imports stays in risk.py. It also already does `from app.schemas.return_basis import ReturnBasisEvidence` (L40), so after AC2 it can add `ReturnBasis` to that line.
  - EXTRA consumer the story misses — `services/attribution_engine.py:21` `from app.analytics.risk import FACTOR_PROXY_MAP` (used L90). Retarget to `analytics.factor_model`.
  - `test_attribution.py` L411-426 patches the fit helper on the CONSUMER module: `attr_mod = app.analytics.attribution`; `real_fit = attr_mod._fit_factor_model` (L416); `monkeypatch.setattr(attr_mod, "_fit_factor_model", fake_fit)` (L426). AC5 covers test_analytics.py but not this — T-43.2.3 must also retarget these two lines to whatever name `attribution.py` imports (`fit_factor_model`, or a kept `_fit_factor_model` private alias).
  - `test_stress_engine.py:13` `from app.analytics.risk import STRESS_SCENARIOS` — STRESS_SCENARIOS stays in risk.py, so NO change needed here. Confirmed.
  - test_analytics.py factor/ReturnBasis import lines: L6 `from app.analytics import risk as risk_module`; L15 `from app.analytics.risk import DEFAULT_FACTOR_DEFINITIONS, build_etf_overlap_pairs, ... ` (only `DEFAULT_FACTOR_DEFINITIONS` is in the moving set on this line; `build_statistical_factor_model` and `build_stress_scenarios` on the same line STAY). L16 (`apply_return_basis_status_*`) — STAY, no change. L17 (`_apply_mapping_hard_caps, _build_factor_risk_contributions, _build_shared_sector_overlap, _classify_volatility_regime, _compute_covariance_matrix, _fund_category_proxy_sector, _mapping_match_label`) — NONE of these move; contra story AC5's "L17-18 private-symbol imports are updated", no L17/L18 symbol is in the moving set. L18 (`_portfolio_time_weighted_return_series`) — STAYS. L19 (`from app.analytics.attribution import _portfolio_return_series`) — unaffected.
  - test_analytics.py monkeypatch / direct-ref sites on moving symbols: L5298 `monkeypatch.setattr(risk_module, "DEFAULT_FACTOR_DEFINITIONS", [MarketOnlyDefinition()])` (then L5316 calls `risk_module._build_rolling_factor_loadings`); L7907 same setattr (then L7926 calls `_build_rolling_factor_loadings`); L7914 `real_fit = risk_module._fit_factor_model`; L7924 `monkeypatch.setattr(risk_module, "_fit_factor_model", nan_first_fit)` (then L7926 `risk_module._build_rolling_factor_loadings(...)`); L7992 `risk_module._orthogonalize_factors_window(...)` direct call (test `test_orthogonalize_factors_window_reports_dropped_duplicate`, def L7988). That is the ~4 the story predicted (story's approx lines L7924 / L5298 / L7907 / L7992 all confirmed). No monkeypatch anywhere targets `FACTOR_KEY_MAP`, `FACTOR_PROXY_MAP`, `ROLLING_RIDGE_FLOOR`, `ReturnBasis`, `_selected_history_return_series`, or the linalg trio.
  - AC5 mechanics: L5298/L7907 patch a risk.py MODULE attribute read by `_build_rolling_factor_loadings` (stays in risk.py) — still works if risk.py holds `DEFAULT_FACTOR_DEFINITIONS` as a re-imported module-level name. L7924 patches `risk_module._fit_factor_model`; for it to take effect, risk.py's `_build_rolling_factor_loadings` must call it via a risk.py module-level binding (e.g. `from app.analytics.factor_model import fit_factor_model as _fit_factor_model`). L7914/L7992 read/call `risk_module._<name>` directly and BREAK unless risk.py keeps a `_fit_factor_model` / `_orthogonalize_factors_window` alias, else retarget to the factor_model module. This is the crux the AC5 identity test is meant to pin.
  - `DEFAULT_FACTOR_DEFINITIONS` references in test_analytics.py: import at L15 + 24 usage lines — L1050, L1533, L2283, L4795, L4826, L4879, L5270, L5298, L5376, L5436, L5506, L5604, L5630, L5656, L5876, L5926, L5952, L6161, L6274, L7810, L7867, L7907, L8247, L8288 (25 sites total; story said "~25"). All but L5298 & L7907 use the name bound by the L15 import, so retargeting L15 to `analytics.factor_model` fixes them in one edit.
  - `schemas/return_basis.py` current contents (43 lines): module-level `Literal` aliases `ReturnBasisContract` (L6), `ReturnBasisPathTrust` (L7), `ReturnBasisVerificationStatus` (L8), `ReturnBasisEconomicBasis` (L9), `ReturnBasisConstructionMethod` (L10-16); Pydantic models `ReturnBasisEvidence` (L19) plus a large `PortfolioProof*` family (L29-217). There is NO bare name `ReturnBasis` — no collision; the execution-basis literal slots in as a new top-level `ReturnBasis = Literal[...]` alongside the family. Imports only `typing` and `pydantic` (L1-3) — see § Cycle check.
  - CONFIRM attribution.py structure: import block L28-37; `_portfolio_return_series` def L59-99 (the US-34.8-divergent one the story's Out-of-scope L145-148 and tech-debt L345-362 say must NOT be touched); `build_factor_attribution` def L102-336; `_unavailable_response` L339-348. The three moved factor helpers are used only inside `build_factor_attribution` (and `_FACTOR_LABEL`/`_FACTOR_ORDER` module dicts at L55-56 from `DEFAULT_FACTOR_DEFINITIONS`). `_portfolio_return_series` references none of the moving symbols.
  - Stale-docstring note (not in scope, but design will read it): `analytics/attribution.py` module docstring L2-7 and `risk.py:1703` both mention `_orthogonalize_factor_series`, a full-series variant that was DELETED in US-23.2 (tech-debt-register L243). No such symbol exists; do not try to move it.
  - `FACTOR_BY_LABEL` (risk.py:134) and `FACTOR_MODEL_MIN_SHARED_OBSERVATIONS` (risk.py:226) are factor-definition-derived constants NOT in the story's moving list. `FACTOR_BY_LABEL` is used only by `_build_factor_collinearity_warnings` (risk.py:1351-1352, stays); `FACTOR_MODEL_MIN_SHARED_OBSERVATIONS` only by `build_statistical_factor_model` (1390, stays). Both can stay in risk.py; design should confirm whether co-locating them in factor_model.py is cleaner given they read `DEFAULT_FACTOR_DEFINITIONS`.
  - CONTEXT.md exists at repo root (`C:\projects\investments\portfolio\CONTEXT.md`) — T-43.2.4's "confirm CONTEXT.md" is a live file, not a lazy-created stub as CLAUDE.md implies.

risks:
  - The story's moving list includes `_selected_history_return_series` but that function is genuinely multi-concern (benchmark return series + position risk contributions are non-factor callers). Moving it is defensible only if the design accepts risk.py importing it back at 4 sites AND resolves the `select_history_price_series` back-import cycle. An alternative the design may prefer — leave `_selected_history_return_series` + `_series_to_returns` in risk.py and have `factor_model.py` / `attribution.py` import them from risk.py — is not what AC1 lists. Flagging as a design decision, not resolving it (non-goal).
  - I did not find an explicit standalone "row US-43.2" table entry beyond docs/tech-debt-register.md L339 (the Epic 43 relocation table) and the related L345-362 methodology-divergence note; if T-43.2.4 expects a separate register row it may need creating, not just editing.
  - `apply_return_basis_status_to_factor_model` / `apply_return_basis_status_to_model_reliability` (risk.py:1000, 1014; imported by diagnostics_engine.py L11-12 and test_analytics.py L16) were not deep-read — they are not in the moving set and their names imply schema-status mutation, but the design should spot-check they reference no `_private` moving symbol before finalising the risk.py import-back list.
  - Line numbers are from the working tree at recon time (risk.py = 2296 lines; tech-debt register says 2,295). Any edit landed before T-43.2.2 shifts them.

---

## Orchestrator brief

Recon for US-43.2 (move factor-model internals out of `analytics/risk.py` into
`analytics/factor_model.py`; move the `ReturnBasis` execution-basis `Literal`
into `schemas/return_basis.py`). Read-only, no verification. Every finding is a
`file:line`. The sections below are the line-level map the design and build
lanes work from.

- **§ Moving symbols — exact spans** — file:line + body span for each named symbol.
- **§ Linalg trio callers (AC3)** — every caller of `_least_squares` / `_solve_linear_system` / `_dot`, classified. Verdict: no non-factor caller → they move.
- **§ Private refs of the moving functions** — what each of the three fit/orthogonalize/return-series functions reaches for.
- **§ Cross-seam importers** — the five app/ modules importing in-scope symbols from risk.py, with in-scope vs stays split. Story lists two; there are five.
- **§ ReturnBasis** — every importer of the bare `ReturnBasis` name (2 outside risk.py) + use sites.
- **§ schemas/return_basis.py** — current contents; no `ReturnBasis` collision.
- **§ test_analytics.py sites** — import lines, the 4 monkeypatch/direct-ref sites on moving symbols, the 25 `DEFAULT_FACTOR_DEFINITIONS` sites.
- **§ Other test files** — test_attribution.py (misses AC5 coverage), test_stress_engine.py (no change needed).
- **§ Cycle check** — definitive: `schemas/return_basis.py` is acyclic; `risk.py <-> factor_model.py` is acyclic ONLY for the fit/orthogonalize pair; `_selected_history_return_series` moving introduces a cycle via `select_history_price_series`.
- **§ attribution.py structure** — import block range, `_portfolio_return_series` / `build_factor_attribution` spans; the reconciliation function is untouched.

---

## Moving symbols — exact spans

All in `services/quant-engine/app/analytics/risk.py`.

| Symbol | Decl line | Body span | Notes |
|---|---|---|---|
| `ReturnBasis` (execution-basis `Literal`) | 62 | 62 (single line; explanatory comment L52-61) | AC2 target = `schemas/return_basis.py`. |
| `FactorDefinition` (frozen dataclass) | 98 (decorator L97) | 97-111 | 12 fields, ends `description: str` L111. |
| `DEFAULT_FACTOR_DEFINITIONS` | 113 | 113-130 | 17-tuple of `FactorDefinition`; closing `)` L130. Depends on `FactorDefinition` + `UcitsCandidateMapping` (L65-77, NOT in story's list — see note). |
| `FACTOR_PROXY_MAP` | 132 | 132 | `{label: us_proxy}` comprehension over `DEFAULT_FACTOR_DEFINITIONS`. |
| `FACTOR_KEY_MAP` | 133 | 133 | `{label: key}` comprehension. |
| `ROLLING_RIDGE_FLOOR` | 143 | 143 (comment L139-142) | `{20:1e-5,60:1e-5,252:1e-5}`. |
| `_selected_history_return_series` | 871 | 871-873 | calls `select_history_price_series` (stays) + `_series_to_returns`. |
| `_orthogonalize_factors_window` | 1698 | 1698-1738 | needs `ORTHOGONALIZATION_ZERO_RESIDUAL_THRESHOLD` (L1695), `_least_squares`, `_dot`. |
| `_fit_factor_model` | 1741 | 1741-1750 | needs `_least_squares`, `_dot`. |
| `_least_squares` | 2211 | 2211-2220 | calls `_solve_linear_system`. |
| `_solve_linear_system` | 2223 | 2223-2240 | leaf. |
| `_dot` | 2243 | 2243-2244 | leaf. |
| `_series_to_returns` (travels with `_selected_history_return_series`) | 2247 | 2247-2255 | sole caller = risk.py:873. |
| `ORTHOGONALIZATION_ZERO_RESIDUAL_THRESHOLD` (travels with orthogonalize) | 1695 | 1695 | sole user = `_orthogonalize_factors_window` L1734. |

`UcitsCandidateMapping` (risk.py:65-77, frozen dataclass) is a field type inside
`FactorDefinition` and `DEFAULT_FACTOR_DEFINITIONS`. It is NOT in the story's
moving list but `factor_model.py` will need it importable (many `risk.py`
UCITS-scoring helpers, L234-548, also consume it and stay). Design must decide:
import `UcitsCandidateMapping` from risk.py into factor_model.py, or leave
`DEFAULT_FACTOR_DEFINITIONS` construction able to see it. This is a fourth
back-import edge to weigh in the cycle analysis.

## Linalg trio callers (AC3)

Exhaustive — grep of `_least_squares` / `_solve_linear_system` / `_dot(` over all
of `app/**/*.py` (non-test and test):

| Callee | Call site | Enclosing fn | Class |
|---|---|---|---|
| `_least_squares` | risk.py:1731 | `_orthogonalize_factors_window` | factor-model (moving) |
| `_least_squares` | risk.py:1743 | `_fit_factor_model` | factor-model (moving) |
| `_solve_linear_system` | risk.py:2220 | `_least_squares` | factor-model (transitive) |
| `_dot` | risk.py:1732 | `_orthogonalize_factors_window` | factor-model (moving) |
| `_dot` | risk.py:1744 | `_fit_factor_model` | factor-model (moving) |

No other file in `app/` references any of the three. **No non-factor caller
remains in risk.py.** Per AC3 the trio (and `_solve_linear_system` with it) move
to `factor_model.py`; risk.py does not need to import them back.

## Private refs of the moving functions

- `_orthogonalize_factors_window` → `ORTHOGONALIZATION_ZERO_RESIDUAL_THRESHOLD` (const L1695), `_least_squares` (L2211), `_dot` (L2243). All move / travel with it. Self-contained after move.
- `_fit_factor_model` → `_least_squares` (L2211), `_dot` (L2243). Self-contained after move.
- `_selected_history_return_series` → `select_history_price_series` (PUBLIC, risk.py:839 — **stays in risk.py**), `_series_to_returns` (risk.py:2247 — private, sole caller, can travel). The `select_history_price_series` dependency is the cycle source (see § Cycle check).

## Cross-seam importers (all of app/, non-test)

| Module | Import line | In-scope names (action) | Names that STAY (no change) |
|---|---|---|---|
| `analytics/attribution.py` | L28-37 | `DEFAULT_FACTOR_DEFINITIONS`, `FACTOR_KEY_MAP`, `FACTOR_PROXY_MAP`, `ROLLING_RIDGE_FLOOR`, `ReturnBasis`, `_fit_factor_model`, `_orthogonalize_factors_window`, `_selected_history_return_series` → repoint to `analytics.factor_model` (+ `ReturnBasis` to `schemas.return_basis`) | — |
| `services/stress_engine.py` | L18-23 | `FACTOR_PROXY_MAP` → repoint to `analytics.factor_model` | `STRESS_SCENARIOS` (risk.py:152-156), `build_statistical_factor_model`, `build_stress_scenarios` |
| `services/diagnostics_engine.py` | L4-25 | `FACTOR_PROXY_MAP` (L6), `ReturnBasis` (L9) → repoint | `COLLINEARITY_WARNING_THRESHOLD`, `RISK_CONTRIBUTION_WINDOW_DAYS`, `ROLLING_WINDOWS`, `WINDOW_MIN_OBSERVATIONS`, `apply_return_basis_status_to_factor_model`, `apply_return_basis_status_to_model_reliability`, `build_factor_exposures`, `build_factor_registry`, `build_factor_shift_diagnostics`, `build_model_reliability_snapshot`, `build_portfolio_risk_summary`, `build_relative_risk_summary`, `build_risk_contribution_breakdown`, `build_rolling_risk_series`, `build_statistical_factor_model`, `build_stress_scenarios`, `build_volatility_regime_payload`, `factor_model_methodology` |
| `services/attribution_engine.py` | L21 | `FACTOR_PROXY_MAP` → repoint | — |

`STRESS_SCENARIOS` / `build_statistical_factor_model` are OUT of scope to move
(story Notes L152-156). risk.py keeps `build_statistical_factor_model` and
imports `_selected_history_return_series` (4 sites: L1384, L1622, L1994, L2043),
`_fit_factor_model` + `_orthogonalize_factors_window` (via
`_build_rolling_factor_loadings` L1781-1782), `FACTOR_PROXY_MAP` (L1388),
`DEFAULT_FACTOR_DEFINITIONS` (~30 sites), `FactorDefinition` (type hints L247+),
`ROLLING_RIDGE_FLOOR` (L1769) back from `factor_model.py`.

## ReturnBasis

Bare-name `ReturnBasis` (exact word) across app/:

| Location | Kind |
|---|---|
| risk.py:62 | definition (moving to schemas/return_basis.py) |
| risk.py:551, 572, 804, 876, 1206, 1381, 1542, 1552 | param annotations in `build_*` / `_build_*` fns that stay in risk.py → risk.py imports `ReturnBasis` from `schemas.return_basis` |
| analytics/attribution.py:33 (import), 62, 107 | import + 2 annotation use sites |
| services/diagnostics_engine.py:9 (import), 403 | import + 1 annotation use site |
| schemas/reconciliation.py:569 | prose comment only — not code, no change |

No test file imports the bare `ReturnBasis` (test_correlation_engine.py:282
`class TestReturnBasis` is an unrelated test-class name).

## schemas/return_basis.py — current contents

43 lines. `from typing import Literal` (L1), `from pydantic import BaseModel,
Field` (L3). Module-level `Literal` aliases: `ReturnBasisContract` (L6),
`ReturnBasisPathTrust` (L7), `ReturnBasisVerificationStatus` (L8),
`ReturnBasisEconomicBasis` (L9), `ReturnBasisConstructionMethod` (L10-16).
Models: `ReturnBasisEvidence` (L19-26), then `PortfolioProof*` /
`PortfolioCorporateAction*` family (L29-217). **No bare `ReturnBasis` name
exists → no collision.** The execution-basis literal adds as a new top-level
`ReturnBasis = Literal["portfolio_value", "market_value",
"market_value_trade_neutral"]`.

## test_analytics.py sites

- Imports: L6 `from app.analytics import risk as risk_module`; L15 `from app.analytics.risk import DEFAULT_FACTOR_DEFINITIONS, ...` (moving name on this line: `DEFAULT_FACTOR_DEFINITIONS` only; `build_statistical_factor_model`, `build_stress_scenarios` stay); L16-19 carry no moving symbol.
- Monkeypatch / direct-ref on moving symbols (the "~4" AC5 sites): L5298 `monkeypatch.setattr(risk_module, "DEFAULT_FACTOR_DEFINITIONS", ...)`; L7907 same; L7914 `real_fit = risk_module._fit_factor_model`; L7924 `monkeypatch.setattr(risk_module, "_fit_factor_model", nan_first_fit)`; L7992 `risk_module._orthogonalize_factors_window(...)`. Each is followed by a call into `risk_module._build_rolling_factor_loadings` (L5316 / L7926 / L7958 / L7979) which STAYS in risk.py — so risk.py must hold these as module-level re-imported names for the patches to bind.
- No monkeypatch targets `FACTOR_KEY_MAP`, `FACTOR_PROXY_MAP`, `ROLLING_RIDGE_FLOOR`, `ReturnBasis`, `_selected_history_return_series`, `_least_squares`, `_solve_linear_system`, `_dot`.
- `DEFAULT_FACTOR_DEFINITIONS` — 25 sites: import L15; usages L1050, L1533, L2283, L4795, L4826, L4879, L5270, L5298, L5376, L5436, L5506, L5604, L5630, L5656, L5876, L5926, L5952, L6161, L6274, L7810, L7867, L7907, L8247, L8288. Only L5298 & L7907 are `risk_module` setattrs; the rest resolve through the L15 import binding.
- `STRESS_SCENARIOS` referenced in a comment at test_analytics.py:6219 only (no import; symbol stays anyway).

## Other test files

- `test_attribution.py`: L411 `from app.analytics import attribution as attr_mod`; L416 `real_fit = attr_mod._fit_factor_model`; L426 `monkeypatch.setattr(attr_mod, "_fit_factor_model", fake_fit)`. Patches the name as imported into `attribution.py`. T-43.2.3 must retarget both to the name `attribution.py` ends up importing. AC5 as written only mentions test_analytics.py.
- `test_stress_engine.py:13` `from app.analytics.risk import STRESS_SCENARIOS` — STRESS_SCENARIOS stays → no change.
- `test_analytics.py` also calls `risk_module._build_position_risk_contributions` (L5797, L5803), `risk_module._build_rolling_factor_loadings` (see above), `mocker.spy(risk_module, "_portfolio_time_weighted_return_series")` (L8238, L8279) — all on symbols that STAY.

## Cycle check — definitive

1. `schemas/return_basis.py` imports only `typing` + `pydantic` (L1-3). Adding
   `ReturnBasis` there and importing it into `risk.py`, `factor_model.py`,
   `attribution.py`, `diagnostics_engine.py` is **acyclic** — `schemas/` never
   imports `analytics/`. Safe. (`analytics` → `schemas` is the sanctioned
   direction per project profile L98-104.)

2. `factor_model.py` holding `FactorDefinition`, `DEFAULT_FACTOR_DEFINITIONS`,
   the 3 maps/constants, `_fit_factor_model`, `_orthogonalize_factors_window`,
   the linalg trio, and `ORTHOGONALIZATION_ZERO_RESIDUAL_THRESHOLD` — those
   reference nothing in `risk.py`. `risk.py` importing them back while
   `factor_model.py` imports nothing from `risk.py` is **acyclic**. Confirmed.

3. `_selected_history_return_series` moving BREAKS acyclicity: its body calls
   `select_history_price_series` (risk.py:839, must stay — tests + two other
   risk.py fns consume it). `factor_model.py` would then
   `from app.analytics.risk import select_history_price_series` while `risk.py`
   does `from app.analytics.factor_model import _selected_history_return_series`
   → import cycle at module load. Resolution options (design picks one, not
   recon's call): (a) keep `_selected_history_return_series` + `_series_to_returns`
   in risk.py, have `factor_model.py` / `attribution.py` import them from risk.py;
   (b) also move `select_history_price_series` + `SelectedHistoryPriceSeries`
   (risk.py:81-86) + `_series_to_returns` to `factor_model.py` and repoint
   risk.py:89/93 + test_analytics.py:15/L5671/L5682; (c) move the price-series
   selection trio into a third leaf module both import.

4. `UcitsCandidateMapping` (risk.py:65-77) is a `FactorDefinition` field type;
   the UCITS-scoring helpers that consume it (risk.py:234-548) stay in risk.py.
   `factor_model.py` needs it importable from risk.py — another `factor_model →
   risk` edge. `UcitsCandidateMapping` itself imports nothing problematic
   (stdlib `dataclasses` only), so `factor_model → risk` for just that name is
   acyclic *iff* risk.py's import of factor-model symbols is deferred past the
   `UcitsCandidateMapping` definition — Python resolves this fine for top-level
   `from x import name` as long as neither module needs the other's not-yet-defined
   name at import time. Design should verify import ordering, or move
   `UcitsCandidateMapping` too.

## attribution.py structure

`services/quant-engine/app/analytics/attribution.py`, 349 lines:

- Module docstring L1-22 (mentions the deleted `_orthogonalize_factor_series` — stale).
- Import block L23-44; the risk.py import is L28-37.
- Module consts L47-56: `ATTRIBUTION_METHODOLOGY_NOTE` (L47), `_RECONCILIATION_TOLERANCE` (L53), `_FACTOR_LABEL` (L55), `_FACTOR_ORDER` (L56) — last two derived from `DEFAULT_FACTOR_DEFINITIONS`.
- `_portfolio_return_series` — def L59-99. **Do not touch** (US-43.2 Out-of-scope L145-148; tech-debt-register L345-362: it has diverged from `risk.py::_portfolio_time_weighted_return_series` by omitting the US-34.8 reconciliation correction — that is a separate methodology story). References none of the moving symbols.
- `build_factor_attribution` — def L102-336. Sole in-file user of `_orthogonalize_factors_window` (L198), `_fit_factor_model` (L205), `_selected_history_return_series` (L133), `FACTOR_PROXY_MAP` (L140), `FACTOR_KEY_MAP` (L215), `ROLLING_RIDGE_FLOOR` (L178).
- `_unavailable_response` — def L339-348.
