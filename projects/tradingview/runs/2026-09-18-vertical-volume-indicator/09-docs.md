REPORT 2026-09-18-vertical-volume-indicator/09
status:      DONE
verdict:     NONE

changed:
  - volume_profile.pine:81-101 (header, Reconciliation bullet) — corrected to say the ~1.00 invariant is closed only when Status reads a bare "OK" (no na-skip note); when Status reads "OK — N na intrabar(s) skipped", a ratio below 1.00 by exactly the skipped volume's share is the expected, non-suspect reading, per FINDING 6 (07-quant-audit.md) and 06-backend.md § changed.
  - docs/volume-profile.md (new) — created with the six sections capabilities/docs.md names: What it computes, Inputs, Plots and outputs, Sources, Known limits, Reproducing the fixture.

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order's verification field was NONE; prose-only change, docs lane holds no Bash in this project.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - docs/volume-profile.md § Known limits carries 04-quant-audit.md's F2-F5 (open, non-blocking) and 07-quant-audit.md's F7 (open, non-blocking, informational) by name, so a future run does not have to re-derive them from the audit reports.
  - test-engineer coverage still needed per 06-backend.md/07-quant-audit.md handoffs: a partial-na fixture (some intrabars na, some not), a close-is-na fixture (no runtime error, visible degrade), and the composed includeCurrentBar=true + na-skip Status string — none of that is mine to write.
  - the compile check (TradingView editor) remains this project's acceptance command and has not run for this script in this run, per project.md § "Why this project is unusual" — docs cannot substitute for it.

risks:
  - none
