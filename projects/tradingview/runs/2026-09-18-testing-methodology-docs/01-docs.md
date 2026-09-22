REPORT 2026-09-18-testing-methodology-docs/01
status:      DONE
verdict:     NONE

changed:
  - C:\projects\investments\tradingview\docs\testing-methodology.md — new file: three verification layers (static check / hand-derivation / live compile check), the clipboard-based paste method for the Pine Editor, why character-by-character/insertText paste corrupts indentation, how to read compile vs. symbol-resolution failures, and the no-autosave experimentation note.
  - C:\projects\investments\tradingview\docs\tradingview-symbol-verification.md — new file: the bare-ticker COT symbol finding (no `COT2:`/`COT:` prefix, no `_ALL` suffix), why it matters against guardrail 3, the general verification method, and a dated caveat.

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order's verification field was NONE; no command was specified or run.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Both new docs are cross-linked by relative path (`docs/testing-methodology.md` <-> `docs/tradingview-symbol-verification.md`) per the order's requirement.
  - Neither file was checked against `scripts/check_report.py` or any Pine tooling since this lane holds no Bash — content is prose only, drawn from `compile.md` and `run.md`'s Replans v3/v4 rows as instructed, not independently re-verified.
  - Nothing in `mm_cot_long_short_index.pine`, its header, or `docs/mm-cot-long-short-index.md` was touched, per non_goals.

risks:
  - none
