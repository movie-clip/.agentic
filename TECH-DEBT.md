# Tech debt — `.agentic`

What is wrong or missing in the network **right now**. Each item has an ID;
[`ROADMAP.md`](./ROADMAP.md) schedules them by that ID.

**Rules for this file.**

- Present tense only. When an item is fixed, delete it here and record the
  fix in the commit that fixes it. No "done" rows, no history.
- One item per problem: what is wrong, the evidence, the direction of the fix.
- A gap kept on purpose stays listed, marked **by choice**, with the
  condition that would reopen it.

Last reviewed: 2026-10-06, at v0.8.0.

---

## Enforcement — rules that rest on an agent's judgment

| ID | Problem | Evidence | Fix direction |
|---|---|---|---|
| TD-01 | **Technique-skill calls rest on prose.** A pack names the trigger; nothing forces the call. `skill_calls:` makes a skip visible, and only tech-lead INTEGRATION check 7 judges it. | v0.7.14: two lanes wrote past a mandatory bullet in the same run. | Keep the field; measure skip honesty across the next runs before building more. |
| TD-02 | **Nobody checks the tech lead's own `skill_calls:`.** Check 7 reads the reports the tech lead reviews, not the one it writes. | v0.7.14: the tech lead cited the trigger's exact case as precedent and never called the skill. | Give the check to `reviewer`, or to the close-out sweep as a human-read `Open` row. |
| TD-03 | **The authoring gate is judgment, not a check.** Only frontmatter parsing and `model:`/`effort:` are mechanical. Index correctness, bullet length and contradictions are read by an Opus agent. | `2026-09-30-lint-mattpocock-skills`: 7 style FAILs, 1 real contradiction filed as a risk; the 200-char rule blocked in one earlier run and not in another. v0.7.16 made style non-blocking and added rule 9. | Script the countable parts (`check_pack.py`: index ↔ headings, bullet length on added lines). Leave only contradictions and placement to the agent. |
| TD-04 | **A lint `PASS` says nothing about facts.** The linter never opens the bound repo. | Every skill name and path in the mattpocock wiring was unverified at PASS. | `UNVERIFIED:` risks (v0.7.16) make it visible. A fact check stays with the lanes' `pack_corrections`. |
| TD-05 | **Nothing blocks an unlinted network edit — the `Stop` hook only mentions it.** `check_network_edit.py` decides the condition and `network_edit_gate.py` puts it in front of whoever is finishing the session, then releases. Claude Code's own guidance is that a hook is not where a hard deny belongs; `--strict` in a pre-commit hook is. | v0.7.17 built the check after v0.7.16's contradiction sat live for a day. The reminder half shipped; the blocking half did not. | ROADMAP item 5 wires `--strict` as a pre-commit hook. Until then, same shape as TD-14: run it by hand. |
| TD-06 | **A work order's factual claims are unchecked.** `orchestrator.md` § 6 requires each claim to be sourced; nothing verifies it. | The first phase-model run asserted a file that was never in git. | Hard to mechanise. Watch for it in gate findings. |
| TD-07 | **A phase skipped on a false clause may stay skipped.** The clause is on disk; whether anyone re-reads it when it turns true is prose. | — | Watch. |
| TD-08 | **Conditional pack sections rely on the agent choosing to read them.** | — | Covered by the always-read rule in `authoring.md`; TD-03's script would check index shape. |
| TD-09 | **The scope fence is prose.** **By choice.** No recorded breach across ~110 dispatches. | — | Reopen on the first real breach. |
| TD-10 | **`Bash` is a write primitive** for lanes otherwise bounded by having no `Edit`. | — | Reopen with TD-09. |

## Wiring and configuration

