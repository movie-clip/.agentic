REPORT 2026-09-23-active-scene-diagnostic/05
status:      DONE
verdict:     NONE

changed:
  - Impact/Packages/athena.core/PACKAGE_DOCUMENTATION.md — added `ActiveSceneDiagnosticSystem` to Purpose bullets, "What It Actually Contains", and a new "Active scene diagnostic" subsection under "How It Works Today", same detail level as the existing `SessionStartDiagnosticSystem` entry
  - Impact/PACKAGE_ARCHITECTURE.md — extended the `athena.core` note (which already named `SessionStartDiagnosticSystem` individually) to also name the new `ActiveSceneDiagnosticSystem`

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order's verification field was NONE — doc reconciliation, no compile/test step owed

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - none
