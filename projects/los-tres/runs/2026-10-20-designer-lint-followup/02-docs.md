REPORT 2026-10-20-designer-lint-followup/02
status:      DONE
verdict:     NONE
changed:
  - C:\projects\investments\.agentic\protocol\orchestrator.md — CR-1: line 487 reduced to a pointer to core § 5 with no added rule

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    no Bash tool in this lane; the orchestrator runs check_report.py. Edit applied to line 487 only.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Re-run protocol-lint on protocol/orchestrator.md:487 to confirm B1 is cleared (CR-1 round 1 of 2).
  - Not touched, per non_goals: protocol/orchestrator.md:78 example ledger (SHOULD_FIX CR-2 with no Rounds row) and protocol/gates.md:68-70.

skill_calls:
  - none

risks:
  - The order named check_report.py as the verification command, but this lane has no Bash, so the orchestrator runs it.
  - Binding: bound via C:\projects\investments\los-tres\.agentic.json as the order directed.

## Orchestrator brief
CR-1 applied: protocol/orchestrator.md:487 now reads "Non-blocking findings follow core § 5: they do not hold the slice, and reach the human through an `Open` row." This is B1's suggested wording; it matches core § 5 (PROTOCOL.md:334-336) and adds no rule. Nothing else edited.
