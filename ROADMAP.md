# Roadmap — `.agentic`

How the network gets better from here. Problems live in
[`TECH-DEBT.md`](./TECH-DEBT.md); this file orders the work that fixes them.

**Rules for this file.**

- Every item cites the debt IDs it closes, or says it is new capability.
- When an item ships, delete it here, delete its debt rows, and record both in
  `CHANGELOG.md` under the version that shipped them.
- Change priorities on evidence from runs, not on a hunch.
- **A run that is mid-flight is not an item here.** Its ledger carries `status`,
  `next` and `blocked_on`, and that is the authority; a copy in this file is a
  second place to go stale. This file is for changes to the network itself.

Last reviewed: 2026-10-02, at v0.7.17.

---

## Now — finish the authoring gate, and prove the entry point

| # | Item | Closes | Done when |
|---|---|---|---|
| 1 | Live-test the entry guard: send "this number looks wrong" in `portfolio`, `budget` or `impact` and see which skill loads | TD-11 | the request opens a run, not `diagnosing-bugs` |
| 2 | `scripts/check_pack.py` — index rows ↔ headings, and one section per index row | TD-08, TD-03 | an index row naming a heading that does not exist fails a check instead of an Opus read |
| 3 | Decide `frontend-design` in `portfolio`: write its trigger into `frontend.md`, or disable it | TD-12 | no enabled skill without a pack trigger |

Item 2 is the half of the authoring gate worth mechanising: an index row pointing
at a heading that is not there means a lane never reads that section, silently.
Bullet length is the other half and is deliberately not in it — v0.7.16 already
ruled that non-blocking, so a script for it buys cheaper lint rounds, not
correctness.

## Later — coverage and cross-checks

| # | Item | Closes | Done when |
|---|---|---|---|
| 4 | Clear the four rule-8 bullets `2026-10-01-lint-v0.7.16-network-edit/02` left open in `authoring.md` — `:357-360`, `:220`, `:223`, `:230` | TD-03 | a reader stops meeting a 298-character bullet in the file that sets the limit at 200 |
| 5 | Wire `check_network_edit.py --strict` as a pre-commit hook in this repo | TD-05 | an unlinted network edit cannot be committed, rather than being mentioned once at `Stop` |
| 6 | First `datoro` run on a small real request | TD-15 | a closed datoro run |
| 7 | Cross-check the tech lead's own `skill_calls:` (reviewer, or the close-out sweep) | TD-02 | some reader other than the author judges it |
| 8 | Delete `build-story` from portfolio through a portfolio run | TD-13 | the skill is gone from the repo |
| 9 | Review skill-call honesty across the next 5 runs with a technique trigger | TD-01 | a decision: keep the field as is, or strengthen it |
| 10 | Use or drop the unused tool-server tools | TD-16 | each tool appears in a run, or is removed |
| 11 | Bind-time check that each repo's hooks are installed, including this repo's own `Stop` hook | TD-14, TD-05 | a missing hook is reported at intake instead of being silent |

## Watching — reopen only on evidence

| Trigger | Then | Debt |
|---|---|---|
| First recorded scope-fence breach | enforce the fence mechanically, and bound `Bash` writes with it | TD-09, TD-10 |
| A gate finding traced to an unsourced work-order claim | add a sourcing check to the ledger script | TD-06 |
| A run that should have re-opened a skipped phase and did not | make the re-read a ledger step | TD-07 |
