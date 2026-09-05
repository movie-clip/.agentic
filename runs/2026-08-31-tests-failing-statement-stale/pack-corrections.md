# Pack corrections — run 2026-08-31-tests-failing-statement-stale

## 1. Statement-refresh blast-radius heuristic under-counts inline replay pins
- **Source:** run findings — scout (02) and tech-lead DESIGN (03) both classified
  `app/tests/test_analytics.py` as class-(a) ("needs no numeric change beyond the
  shared `IB_STATEMENT_PERIOD` pin"). It actually held a 9-test / 16-assertion
  class-(c) inline replay-pin cluster (~l.8500–8940: `anchor.residual`,
  `reconciliation_adjustment`, range TWRs, `money_weighted_return_pct`,
  `investment_gain`, `len(series)`, terminal-day return, date guards). The test
  lane hit this only after 04's suite run failed on it, forcing a scope
  extension (04b).
- **Correction:** when scoping a statement refresh, do not classify a test file
  from reading its asserts — run the actual `pytest -q` failure list first and
  map every failing node. The inline class-(c) pins (replay-engine-derived,
  hand-regenerated each refresh) live in at least THREE files, not two:
  `test_ledger_replay_audit.py`, `test_portfolio_state.py`, **and**
  `test_analytics.py`.
- **Target:** whichever `.agentic` capability pack / project-profile section
  documents the statement-refresh workflow scope (testing pack), and
  `docs/architecture/testing-architecture.md#statement-refresh-workflow` (repo
  side — routed to the docs lane at close-out as part of the option-(ii) doc
  amendment).
