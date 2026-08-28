REPORT 2026-08-27-next-epic-or-story/05
status:      DONE
verdict:     NONE

changed:
  - docs/contracts/correlation-fields.md — moved the mis-placed `coverage` row out of the `MultiBenchmarkCorrelationRequest` table (it is a Result field, not a Request field, per `correlation.py`) into the `MultiBenchmarkCorrelationResult` table; added a `DriftWindow` field table (8 fields) that the doc previously described only in prose
  - docs/contracts/diagnostics-fields.md — added the three `run_metadata` group members present on `DiagnosticsRunMetadata` but absent from the doc (`section_trust`, `return_basis_evidence`, `portfolio_proof`), each with a short schema-grounded subsection

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only order for schemas; docs lane has no Bash. Orchestrator runs `python scripts/run_all_tests.py` after this order lands.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - `services/quant-engine/app/schemas/currency_risk.py` (`CurrencyRiskResult`, `CurrencyRiskRequest`, `CurrencyLegContribution`) has no field-inventory contract doc — it is covered only by a prose paragraph in `docs/contracts/exposure-fields.md:361`. Closing this needs new-doc authoring (a `currency-risk-fields.md` or a proper table appended to exposure-fields.md), which is outside this order's "correct rows in place" fence. Route to a follow-up docs order.
  - TS-type column accuracy for the rows added to `correlation-fields.md` (`DriftWindow`, the relocated `coverage`) was NOT verified — this order is contract-doc vs Pydantic-schema only (non-goal bars `apps/desktop/**`). A frontend/test lane should confirm `apps/desktop/src/features/portfolio/types.ts` `DriftWindow` / `MultiBenchmarkCorrelationResult` match.
  - `correlation-fields.md` § US-9.2 header cites `analytics/risk.py — build_rolling_risk_series` as "Backend schema:", and `factor-drift-fields.md` cites component/exposure types — the actual Pydantic class `RollingRiskPoint` lives in `app/schemas/reconciliation.py`. Header-citation nuance, not field drift; left untouched per "correct rows in place only". A future doc pass could tighten the "Backend schema:" line.

risks:
  - No schema-side smell found. Fail-closed defaults (`trust = "unavailable"` on `DriftWindow`, `EpisodeContributor`) and `FiniteFloat` NaN-guards (`ImportAdmissionCheckValue.value`, `.delta`) are used consistently; the one known nullability mismatch — `DashboardRangeMetrics.window_start_date` is backend-always-serialized but TS-optional — is already recorded as tech-debt in `dashboard-fields.md:324`, not a new finding.
  - `diagnostics-fields.md` is by design a partial "key contract fields" digest, not a full inventory. Top-level `DiagnosticsResult` fields `rolling_risk`, `factor_exposures`, `factor_shift_diagnostics`, `risk_contribution_breakdown`, `model_reliability`, `factor_registry`, `factor_methodology`, `statistical_factor_model`, `stress_scenarios`, `snapshot` have no row in it (several are documented in `exposure-fields.md` instead, which consumes `DiagnosticsEngineResponse`). Bringing them in would be a restructure (a non-goal), so completeness there is left as-is.
  - `dashboard-fields.md` and `exposure-fields.md` are UI-traceability docs keyed on frontend `analysis.*` / `result.*` state names, not raw schema field paths (e.g. schema `availability` surfaces as `analysis.exposure_availability`). A strict schema-field-name diff does not cleanly apply to their tables; what they document was checked against the schemas and matches. `dashboard-fields.md` was also diffed by 02-scout.md § H and found clean.

## Summary table

| Contract doc | Schema(s) diffed | Result | Doc-side corrections | Schema smells |
|---|---|---|---|---|
| attribution-fields.md | `attribution.py` | clean | 0 | 0 |
| intra-correlation-fields.md | `intra_correlation.py` | clean | 0 | 0 |
| provenance-fields.md | `provenance.py` | clean | 0 | 0 |
| import-admission-fields.md | `import_bootstrap.py` | clean | 0 | 0 |
| cache-fields.md | `cache.py` | clean | 0 | 0 |
| risk-fields.md | `stress.py`, `drawdown.py`, `distribution.py`, `reconciliation.py::StressScenarioResult` | clean | 0 | 0 |
| correlation-fields.md | `correlation.py`, `drift.py`, `reconciliation.py::RollingRiskPoint` | corrected | 2 | 0 |
| diagnostics-fields.md | `diagnostics.py` (+ `dashboard_history.py`, `return_basis.py` for nested types) | corrected | 3 fields (1 edit cluster) | 0 |
| factor-drift-fields.md | none — card is client-derived from `ExposureAnalysis`, doc self-declares "Backend schema: _none_" | n/a | 0 | 0 |
| exposure-fields.md | `exposure.py`, `portfolio_engine.py`, `currency_risk.py` (prose only) | clean | 0 | 0 |
| dashboard-fields.md | `dashboard_history.py`, `reconciliation.py::PerformancePoint` (scout § H + spot-check here) | clean | 0 | 0 |
| ui-design-system.md | n/a — design-system token/primitive contract, not a field inventory | not in scope | 0 | 0 |

Totals: 12 contract docs present, 11 field-inventory docs checked field-by-field, 2 corrected, 5 doc-side field rows fixed, 0 schema-side smells, 0 contract docs pointing at a deleted schema, 1 schema with no contract doc (`currency_risk.py`, handoff).

## Detail — the two corrected docs

### correlation-fields.md

1. **`coverage` in the wrong table.** `correlation.py` defines
   `MultiBenchmarkCorrelationRequest` with exactly `snapshot` + `lookback_days`;
   `coverage: SyntheticHistoryCoverage | None` is a field of
   `MultiBenchmarkCorrelationResult`. The doc listed `coverage` as a third row of
   the Request table (with malformed columns copied from the attribution doc) and
   omitted it from the Result table. Moved the row to the Result table in that
   table's 7-column format.
2. **`DriftWindow` undocumented.** § US-9.1 documented `DriftDailyPoint` and
   `DriftResult` field-by-field but described the `DriftWindow` entries only in
   the `windows` row's Notes prose. Added a `### DriftWindow` table (`label`,
   `start_date`, `end_date`, `portfolio_return_pct`, `benchmark_return_pct`,
   `spread_pct`, `trust`, `note`) matching the section's existing per-type
   subsection format and `drift.py`'s annotations/defaults.

### diagnostics-fields.md

`DiagnosticsRunMetadata` (`diagnostics.py:49-86`) carries `section_trust`,
`return_basis_evidence` and `portfolio_proof` between `source_status` and
`investor_economics_status`; the doc's `## Run Metadata` enumeration listed 9 of
the 12 members and skipped those three. Added them to the enumeration in schema
order and gave each a short subsection grounded in the schema
(`SectionTrust` enum values; the `ReturnBasisEvidence` bundle keys; the
`PortfolioProofMetadata` reference). `factor_model_parameters` and
`reproducibility` sub-field lists were re-checked and already match.
