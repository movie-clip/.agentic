REPORT 2026-11-21-example-path/01
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   python C:\projects\investments\.agentic\scripts\check_report.py C:\projects\investments\.agentic\runs\2026-11-21-example-path\01-protocol-lint.md --lane protocol-lint
  result:    PASS
  detail:    protocol/orchestrator.md:312 judged against protocol/authoring.md (anchor: rule text; subject is not authoring.md or protocol-linter.md); 0 BLOCKING, 0 SHOULD_FIX; plugin validate passed; 0 UNVERIFIED premises.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

skill_calls:
  - none

risks:
  - Out of scope: plugins/agentic-core/evals/_fixture/los-tres.sh:12-18 and corpus-run.sh:17-24 build the los-tres path as $INV/los-tres; they will break when the folder moves.
  - Not a finding: protocol/orchestrator.md:312 now matches the binding in PROTOCOL.md:32 and portfolio/.agentic.json (projectDir "agentic"), which I opened; no rule 1, 2 or 9 conflict.
