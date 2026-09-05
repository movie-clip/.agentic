REPORT 2026-09-04-us43.4-collapse-import-composer/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   grep -rn "import_engine_composer|compose_import_bootstrap_response" app/ (via Grep tool, path services/quant-engine/app)
  result:    PASS
  detail:    3 matches total — import_engine_composer.py:14 (def site), import_engine.py:5 (import), import_engine.py:31 (call site). No match in app/tests/** for either the module name or the function name.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Full body of `compose_import_bootstrap_response` is `services/quant-engine/app/services/import_engine_composer.py` lines 1-37 in full (imports on lines 1-11, function signature line 14-24, body — a single `return ImportedBootstrapResponse(...)` call — lines 25-36); this is the entire file, nothing else in it.
  - Composer's imports needed by the fold: `from app.schemas.exposure import ExposureAvailability, ExposureCurrentStateConcentration`; `from app.schemas.portfolio_engine import PortfolioHistoryContext`; `from app.schemas.reconciliation import LookThroughOverview, LookThroughSectorExposure, MarketOverlapSummary, PortfolioOverview` (note `PortfolioRiskSummary` already imported in import_engine.py:3, so composer's reconciliation import list minus `PortfolioRiskSummary` is the delta); `from app.services.import_admission import build_import_admission_summary` — none of these five import lines currently exist in import_engine.py except `PortfolioRiskSummary`, `ImportedBootstrapResponse` (already imported at import_engine.py:2).
  - The exact call site: `services/quant-engine/app/services/import_engine.py` lines 31-52, inside `build_import_bootstrap_from_snapshot` (function spans lines 23-52) — `return compose_import_bootstrap_response(` at line 31, closing paren/return at line 52, passing `snapshot`, `overview`, `lookthrough`, `lookthrough_sector_exposure`, `market_overlap`, `current_state_concentration`, `availability`, `risk_summary=PortfolioRiskSummary(...)` (constructed inline lines 39-50), `history_context` — all by keyword, matching the composer's parameter names exactly.
  - `import_engine.py`'s own composer import is a single line: `from app.services.import_engine_composer import compose_import_bootstrap_response` at line 5 — this is the only line to remove for AC1/AC4 besides the deletion of the file itself.
  - Grep confirms import_engine.py is the sole consumer of both the module and the function anywhere under app/ — no test file references `import_engine_composer` or `compose_import_bootstrap_response` by name, so AC4's "no dangling reference" check has zero test-side surface to update beyond the new pin assertion.
  - Best-suited existing test file for the AC1/AC4 pin assertion is `services/quant-engine/app/tests/test_analytics.py` — it already imports `pytest` (line 4) and `build_import_bootstrap_from_snapshot` at module level (line 53: `from app.services.import_engine import build_import_bootstrap_from_snapshot`), and already carries two synthetic (fixture-free, always-run — no PDF-existence guard) tests for this exact function: `test_build_import_bootstrap_from_snapshot_merges_statement_windows_into_history_context` (lines 684-729) and `test_build_import_bootstrap_from_snapshot_falls_back_to_ledger_and_position_dates_when_statement_period_missing` (lines 737-778); the new pin test drops in immediately after line 778, before the next test at line 781.
  - Runner-up candidate `services/quant-engine/app/tests/test_importer.py` has a related test `test_import_bootstrap_three_broker_no_crash` (lines 515-533) but it early-`return`s (lines 516-517) when three specific broker PDF fixtures are absent from disk, so it is not guaranteed to run — less suitable than test_analytics.py for a pin that must always execute.
  - test_import_admission.py also imports `build_import_bootstrap_from_snapshot` at module level (line 13) and calls it at line 250, but has no existing pair of composer-adjacent tests to sit the new assertion next to — test_analytics.py remains the stronger fit.
  - The three public entry functions in import_engine.py, current signatures verbatim: `build_import_bootstrap(statement_paths: str | list[str], benchmark_symbol: str, symbol_overrides: dict[str, list[str]]) -> ImportedBootstrapResponse` (line 12); `build_import_bootstrap_from_portfolio_snapshot_request(request: SnapshotAnalysisRequest) -> ImportedBootstrapResponse` (line 18); `build_import_bootstrap_from_snapshot(snapshot: ImportedPortfolioSnapshot, benchmark_symbol: str, symbol_overrides: dict[str, list[str]]) -> ImportedBootstrapResponse` (lines 23-27) — none of these three signatures reference the composer directly, so AC2 (unchanged names/signatures) requires no edit to them at all; only the internal call inside the third function's body changes.
  - Stale `.pyc` artifacts found under `services/quant-engine/app/services/__pycache__/`: `import_analysis_composer.cpython-312.pyc` and `import_analysis.cpython-312.pyc` — these are compiled bytecode for a *different, older* module-name pair (`import_analysis` / `import_analysis_composer`, not `import_engine` / `import_engine_composer`), confirming the story's own note that this is a prior, unrelated rename; they do not reference or shadow the current `import_engine_composer.py` in any way and need no action.
  - Docs referencing `import_engine_composer` by name today (to check at T-43.4.2 close-out): `docs/architecture/system-architecture.md`, `docs/tech-debt-register.md`, `docs/product/epic-roadmap.md`, `docs/product/stories/README.md`, `docs/contracts/exposure-fields.md`, `docs/product/prd/epic-43-engine-seam-consolidation.md`, `docs/product/prd/epic-8-reset-to-analysis-core.md`, plus the story file itself.

risks:
  - I did not open every listed doc's exact line for the `import_engine_composer` mention (system-architecture.md, tech-debt-register.md, epic-roadmap.md, exposure-fields.md, the two PRDs, stories/README.md) — T-43.4.2 is a docs-lane ticket and out of this recon's scope, but the design pass should route those six doc files (beyond the story itself) to the docs lane as the T-43.4.2 blast radius, not assume only system-architecture.md and CONTEXT.md need checking as the story text implies.
  - CONTEXT.md is named by the story (T-43.4.2) as a doc to check for "import bootstrap" references, but no CONTEXT.md exists yet at repo root per CLAUDE.md ("neither exists yet — created lazily by /domain-modeling") — confirm this is still the case before routing a docs order that assumes the file exists.
