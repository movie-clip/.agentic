REPORT 2026-10-06-lint-v0.8.0-orchestrator/02
status:      DONE
verdict:     PASS
changed:
  - none

verification:
  command:   claude plugin validate C:\projects\investments\.agentic\plugins\agentic-core
  result:    PASS
  detail:    Validation passed. Anchor: authoring.md (not under edit) + 01 findings + git diff; 9 of 9 BLOCKING RESOLVED, 0 new blocking; 1 SHOULD_FIX open; 2 UNVERIFIED premises.

contract_notes:
  - orchestrator.md:254-256 still says every main-session edit is put to the human while a run is open; the hook asks only on writes outside runs/ and git rm/mv, as orchestrator.md:748-750 and SKILL.md:24-26 now say correctly.

pack_corrections:
  - none

handoff:
  - RESOLVED F1 (rule 9): orchestrator.md:179-181 now scopes the gates rule to runs that close and names the abandoned exception, agreeing with orchestrator.md:250-251.
  - RESOLVED F2 (rule 2): SKILL.md:84-85 cites orchestrator.md § 1 'A run that will not finish is abandoned' and restates none of it.
  - RESOLVED F3 (rule 2): SKILL.md:196-200 cites orchestrator.md § 3 'A gate that fails routes' and keeps only the sequence; SendMessage now appears only at orchestrator.md:477-480.
  - RESOLVED F4 (rule 9): SKILL.md:122-124 cites authoring.md § 'Escalating a single dispatch' instead of listing a subset of its triggers.
  - RESOLVED F5 (rule 2): orchestrator.md:485-487 now says a third round is not dispatched (re-plan, take it to the human), agreeing with gates.md:82-83.
  - RESOLVED F6 (rule 1): SKILL.md names no project; grep for tradingview and portfolio matches only the pre-existing description examples at SKILL.md:3.
  - RESOLVED F7 (rule 9): SKILL.md:192-195 defers acceptance-check timing to phases.md, which sets it at phases.md:124-126.
  - RESOLVED F8 (rule 2): the write list now heads orchestrator.md § 7 (:743-750) and SKILL.md:22-23 cites it.
  - RESOLVED F9 (rule 9): phases.md:134-136 now lists review (when it fires) among the orders taking compile.md, agreeing with phases.md:95-97.
  - RESOLVED (rule 8): run-history provenance removed from orchestrator.md and phases.md; phases.md:128-131 now keeps only the why.
  - SHOULD_FIX rule 8: SKILL.md bullets at lines 81, 146, 175, 183, 188, 192, 196 still exceed 200 characters; 175, 183 and 196 carry several facts each.

skill_calls:
  - none

risks:
  - UNVERIFIED: SendMessage resumes a finished subagent from the main session (orchestrator.md:477-480); not checked against Claude Code docs.
  - UNVERIFIED: Claude Code now lets subagents nest (orchestrator.md § 5); not checked against Claude Code docs.
  - Wording: orchestrator.md:746-747 calls git rm/mv 'a work order' and then 'the human's'; read with core § 3 as human-owned, so not judged a contradiction.
  - Re-lint judged the changed lines and their always-read neighbours only, per non_goals; unchanged sections were not re-linted from scratch.
