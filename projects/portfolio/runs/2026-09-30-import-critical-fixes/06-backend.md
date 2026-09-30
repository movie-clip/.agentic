REPORT 2026-09-30-import-critical-fixes/06
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/schemas/import_bootstrap.py — added ImportAdmissionConstituentV1, ImportAdmissionRollupV1, ImportAdmissionSummaryV1.rollup, CombinedImportBootstrapRequest, ImportedBootstrapResponse.constituent_snapshots (C3, C4)
  - services/quant-engine/app/services/statement_importer.py — C5 guards only: repeated-account-part refusal on any input, combined-input-shares-account refusal inside combine_imported_snapshots
  - services/quant-engine/app/services/import_admission.py — DECISION_RANK and TRUST_LEVEL_RANK ladders, build_combined_admission_summary (weakest of combined recompute, every input, every carried summary)
  - services/quant-engine/app/services/import_engine.py — new build_combined_import_bootstrap seam; build_import_bootstrap now imports each path, calls the seam, sets constituent_snapshots when more than one file
  - services/quant-engine/app/api/routes/imports.py — POST /portfolios/import/analyze-combined (ValueError to 400 with detail); main.py untouched, imports.router already included

verification:
  command:   cd services/quant-engine && SKIP_GOLDEN_FRESHNESS_CHECK=1 python -m pytest app/tests/test_routes.py app/tests/test_import_admission.py app/tests/test_importer.py -k "combine or admission or bootstrap or analyze"; plus scratch probe be1_probe.py; detect_deadcode.py --strict
  result:    PASS
  detail:    40 passed, 39 deselected (same 40 as before my edits). Bare command without the env var: 40 errors at setup (golden freshness, FrozenMarketDataMiss after BE-2). Wider run: 312 passed, 3 failed, all Freedom24 (BE-2). Dead-code strict clean. see § Verification detail

contract_notes:
  - types.ts ImportAdmissionSummaryV1 (~:1183) lags: add optional rollup plus ImportAdmissionRollup and ImportAdmissionConstituent exactly as 05-design C3 TS mirror
  - types.ts ImportedBootstrapResponse (~:1208) lags: add constituent_snapshots?: ImportedSnapshot[]; response is always present as a list, empty for single input and analyze-combined
  - types.ts lacks the analyze-combined request type: snapshots, benchmark_symbol, symbol_overrides, carried_admissions (list of ImportAdmissionSummaryV1)
  - docs/contracts/import-admission-fields.md lags: needs rollup, constituent and combined_snapshot_* fields plus the weakest-of rule and ladders (T-46.3.5)
  - docs/contracts/imports-fields.md is still to be created (C4 response additions, C5 merge guards)
  - docs/contracts/dashboard-fields.md § Combine Imported Snapshots and system-architecture.md:34 lag: new route POST /portfolios/import/analyze-combined; combine-snapshots now also returns 400 for chained inputs
  - financial-methodology.md lags: E2 (combined admission, weakest-of rule) and E3 plus flat-combine and chained-input guard text in § Multi-Statement Snapshot Merge (lines 2332-2333, 2405 name combine-snapshots)
  - workspaceTypes.ts ImportedNodeSource (importedConstituents, derivationVersion) is not touched by BE-1; it is FE-1 per C6 and is unchanged in this lane

pack_corrections:
  - none

handoff:
  - Route: POST /portfolios/import/analyze-combined, body {snapshots[min 1], benchmark_symbol default SPY, symbol_overrides, carried_admissions}; empty snapshots gives 422, refused combine gives 400 with detail str
  - Guard messages surface as importError: chained input starts "Cannot combine: an already-combined portfolio shares account <id> with another statement"; doubled legacy starts "Cannot combine: the saved combined statement '<id>' repeats an account identifier"
  - A single stored snapshot with a repeated account part (A + B + B) is refused even as the only input; a stored non-repeating combined snapshot alone (IB+ESPP) analyses fine and gets rollup None
  - Carried constituents come after statement constituents; carried statement_ids and source_names are copied from the carried summary provenance; a carried summary's own rollup is not nested
  - Top-level checks and provenance on a rolled-up summary are the combined snapshot's own; decision and trust_level are independently the weakest across all labels
  - Test lane: combine(S,S)=S on IB2026; analyze-combined on IB2026.csv and ESPP2026.pdf (18 positions, 62843.22, VUAA 80, USD 146.065631); [IB,ESPP,IB] positions equal [IB,ESPP]; chained-input refusal; doubled-account single refusal; five fixture pairs; offsetting-delta synthetic pair on two accounts; superseded same-account case
  - Test lane: path independence (build_import_bootstrap on two paths vs analyze-combined on the same snapshots gives equal decision, trust, constituent set); refused combine returns 400 and no summary; single input equals build_import_bootstrap_from_snapshot; carried_admissions raises the label
  - Tests left red by BE-1: none. Red in the same scoped runs and owned by BE-2: test_importer.py test_import_freedom24_statement_returns_expected_snapshot, test_freedom24_parsers_skip_malformed_records_without_raising, test_analytics.py test_ff2026_dashboard_truth_values_match_imported_history_and_overview
  - Scratch probe: runs/2026-09-30-import-critical-fixes/scratch/be1_probe.py — cleanup: git rm is not needed (untracked under .agentic run dir); leave or delete by hand
  - BE-3 note: _merge_terminal_positions still sums cost_basis and unrealized_pnl unguarded (C5 last bullet, BE-3 scope); left untouched here

