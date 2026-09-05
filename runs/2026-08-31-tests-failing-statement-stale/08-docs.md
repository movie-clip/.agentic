REPORT 2026-08-31-tests-failing-statement-stale/08
status:      DONE
verdict:     NONE

changed:
  - docs/architecture/testing-architecture.md — § "Statement refresh workflow": step 3 re-titled to "importer-derived statement-truth pins" and its "structural tests ... must not fail" sentence narrowed to snapshot-derived tests only; new "Replay-audit regression pins (step 3b)" paragraph added naming test_ledger_replay_audit.py, test_portfolio_state.py AND test_analytics.py as the replay-engine-derived, hand-regenerated inline-pin class; closing regression-pin paragraph narrowed to explicitly exclude that class as a known documented exception.

verification:
  command:   NONE (read-only order; verification field was NONE)
  result:    NOT_RUN
  detail:    Order carried verification: NONE. Amendment cross-checked by reading the shipped test files: grep of "statement refresh:" confirms all three files (test_ledger_replay_audit.py, test_portfolio_state.py, test_analytics.py) carry "# 2026-08-28 statement refresh: <old> -> <new>" comments above the re-pinned approx() literals; statement_truths.py holds only the importer-derived pins (period 2026-01-01 - 2026-08-28).

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - pack-corrections.md item 1 NOT applied to a capability pack: neither capabilities/testing.md nor projects/portfolio/project.md has a statement-refresh-workflow / pin-scoping section, and the order forbids forcing it into an unrelated one. The premise was verified true (test_analytics.py does carry inline replay pins; scout 02 classified it as needing "no numeric change beyond the shared IB_STATEMENT_PERIOD pin"). Suggested addition to capabilities/testing.md — see § Pack correction item 1: suggested wording.
  - For the human close-out: the doc amendment is the interim fix. The proper fix is a diff_replay_truths harness (replay-engine + frozen golden) that test_statement_refresh.py's swap simulation could assert against, closing the "only the truths module moves on a refresh" exception. That is a future producer story (already in 03 and 06 risks); the doc now names it as an unbuilt follow-up.
  - Scope confirmations recorded for close-out: NO docs/product/ change (producer resolved there is no story — 03 § Scope confirmation); NO docs/contracts/ change (no field added/removed/retyped — 03, 06 DoD item 6); NO docs/finance/ methodology change (fixture/pin refresh only, no formula moved — quant-audit 05 via 06). Only testing-architecture.md § "Statement refresh workflow" was touched this lane.
  - statement_truths.py docstring (l.4, l.30 period bump) was the test lane's edit and is already done — this lane did not touch any file under app/tests/.

risks:
  - The amended closing paragraph now asserts the diff_replay_truths harness is "tracked as a producer follow-up", but there is no story ID for it yet (03/06 call it a future producer story, not a filed ticket). If the producer never files it, the documented step-3b exception is permanent rather than interim — the human close-out should decide whether to open that story now.
  - Pack correction item 1 remains unabsorbed into any capability pack (only the repo-side doc half is applied). Per protocol/packs.md an unapplied correction is a real defect surfaced to the human; the suggested wording below is editable and ready to drop in if approved.

## Orchestrator brief

- One repo doc amended (testing-architecture.md § "Statement refresh workflow"); no capability pack file changed.
- pack-corrections.md item 1: premise verified true, but no valid home in testing.md or project.md — recorded not applied, exact suggested wording provided in § "Pack correction item 1: suggested wording" for the human to approve.
- Sections below: "Pack correction item 1: suggested wording" — the editable testing.md addition (one Index row + one new section).

## Pack correction item 1: suggested wording

Target file: `C:\projects\investments\.agentic\projects\portfolio\capabilities\testing.md`.

Add this row to the Index table (under "Read it when"):

```
| Statement refresh — pin classes and scoping | your order refreshes docs/IB2026.csv, or touches statement_truths.py or the replay-audit tests |
```

Add this new section (placement: after "Shared fixtures — mandatory, do not re-implement", before "Assertion conventions"):

```
## Statement refresh — pin classes and scoping

When scoping a `docs/IB2026.csv` refresh, do NOT classify a test file from
reading its assertions — run the actual `pytest -q` failure list first and map
every failing node. Two distinct pin classes move on a refresh:

1. **Importer-derived truths** — `app/tests/statement_truths.py`, one module,
   checked by `diff_statement_truths`. Symbol lists, ledger counts, totals,
   TWR, implied FX.
2. **Replay-engine-derived inline pins** — `pytest.approx` literals
   hand-regenerated each refresh, carrying `# <date> statement refresh:
   <old> -> <new>` comments. They live in at least THREE files, not two:
   `test_ledger_replay_audit.py`, `test_portfolio_state.py` AND
   `test_analytics.py`. `diff_statement_truths` cannot see them; the
   swap-simulation meta-test does not exercise them.

Full workflow: `docs/architecture/testing-architecture.md#statement-refresh-workflow`
steps 3 and 3b.
```
