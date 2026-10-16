REPORT 2026-10-16-github-tracker-lint/04
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   claude plugin validate C:\projects\investments\.agentic\plugins\agentic-core
  result:    PASS
  detail:    parser PASS; projects/los-tres/project.md judged in full, rules 1-9; 0 BLOCKING, 0 SHOULD_FIX; anchor: authoring.md + phases.md § Git and the tracker, orchestrator.md § 7, agent tools: lines; 1 UNVERIFIED premise

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - projects/los-tres/project.md § Mechanical gates (commit to the run's branch and push it; only a human merges) matches phases.md § Git and the tracker and orchestrator.md § 7 exactly.
  - projects/los-tres/project.md § Lane routing, "No project tool server", agrees with the agent files: every tools: line is an explicit allowlist with no mcp__github__*, and los-tres/.mcp.json declares only `github`.
  - projects/los-tres/project.md Index: all six headings match their entries, and every always-read section is a hazard or guardrail; the three conditional sections have conditions a lane can evaluate.

skill_calls:
  - none

risks:
  - Out of scope (repo file): los-tres/CLAUDE.md:76 says specialist lanes "never touch git", which conflicts with producer.md:50-57 ("Use git for it", git log) in a lane that reads both.
  - Out of scope (repo file): los-tres/CLAUDE.md:71-74 says "Each story gets one branch" and "commit to a story branch"; project.md and phases.md say the run's branch, including plain-issue runs.
  - UNVERIFIED: projects/los-tres/project.md:87 "There is no backlog yet" may now be stale with GitHub Project 3 in use; this is a fact, not an authoring rule.
