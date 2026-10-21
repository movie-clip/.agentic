REPORT 2026-10-21-s5-2-home-category-tree/11
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   git diff of capabilities/frontend.md; read of § Layout and the pack's other always-read sections against authoring.md
  result:    PASS
  detail:    F1 resolved: frontend.md:36 is one rule with precedence (span/h2 first, two-class override only where it must stay a p); 0 new rule 1-9 findings in § Layout; anchor authoring.md (unchanged since 09); 0 UNVERIFIED

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - F1 (09-protocol-lint.md § Finding F1) closed: frontend.md:36 now states the rule and its exception as one fact and says which applies first; the duplicated specificity clause is gone.

skill_calls:
  - none

risks:
  - none
