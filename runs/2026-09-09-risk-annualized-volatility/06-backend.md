REPORT 2026-09-09-risk-annualized-volatility/06
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/core/constants.py — added `RISK_TAB_ANNUALIZED_VOL_MIN_OBSERVATIONS = 60` beside `MIN_DAILY_OBSERVATIONS`, with the disambiguation comment and grounding cite to 02-quant-research.md § 2.4.
  - services/quant-engine/app/schemas/diagnostics.py — added `RiskTabVolatilityTrust` literal, the `RiskTabAnnualizedVolatility` model (docstring: formula, units, truth class, methodology ref, rungs), and required `risk_tab_volatility` field on `DiagnosticsResult` (no default).
  - services/quant-engine/app/services/diagnostics_engine.py — added `_build_risk_tab_annualized_volatility(risk_summary)` (classifies on `risk_summary.observations`; copies the value through at N>=60, no recompute) and wired it into both the populated path and `build_unavailable_diagnostics_result`; imported the constant and the model.

verification:
  command:   cd services/quant-engine && python -m ruff check app/core/constants.py app/schemas/diagnostics.py app/services/diagnostics_engine.py && python -m pytest app/tests -q
  result:    PASS
  detail:    ruff clean on all 3 files. pytest 983 passed, 0 failed, 50 warnings in 95.74s. The order anticipated diagnostics/golden fixture failures on the new required field; none surfaced in app/tests — the backend suite holds no frozen diagnostics JSON fixture, so nothing asserts full DiagnosticsResult shape there. The engine builders populate `risk_tab_volatility` on every path, so construction stays valid. Expected regen breakage lands in the frontend/goldens lane (TS diagnostics fixtures, dashboardGoldens.ts) — T-44.1.3, outside this command. Ran `python -m ruff` / split commands because bare `ruff` is not on PATH here. detect_deadcode.py --strict also run: clean (ruff/vulture/knip).

contract_notes:
  - apps/desktop/src/features/portfolio/types.ts — mirror `RiskTabAnnualizedVolatility` + the `synthetic|withheld|unavailable` trust union onto every shape that mirrors `DiagnosticsResult` (DiagnosticsEngineResponse, ImportedDiagnosticsSource, the snapshot-request variant) or tsc diverges. Triggered by the schema_edit_reminder hook on diagnostics.py.
  - docs/contracts/risk-fields.md — NEW section for `risk_tab_volatility`, 4 fields: `annualized_volatility_pct` (float|None, non-null iff published), `trust` (synthetic|withheld|unavailable), `observations` (int), `minimum_observations` (int). Note the `withheld` rung extends the Risk-tab preamble's synthetic|unavailable vocabulary for this figure only; sourced from the diagnostics engine.
  - docs/contracts/diagnostics-fields.md — `volatility_summary` block (~line 216) needs a cross-reference: `risk_tab_volatility.annualized_volatility_pct` is the publication-gated Risk-tab view of `volatility_summary.portfolio_volatility_pct` (same scalar, same code path, adds a 60-paired-observation floor).
  - docs/finance/financial-methodology.md — "Annualized realized volatility" (~line 1012) AMENDMENT: Risk-tab floor N>=60 paired observations; N=0 -> unavailable, 1..59 -> withheld (not collapsed), >=60 -> `synthetic`; zero-variance at N>=60 publishes 0.00%; Dashboard unchanged/unfloored; constant distinct from `MIN_DAILY_OBSERVATIONS`; cite 02 § 2.4.
  - docs/product/current-product-state.md — inventory add at close-out: Risk-tab annualized volatility figure now in shipped Risk-tab scope.

pack_corrections:
  - none

handoff:
  - Frontend T-44.1.2: `risk_tab_volatility` sits beside `volatility_summary` on `DiagnosticsResult`. `annualized_volatility_pct` is non-null iff `trust == "synthetic"`; below the floor it is `null` (never 0, never `-`). `minimum_observations` (=60) and `observations` are on the wire — no mirrored frontend constant; `observations` drives the "N of 60" copy.
  - Server decides the N=0 vs 1..59 split; the card renders the arriving `trust` only. States: synthetic (number + badge), withheld (EmptyState: 60-trading-day requirement, "N of 60", Dashboard shows an unfloored estimate), unavailable (EmptyState "no return history", distinct from withheld).
  - Published value is a straight copy of `risk_summary.portfolio_volatility_pct`, byte-identical to `volatility_summary.portfolio_volatility_pct` in the same response — cross-surface tests can assert equality at N>=60 and divergence somewhere in 2<=N<60.
  - Test lane T-44.1.3: backend suite has no frozen diagnostics JSON fixture — no backend fixture regen for this field. TS diagnostics fixtures and dashboardGoldens.ts carry the shape and need regeneration once the required field lands.
  - Backend cases for T-44.1.3: N=0 -> unavailable/null; N in [1,59] -> withheld/null (N=1 never yields 0.00% here); N>=60 -> synthetic/number; zero-variance at N>=60 -> synthetic 0.00%; withheld serializes distinct from unavailable; boundary tests import the constant, not a literal 60.
  - Helper: `diagnostics_engine.py::_build_risk_tab_annualized_volatility(risk_summary: PortfolioRiskSummary) -> RiskTabAnnualizedVolatility`.

risks:
  - Zero-variance at N>=60 implemented per the human ruling as the plain `trust="synthetic"` passthrough (no `vol == 0.0 -> withheld` branch), matching 05 § 5. quant-audit should confirm against guardrail 4 — a computed 0.00% here is a genuine dispersion value, and the ACs leave this case unasserted.
  - The gate keys on `risk_summary.observations` (paired portfolio+benchmark returns), not the distribution engine's unpaired `return_count`. So the VaR card can populate (N>=20) while this figure withholds (N<60). 02 § 3.2 calls this the intended stricter-floor asymmetry; quant-audit to confirm.
  - In `build_unavailable_diagnostics_result` I lifted the previously-inline `PortfolioRiskSummary(...)` to a local var so both `risk_summary=` and `risk_tab_volatility=` reference one object. Behaviourally identical (observations=0 -> unavailable), but a small structural change beyond a pure addition.
  - The order predicted diagnostics/golden fixture failures in `pytest app/tests`; none occurred — the backend suite has no frozen diagnostics fixture. Flagging so this is not read as a missed failure; the regen work is real but lives in the frontend/test lane.
