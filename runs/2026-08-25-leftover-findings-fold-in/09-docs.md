REPORT 2026-08-25-leftover-findings-fold-in/09
status:      PARTIAL
verdict:     NONE

changed:
  - docs/finance/financial-methodology.md — added "## Multi-Statement Snapshot Merge" section (after Indexed Return Series, before FX Conversion Fallback Disclosure, near the cash-anchor rule at ~line 2232) documenting combine_imported_snapshots' NAV selection, TWR compounding, and the CR-1 account-identity guard.

verification:
  command:   grep -n "combine_imported_snapshots\|multi-statement merge" docs/finance/financial-methodology.md
  result:    PASS
  detail:    4 hits — section heading (2263), body reference (2265, 2315), Implementation list (2332). Confirmed by direct grep re-run after edit.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - New section cross-references the Cash anchor rule (~line 2232) it feeds and names both statement_importer.py and imports.py as Implementation anchors, per the one-formula-one-doc-section-one-code-path convention.
  - Every claim in the new section was verified against the current (post-CR-1) code by direct reading of statement_importer.py:66-347, not transcribed from AUDIT-quant.md's pre-CR-1 prose — see § Verification detail below.

risks:
  - Pack convention (capabilities/docs.md "Auto-update vs flag-for-human") says any new methodology section is flag-for-human, not auto-write; this order explicitly directed writing it with a fully-specified DoD (exact formulas, exact account-identity rule), so I wrote it per protocol core §3's rule that a pack convention does not block an explicit order — flagging the conflict here per that same rule, status set to PARTIAL accordingly.
  - The section's account-identity guard description matches CR-1 as landed in 07-backend.md and re-confirmed by my own read of _validate_compatible_snapshots (statement_importer.py:130-147); no discrepancy found between 07-backend.md's summary and the code.

## Verification detail

Read `statement_importer.py:66-347` directly (not AUDIT-quant.md's prose, which predates CR-1):
- `combine_imported_snapshots` (:66-98): sorts inputs by `_snapshot_sort_key`, validates via `_validate_compatible_snapshots`, then builds `statement_totals` via `_merge_statement_totals(ordered, terminal_snapshots)` where `terminal_snapshots = _latest_snapshot_by_account(ordered)`.
- `_merge_statement_totals` (:190-243): `starting_nav` = `earliest.starting_nav` (first non-None total in the date-sorted `totals` list) with a positive-value fallback; `ending_nav`/`cash_total`/`stock_total` = summed across `terminal_snapshots`' own cash/stock totals; `time_weighted_return_pct` = geometric compounding (`growth *= 1 + twr_i/100`) across every input statement's own TWR, in sorted (oldest-first) order.
- `_validate_compatible_snapshots` (:130-147): now (post-CR-1, confirmed against 07-backend.md's `changed` line) raises `ValueError` when `len(snapshots) > 1 and any(not snapshot.statement.account_id for snapshot in snapshots)` — i.e. any falsy account_id in a multi-input combine, before any merge logic runs. Comment at :135-140 explains the same-account-vs-different-account ambiguity this closes.
  `_latest_snapshot_by_account` (:256-266): buckets by `account_id`, latest-per-account wins (dict overwrite in sorted order) — confirmed its `fallback_snapshots` branch (for falsy account_id) is now unreachable via `combine_imported_snapshots` because validation raises first, matching 07-backend.md's risk bullet.
- `_merge_terminal_positions` (:269-293): sums quantities/cost_basis/market_value/unrealized_pnl per `(symbol, currency, as_of_date)` key across the terminal-snapshot list — same account_id collapses to one terminal entry (replace), distinct account_ids each contribute their own terminal entry (summed together by this function).
- `_merge_ledger_entries`/`_merge_instruments`: accumulate across all inputs regardless of account_id, deduped by exact tuple/symbol — documented as a distinct (unconditional) accumulation path, not part of the account-identity rule.
