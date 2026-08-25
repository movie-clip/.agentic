REPORT 2026-08-25-leftover-findings-fold-in/10
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd services/quant-engine && python -m pytest app/tests/test_importer.py -v
  result:    PASS
  detail:    28 passed, 0 failed, including test_three_broker_combine_ib_ff_espp and the 3 new CR-1 regression tests.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Both MATERIAL findings from AUDIT-quant.md are closed. No new BLOCKING finding. One new MINOR finding (Finding 3) for the docs lane's optional follow-up — non-blocking.

risks:
  - Golden PDF-based multi-statement tests silently no-op (early `return`) in THIS checkout -- docs/IB2026.pdf and docs/U8516450_20260101_20260408.pdf are absent locally. See § Finding 1 re-audit.
  - Pre-existing test-infra gap, not introduced by CR-1; I substituted independent synthetic scripts instead of trusting the skip-disguised-as-pass. See § Finding 1 re-audit.
  - I did not re-verify US-40.1 or any other part of US-40.2's original scope -- out of scope per this order's non_goals.

## Orchestrator brief
- Both findings independently re-verified CLOSED. Finding 1: all 3 original repro cases (both-equal/both-falsy/one-falsy, both directions) re-run against current statement_importer.py via a fresh independent script -- match 07-backend.md's claims exactly (unaffected/raises/raises). See § Finding 1 re-audit.
- Distinct-account N>2 case (the genuinely-different-accounts path) verified NOT overcorrected -- via my own synthetic 3-account script (same-symbol-different-account correctly SUMS; different-symbol case correctly aggregates), since the repo's own golden 3-broker PDF test is a silent no-op in this checkout (see risks). See § Finding 1 re-audit.
- Generalization judgment (guard applies to any len>1 combine, not just pairs) assessed SOUND: fail-closed is the only safe choice when account_id can't classify same-vs-different account: confirmed by testing a synthetic N=3 case with one falsy id -- correctly raises, and does not regress the tested distinct-id N=3 case. See § Generalization judgment assessment.
- Finding 2: read financial-methodology.md:2263-2344 directly and cross-checked every formula claim (sort order, starting_nav earliest+fallback, ending_nav=cash+stock terminal sum, TWR geometric compounding + numeric example, account-identity guard, same-account-replace vs distinct-account-sum including the same-symbol case) against statement_importer.py line-by-line -- all match. See § Finding 2 re-audit.
- One new MINOR finding: the doc's TWR formula doesn't mention that a single None input TWR nulls the whole compounded result rather than partially compounding -- undocumented edge case, not a formula error. See § Finding 3 (new).
- No CRITICAL, no MATERIAL findings this round. Verdict PASS.
- Sections: § Finding 1 re-audit, § Generalization judgment assessment, § Finding 2 re-audit, § Finding 3 (new), § Anchors used.

---

## Finding 1 re-audit

**Independent script (anchor: closed-form/hand-computed case, re-derived from scratch against current code, not 07-backend.md's ad hoc script).** Built five ImportedPortfolioSnapshot pairs via pydantic `model_validate` (base Jan AAPL qty 10 ending_nav 2000 / new Feb AAPL qty 15 ending_nav 3000, matching AUDIT-quant.md Finding 1's original repro shape) and ran them through the current `combine_imported_snapshots`:

```
both-present-and-equal (U1234567/U1234567): OK positions=[('AAPL', 15.0)] ending_nav=3000.0
both-falsy (None/None):                     RAISED ValueError: "...at least one statement has no parsed account identifier..."
one-present-one-falsy (U1234567/None):      RAISED ValueError (same message)
one-falsy-one-present (None/U1234567):      RAISED ValueError (same message)  [not in original 3 cases, added for symmetry]
both-present-DIFFERENT (U1/U2):             OK positions=[('AAPL', 10.0), ('AAPL', 15.0)] ending_nav=5000.0  [legitimate distinct accounts, correctly unaffected]
```

All three cases named in this order's DoD (both-equal, both-falsy, one-falsy) reproduce exactly what 07-backend.md claimed in its `handoff` section (word-for-word matching numbers), from a freshly-written script against the current file, not from re-reading 07-backend.md's own claim. This closes DoD item 1.

