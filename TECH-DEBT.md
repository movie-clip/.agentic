# Tech debt — `.agentic`

What is wrong or missing in the network **right now**. Each item has an ID;
[`ROADMAP.md`](./ROADMAP.md) schedules them by that ID.

**Rules for this file.**

- Present tense only. When an item is fixed, delete it here and record the
  fix in the commit that fixes it. No "done" rows, no history.
- One item per problem: what is wrong, the evidence, the direction of the fix.
- A gap kept on purpose stays listed, marked **by choice**, with the
  condition that would reopen it.

Last reviewed: 2026-11-20, at v0.10.2. v0.10.0 is tagged as the known-good baseline.

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
| TD-11 | **The entry-point guard has never been tested live, and two repos lack it.** `portfolio` and `budget` carry the paragraph. `los-tres` and `los-tres-collector` enable `mattpocock-skills` too, and their `CLAUDE.md` does not name `orchestrate-feature`. Whether a main session obeys the paragraph over `diagnosing-bugs` is unmeasured. | `grep orchestrate-feature */CLAUDE.md`, 2026-11-20; `impact` was not checked. `tradingview` and `datoro` enable no competing skill. | Add the paragraph to the two repos through a run in each. Then send a matching request and see which skill loads. Prose is all this can ever be — nothing can intercept the main session's own skill choice. |
| TD-12 | **`frontend-design` is enabled in `portfolio` with no pack guidance.** The frontend lane can call it and nothing says when; it may compete with the mandatory `ui-polish`. | `portfolio/.claude/settings.json`. | Either write the trigger into `frontend.md` or disable it there. |
| TD-13 | **`build-story` is superseded, not deleted.** It still sits in `portfolio/.claude/skills/`, now routing to `orchestrate-feature`. | — | Delete it through a portfolio run (repo file, not network wiring). |
| TD-14 | **Hooks are wired by hand in each bound repo, and unevenly.** They live in each repo's `.claude/settings.json`; an uninstalled hook is silent. The plugin ships no `hooks/hooks.json`, which is where Claude Code's docs say a plugin's hooks belong. | Only `portfolio` wires a `PreToolUse` commit gate; the other repos carry the two report hooks. `test_hooks.py` pins behaviour, not installation. | Ship the report hooks in the plugin, no-op where no `.agentic.json` is found, then remove the per-repo lines by hand. |

## Coverage — built but not exercised

| ID | Problem | Fix direction |
|---|---|---|
| TD-15 | **`datoro` is bound but has never run, and four projects have no run on disk.** `portfolio`, `budget`, `tradingview` and `datoro` hold an empty `runs/`, so every measurement of the network today comes from `los-tres` and `los-tres-collector`. | One small real request in `datoro`. Until another project runs, treat a conclusion drawn from the corpus as a web-app conclusion. |
| TD-16 | **`probe_engine`, `build_snapshot` and `reset_goldens` are tested but unused.** Only `run_tests` and `check_gates` appear in a run. | Keep until a run needs them; drop if still unused after several portfolio runs. |
| TD-18 | **The orchestrator and grill evals are six cases from one project, and the gates have none.** Three intake cases (request → which phases fire) and three grill cases (planning artifact → what reaches the human) are built from real `los-tres` runs through `evals/_fixture/corpus-run.sh`. Baseline at v0.10.2, one run each on 2026-11-20: all six score 1.00 on the graders as they now stand, at $0.30 to $0.65 and one to three minutes a case. Two limits. The grill fixtures lack facts the real stop had, so the grill holds the go behind a fact check where the real run asked it at once. And the judge model split 2 to 1 against a correct reply once, so that grader is now a regex; the other LLM graders have one reading each behind them. Anthropic recommends 20 to 50 cases, judged on the end state, balanced between what should and should not happen. | A fourth case of each kind (ROADMAP 2a, 2b), then gate cases from the recorded FAILs (2c). Before changing `orchestrate-feature`, `orchestrator.md` or `grill-plan`, run `--case "intake-*"` or `--case "grill-*"` with `--scaffold --runs 1`, and again after. |
| TD-19 | **`protocol/orchestrator.md` is 840 lines, read in full at every intake.** With `PROTOCOL.md` (418) and the skill (282) that is about 1,540 lines of rules and rationale before the first dispatch. Anthropic's guidance is the smallest high-signal context, plus examples instead of lists of edge cases. Measured with `wc -l`, 2026-11-20. | Condense to 400 lines or fewer: keep every rule, and move each war story to `ARCHITECTURE.md` or `git log`. Only after TD-18's cases exist, so the cut can be scored. It goes through a `protocol-lint` run. |

## Measurement — what the network cannot say about itself

Counts are from the 24 closed runs in `corpus/` on 2026-11-20
(22 `los-tres`, 2 `los-tres-collector`).

