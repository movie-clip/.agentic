# Roadmap — `.agentic`

How the network gets better from here. Problems live in
[`TECH-DEBT.md`](./TECH-DEBT.md); this file orders the work that fixes them.

**Rules for this file.**

- Every item cites the debt IDs it closes, or says it is new capability.
- When an item ships, delete it here, delete its debt rows, and record both in
  `CHANGELOG.md` under the version that shipped them.
- Change priorities on evidence from runs, not on a hunch.

Last reviewed: 2026-09-30, at v0.7.16.

---

## Now — clean state

| # | Item | Closes | Done when |
|---|---|---|---|
| 1 | Resume or close the three stalled runs | TD-18 | each is `CLOSED`, or has a current `next:` you intend to act on |
| 2 | Lint v0.7.16 (linter + `authoring.md` rule 9) against the other agent files as anchor | TD-05 (for this edit) | a `protocol-lint` artifact exists for it |

## Next — make the entry point and the authoring gate reliable

| # | Item | Closes | Done when |
|---|---|---|---|
| 3 | Live-test the orchestrator entry guard: send "this number looks wrong" in portfolio and check which skill loads | TD-11 (portfolio) | the request opens a run, not `diagnosing-bugs` |
| 4 | Add the same guard to `budget` and `impact` `CLAUDE.md` | TD-11 | all three repos with `mattpocock-skills` carry it |
| 5 | `scripts/check_pack.py`: index rows ↔ headings, one section per index row, bullet length on added lines | TD-03, TD-08 | the linter cites the script's output instead of counting |
| 6 | Flag unlinted network edits at close-out or commit | TD-05 | a diff to agents, protocol or packs with no lint artifact fails or warns |
| 7 | Decide `frontend-design` in portfolio: write its trigger into `frontend.md`, or disable it | TD-12 | no enabled skill without a pack trigger |

## Later — coverage and cross-checks

| # | Item | Closes | Done when |
|---|---|---|---|
| 8 | First `datoro` run on a small real request | TD-15 | a closed datoro run |
| 9 | Cross-check the tech lead's own `skill_calls:` (reviewer or close-out) | TD-02 | some reader other than the author judges it |
| 10 | Delete `build-story` from portfolio through a portfolio run | TD-13 | the skill is gone from the repo |
| 11 | Review skill-call honesty across the next 5 runs with a technique trigger | TD-01 | a decision: keep the field as is, or strengthen it |
| 12 | Use or drop the unused tool-server tools | TD-16 | each tool appears in a run, or is removed |
| 13 | Bind-time check that each repo's hooks are installed | TD-14 | the orchestrator reports a missing hook at intake |

## Watching — reopen only on evidence

| Trigger | Then | Debt |
|---|---|---|
| First recorded scope-fence breach | enforce the fence mechanically, and bound `Bash` writes with it | TD-09, TD-10 |
| A gate finding traced to an unsourced work-order claim | add a sourcing check to the ledger script | TD-06 |
| A run that should have re-opened a skipped phase and did not | make the re-read a ledger step | TD-07 |