skill_calls:
  - mattpocock-skills:diagnosing-bugs — not called, no fix attempt failed
  - mattpocock-skills:tdd — not called, order forbids editing tests and named no TDD trigger

risks:
  - The order's verification command errors at setup (40 errors) because BE-2's freedom24 change made the golden freshness check raise FrozenMarketDataMiss; I ran it with SKIP_GOLDEN_FRESHNESS_CHECK=1, the conftest's documented escape hatch, not a gate bypass; H-1 clears it
  - Guard 1 also refuses two identical combined inputs (A+B and A+B), where key equality would have replaced correctly; built to the design wording (shares an account) and is stricter, not looser
  - The chained-input and doubled-account guards are inside combine_imported_snapshots, so the published /combine-snapshots route now returns 400 for those inputs; the design says this route stays but accepts the fail-closed guard
  - combine_imported_snapshots with a single doubled-account input now raises where it used to return it unchanged; import_statements single path is unaffected
  - build_import_bootstrap sets constituent_snapshots by attribute assignment after construction (no validate_assignment on the model); a constructor argument would be neater but touches the shared compose helper
  - The rule field on ImportAdmissionRollupV1 has no default, per the design contract; any client building a rollup must send it

## Orchestrator brief
- BE-1 built to 05-design C3, C4, C5 guards exactly: roll-up schema, analyze-combined route, build_combined_import_bootstrap seam, constituent_snapshots on the path-upload route.
- Probe on real IB2026 and ESPP2026: IB+IB gives 18 positions, 62,843.22, VUAA 80, USD 146.07; IB+ESPP+IB leaves IB unchanged; IB+ESPP is degraded/degraded.
- No BE-1 test is left red; 3 Freedom24 tests are red from BE-2 in the same runs.
- The order's verification command needs SKIP_GOLDEN_FRESHNESS_CHECK=1 until H-1 (BE-2 broke the golden window).
- Section Verification detail: full counts and every probe result.

## Verification detail

- Scoped command with SKIP_GOLDEN_FRESHNESS_CHECK=1: 40 passed, 39 deselected.
- Same command without the env var: 40 errors at fixture setup, message "Dashboard goldens freshness check could not regenerate goldens: FrozenMarketDataMiss('No frozen series for (SPY, 2026-03-31, 2026-04-11)')". Cause: BE-2 in the working tree.
- Wider run (test_routes, test_import_admission, test_importer, test_analytics, test_route_inventory, test_architecture_doc_route_inventory, test_engine_response_integrity): 312 passed, 3 failed; the 3 are Freedom24 pins owned by BE-2/T-1.
- python scripts/detect_deadcode.py --strict: ruff, vulture, knip all clean.
- Scratch probe (market data mocked at app.services.exposure_engine.MarketDataService, real IB2026.csv and ESPP2026.pdf):
  - IB alone: 18 positions, raw MV 62843.22, VUAA 80, USD 146.065631; admission degraded/degraded, rollup null.
  - ESPP alone: 1 position; admitted/verified, rollup null.
  - IB + IB: 18 positions, raw MV 62843.22, VUAA (80.0, 12004.8), USD 146.065631, EUR 0, GBP 0; account_id U8516450; degraded/degraded with two statement constituents.
  - IB + ESPP: 19 positions, raw MV 66234.46, USD 156.51; account_id "I09548809 + U8516450"; degraded/degraded; constituents degraded/degraded and admitted/verified; combined_snapshot degraded/degraded.
  - IB + ESPP + IB: positions and quantities equal IB + ESPP (True); three constituents.
  - Chained (IB+ESPP snapshot) + IB: HTTP 400 with the shared-account message.
  - Single snapshot with account_id "I09548809 + U8516450 + U8516450": HTTP 400 with the repeated-identifier message.
  - Stored combined IB+ESPP alone: HTTP 200.
  - ESPP + carried IB admission: degraded/degraded, constituents [statement admitted, carried degraded].
  - Empty snapshots: HTTP 422.
  - build_combined_import_bootstrap([IB]) equals build_import_bootstrap_from_snapshot(IB) apart from generated_at: True.
  - build_import_bootstrap([IB, ESPP]): degraded/degraded, constituent_snapshots 2 (interactive_brokers, espp); single path: 0 constituents, rollup None; empty paths: ValueError "At least one broker statement is required".
