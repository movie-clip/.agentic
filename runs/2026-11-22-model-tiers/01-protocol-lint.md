REPORT 2026-11-22-model-tiers/01
status:      DONE
verdict:     FAIL
verification:
  command:   claude plugin validate plugins/agentic-core; python scripts/check_report.py runs/2026-11-22-model-tiers/01-protocol-lint.md --lane protocol-lint
  result:    PASS
  detail:    validate passed (0 frontmatter errors); 1 BLOCKING (rule 9), 3 SHOULD_FIX (rule 8); 10/10 agent frontmatters match both authoring.md tables; 0 leftover old values; 2 UNVERIFIED; anchor: the ten agent files' frontmatter plus protocol/orchestrator.md and orchestrate-feature SKILL.md, not authoring.md's own text; scope judged: protocol/authoring.md, protocol/orchestrator.md, plugins/agentic-core/skills/orchestrate-feature/SKILL.md, plugins/agentic-core/agents/engineer.md, plugins/agentic-core/agents/reviewer.md, plugins/agentic-core/agents/tech-lead.md, plugins/agentic-core/agents/test-engineer.md, plugins/agentic-core/agents/protocol-linter.md

changed:
  - none

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - BLOCKING rule 9 (Two instructions may not disagree): protocol/authoring.md:164-167 says `max` is the escalation for any struggling lane; :205-206 now allows an effort override only where the lane is already on Opus. For a struggling Sonnet lane they direct different actions (sonnet/max vs opus).
  - Satisfy the rule 9 finding: reword authoring.md:164-167 so effort escalation (up to `max`) is scoped to Opus lanes and a Sonnet lane escalates its model, matching :205-206 and the orchestrator.md:73 example; or drop the Opus-only clause at :206. Either way state one rule.
  - SHOULD_FIX rule 8 (Writing for the reader): protocol/authoring.md:158 - "moved here on 2026-11-22 after two change requests in one day came from its lane" is provenance; move it to the commit message and keep only the why that changes behaviour.
  - SHOULD_FIX rule 8: protocol/authoring.md:161-162 - "tech-lead did until 2026-11-22" is change history; "No lane runs at `low`; `medium` is the floor" alone carries the rule.
  - SHOULD_FIX rule 8: protocol/authoring.md:126-128 - "so a new Opus lane is added by a ruling" does not follow from frequency, and "ruling" reads as excluding lanes the test puts on Opus; say every Opus lane, test-found or ruled, gets a row in the table.

skill_calls:
  - none

risks:
  - scripts/check_report.py:1110-1129 (out of scope) compares the ledger model cell to the agent's `model:` verbatim, so `opus/high↑` or `opus↑` as orchestrator.md:69/73 and SKILL.md:123 spell it would be reported as a mismatch; I read the code but did not run it on a ledger.
  - claude plugin validate reports LICENSE_MISSING and ICON_MISSING for the plugin directory profile; out of scope here and not a frontmatter error.
  - UNVERIFIED: authoring.md:158 claims two change requests in one day came from the test-engineer lane; I did not open the runs that would confirm it.
  - UNVERIFIED: the content of the owner's 2026-11-22 ruling is taken from the work order's context; I judged only that the files state it consistently.
