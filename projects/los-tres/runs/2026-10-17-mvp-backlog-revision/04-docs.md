REPORT 2026-10-17-mvp-backlog-revision/04
status:      DONE
verdict:     NONE

changed:
  - C:\projects\investments\los-tres\docs\product\mvp.md — § Product and offers, bullet "When a product loses all its offers" (CR-1): page stays as it is, with two named changes (offer list shows "No offers right now" with last known lowest price and date; structured data omitted)
  - C:\projects\investments\.agentic\projects\los-tres\project.md — line 13: "a repo that has no code yet" became "building before a stack decision exists"
  - C:\projects\investments\.agentic\projects\los-tres\project.md — line 18 paragraph: "greenfield" rewritten as "young"; states stack recorded (decisions 0001-0011) and slices A and B exist
  - C:\projects\investments\.agentic\projects\los-tres\project.md — line 87: "There is no backlog yet." replaced with the Project 3 backlog and Slice field wording
  - C:\projects\investments\.agentic\projects\los-tres\project.md — § Building before the stack exists: stack is recorded, owner owns Stack changes, tech-lead and BLOCKED rules limited to choices no decision covers; heading kept so the Index still resolves
  - C:\projects\investments\.agentic\projects\los-tres\project.md — § Mechanical gates: "There is no gate command yet" replaced with `npm run gate` per CLAUDE.md § Commands
  - C:\projects\investments\.agentic\projects\los-tres\capabilities\product.md — line 4: "no code and no backlog yet" replaced with the corrected wording
  - C:\projects\investments\.agentic\projects\los-tres\capabilities\product.md — § Where the plan lives: added GitHub Project 3 row

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    prose-only order; verification NONE

contract_notes:
  - docs/product/mvp.md is a repo file edited here; the orchestrator must commit it. Stories S6.1 and S8.4 should be read against the new bullet (structured data omitted with no offers).

pack_corrections:
  - none

handoff:
  - Run protocol-lint over project.md and capabilities/product.md; the headings were kept so the project.md Index entries still resolve.
  - Test coverage to name: product page with zero offers shows "No offers right now", last lowest price and date, and emits no JSON-LD.

skill_calls:
  - none

risks:
  - project.md line 18 paragraph was rewritten beyond the cited line (heading "greenfield" to "young") because the whole paragraph was false; the lines changed are listed above.
  - The phrase "Slice field" and "slices A and B" come from the pack-corrections entries and recon, not from a Project 3 check; the GitHub board was not read.
  - project.md § Index still says "Building before the stack exists" is always-read; the section name is now slightly dated but was kept to avoid an Index change outside the order.
