# Roadmap — `.agentic`

How the network gets better from here. Problems live in
[`TECH-DEBT.md`](./TECH-DEBT.md); this file orders the work that fixes them.

**Rules for this file.**

- Every item cites the debt IDs it closes, or says it is new capability.
- When an item ships, delete it here, delete its debt rows, and say what shipped
  in the commit message that ships it.
- Change priorities on evidence from runs, not on a hunch.
- **A run that is mid-flight is not an item here.** Its ledger carries `status`,
  `next` and `blocked_on`, and that is the authority; a copy in this file is a
  second place to go stale. This file is for changes to the network itself.

Last reviewed: 2026-11-20, at v0.10.2.

---

## The order, and why

v0.10.0 does its job, and is tagged as the baseline. So the order is: measure
before changing, build the cases that can score a change before making it, and
leave the changes that touch behaviour for last.

## How every change below ships

A change to an agent, a skill, the protocol or a script follows these steps.
They exist so that a change which makes the network worse is seen at once and
undone in one command.

1. No network edit while any run is open (`check_report.py` compares ledger
   cells to the current agent files).
2. One change, one version bump in `plugin.json`, one tag.
3. The script tests pass, and `replay_corpus.py` reports every real run
   replaying as the baseline.
4. A `protocol-lint` run passes for an edit to an agent, a skill or the
   protocol.
5. The eval cases that cover the changed file run before and after: one case,
   one run by default; anything larger is costed and agreed first.
6. One real run is watched, and its numbers compared with the stats of the
   runs before it.
7. Worse means back to the previous tag.

## 1 — Measure

No behaviour changes. Everything here reads ledgers or adds a field.
`run_stats.py` prints what is measured so far; run it before and after every
change below.

| # | Item | Closes | Done when |
|---|---|---|---|
| 1d | The orchestrator's own tokens per run, from the main session's transcript | TD-20 | a run's cost includes the session that dispatched it |

## 2 — Evals

| # | Item | Closes | Done when |
|---|---|---|---|
| 2a | A fourth intake case, from a project that is not a web app | TD-18 | the intake set is not all `los-tres` |
| 2b | A fourth grill case: a planning artifact with nothing open. And a fixture that carries the facts the real stop already had, so the go is asked in round one | TD-18 | the grill set covers the empty case, and a case scores what was asked, not what was held |
| 2c | Gate cases from the recorded FAILs: the work a gate failed, and the same work fixed | TD-18 | a gate change can be scored on a case it should fail and one it should pass |

## 3 — Enforce

Each item is one version.

| # | Item | Closes | Done when |
|---|---|---|---|
| 3a | Built 2026-11-20 (v0.10.6): `plugins/agentic-core/hooks/hooks.json` ships the write check, the handback gate and the stop record through `hooks/run.py`, silent where no `.agentic.json` is found or the repo wires the same script itself. Remaining: the owner removes the three hook entries from each bound repo's `settings.json`, then one run is watched | TD-27 | a bound repo with no hook entries of its own still gets head files, usage files and a held bad handback |
| 3b | CI running the gate command in `los-tres`, `los-tres-collector` and `tradingview`, as a work order in each | TD-26 | a red gate blocks the pull request |
| 3c | A readiness command in the profile, run at intake before the first build dispatch | TD-23 | Docker being down costs a sentence, not a dispatch |
| 3d | Done 2026-11-20: `scripts/hooks/pre-commit` is installed in this repo's `.git/hooks` | TD-05 | an unlinted network edit cannot be committed |
| 3e | The entry-point paragraph in `los-tres` and `los-tres-collector`, then one live test | TD-11 | a matching request opens a run, not `diagnosing-bugs` |

## 4 — Optimise

Only with the numbers from 1 and the cases from 2. Each item is one version and
is undone if the watched run is worse.

| # | Item | Closes | Done when |
|---|---|---|---|
| 4a | Move the decision classes the owner accepted as recommended every time to the grill's assumed list, one class at a time | TD-22 | fewer active rulings a run, and no ruling reversed after the fact |
| 4b | Derive the build budget after `design` returns, not at intake | TD-21 | re-plans caused by the build split stop |
| 4c | Condense `protocol/orchestrator.md` to 400 lines or fewer, every rule kept | TD-19 | intake reads under 1,100 lines, lint passes, the intake and grill cases score as before |
| 4d | `scripts/check_pack.py` — index rows ↔ headings | TD-08, TD-03 | an index row naming a missing heading fails a check instead of an Opus read |

## Later

| # | Item | Closes | Done when |
|---|---|---|---|
| 5 | Decide `frontend-design` in `portfolio`: write its trigger into `frontend.md`, or disable it | TD-12 | no enabled skill without a pack trigger |
| 6 | First `datoro` run on a small real request | TD-15 | a closed datoro run in the corpus |
| 7 | Cross-check the tech lead's own `skill_calls:` | TD-02 | some reader other than the author judges it |
| 8 | Delete `build-story` from portfolio through a portfolio run | TD-13 | the skill is gone from the repo |
| 9 | Review skill-call honesty across 5 runs with a technique trigger | TD-01 | a decision: keep the field as is, or strengthen it |
| 10 | Use or drop the unused tool-server tools | TD-16 | each tool appears in a run, or is removed |
| 11 | Clear the four over-length bullets left in `authoring.md` (`:357-360`, `:220`, `:223`, `:230` when filed) | TD-03 | the file that sets the bullet limit no longer breaks it |

## Watching — reopen only on evidence

| Trigger | Then | Debt |
|---|---|---|
| First recorded scope-fence breach | enforce the fence mechanically, and bound `Bash` writes with it | TD-09, TD-10 |
| A gate finding traced to an unsourced work-order claim | add a sourcing check to the ledger script | TD-06 |
| A run that should have re-opened a skipped phase and did not | make the re-read a ledger step | TD-07 |
| A second Artifacts row naming the orchestrator as the agent | an eval case, and a check in `ledger.py` | TD-24 |
| The integration gate passes work a later gate or the owner rejects | calibrate it against that case | TD-18 |
