REPORT 2026-11-21-head-file-and-cr-path/01
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   claude plugin validate plugins/agentic-core; git diff of the three scoped files; read of report_head_gate.py and check_report.py head_for, _cr_source
  result:    PASS
  detail:    validate passed (0 errors); 3 files, 0 BLOCKING, 1 SHOULD_FIX; anchor: scripts/hooks/report_head_gate.py and check_report.py _cr_source/head_for (code, not prose); 1 UNVERIFIED premise

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - SHOULD_FIX authoring.md § Writing for the reader you actually have: PROTOCOL.md:341-346, the `raised by` bullet now carries four facts (path not quotation, accepted forms, rejected form, consequence).
  - SHOULD_FIX fix for PROTOCOL.md:341-346: move the two sentences on accepted and rejected path forms into their own bullet, leaving the existing bullet as rule plus consequence.

skill_calls:
  - none

risks:
  - UNVERIFIED: orchestrator.md:609-619 cases 1 and 3 are exclusive only if the artifact is unchanged between the hook's pass and the orchestrator's --head; judged exclusive, since the same _check_head runs on the same inputs.
  - Outside scope: claude plugin validate reports LICENSE_MISSING and ICON_MISSING for plugins/agentic-core; directory-profile issues only, validation itself passed.
  - The hook saves a head only where a bound repo wires it (PROTOCOL.md § 4); orchestrator.md:609 conditions on the file existing, so repos without the hook fall through to case 2 correctly.
