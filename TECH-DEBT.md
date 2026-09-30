# Tech debt — `.agentic`

What is wrong or missing in the network **right now**. Each item has an ID;
[`ROADMAP.md`](./ROADMAP.md) schedules them by that ID.

**Rules for this file.**

- Present tense only. When an item is fixed, delete it here and record the
  fix in `CHANGELOG.md`. No "done" rows, no history.
- One item per problem: what is wrong, the evidence, the direction of the fix.
- A gap kept on purpose stays listed, marked **by choice**, with the
  condition that would reopen it.

Last reviewed: 2026-09-30, at v0.7.16.

---

## Enforcement — rules that rest on an agent's judgment

| ID | Problem | Evidence | Fix direction |
|---|---|---|---|
| TD-01 | **Technique-skill calls rest on prose.** A pack names the trigger; nothing forces the call. `skill_calls:` makes a skip visible, and only tech-lead INTEGRATION check 7 judges it. | v0.7.14: two lanes wrote past a mandatory bullet in the same run. | Keep the field; measure skip honesty across the next runs before building more. |
| TD-02 | **Nobody checks the tech lead's own `skill_calls:`.** Check 7 reads the reports the tech lead reviews, not the one it writes. | v0.7.14: the tech lead cited the trigger's exact case as precedent and never called the skill. | Give the check to `reviewer`, or to the close-out sweep as a human-read `Open` row. |
| TD-03 | **The authoring gate is judgment, not a check.** Only frontmatter parsing and `model:`/`effort:` are mechanical. Index correctness, bullet length and contradictions are read by an Opus agent. | `2026-09-30-lint-mattpocock-skills`: 7 style FAILs, 1 real contradiction filed as a risk; the 200-char rule blocked in one earlier run and not in another. v0.7.16 made style non-blocking and added rule 9. | Script the countable parts (`check_pack.py`: index ↔ headings, bullet length on added lines). Leave only contradictions and placement to the agent. |
| TD-04 | **A lint `PASS` says nothing about facts.** The linter never opens the bound repo. | Every skill name and path in the mattpocock wiring was unverified at PASS. | `UNVERIFIED:` risks (v0.7.16) make it visible. A fact check stays with the lanes' `pack_corrections`. |
| TD-05 | **Network edits are gated only when someone asks.** Main-session edits to packs, agents or protocol skip `protocol-lint` unless a lint run is requested. | impact's skill wiring shipped unlinted. v0.7.16's own edit to `protocol-linter.md` and `authoring.md` is unlinted. | A close-out or pre-commit check that flags a diff under `plugins/`, `protocol/` or `projects/*/{project,phases}.md`/`capabilities/` with no lint artifact. |
| TD-06 | **A work order's factual claims are unchecked.** `orchestrator.md` § 6 requires each claim to be sourced; nothing verifies it. | The first phase-model run asserted a file that was never in git. | Hard to mechanise. Watch for it in gate findings. |
| TD-07 | **A phase skipped on a false clause may stay skipped.** The clause is on disk; whether anyone re-reads it when it turns true is prose. | — | Watch. |
| TD-08 | **Conditional pack sections rely on the agent choosing to read them.** | — | Covered by the always-read rule in `authoring.md`; TD-03's script would check index shape. |
| TD-09 | **The scope fence is prose.** **By choice.** No recorded breach across ~110 dispatches. | — | Reopen on the first real breach. |
| TD-10 | **`Bash` is a write primitive** for lanes otherwise bounded by having no `Edit`. | — | Reopen with TD-09. |

## Wiring and configuration