| ID | Problem | Evidence | Fix direction |
|---|---|---|---|
| TD-20 | **The orchestrator's own cost is unmeasured.** From v0.10.2 the stop hook writes each lane dispatch's tokens and duration to `<nn>-usage.json`, read from the lane's transcript, and `run_stats.py` reports them. The main session's requests are not in any lane transcript, and one session can span several runs. A slot is also left unmeasured when its transcript is gone or unreadable. | Backfill on 2026-11-20: 253 of 272 slots measured, 1,391 lane-minutes, 5.2M output tokens, 431M cache-read tokens. | Attribute main-session requests to a run by the ledger's first and last dispatch times. Read `measured` in the cost table before trusting a total. |
| TD-21 | **Intake under-estimates two runs in three.** `ledger.py` stamps `intake:` from v0.10.1, so the estimate is on the record beside `spent`; nothing yet acts on the gap. | `run_stats.py`: intake 204, spent 272 (1.33x); 17 of 24 runs re-planned. The usual causes: design split the build into more dispatches than intake assumed, and human follow-ups after close. | Consider deriving the build budget after `design`, not at intake. |
| TD-22 | **The grill sends the human about seven active rulings a run.** 264 rulings in 24 runs; 93 passed as assumed and 171 were asked, and the owner reports accepting the recommendation almost every time. `grill-plan` § 2 defaults an unsure node to a human decision. | `decisions.md` across the corpus; owner, 2026-11-20. | Find the decision classes accepted as recommended every time and move those to the assumed list. One class at a time, scored by TD-18's grill cases. |
| TD-23 | **A dispatch is spent to discover the environment is down.** Lanes return `BLOCKED` or `PARTIAL` because Docker or the database is not running, or a permission prompt refused a write. | `2026-11-16-s5-8-filter-by-car` slots 11 and 12; `2026-11-18-s3-1-admin-feeds` slots 13 and 14. | A readiness command the profile declares and intake runs before the first build dispatch. |
| TD-24 | **The orchestrator has filed its own work as a slot.** One Artifacts row names agent `orchestrator`, mode `inline`, with no head — the failure `orchestrator.md` § 7 describes, recorded rather than hidden. | `2026-11-16-s5-8-filter-by-car` row 23; it is the one run the corpus replay fails. | Watch. A second occurrence makes it a TD-18 case. |
| TD-25 | **Run evidence is saved only by hand.** Runs are gitignored and pruned; `replay_corpus.py --add` copies them into `corpus/`, and nothing prompts for it at close. | — | Run `--add` before pruning. Reopen if a pruned run turns out to be missing. |
| TD-26 | **Three bound repos have no CI.** The design names the test runner, the commit hook and CI as the final authority; `los-tres`, `los-tres-collector` and `tradingview` have no workflow, so the gate command runs only when a lane runs it. | `ls <repo>/.github/workflows`, 2026-11-20. Branch rules on the host were not checked. | A workflow running each repo's gate command, delivered as a work order in that repo. |
| TD-27 | **The stop hook can no longer hold a lane.** Claude Code 2.1.329 ends a subagent on a `SubagentHandback` tool call. The `SubagentStop` payload carries no `last_assistant_message`, and an exit 2 from the hook after the handback does not wake the lane (probed 2026-11-20: the hook returned 2 on a malformed artifact and the lane's transcript shows nothing after the handback). Until v0.10.3 the hook found no head, so it wrote no head file and no usage file; the orchestrator derived every head by hand with `--emit-head`. From v0.10.3 the hook reads the head from the transcript, so head and usage files are written again, but a bad head or artifact is still only caught by the write-time hook and the orchestrator's sweep. | Decide whether the hold is worth restoring. Candidates: a `PreToolUse` hook on `SubagentHandback` that checks the message before it is delivered, or accepting the sweep as the gate and deleting the hold code. Needs one probe to confirm `PreToolUse` fires for that tool. |

---

## Enforcement map

What backs each rule today. A rule you believe is enforced, and isn't, is
worse than one you know is on trust.

| Rule | Backed by |
|---|---|
| No lane commits | hook — `pre_commit_gate.py`, wired in `portfolio` only. A project with a tracker lets the orchestrator commit to the run's branch (`orchestrator.md` § 8); its deny list blocks merge and force-push |
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
| The validator, hooks and checks are correct | tests — `test_check_report.py` 228, `test_hooks.py` 41, `test_ledger.py` 61, `test_check_network_edit.py` 17, `test_pine_check.py` 55, `test_run_stats.py` 18, `test_usage.py` 18 |
| A script change leaves the verdict on every real closed run unchanged | script — `replay_corpus.py` against `corpus/baseline.json`; local only, 24 runs |
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
| A run's intake estimate and network version are on record | script — `ledger.py` stamps `intake:` and `network:` on the first write and refuses to set either |
| A lane dispatch's tokens and duration are on record | hook — `report_head_gate.py` at `SubagentStop` calls `usage.py`; it never holds a lane, so a missing file means unmeasured. Installed per repo, TD-14 |
| A run's cost matches its plan | nothing — the 2x ceiling is the only stop; TD-20, TD-21 |
| The orchestrator decides well | nothing — TD-18 |
| The grill sends the right decisions to the human | nothing — TD-18, TD-22 |
| A report's contents are true | nothing can — that is what the gates are for |
