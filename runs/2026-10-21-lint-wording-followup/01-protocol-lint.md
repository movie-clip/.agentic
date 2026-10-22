REPORT 2026-10-21-lint-wording-followup/01
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   claude plugin validate C:/projects/investments/.agentic/plugins/agentic-core
  result:    PASS
  detail:    Validation passed, 0 frontmatter errors. 4/4 edits judged: 3 clean, 1 BLOCKING (F1, packs.md:20-21). 0 SHOULD_FIX, 2 UNVERIFIED. Files: PROTOCOL.md, protocol/authoring.md, protocol/packs.md, protocol/orchestrator.md. Anchors: orchestrator.md § 8, orchestrate-feature/SKILL.md:215,236, check_report.py:10-11.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - BLOCKING F1, rule One rule, one home + Two instructions may not disagree: protocol/packs.md:20-21 says the orchestrator commits pack corrections wherever a tracker is declared. orchestrator.md:783-785 says no commit unless build fired. see § F1
  - F1 fix: replace packs.md:20-21 with a pointer that states no condition, e.g. "Who commits them is `orchestrator.md` § 8's rule." Alternatively, restate § 8 in full: "where a tracker is declared and `build` fired".
  - Edit PROTOCOL.md:99-100 clean: lint run_dir agrees with authoring.md:383, orchestrator.md:18-19 and check_report.py:10-11. It puts the run_dir exception beside the core § 2 template it qualifies.
  - Edit authoring.md:402-404 clean: agentic/runs/README.md matches the existing portfolio/agentic/runs/README.md. A README is not a run.md, so the orchestrator.md:238-239 intake listing is unaffected.
  - Edit orchestrator.md:251-252 clean: it agrees with § 8:802-804 (stage only paths named in lanes' artifacts) and SKILL.md:215 ("commit its paths"), so the run dir stays out of the pull request.
  - F1-F10 of run 2026-10-21-move-capability-layer are not reopened: the four edits touch none of the lines those findings cite.

skill_calls:
  - none

risks:
  - UNVERIFIED: only portfolio was checked for agentic/runs/README.md. Budget, datoro, impact and los-tres repos were not opened.
  - UNVERIFIED: authoring.md:406 assumes lanes' Grep/Glob honour .ignore. Carried from run 2026-10-21-move-capability-layer/03; not tested.
  - plugin validate printed LICENSE_MISSING and ICON_MISSING directory-profile checks. Both are outside scope, and neither is a parse error.
  - orchestrator.md:265-266 gives the png ignore as agentic/runs/**/*.png. A lint run in .agentic/runs/ falls outside that glob. This line was not edited here; noted only.

## Orchestrator brief
Verdict FAIL on one BLOCKING finding, F1 in protocol/packs.md:20-21. The other three edits are clean.
§ F1 holds the evidence and the fix.
§ Edits judged gives each edit's verdict with file:line.

## F1

| Field | Value |
|---|---|
| Rule | authoring.md § "One rule, one home" (orchestrator rules live in `orchestrator.md` only) and § "Two instructions may not disagree" (a rule and its exception are one fact) |
| File:line | protocol/packs.md:20-21: "The orchestrator commits them where the project declares a tracker, and the human commits them everywhere else (`orchestrator.md` § 8)." |
| Source it restates | protocol/orchestrator.md:783-785: "The branch exists only once `build` has fired. In a tracked run where it did not, you make no commit and no push, and whatever the `close` lane edited stays uncommitted for the human". The same condition appears at orchestrate-feature/SKILL.md:215 and :236 ("once `build` has fired"). |
| Consequence | A tracked run where build did not fire can still emit a pack correction, for example a recon-only run. Its close-out docs order edits packs, and the two files then direct opposite actions. packs.md says the orchestrator commits them. § 8 says it must not, and the human does. packs.md quotes no condition, so a reader sees nothing that makes it the wrong copy. |
| What satisfies it | Make packs.md:20-21 a bare pointer that restates no condition, e.g. "Who commits them is `orchestrator.md` § 8's rule." The docs lane has no Bash (docs-engineer.md:4) and commits nothing, so it loses no action. |

## Edits judged

| Edit | Verdict | Evidence |
|---|---|---|
| PROTOCOL.md:99-100 lint run_dir | clean | Agrees with authoring.md:383 (`<agenticRoot>/runs/<date>-<slug>/run.md`), orchestrator.md:18-19, and PROTOCOL.md:38-40 (`.agentic` has no projectDir). It qualifies the `<projectDir>` term in the same fence bullet, so it is one fact and not a second rule. |
| authoring.md:402-404 runs/README.md | clean | Matches the existing `portfolio/agentic/runs/README.md`. orchestrator.md:238-239 lists only `run.md`. check_network_edit.py:32 excludes runs/**. |
| packs.md:20-21 who commits | BLOCKING | F1 |
| orchestrator.md:251-252 run dir out of PR | clean | Consistent with § 8:802-804 and SKILL.md:215. § 8:774 has the human commit in untracked runs, which matches "The human commits runs". |
