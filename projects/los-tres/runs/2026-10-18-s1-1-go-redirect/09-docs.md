REPORT 2026-10-18-s1-1-go-redirect/09
status:      DONE
verdict:     NONE

changed:
  - capabilities/testing.md — CR-1: the always-read cookie/origin bullet now states the /go click-through exception, pointing at § Shared scaffolding and gotchas
  - capabilities/testing.md — CR-1: the page.route redirect-target paragraph moved out of § Running tests into § Shared scaffolding and gotchas as a bullet
  - capabilities/testing.md — CR-5: the vi.mock failure-forcing recipe and the Python backspace gotcha are now two bullets
  - capabilities/testing.md — CR-8: guardrail (5) bullet split into the lead fact plus three sub-bullets
  - capabilities/frontend.md — CR-2: the page carve-out in § Layout now lists goPath (src/server/clicks/go-path.ts); guardrail (2) says the page maps goPath and passes the href down
  - capabilities/frontend.md — CR-4: § Before the stack is recorded drops "only" and adds the uncovered framework or package-manager case, citing project.md
  - capabilities/frontend.md — CR-8: guardrail (2) offer-row text split into three sub-bullets
  - capabilities/backend.md — CR-4: § Before the stack is recorded drops "only" and adds the uncovered framework or package-manager case, citing project.md
  - capabilities/backend.md — CR-6: guardrail (5) bullet split into the lead fact plus four sub-bullets
  - capabilities/architecture.md — CR-7: Click log seam recast as a lead sentence plus five sub-bullets, one file and role each
  - phases.md — CR-3: design row now also fires when the request needs a choice no recorded decision covers, citing project.md § Building before the stack exists

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order verification was NONE; edits re-read against the lint handoff by eye, no index or contents block changed

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - capabilities/docs.md:5 still says "stack run that the owner approved", a procedure phases.md no longer defines; outside this order's scope, flagged by protocol-lint
  - Re-run protocol-lint on the five edited files to confirm F1 to F4 clear

skill_calls:
  - none

risks:
  - All eight CRs applied as written; none refused.
  - CR-2 says "the page maps it"; I worded it as the page maps goPath and passes the finished href to the component, consistent with the rule that components receive finished strings.
  - The CRs' raised-by block gives only the fix direction; the exact wording of the new clauses is mine, kept close to the lint handoff text.
  - No section was added or renamed, so no Index or Contents block needed to change.
  - phases.md design row contains no condition keyed on § Stack reading "not chosen".
