REPORT 2026-10-16-tracker-v081-lint/05
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   claude plugin validate C:\projects\investments\.agentic\plugins\agentic-core
  result:    PASS
  detail:    parser PASS; F-5 fixed, F-1..F-4 still fixed; D-2 § 7 pointer clean; 5 scoped files, rules 1-9; 0 BLOCKING, 0 SHOULD_FIX; anchor: authoring.md, and for § Wiring a tracker the 11 agent tools: lines, los-tres .mcp.json/settings.json/CLAUDE.md; 3 UNVERIFIED

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - F-5 fixed: SKILL.md:216 is scoped "once `build` has fired", and SKILL.md:252-254 gives the PR URL only where a tracker is declared and build fired, else uncommitted paths and the command, citing § 8. see § F-5
  - F-1..F-4 spot-confirmed still fixed at SKILL.md:215, :236, project.md:147, authoring.md:406-407, SKILL.md:218-219. see § Round-1 findings
  - D-2 edit clean: orchestrator.md:744 is a pointer to § 8 only; § 8:757-760 is now the single home of the no-tracker default. see § Anchor
  - No new findings on rules 1-9 across the five scoped files. see § Anchor

skill_calls:
  - none

risks:
  - Still true, repo file: los-tres/.claude/settings.json:29-38 denies `gh pr merge` only, not `gh`; orchestrator.md:773-774 says the deny list removes the host's CLI.
  - Still true, repo file: settings.json:30-31 push denies match only `git push origin main` / `HEAD:main`; a bare `git push` with main as upstream is not denied.
  - UNVERIFIED: movie-clip/los-tres protects `main` (PRs only, no force-push, no deletion, no bypass), per authoring.md:418-420; not opened.
  - UNVERIFIED: Project 3 has status options Backlog, Ready, In progress, In review, Done and the repo has labels type:epic/story/ticket, per phases.md:78-79; not opened.
  - UNVERIFIED: Project 3's built-in automation moves a merged issue to Done, as SKILL.md:219 asserts; not opened.

## Orchestrator brief

Verdict PASS; parser clean; no BLOCKING and no SHOULD_FIX findings. F-5
(round 2 of 2, F-1 lineage) is closed by 04's two SKILL.md edits, and the
tracked-no-build situation now reads the same in orchestrator.md § 8, the
Tracker table, the Close checklist and the close-out report list. The D-2
§ 7 pointer leaves § 8 as the only statement of the no-tracker default.
Risks carry two still-true repo-side deny-list gaps (non-goal, not findings)
and three UNVERIFIED host-side premises.

- § F-5 — the fix, line by line, against the situation it named.
- § Round-1 findings — F-1..F-4 spot-confirmation.
- § Anchor — rules 1-9 per scoped file, and what each was checked against.

## F-5

- **Situation:** tracked run, `build` never fires, `close` edits the repo
  (phases.md:43-52, the stack run and the pure-scope run).
- **Rule home:** orchestrator.md:768-770 — no commit, no push, close-lane edits
  stay uncommitted, the close-out report says so.
- **SKILL.md:216:** the PR actions and *reviewing* are now gated "once `build`
  has fired"; the issue stays where framing put it. Consistent.
- **SKILL.md:252-254:** PR URL only "where the profile declares a tracker and
  `build` fired"; otherwise "the uncommitted paths and that command", citing
  § 8. Either antecedent of "where it did not" yields paths plus command, which
  satisfies § 8's "the close-out report says so". Consistent.
- **SKILL.md:256-257:** "except the commits `orchestrator.md` § 8 allows"
  defers to § 8's build condition. Consistent.
- **Rule 2 on the new text:** each SKILL.md mention (216, 218, 236, 252-254)
  scopes a step and cites § 8 rather than re-arguing it; the rule's text lives
  only at orchestrator.md:768-770. No duplication.

## Round-1 findings

- **F-1:** SKILL.md:215 "once `build` has fired"; :236 "tracker declared and
  `build` fired ... (`orchestrator.md` § 8)". Still fixed.
- **F-2:** project.md:147 "Git and GitHub: `CLAUDE.md` § Git and tickets." —
  pointer only. Still fixed.
- **F-3:** authoring.md:406-407 points to orchestrator.md § 8. Still fixed.
- **F-4:** SKILL.md:218-219 holds the § 8 citation and the board-automation
  sentence; "never merge" lives only at orchestrator.md:785. Still fixed.

## Anchor

- **Parser:** `claude plugin validate` passed; no agent file is in scope, so
  rules 3, 4 and 7 have no subject beyond confirming § 8's `git` under `Bash`
  is the main session's, not a lane's.
- **§ Wiring a tracker (subject, not anchor):** checked against network and
  repo files. los-tres/.mcp.json declares only `github`, matching phases.md:75;
  none of the 11 `tools:` lines holds `mcp__github__*`; phases.md:33 build
  human stop reads **yes**; phases.md:71-82 and project.md:127-131, :147
  restate no § 8 procedure or limit; los-tres/CLAUDE.md § Git and tickets
  says only the orchestrator commits and only a human merges.
- **Rule 1:** no repo path, framework or command in orchestrator.md § 1/7/8 or
  SKILL.md; repo specifics sit in phases.md § Tracker.
- **Rule 2:** orchestrator.md § 7:744 no longer restates § 8:757-760 (D-2).
  Grep of PROTOCOL.md, protocol/, skills/ for "uncommitted" and "`build` has
  fired" finds only § 8 and SKILL.md citations.
- **Rules 5, 6:** phases.md `## Contents` lists every heading incl. Tracker;
  project.md `## Index` unchanged, guardrails and Mechanical gates always-read.
- **Rule 8:** nothing in the 04 edits.
- **Rule 9, other pairs judged consistent:** orchestrator.md § 7:738-740 lists
  run-dir files without `tracker.md`, but "only the run dir" governs and
  § 1:30-31, § 8:796 and SKILL.md:207 place it there, so no action differs
  (same call as 01). SKILL.md:22-25 vs § 7/§ 8; phases.md:79 unlabelled
  single-lane issue vs SKILL.md:212; build stop phases.md:33 vs SKILL.md:129,
  :214.