| ID | Problem | Evidence | Fix direction |
|---|---|---|---|
| TD-11 | **The entry-point guard has never been tested live.** All three repos that enable `mattpocock-skills` — `portfolio`, `budget`, `impact` — now carry the paragraph, each naming its own consequence. Whether a main session actually obeys it over `diagnosing-bugs` is unmeasured. | `tradingview` and `datoro` enable no competing skill, so there is nothing there to guard. | Send a matching request in one of the three and see which skill loads. Prose is all this can ever be — nothing can intercept the main session's own skill choice. |
| TD-12 | **`frontend-design` is enabled in `portfolio` with no pack guidance.** The frontend lane can call it and nothing says when; it may compete with the mandatory `ui-polish`. | `portfolio/.claude/settings.json`. | Either write the trigger into `frontend.md` or disable it there. |
| TD-13 | **`build-story` is superseded, not deleted.** It still sits in `portfolio/.claude/skills/`, now routing to `orchestrate-feature`. | — | Delete it through a portfolio run (repo file, not network wiring). |
| TD-14 | **Hook installation is unverifiable from here.** The hooks live in each bound repo's `.claude/settings.json`; an uninstalled hook is silent. | `test_hooks.py` pins behaviour, not installation. | The close-out sweep is the backstop; a bind-time check could confirm it. |

## Coverage — built but not exercised

| ID | Problem | Fix direction |
|---|---|---|
| TD-15 | **`datoro` and `los-tres` are bound but have never run.** Their profiles, phases and packs are untested. `los-tres` was bound before any code existed (2026-10-12), so its packs hold constraints and empty `Layout` sections that its first slices fill. | One small real request each. For `los-tres`, the first is the MVP-scope framing run. |
| TD-16 | **`probe_engine`, `build_snapshot` and `reset_goldens` are tested but unused.** Only `run_tests` and `check_gates` appear in a run. | Keep until a run needs them; drop if still unused after several portfolio runs. |
| TD-18 | **The orchestrator has no behavioural evaluation.** Scripts are pinned by tests and lanes by gates; nothing checks the orchestrator's decisions (which phases fire, the budget, where it stops for the human) against known-good answers. Anthropic recommends starting with about 20 real cases and judging the end state. | On 2026-10-06, 1 of 5 runs had closed, and it spent twice its derived budget. | Write about 10 eval cases from requests already run (request → expected phase verdicts, human stops, budget range). Run them with `claude plugin eval` before changing the skill or `orchestrator.md`. |
| TD-19 | **`protocol/orchestrator.md` is about 750 lines, read in full at every intake.** With `PROTOCOL.md` it puts about 1,150 lines of rules and rationale in front of the first dispatch. Anthropic's guidance is the smallest high-signal context, plus examples instead of lists of edge cases. v0.8.0 cut the skill from 510 lines to about 260 and left the protocol alone. | `wc -l`, 2026-10-06. | Condense to 400 lines or fewer: keep every rule, and move each war story to `ARCHITECTURE.md` or `git log`. It goes through a `protocol-lint` run. |

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
| Planning artifacts carry a brief | script — `check_report.py`; usefulness unchecked |
| Agent frontmatter parses; model and effort pinned | command + script — `claude plugin validate`, `check_agents` |
| The validator, hooks and checks are correct | tests — `test_check_report.py` 220, `test_hooks.py` 34, `test_ledger.py` 43, `test_check_network_edit.py` 15, `test_pine_check.py` 55 |
| An unfinished run is seen again | prose — intake lists every ledger not `CLOSED` and the human resumes, drops or leaves it |
| A run survives a restart | the ledger on disk |
| Read-only lanes don't edit | tool grant — no `Edit`; see TD-10 |
| A network file edit is sound | gate by judgment — TD-03, TD-04 |
| A network file edit was gated at all | script — `check_network_edit.py --strict`, exit 1. `network_edit_gate.py` at `Stop` is the reminder that it exists, not the enforcement: a `Stop` hook releases after one hold, does not block on a timeout, and is one settings line from gone. The enforcement point is the commit, TD-05 |
| A technique skill is called when triggered | prose + field — TD-01, TD-02 |
| The orchestrator is the entry point | prose in three `CLAUDE.md` files, untested live — TD-11 |
| A work order's claims are true | prose — TD-06 |
| A pack section is read when needed | prose + `## Index` — TD-08 |
| `scope` fences a work order | prose, by choice — TD-09 |
| A run's cost matches its plan | nothing, by choice — the 2x ceiling is the only stop |
| The orchestrator decides well | nothing — TD-18 |
| A report's contents are true | nothing can — that is what the gates are for |