**Genuinely-distinct-account case (DoD item 2).** The repo's own `test_three_broker_combine_ib_ff_espp` (test_importer.py:377) and its sibling PDF-fixture tests (`test_combine_imported_snapshots_merges_sequential_ib_statements`, `test_combine_imported_snapshots_allows_mixed_broker_same_currency_imports`, `test_multi_year_combination_does_not_backfill_fake_pre_funding_positions`) all guard on `if not <path>.exists(): return`. In this checkout `docs/IB2026.pdf` and `docs/U8516450_20260101_20260408.pdf` do not exist (confirmed via `ls docs/*.pdf` and a direct `Path.exists()` check) — every one of these tests hits its early `return` and pytest reports PASSED without ever calling `combine_imported_snapshots` on real distinct-account data. This is a pre-existing characteristic of this checkout (both `IB2026.pdf`'s and `U8516450_20260101_20260408.pdf`'s absence predate CR-1; `IB2026.pdf` has git history but is not currently tracked), not something CR-1 introduced, and it also means 07-backend.md's and 08-test.md's own "test_three_broker...passing" claims did not actually exercise this path locally either — they inherited the same blind spot.

I substituted independent synthetic verification instead of trusting the skip-disguised-as-pass: built two distinct-account snapshots with the SAME symbol (AAPL) and the same as_of_date (the case that most stresses the account-identity distinction, since it's the one place same-symbol data from different accounts must legitimately combine by summation rather than collide):

```
distinct-accounts-same-symbol-same-date positions: [('AAPL', 25.0)]   (10 from ACCT_A + 15 from ACCT_B, correctly summed)
ending_nav: 5000.0                                                     (2000+3000, correctly summed)
```

And the N=3 distinct-symbol case (AAPL/MSFT/GOOG across three accounts, mirroring the three-broker shape):

```
3-distinct-accounts: positions=[('AAPL', 10.0), ('GOOG', 2.0), ('MSFT', 5.0)]  ending_nav=4000.0
```

Both match hand-computed expectations exactly. This closes DoD item 2 without relying on the locally-skipped golden test.

## Generalization judgment assessment

07-backend.md flagged: the guard fires for `len(snapshots) > 1 and any falsy account_id`, i.e. any-length combine, not just the 2-input add_snapshot case the DoD's worked examples used.

Assessed as sound. The underlying reasoning in `_validate_compatible_snapshots`'s own comment (`statement_importer.py:135-140`) is length-independent: `_latest_snapshot_by_account` cannot distinguish "same account, unparsed id" from "another account, unparsed id" regardless of how many other snapshots are in the batch — a 2-input and a 5-input combine face the identical ambiguity per falsy-id snapshot. Narrowing the guard to len==2 would leave the exact same double-counting bug reachable via the pre-existing multi-file initial-import path (`import_statements`, still calls `combine_imported_snapshots` with N>2 inputs) — reintroducing Finding 1 through a different door.

Verified numerically that this does not overcorrect the legitimate N>2 distinct-account case: built a 3-input combine with two valid distinct account_ids (IB_ACCT, FF_ACCT) and one falsy id (None) —

```
3-with-one-falsy: RAISED ValueError (same message)
```

This is correct fail-closed behavior, not overcorrection: even with two accounts confidently distinct, the third snapshot's unparseable id is still ambiguous (could be a third distinct account that should sum, or a duplicate/retry of one of the other two that should replace) and the function has no way to tell. Re-confirmed the currently-passing distinct-id N=3 case (`test_three_broker_combine_ib_ff_espp`'s semantic equivalent, all three ids present and valid) is unaffected by the guard — shown in § Finding 1 re-audit's second script block, ending_nav=4000, no exception.

The one real behavioral consequence: a legitimate 3-broker combine where exactly one broker's account_id genuinely fails to parse is now hard-blocked (HTTP 400, degradation-disclosure path) rather than silently miscounted. That is the intended trade-off of closing Finding 1 (fail closed over guessing), not a defect.

## Finding 2 re-audit

