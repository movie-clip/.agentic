REPORT 2026-10-21-move-capability-layer/03
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   claude plugin validate C:/projects/investments/.agentic/plugins/agentic-core
  result:    PASS
  detail:    Validation passed, 0 frontmatter errors. F10 RESOLVED at protocol/orchestrator.md:17-21; F1-F9 not reopened; 0 new BLOCKING, 0 SHOULD_FIX, 2 UNVERIFIED premises. Anchors: orchestrator.md:201-206, authoring.md:377-414, check_report.py, check_network_edit.py. 18/18 judged: PROTOCOL.md, protocol/authoring.md, protocol/orchestrator.md, protocol/packs.md, plugins/agentic-core/skills/agentic-protocol/SKILL.md, plugins/agentic-core/skills/orchestrate-feature/SKILL.md, plugins/agentic-core/agents/backend-engineer.md, plugins/agentic-core/agents/designer.md, plugins/agentic-core/agents/docs-engineer.md, plugins/agentic-core/agents/frontend-engineer.md, plugins/agentic-core/agents/producer.md, plugins/agentic-core/agents/protocol-linter.md, plugins/agentic-core/agents/quantitative-researcher.md, plugins/agentic-core/agents/reviewer.md, plugins/agentic-core/agents/scout.md, plugins/agentic-core/agents/story-author.md, plugins/agentic-core/agents/tech-lead.md, plugins/agentic-core/agents/test-engineer.md

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - F10 RESOLVED: orchestrator.md:17-21 now files a lint run in <agenticRoot>/runs/ for both a network edit and an onboarding lint, matching orchestrator.md:203-206 and authoring.md:411-413. see § F10
  - F1-F9 not reopened: the F10 fix touched only orchestrator.md:17-21, and F2/F6/F7 lines (201-206, 214-217, 263-264) read as 02 recorded them.

skill_calls:
  - none

risks:
  - UNVERIFIED: authoring.md:405-406 assumes the lanes' Grep/Glob honour the repo's .ignore; carried from 02, not tested.
  - UNVERIFIED: an onboarding lint run in <agenticRoot>/runs/ closes under check_network_edit.py --strict because .agentic shows no network change; I read the script, did not run it on such a run.
  - protocol-linter.md:3 also names "a pack audit" as a lint subject; orchestrator.md:18 opens "A lint run lives in <agenticRoot>/runs/", which covers it by its general clause. Not a contradiction, noted only.
  - plugin validate printed LICENSE_MISSING and ICON_MISSING directory checks against plugin.json/LICENSE, outside scope; neither is a parse error.
  - authoring.md and protocol-linter.md are subjects and my anchor; the F10 fix is in orchestrator.md, so I judged it against authoring.md and the scripts, not the edit against itself.

## Orchestrator brief
Verdict PASS. F10 (round 2 of 2, caused by F3) is RESOLVED; no new blocking finding.
§ F10 holds the evidence with file:line.
§ Explicit checks lists what was re-confirmed after the fix.

## F10

| # | State | Evidence |
|---|---|---|
| F10 | RESOLVED | protocol/orchestrator.md:17-21: "(A lint run lives in `<agenticRoot>/runs/` instead — over an edit to the network itself, or over a new project's profile and packs at onboarding; `authoring.md` § "Linting a network edit" and § "Adding a project" say how.)" Agrees with orchestrator.md:203-206 and authoring.md:411-413; both cited sections exist (authoring.md:377, :400). |

## Explicit checks
- Parse: `claude plugin validate` passed with 0 frontmatter errors.
- The fix is the only unstaged change to orchestrator.md since 02 (`git diff` hunk @@ -15,9 +15,10 @@); no other file in scope changed in a way that bears on run location.
- Grep for run-location statements over all 18 files: PROTOCOL.md:73-74 and orchestrate-feature/SKILL.md:78,87 describe project delivery runs, which § 1's exception carves out explicitly; no remaining statement limits <agenticRoot>/runs/ to network edits only.
- check_report.py treats any run.md three levels below PROTOCOL.md as owing protocol-lint, so an onboarding run filed there is held to the gate as orchestrator.md:203-206 says.
