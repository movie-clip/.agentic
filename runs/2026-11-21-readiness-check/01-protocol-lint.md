REPORT 2026-11-21-readiness-check/01
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   claude plugin validate plugins/agentic-core; git diff -- protocol; git -C los-tres diff -- agentic/phases.md; read of authoring.md, orchestrator.md §§ 1-3, 6-8, SKILL.md, los-tres agentic/phases.md in full
  result:    PASS
  detail:    PASS on protocol/orchestrator.md, protocol/authoring.md, agentic/phases.md (los-tres). 0 BLOCKING, 2 SHOULD_FIX (rule 8). Validator passed. Anchor: authoring.md, not under edit in the clauses applied. 2 UNVERIFIED premises.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - SHOULD_FIX protocol/orchestrator.md:438-440 (authoring.md § "Writing for the reader you actually have"): the sentence naming runs 2026-11-16-s5-8-filter-by-car and 2026-11-18-s3-1-admin-feeds is provenance; move it to the commit message.
  - SHOULD_FIX los-tres agentic/phases.md:73-74 (authoring.md § "Writing for the reader you actually have"): template is "<what it proves, in one line>"; drop "Every build lane's tests and both runtime gates need it." It changes no action and "runtime gates" is undefined here.

skill_calls:
  - none

risks:
  - UNVERIFIED: that `docker compose up -d --wait db` exits non-zero when Docker is down and is cheap; package.json:14 maps db:up to it, but the command was not run.
  - UNVERIFIED: that the main session can run `npm run db:up` in los-tres without a blocking permission prompt; .claude/settings.json denies no npm command, and it allows none either.
  - Outside the edit: los-tres agentic/phases.md ### "What `ux` feeds" (line 62) has no `## Contents` line; it predates this diff.
  - Outside scope: `claude plugin validate` reports LICENSE_MISSING and ICON_MISSING as plugin-directory checks; validation itself passed.

## Orchestrator brief

PASS. No BLOCKING findings, and two SHOULD_FIX findings (rule 8), listed in handoff, for Open rows.
- Findings by file: for each of the three files, the rules applied. This covers the rule 9 checks against orchestrator.md § 3, § 7, § 8 and SKILL.md (no conflict found), whether the rule has one home (yes), and whether the los-tres block restates procedure (no).

## Findings by file

**protocol/orchestrator.md** — new § 3 subsection "Readiness is checked before the first build order" (lines 423-440).

- Rule 1 (four-layer split): passes. Names no repo, framework or command. The run ids in 439-440 are provenance, filed under rule 8, not rule 1: they direct no action.
- Rule 2 (one home): passes. The operative rule (when, and what each exit code means) is only here. `authoring.md` § "Declaring readiness" holds the block's shape and what the command must do, and it sends "when and how" back to § 3. That is the same split as `## Tracker`. The lead-in clause "one command that exits 0 when the environment … is up" echoes the author-side contract as a gloss. The two copies agree, and the orchestrator's action rests on the bullets, so it is not a second rule.
- Rule 9 vs § 3 control loop: no conflict. The check sits in front of step 6 and spends no budget. Its `BLOCKED` + `blocked_on:` follows § 1 and § "Two field rules". After a fix in the same session, "before the first build order" still holds, so the check runs again with no extra rule.
- Rule 9 vs § 3 "A resumed session is the same session": no conflict. That section makes ledger state identical. The new clause re-checks the environment, which is not ledger state, and it gives that reason.
- Rule 9 vs § 3 re-plan triggers: no conflict. No head returns, so "a head returns BLOCKED" does not fire.
- Rule 9 vs § 7: no conflict. § 7 limits what the main session writes. The check writes nothing in the repo, and the subsection says why it is not a lane's work. The carve-out is no broader than the one command the profile declares.
- Rule 9 vs § 8: no conflict. § 8 governs git and tracker writes, and the check makes none.
- Rule 9 vs SKILL.md: no conflict. SKILL "Before build … wait for a go" and its Tracker row "the human says go … create the branch" both run at the go, and readiness follows the go. Neither orders readiness against branch creation, so a failed check can leave a branch on a BLOCKED run. Both instructions allow that, so they do not contradict. SKILL.md defers to orchestrator.md § 3 for the loop and restates no readiness rule.
- Rule 8: SHOULD_FIX, see handoff (provenance sentence).

**protocol/authoring.md** — Contents line (31-32) and new § "Declaring readiness" (496-512).

- Rule 2: passes. Only the shape and the command's obligations, for the author who needs them. It explicitly does not restate § 3.
- Rule 5 / Contents: the Contents line matches the section name and order.
- Rule 9 inside authoring.md: no conflict with § "Adding a project" (profile edits owe no lint; this lint was ordered anyway) or § "Wiring a tracker" (same placement, after `## Phases`). "cheap enough to run before every build" puts a property on the command. It does not tell the orchestrator when to run it, so it does not compete with § 3.

**agentic/phases.md (los-tres)** — Contents line (15-16) and `## Readiness` (71-74).

- Restates orchestrator procedure? No. The block holds one command and what it proves. The Contents line points at `orchestrator.md` § 3 and says nothing about when, how, or what happens on failure.
- Shape: the block sits after `## Phases` and before `## Tracker`, as authoring.md requires. It has no table, so `check_report.py`'s `## Phases` parse (`_verify_lanes`, `_stop_lanes`) is unaffected.
- Rule 7: `npm run db:up` runs in the main session under Bash. package.json:14 defines it, and no deny rule covers it.
- Rule 8: SHOULD_FIX, see handoff (second sentence beyond the one-line template).
