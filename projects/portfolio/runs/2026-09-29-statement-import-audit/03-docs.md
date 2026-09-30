REPORT 2026-09-29-statement-import-audit/03
status:      DONE
verdict:     NONE

changed:
  - portfolio/docs/tech-debt-register.md — appended 24 rows after the existing table: F1-F20 (High for F1-F4, Medium for F5-F12, Low for F13-F20), plus realized_cash_flow untraceable, import-boundary field contract, and Freedom24/ESPP scope question
  - portfolio/docs/architecture/testing-architecture.md — line 106 docs/IB2026.pdf corrected to docs/IB2026.csv; line 59 dead "-> Epic 24" pointer removed

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order verification was NONE; docs-only edit

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - F10, F12, F13 rows state they need a methodology-owner ruling; decisions.md D-1 did not resolve them, so no engineering CR should be opened against them.
  - F1-F4 (CRITICAL, register rows High) are the D-1 fix scope: F1/F4 backend (freedom24.py plus schema), F2/F3 frontend. F4 needs Optional schema fields, desktop types.ts:37-39 mirror, and the new imports contract doc row.
  - F16 (stale figures in financial-methodology.md) and the realized_cash_flow row need methodology content; flagged to the quant lane, not written here.
  - Test lane must cover: F1 trade dates, F2 combined admission label, F3 same-account overlay, F7 fee double count, F11 None cash merge.
  - Absorbed notes: audit note 1 folded into F4 and the imports-contract row; audit note 2 has its own row and is cross-referenced from F5; recon notes 1 and 2 share one row; note 3 corrected in place; note 4 registered as a question.

skill_calls:
  - none

risks:
  - testing-architecture.md line 60 still says the register carries a "removal protocol" checklist; the register has none. Outside the named stale references, so left untouched.
  - testing-architecture.md lines 73-76 (ranking/construction artifact tests, recon D-05) were not in the order's named references and were not edited.
  - The order's row format has no grade for the three non-F rows; I labelled them UNGRADED or QUESTION and chose priority Medium, Medium, Low myself, which is a judgment the human may change.
  - F16's suggested direction adds "Methodology-doc edit: needs the quant/methodology owner" beyond the audit's own words.
  - Pipe characters were avoided in cells to keep the markdown table valid; a few audit strings were lightly reworded ("and" for "|") where needed.
