REPORT 2026-10-16-tracker-v081-lint/04
status:      DONE
verdict:     NONE

changed:
  - C:\projects\investments\.agentic\plugins\agentic-core\skills\orchestrate-feature\SKILL.md: Tracker table close row (line 216) now opens "once `build` has fired, mark the pull request ready ..." ; resolves F-5 (SKILL.md:216 half)
  - C:\projects\investments\.agentic\plugins\agentic-core\skills\orchestrate-feature\SKILL.md: Close report list item (lines 252-254) gives the pull request URL only where the profile declares a tracker and build fired; otherwise the uncommitted paths and the command, citing orchestrator.md § 8; resolves F-5 (SKILL.md:252-253 half)
  - C:\projects\investments\.agentic\protocol\orchestrator.md: § 7 "Git and tracker writes" paragraph reduced to "**Git and tracker writes.** § 8 says when you make any, and its limit."; resolves decisions.md D-2 (restated no-tracker default, lint risk bullet 1)

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order verification NONE; edits are three exact-match replacements, no retry needed, no stray text

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - re-run protocol-lint on SKILL.md:216, :252-254 and orchestrator.md:744 to confirm F-5 closed (round 2 of 2 fix)
  - SKILL.md:255-256 ("except the commits orchestrator.md § 8 allows where the profile declares a tracker") was out of scope and untouched

skill_calls:
  - none

risks:
  - Out of scope, untouched: los-tres .claude/settings.json deny list does not deny `gh` generally or a bare `git push`; branch protection UNVERIFIED (non-goals).
