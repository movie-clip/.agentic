REPORT 2026-08-31-tests-failing-statement-stale/04b
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/tests/test_analytics.py — class-(c) replay-pin cluster (9 tests, l.8493-8958) re-pinned to observed Aug-28 IB2026 values; each pin carries a `# 2026-08-28 statement refresh: <old> -> <new>` continuation

verification:
  command:   python scripts/run_all_tests.py  (from repo root)
  result:    PASS
  detail:    run_all_tests.py green. Backend 979 passed (pytest -n auto); frontend 359 passed / 40 files; tsc --noEmit clean; dead-code strict clean. .claude/.last-test-pass written 2026-08-31 17:50:56. test_analytics.py in isolation: 215 passed.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Named pins refreshed: l.8509 anchor.residual 46.69->-1.15; l.8546 daily_states[-1].date and l.8939 terminal.date "2026-08-11"->"2026-08-28"; l.8594 vol_pct 13.81->13.43; l.8681 len(series) 148->161; l.8725 twr["1M"] 4.14->5.68.
  - Named pins refreshed (cont.): l.8809 money_weighted_return_pct 2.76->3.49; l.8837 investment_gain 1645.99->2091.78; l.8901 peak_net_cash_invested 2130.62->2138.01.
  - 5 more pins were hidden behind the first-failing assert in the same test and also refreshed: l.8552 reconciliation_adjustment -19.98->-5.95; l.8684 len(published) 144->157; l.8727 twr["3M"] 1.56->-0.79; l.8729 twr["All"] 0.43->1.11; l.8958 terminal-day return -0.000545->-0.001155.
  - 3 stale terminal-date-string guards updated for correctness (were passing): l.8533, l.8690, l.8916 `"2026-08-11"` -> `"2026-08-28"` in `not in` checks. Plus docstring l.8672 "141 of 148"/"7 gaps" -> "157 of 161"/"4 gaps".
  - History-comment format on every pin: `# 2026-08-28 statement refresh: <old> -> <new>` above the assertion, matching 04. No tolerance widened. No pin raised instead of assert-failing.
  - Only hand-derived value: len(published) 157 = len(series) 161 minus the unchanged 4-day withheld set; confirmed green. No shared fixture touched — only test_analytics.py edited this lane.
  - anchor.residual -1.15 matches the value 04 re-pinned for the same assertion in test_ledger_replay_audit.py l.134 and test_portfolio_state.py l.773 — cross-file consistent.

risks:
  - twr["3M"] flipped sign (1.56 -> -0.79) and twr["All"] rose (0.43 -> 1.11); these are large relative moves. They track the window extending Aug-11 -> Aug-28 (+13 trading days, every position re-marked, one new SBIO BUY) and the statement TWR moving 4.77% -> 5.51%. quant-audit should confirm the range TWRs against the raw CSV, same as the statement_truths.py TWR anchor.
  - terminal-day series return pinned at -0.001155 inside a tight abs=1e-5 band (unchanged tolerance). It landed at -0.00115468, comfortably inside, but this is the narrowest band in the cluster — a future re-mark that shifts the terminal day by >1e-5 return will need this pin refreshed, not the band widened.
  - Scope-classification gap (already flagged by 04, now closed): 02-scout-map and 03-technical-plan classified test_analytics.py as class-(a) needing no numeric change. It carried this 9-test / 16-assertion class-(c) cluster. Mechanical, same pattern as the three files 04 handled.
