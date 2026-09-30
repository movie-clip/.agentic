# Decisions — 2026-09-30-import-critical-fixes (D-1 carried verbatim from 2026-09-29-statement-import-audit)

## D-1 · verify (post quant-audit FAIL) · 2026-09-30
open decision:  scope after audit FAIL — plan fixes now, or record findings and close; plus rulings on F10/F12 (overlapping-statement merge methodology) and F13 (multi-currency admission `verified`)
raised by:      02-quant-audit.md § Findings; 02-quant-audit.md § Orchestrator brief
ruling:         "okay, put all your findings into docs/tech-debt-register.md, and then start working to fix critical problems"
by:             the human, in session
note:           the ruling does not address F10/F12/F13; they are recorded in the register and remain open for a later human decision. "critical problems" = the CRITICAL-graded findings F1-F4 in 02-quant-audit.md § Findings.

## D-2 · framing · 2026-09-30
open decision:  include F7 (Freedom24 double commission) in the F1 story?
raised by:      02-quant.md § F1; 01-product.md § Open decisions
ruling:         "Include F7 with F1 (Recommended)" — US-46.2 fixes dates and the double commission; ACs can pin TWR 3.81%.
by:             the human, in session (AskUserQuestion)

## D-3 · framing · 2026-09-30
open decision:  D-F2 — admission label rule for a portfolio combined from several statements
raised by:      02-quant.md § F2
ruling:         "Weakest + recompute (Recommended)" — Label = weakest of each statement's own admission AND the recompute on the combined snapshot.
by:             the human, in session (AskUserQuestion)

## D-4 · framing · 2026-09-30
open decision:  D-F1 — Freedom24 replay window anchor (first ledger entry vs statement period start)
raised by:      02-quant.md § F1
ruling:         "Keep current anchor (Recommended)" — No methodology change in this slice; record period-start anchoring in the tech-debt register for later.
by:             the human, in session (AskUserQuestion)

## D-5 · framing · 2026-09-30
open decision:  F4 — behaviour of workspaces saved before the fix that hold fabricated cost basis
raised by:      02-quant.md § F4
ruling:         "Recompute on load (Recommended)" — Re-derive from the stored statement so stale fabricated values disappear.
by:             the human, in session (AskUserQuestion)

## D-6 · framing · 2026-09-30
open decision:  story split and epic placement
raised by:      01-product.md § Open decisions
ruling:         defaults taken (four stories US-46.1..46.4, no epic); presented to the human as "I'll go with that unless you say otherwise" and the human did not object.
by:             the human, in session (implicit acceptance of stated default)

## D-7 · specification (story stop) · 2026-09-30
open decision:  workspaces saved by the old add-statement path (doubled positions; last-file-only admission label)
raised by:      docs/product/stories/US-46.1-add-statement-same-account-replaces.md § Open decisions; US-46.3-combined-portfolio-admission-weakest-label.md § Open decisions
ruling:         "Re-derive on load (Recommended)" — saved combined nodes are recomputed, so old doubled values and labels disappear. Adds ACs and a persistence ticket to each story.
by:             the human, in session (AskUserQuestion)

## D-8 · specification (story stop) · 2026-09-30
open decision:  IB importer drops a whole position when its Cost Basis cell is malformed
raised by:      docs/product/stories/US-46.4-freedom24-cost-basis-unavailable.md § Open decisions
ruling:         "Register it, out of scope (Recommended)" — keep US-46.4 focused on F4; add a tech-debt register row for the IB malformed-cell drop.
by:             the human, in session (AskUserQuestion)

## D-9 · specification (story stop) · 2026-09-30
open decision:  approval of draft stories US-46.1..46.4
raised by:      03-story.md
ruling:         "Approve all four" (with D-7 and D-8 folded in)
by:             the human, in session (AskUserQuestion)

## D-10 · build (pre-build plan stop) · 2026-09-30
open decision:  H-1 golden recapture needs FMP_API_KEY and network
raised by:      05-design.md § Human-run steps (H-1)
ruling:         "Yes, I'll run it" — orchestrator pauses after BE-2/BE-3/FE-1 and hands over the exact commands.
by:             the human, in session (AskUserQuestion)

## D-11 · build (pre-build plan stop) · 2026-09-30
open decision:  H-2 — may saved-node re-derive use persisted per-file admissions on the lineage plus recompute on the stored combined snapshot
raised by:      05-design.md § Saved-node re-derive; § Human-run steps (H-2)
ruling:         "Yes, use saved labels (Recommended)"
by:             the human, in session (AskUserQuestion)

## D-12 · build (pre-build plan stop) · 2026-09-30
open decision:  H-3 — legacy fabricated Freedom24 cost basis in stored snapshots
raised by:      05-design.md § Saved-node re-derive; § Human-run steps (H-3)
ruling:         "Scrub on load (Recommended)" — option (a); BE-4 fires.
by:             the human, in session (AskUserQuestion)

## D-13 · build (pre-build plan stop) · 2026-09-30
open decision:  budget ceiling (hard stop 22 = 2x original 11)
raised by:      run.md budget / orchestrator.md § 3
ruling:         "Allow up to 30"
by:             the human, in session (AskUserQuestion)

## D-14 · build (pre-build plan stop) · 2026-09-30
open decision:  go-ahead on the 05-design lane split
raised by:      05-design.md § Lane split
ruling:         human answered the plan stop's questions (D-10..D-13) and did not object to the presented plan; taken as go.
by:             the human, in session
