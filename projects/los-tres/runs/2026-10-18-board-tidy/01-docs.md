REPORT 2026-10-18-board-tidy/01
status:      DONE
verdict:     NONE

changed:
  - projects/los-tres/project.md — deleted "(once chosen)" after "the stack" in the CLAUDE.md paragraph (was line 8)
  - projects/los-tres/project.md — deleted "The repo was bound before its first line of code." and the range "decisions 0001-0011" in the "young profile" paragraph (was lines 17-18)
  - projects/los-tres/project.md — dropped "decisions 0001-0011" from "Building before the stack exists" (was lines 99-100); text now cites CLAUDE.md § Stack
  - projects/los-tres/project.md — shortened the build-lane BLOCKED bullet by dropping "to complete its order" (was lines 106-108)
  - projects/los-tres/project.md — deleted the "set by the first stack decision ... not guessed here" paragraph (was lines 130-131)
  - projects/los-tres/project.md — split the Mechanical gates bullet into two one-fact bullets (was lines 149-151)

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order verification was NONE; edits checked by reading the edit results only

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - protocol-lint should re-check project.md: Index headings are unchanged and lines 47-74 (the five guardrails) were not edited.
  - The heading "Building before the stack exists" is kept as ordered; architecture.md:53 still resolves.

skill_calls:
  - none

risks:
  - Conflict named per the order: project.md is outside the docs pack's close-out scope (capabilities/**); edited anyway on the human's order.
  - Not fixed: the "Why quant is not bound" paragraph has one long line (about 190 chars, "They are not a methodology ... Gates that apply:") that breaks the wrapping style.
  - Not fixed: the profile intro (line 12-13) still says the profile carries "the rules for building before a stack decision exists", which is dated wording like the heading.
  - Not fixed: the UNVERIFIED premises from 06-protocol-lint.md (Slice field, slices A and B, gate contents vs package.json) were not checked.
  - The "Lane routing" docs row and the paragraph after the table now run into the "No project tool server" paragraph directly after the deletion; reads correctly.
