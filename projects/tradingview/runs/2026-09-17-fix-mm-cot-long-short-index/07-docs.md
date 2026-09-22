REPORT 2026-09-17-fix-mm-cot-long-short-index/07
status:      DONE
verdict:     NONE

changed:
  - mm_cot_long_short_index.pine:52-76 — header "WHAT DEGRADES, AND HOW YOU SEE IT" section restricted the timeframe-invariance claim to chart TF <= "W", added the "n/a (chart TF > W)" degrade description (CR-1 consequence), added a provisional-live-bar-reading disclosure line (FINDING 6), and added the weekly-vs-sub-weekly staleness-basis clarification (FINDING 7).
  - mm_cot_long_short_index.pine:88-96 (pre-edit numbering) — removed the `// NOTE for docs:` marker comment left by backend, per definition_of_done's explicit instruction to remove it once the header is resolved.
  - docs/mm-cot-long-short-index.md:3-22 — top summary rewritten: states the accurate current count (five of eight prior findings fixed, two dissolved, one open) instead of the stale "six... two remain open" line, and explains prior FINDING 1's move from partially-resolved to fixed via CR-1.
  - docs/mm-cot-long-short-index.md § What it computes — invariance claim restricted to chart TF <= "W", na-degrade above it described, provisional-reading behaviour added, all `:NN` line citations replaced with the script's own `// ===== SECTION =====` banner names.
  - docs/mm-cot-long-short-index.md § Inputs — `lookbackWeeks` row updated for the TF <= "W" restriction and its new `minval = 2`; `staleAfterDays` row's "Timeframe-dependent?" column now states the weekly-vs-sub-weekly staleness-basis shift.
  - docs/mm-cot-long-short-index.md § Plots and outputs — table row 4 (`text_color` fix), row 5 (`n/a (chart TF > W)` state) descriptions updated; `n/a` case list gained the chart-TF-above-weekly case; a new bullet discloses the provisional current-week reading; remaining `:NN` citations replaced with section names.
  - docs/mm-cot-long-short-index.md § Known limits — added a "Numbering note" disambiguating "prior FINDING N" (2026-09-16 audit) from the new "§ Second-round audit findings" subsection (05-quant-audit.md, 2026-09-17); prior FINDING 1's table row rewritten to describe CR-1's fix; the "six... two remain open" summary replaced with the accurate five-fixed/two-dissolved/one-open count; all `:NN` citations in the table replaced with section names; added a new "Second-round audit findings" table covering 05-quant-audit.md's own FINDING 1-7 with owner and status for each.

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order's verification field is NONE; this is a prose/documentation-only reconciliation, no static or compile check applies to comment-only and Markdown edits.

contract_notes:
  - 01-quant.md § Inputs contract and § Table contract still quote the pre-CR-1 tooltip and cell text verbatim (noted by 06-backend.md's contract_notes); this remains true after this order and is out of scope here — it is a run artifact, not docs/**.
  - docs/mm-cot-long-short-index.md now cites code locations by section-banner name (e.g. "§ WEEKLY WINDOW", "§ INDEX") instead of line numbers, specifically to stop future line-number drift (FINDING 2's root cause); any future docs edit to this file should preserve that convention rather than reintroducing `:NN` citations.

pack_corrections:
  - none

handoff:
  - test-engineer (carried from 06-backend.md, unchanged by this order): no fixture exercises the chart-TF > "W" branch; a monthly-chart scenario or hand trace of `tfTooCoarse` true with `net` populated is the case CR-1 was written to cover and is still not in 03-test.md.
  - Compile check still outstanding: the header and docs/mm-cot-long-short-index.md both state plainly, unchanged by this order, that the script has not been pasted into TradingView's editor and nothing here claims it compiles or works.

risks:
  - I removed the `// NOTE for docs:` marker comment at mm_cot_long_short_index.pine (below `//@version=6`), which is technically "code below the header comment block" that this order's non_goals says not to edit. The order's own definition_of_done explicitly instructs removing that exact marker once resolved, so I read the non_goal as scoped to substantive code and not to a docs-authored placeholder comment whose whole purpose was to be deleted by this order. If that reading is wrong, the fix is one line: re-add the marker comment (its prior text is in 06-backend.md's `changed` block, mm_cot_long_short_index.pine:88-96 pre-edit).
  - The "Second-round audit findings" subsection I added to docs/mm-cot-long-short-index.md is new structure beyond what the order's definition_of_done literally enumerates; I added it because five separate DoD items (CR-1 consequence, FINDING 2, 3, 6, 7) all needed inline pointers into 05-quant-audit.md's own numbering, and that numbering collides with the prior audit's "FINDING N" labels already used throughout the doc (e.g. this round's FINDING 4 is about `text_color`; the prior audit's FINDING 4 is about the 90/10 scale). Without disambiguation those two numbering schemes would silently collide under the same doc. I judged this necessary to satisfy FINDING 2/3's own requirement that citations "not drift" and be internally consistent, not scope creep — but flagging the judgment call.
  - I did not edit the `lookbackWeeks` or `staleAfterDays` `input.int(...)` tooltip strings themselves (mm_cot_long_short_index.pine:85-89) — those are code below the header, already edited by backend this run and explicitly out of this order's scope (header comment block ONLY). FINDING 7's tooltip clarification is instead carried in the header's "WHAT DEGRADES" section and in the doc's Inputs table, per the DoD's "or state that the threshold's basis varies with chart timeframe" alternative.

## Orchestrator brief

- CR-1 consequence resolved in the header: timeframe-invariance claim now restricted to chart TF <= "W"; the na-degrade above it (`n/a (chart TF > W)`) is described; the `// NOTE for docs:` marker backend left is removed.
- FINDING 2 (doc citations 26-34 lines short): fixed by replacing every `:NN` citation in docs/mm-cot-long-short-index.md with the script's own section-banner names, which cannot drift the way line numbers did.
- FINDING 3 (doc's summary count inconsistent): fixed — doc now states, consistently in two places, "five fixed, two dissolved, one open" (out of the prior audit's eight), and explains why prior FINDING 1 moved from partial to fixed this round.
- FINDING 6 (header omits live-bar provisional disclosure): fixed — one new line in the header's "WHAT DEGRADES" section, mirrored in the doc's § Plots and outputs.
- FINDING 7 (staleness tooltip's basis shifts ~1 week by chart TF): fixed — clarified in the header's staleness bullet and in the doc's Inputs table; the code tooltip string itself was left alone as out of scope (header-only edit permission).
- The doc still states plainly, unchanged, that the TradingView compile check has not run and this is not a claim the script works.
- Two numbering schemes now coexist in the doc (prior 2026-09-16 audit's 8 findings vs. this round's 05-quant-audit.md's own 7 findings); I added a disambiguation note and a dedicated "§ Second-round audit findings" subsection rather than let "FINDING 4" mean two different defects in the same file — see § risks for the judgment call.
- Nothing below `//@version=6` in the .pine file was touched except the removal of the docs-owned `// NOTE for docs:` marker, which the DoD explicitly required.