| ID | Problem | Evidence | Fix direction |
|---|---|---|---|
| TD-11 | **Plugin skills compete with `orchestrate-feature` in the main session.** `diagnosing-bugs` matches "this number looks wrong". If the main session takes it, the run silently no-ops and a formula can change with no quant audit. | Only `portfolio/CLAUDE.md` guards it, in prose, never tested live. `budget` and `impact` have no guard. | Test the portfolio guard with a live request; add the same paragraph to `budget` and `impact` `CLAUDE.md`. |
| TD-12 | **`frontend-design` is enabled in `portfolio` with no pack guidance.** The frontend lane can call it and nothing says when; it may compete with the mandatory `ui-polish`. | `portfolio/.claude/settings.json`. | Either write the trigger into `frontend.md` or disable it there. |
| TD-13 | **`build-story` is superseded, not deleted.** It still sits in `portfolio/.claude/skills/`, now routing to `orchestrate-feature`. | — | Delete it through a portfolio run (repo file, not network wiring). |
| TD-14 | **Hook installation is unverifiable from here.** The hooks live in each bound repo's `.claude/settings.json`; an uninstalled hook is silent. | `test_hooks.py` pins behaviour, not installation. | The close-out sweep is the backstop; a bind-time check could confirm it. |

## Coverage — built but not exercised

| ID | Problem | Fix direction |
|---|---|---|
| TD-15 | **`datoro` is bound but has never run.** Its profile, phases and packs are untested. | One small real request. |
| TD-16 | **`probe_engine`, `build_snapshot` and `reset_goldens` are tested but unused.** Only `run_tests` and `check_gates` appear in a run. | Keep until a run needs them; drop if still unused after several portfolio runs. |

## Housekeeping

| ID | Problem | Fix direction |
|---|---|---|
| TD-18 | **Three runs are stalled open.** `tradingview/2026-09-15-fix-systemic-stress-dashboard` waits on a human ruling since 09-15. `impact/2026-09-24-remove-multiplayer` waits on the Unity Editor being closed. `budget/2026-09-29-refine-potential-rules-frequency-sort` stopped at "dispatch 04 frontend". | Resume or close each; a closed-unfinished run records why. |

---

## Enforcement map

What backs each rule today. A rule you believe is enforced, and isn't, is
worse than one you know is on trust.

| Rule | Backed by |
|---|---|
| No agent commits | hook — `pre_commit_gate.py` in the bound repo |
| Reports use the protocol shape | script + hook — `check_report.py`, `report_artifact_gate.py` on every write under `runs/` |
| A report head matches its artifact | hook — `report_head_gate.py` at `SubagentStop`, bounded at two holds |
| Bullets stay routable | script — on the four gate lanes only; advisory elsewhere by choice |
| Every gate ran or was skipped on purpose | script — close-out sweep reads the gate set from `phases.md` |
| Every phase is accounted for | script — close-out sweep |
| `spent` equals the dispatches made | script — close-out sweep |
| A human ruling is written down | script — `decisions.md` required past a declared human stop |
| The ledger header is coherent; `Open` holds only what is open | script — close-out sweep |
| A run that edited network files accounts for `protocol-lint` | script — when `pack-corrections.md` is non-empty |
| Planning artifacts carry a brief | script — `check_report.py`; usefulness unchecked |
| Agent frontmatter parses; model and effort pinned | command + script — `claude plugin validate`, `check_agents` |
| The validator and hooks are correct | tests — `test_check_report.py` 210, `test_hooks.py` 25, `test_ledger.py` 43 |
| A run survives a restart | the ledger on disk |
| Read-only lanes don't edit | tool grant — no `Edit`; see TD-10 |
| A network file edit is sound | gate by judgment — TD-03, TD-04, TD-05 |
| A technique skill is called when triggered | prose + field — TD-01, TD-02 |
| The orchestrator is the entry point | prose — TD-11 |
| A work order's claims are true | prose — TD-06 |
| A pack section is read when needed | prose + `## Index` — TD-08 |
| `scope` fences a work order | prose, by choice — TD-09 |
| A run's cost matches its plan | nothing, by choice — the `model` column is kept, the tally was never read |
| A report's contents are true | nothing can — that is what the gates are for |
