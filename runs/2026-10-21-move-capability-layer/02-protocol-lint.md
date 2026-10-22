REPORT 2026-10-21-move-capability-layer/02
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   claude plugin validate C:/projects/investments/.agentic/plugins/agentic-core
  result:    PASS
  detail:    Validation passed, 0 frontmatter errors. F1-F9 all RESOLVED; 1 new BLOCKING (F10, caused by the F3 fix), 0 SHOULD_FIX, 1 UNVERIFIED premise. Anchors: check_report.py, check_network_edit.py, los-tres and impact agentic/ + .agentic.json, 6 bound repos' .gitignore/.ignore, run.md, and the 11 other agent files for authoring.md and protocol-linter.md. 18/18 judged: PROTOCOL.md, protocol/authoring.md, protocol/orchestrator.md, protocol/packs.md, plugins/agentic-core/skills/agentic-protocol/SKILL.md, plugins/agentic-core/skills/orchestrate-feature/SKILL.md, plugins/agentic-core/agents/backend-engineer.md, plugins/agentic-core/agents/designer.md, plugins/agentic-core/agents/docs-engineer.md, plugins/agentic-core/agents/frontend-engineer.md, plugins/agentic-core/agents/producer.md, plugins/agentic-core/agents/protocol-linter.md, plugins/agentic-core/agents/quantitative-researcher.md, plugins/agentic-core/agents/reviewer.md, plugins/agentic-core/agents/scout.md, plugins/agentic-core/agents/story-author.md, plugins/agentic-core/agents/tech-lead.md, plugins/agentic-core/agents/test-engineer.md

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - BLOCKING F10, rule 9, caused by F3 (so round 2 of 2): orchestrator.md:17-20 names only network-edit lint runs as living in <agenticRoot>/runs/. Lines 201-205 and authoring.md:411-413 also put onboarding lint runs there. see § Findings
  - F1-F9 are all RESOLVED. Each has a file:line in § Prior findings.

skill_calls:
  - none

risks:
  - UNVERIFIED: authoring.md:405-406 assumes the lanes' Grep/Glob honour the repo's .ignore. All 6 bound repos list agentic/runs in .ignore, but I did not test that the tools skip it.
  - plugin validate printed LICENSE_MISSING and ICON_MISSING under its directory checks. Both concern plugin.json/LICENSE, which is outside scope, and neither is a parse error.
  - authoring.md and protocol-linter.md are both subjects and my anchor. I judged them against the other 11 agent files and check_report.py, not against themselves (gates.md § 2). The model, effort, tools and MCP-grant tables all match the files.

## Orchestrator brief
Verdict FAIL: 1 BLOCKING finding (F10), 0 SHOULD_FIX. F1-F9 from 01 are all RESOLVED.
F10 continues F3's lineage. Under gates.md § 4 its Rounds row reads `caused by F3`, and the fix is round 2 of 2. The main session owns it (authoring.md § "Linting a network edit" step 3).
§ Prior findings holds F1-F9, each with RESOLVED and its file:line evidence.
§ Findings holds F10: the rule, file:line, and what would satisfy it.
§ Explicit checks lists what else was re-judged and found clean.

## Prior findings

| # | State | Evidence |
|---|---|---|
| F1 | RESOLVED | authoring.md:391-396. Step 3 now says it replaces orchestrator.md § 3's CR routing and § 7's work-order boundary for runs in `<agenticRoot>/runs/`, and cites gates.md § 4 for the cap. |
| F2 | RESOLVED | orchestrator.md:201-205 no longer says packs owe no gate. That rule now lives only at authoring.md:409-410. |
| F3 | RESOLVED, with a leftover (F10) | authoring.md:411-413 now files the onboarding lint as a run in `<agenticRoot>/runs/`, and orchestrator.md:202-205 covers it by citation. |
| F4 | RESOLVED | packs.md:15-16 is a pointer to `orchestrator.md` § 1. The rule lives only at orchestrator.md:207-211. |
| F5 | RESOLVED | packs.md:20 reads "Committing them is the orchestrator's, per `orchestrator.md` § 8." |
| F6 | RESOLVED | orchestrator.md:213-216 no longer mentions `pack-corrections.md`. This matches check_report.py:683-713, where `check_gates` reads only the ledger and the profile. |
| F7 | RESOLVED | orchestrator.md:262-263 keeps only the fact that images are gitignored. designer.md:120-122 holds the reporting rule and cites § 1 for the fact. |
| F8 | RESOLVED | agentic-protocol/SKILL.md:43-45 defines only `agenticRoot` and says "the rest of binding is `PROTOCOL.md` § 1". The JSON example stays. |
| F9 | RESOLVED | authoring.md:26-27. `## Contents` now lists "Linting a network edit". |

## Findings

### F10 — rule 9, "Two instructions may not disagree" (a rule split from its exception). Caused by: F3.
- Where: protocol/orchestrator.md:17-20, against protocol/orchestrator.md:201-205 and protocol/authoring.md:411-413.
- What is wrong:
  - § 1 (17-20) says every slice gets a directory under `<projectDir>`. Its only stated exception is "a run that lints edits to the network itself".
  - The F3 fix sends a second kind of run to `<agenticRoot>/runs/`: the onboarding lint over a new profile and packs (201-205, and authoring.md:411-413).
  - An onboarding lint is not a network edit. So by § 1 it goes under `<projectDir>/runs/`, and by § 3's gate paragraph it goes under `<agenticRoot>/runs/`. Both are in the same file, and the orchestrator reads both.
- Why it matters: if an orchestrator follows § 1, it files the onboarding run under the project. There, check_report.py:786-807 takes the owed gates from the new profile, which declares no protocol-lint. The verdict is then owed by nothing, which is exactly the failure F3 named.
- What would satisfy it: widen the parenthetical at orchestrator.md:18-20 to cover both cases. For example: "(A lint run, over a network edit or over a new project's profile and packs at onboarding, lives in `<agenticRoot>/runs/` instead; `authoring.md` § "Linting a network edit" says how.)"

## Explicit checks
- Parse: `claude plugin validate` passed, with 0 frontmatter errors across the 12 agents and 2 skills.
- Model and effort (rules 3 and 4): all 12 agents declare both. None uses `inherit` or `fable`. Opus is set on quantitative-researcher, protocol-linter and tech-lead, matching authoring.md:130 and :155-157.
- Tools (rule 7): the shell-less lanes are scout, story-author and docs-engineer, and their tools: lines lack Bash, matching PROTOCOL.md:258 and authoring.md:314. The MCP grants match authoring.md:363-375 lane by lane.
- Stale layout: grep for `projects/` and `<project>/` over all 18 files returns nothing.
- Bind: los-tres (`../.agentic`) and impact (`../investments/.agentic`) both resolve to .agentic, and `projectDir: agentic` holds project.md, phases.md, capabilities/ and runs/. The `.agentic` file names only `agenticRoot`, matching PROTOCOL.md:38-40.
- The network-lint procedure (authoring.md:383-387) matches check_report.py:775-807 (`_NETWORK_PHASES` when PROTOCOL.md sits three levels above run.md) and check_network_edit.py (`--strict`, `runs/*/*protocol-lint.md`). This run's run.md follows its shape.
- Commit ownership: I judged orchestrator.md:250 ("the human commits runs") against § 8:799-801 ("commit only what lanes changed; anything else goes to the human") and found them consistent.