Read `docs/finance/financial-methodology.md:2263-2344` directly (not 09-docs.md's own "Verification detail" section) and cross-checked every claim against the current `statement_importer.py` (post-CR-1, read in full: `combine_imported_snapshots` :66-98, `_snapshot_sort_key` :101-102, `_merge_statement_totals` :190-243, `_latest_snapshot_by_account` :256-266, `_merge_terminal_positions` :269-293, `_merge_terminal_cash_balances` :296-311, `_validate_compatible_snapshots` :130-147):

| Doc claim | Code check | Result |
|---|---|---|
| Inputs re-sorted oldest-to-newest by `_snapshot_sort_key` before anything else | `combine_imported_snapshots:72`, `ordered = sorted(snapshots, key=_snapshot_sort_key)`, key returns `(start, end)` ascending | match |
| `starting_nav` = earliest statement's own value, falls back to first positive across statements if earliest has none | `:227-231`; confirmed `is not None` (not falsy) is the exact fallback trigger — verified with a real fixture where ESPP's `starting_nav` parses to `None` (not `0.0`) and combine correctly falls back to IB's positive value, matching `test_combine_imported_snapshots_ignores_zero_starting_nav_placeholder`'s own assertion, independently re-derived | match |
| `ending_nav` = terminal cash_total + stock_total | `:217-225` | match (doc omits the `else latest.*` branch when `terminal_totals` is empty — see Finding 3) |
| TWR = geometric compounding, oldest to newest, `growth *= 1+twr_i/100` | `:205-211`; hand-verified 5%/3%/2% -> 10.313% per the doc's own worked example: 1.05×1.03×1.02=1.10313 | match |
| Account-identity guard: falsy id on either side of a >1-input combine raises `ValueError` before any merge | `_validate_compatible_snapshots:141-147` | match, and matches CR-1 as landed (07-backend.md) |
| Same account_id -> latest-wins replace; different account_id -> sum | `_latest_snapshot_by_account` buckets by id (dict overwrite = replace, upstream of the merge functions); `_merge_terminal_positions`/`_merge_terminal_cash_balances` then only ever see one snapshot per account (replace already happened) or several distinct accounts (summed) | match — independently stress-tested the same-symbol-different-account case (§ Finding 1 re-audit) since that is the case most likely to reveal a collision bug, and it summed correctly |
| Contract rule: combined `starting_nav`/`ending_nav` feed the Cash anchor rule unchanged, no special-casing | `portfolio_state.py:519-525` reads `self.snapshot.statement_totals.starting_nav` generically — no branch distinguishing a combined snapshot from a single-statement one | match |

No discrepancies between the new doc section and the current code. This closes DoD item 3 (financial-methodology.md formulas match code independent of 09-docs.md's own verification claims).

## Finding 3 (new)

```
FINDING 3
severity:   MINOR
where:      docs/finance/financial-methodology.md:2286-2291 (TWR compounding description) vs. statement_importer.py:205-211 (_merge_statement_totals)
claim:      the new section states "time_weighted_return_pct = geometric compounding of EVERY input statement's own period return, oldest to newest" with no mention of a missing-value case.
actual:     the code only compounds when EVERY input's time_weighted_return_pct is non-None (`if twr_values and all(value is not None for value in twr_values)`); if even one input snapshot lacks a TWR (e.g. an ESPP statement, which always sets time_weighted_return_pct=None per app/importers/espp.py:90), the combined TWR is None (unavailable), not a partial compound of the available values.
impact:     an auditor or engineer reading only the doc could reasonably expect a partial/available-subset compound, or could mistake a None combined TWR for a bug rather than the documented (once fixed) intended degrade-to-unavailable behavior. Low impact: the actual code behavior is the financially correct one (never fabricate a partial TWR), it is simply unstated.
expected:   add one sentence to the Multi-Statement Snapshot Merge section: "If any input statement's time_weighted_return_pct is null, the combined value is null (unavailable) rather than compounding the available subset — never a partial/silent result."
```

This is MINOR per the pack's rubric (undocumented assumption, code is correct) and does not block PASS.

## Anchors used

- **Finding 1, DoD case reproduction**: `anchor: closed-form/hand-computed case` — a fresh independent script (not 07-backend.md's uncommitted ad hoc script, not read, only its stated numbers were compared against), built from AUDIT-quant.md's own original repro shape, executed against the current code.
- **Finding 1, distinct-account non-overcorrection**: `anchor: closed-form/hand-computed case` — synthetic same-symbol-different-account and N=3-distinct-symbol scripts, substituting for the locally-skipped golden PDF test (see risks).
- **Generalization judgment**: `anchor: closed-form/hand-computed case` — synthetic N=3-with-one-falsy-id script.
- **Finding 2**: `anchor: methodology-doc` (consistency check, appropriate here — Finding 2 was a documentation-gap finding, not a formula-correctness finding, so checking the new doc text against the code it describes is the correct and sufficient anchor) plus one `anchor: closed-form/hand-computed case` (the starting_nav None-vs-zero fallback, and the same-symbol-different-account sum) where the doc's claim was itself checkable independently of the code's own self-description.
