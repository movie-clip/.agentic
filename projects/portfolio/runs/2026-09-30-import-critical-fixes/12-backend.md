REPORT 2026-09-30-import-critical-fixes/12
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/services/statement_importer.py — new scrub_legacy_freedom24_cost_basis(snapshot): nulls every position's cost_basis and unrealized_pnl when any statement is freedom24; no-op and same object otherwise; input not mutated
  - services/quant-engine/app/services/import_engine.py — build_combined_import_bootstrap scrubs every input snapshot before combine, admission and exposure; import line extended
  - C:\projects\investments\.agentic\projects\portfolio\runs\2026-09-30-import-critical-fixes\scratch\be4_probe.py — scratch probe for the DoD numbers

verification:
  command:   cd services/quant-engine && SKIP_GOLDEN_FRESHNESS_CHECK=1 python -m pytest app/tests -k "combine or bootstrap or import" -q; python scripts/detect_deadcode.py --strict; python scratch/be4_probe.py
  result:    PASS
  detail:    1 failed, 174 passed, 932 deselected; the 1 failure is test_ff2026_dashboard_truth_values (2960.63 vs 3048.57, BE-2 window, red before this lane). Dead-code strict clean. Probe: legacy FF VTI None/None, totals None, unavailable; IB 62255.14 / 3491.53 stated. see § Verification detail

contract_notes:
  - No schema or route shape changed. The behaviour is a contract fact for docs: imports-fields.md and E4 must say a stored snapshot with a freedom24 statement has cost_basis and unrealized_pnl nulled on every analyze-combined call (D-12)
  - importedExposureOverride persisted with 3018.96 / 0.00 is not touched by this scrub; FE-2 must replace it from the analyze-combined response (already in the FE-2 behaviour, step 3)

pack_corrections:
  - none

handoff:
  - Docs (accepted per D-12): the scrub over-nulls IB and ESPP stated cost basis and unrealized P&L in a stored multi_broker snapshot that includes Freedom24, because per-position origin is not stored. Probe: stored IB+legacy-FF VUAA (10081.46, 1923.34) becomes (None, None); overview totals were unavailable there anyway
  - Docs: not over-nulled when IB and FF arrive as separate snapshots (fresh upload or add flow); only a stored, already-combined snapshot whose statements list contains freedom24 loses IB values. Stored IB+ESPP (no freedom24) is untouched (65394.29 / 3743.62 stated)
  - FE-2: no request change needed. The scrub runs on every analyze-combined call regardless of derivationVersion, so the call site is the same one the shared re-derive already makes; send the stored importedHistorySnapshot as usual
  - FE-2: the response snapshot positions, overview and exposure carry the nulls, so the re-derived portfolio snapshot and exposure override built from the response show unavailable
  - Test lane: legacy FF (VTI 3018.96 / 0.00) through analyze-combined and build_combined_import_bootstrap gives VTI None/None, overview totals None, cost_basis_trust unavailable, and a response equal to the fresh FF2026 response apart from provenance.generated_at
  - Test lane: scrub unit cases: idempotent (scrub twice equals once); input snapshot not mutated; fresh FF2026, IB2026 and IB+ESPP return the same object; snapshot with statements empty falls back to statement.importer; multi_broker with freedom24 in statements is scrubbed
  - Test lane: IB2026 alone through analyze-combined keeps 62255.14 / 3491.53 stated; stored IB+legacy-FF has VUAA cost basis and P&L None and overview unavailable (pin the over-nulling as documented behaviour)
  - Test lane: the single call site is build_combined_import_bootstrap, so build_import_bootstrap (upload path) is scrubbed too; on fresh data this is a no-op
  - Scratch probe: runs/2026-09-30-import-critical-fixes/scratch/be4_probe.py, untracked under .agentic; leave or delete by hand
  - Still red in the -k run, owned by BE-2 and T-1: test_analytics.py::test_ff2026_dashboard_truth_values_match_imported_history_and_overview. Nothing red is caused by this lane

skill_calls:
  - mattpocock-skills:diagnosing-bugs — not called, no fix attempt failed
  - mattpocock-skills:tdd — not called, order forbids editing tests

risks:
  - The scrub keys on statement.importer == freedom24 in the snapshot's statements list; a stored combined snapshot whose statements list was lost or emptied and whose top-level importer says multi_broker would still resolve through statement.importer only, so a Freedom24 statement missing from statements is not detected. Not seen in any fixture
  - Freedom24 statements never state cost basis, so the scrub is exact for single-broker FF; a future FF statement that does state one would be nulled here when loaded from a stored snapshot until the parser and scrub are revisited
  - The scrub sits in statement_importer.py and is called from import_engine.py as the order specified; the combine route (/combine-snapshots) calls combine_imported_snapshots directly and is not scrubbed, since the order fixed the call site at the top of build_combined_import_bootstrap

## Orchestrator brief
- BE-4 built to 05-design option (a): one scrub function in statement_importer.py, called at the top of build_combined_import_bootstrap; combine and admission logic untouched.
- Legacy FF2026 (VTI 3018.96 / 0.00) through analyze-combined returns VTI None/None, overview totals None, cost_basis_trust unavailable, equal to a fresh FF2026 response.
- Fresh FF2026 and IB2026 alone are unchanged (IB 62255.14 / 3491.53 stated); stored IB+ESPP untouched.
- Over-nulling of IB values in a stored IB+FF combined snapshot (D-12) is stated in handoff for docs.
- Section Verification detail: exact counts and probe output.

## Verification detail

Pytest, exact command `cd services/quant-engine && SKIP_GOLDEN_FRESHNESS_CHECK=1 python -m pytest app/tests -k "combine or bootstrap or import" -q`: `1 failed, 174 passed, 932 deselected`. The failure is test_analytics.py::test_ff2026_dashboard_truth_values_match_imported_history_and_overview, assertion `2960.63 == 3048.57` at :7662 (start_value, BE-2 window change); it was red in BE-1 and BE-3 reports.

Dead-code: `python scripts/detect_deadcode.py --strict` gives ruff, vulture and knip clean.

Probe (be4_probe.py, market data mocked at exposure_engine, real IB2026.csv, FF2026.pdf, ESPP2026.pdf):
```
legacy FF positions: [('VTI', 3018.96, 0.0)]
fresh  FF positions: [('VTI', None, None)]
legacy FF2026 via analyze-combined: 200  VTI (None, None)  total_cost_basis=None total_unrealized_pnl=None cost_basis_trust='unavailable'  admission degraded/degraded
fresh FF2026: 200  VTI (None, None)  totals None  unavailable
legacy-scrubbed response == fresh response (generated_at blanked): True
IB2026 alone: 200  total_cost_basis=62255.14 total_unrealized_pnl=3491.53 cost_basis_trust='stated'
stored IB+legacyFF (multi_broker): VUAA stored (10081.463136, 1923.336864) -> after scrub (None, None); VTI None/None; totals None, unavailable
stored IB+ESPP (no freedom24): VUAA (10081.463136, 1923.336864) kept; totals 65394.29 / 3743.62 stated
idempotent: True | input not mutated: True | fresh FF same object: True | IB same object: True
```
