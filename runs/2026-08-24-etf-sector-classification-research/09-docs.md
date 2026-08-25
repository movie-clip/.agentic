REPORT 2026-08-24-etf-sector-classification-research/09
status:      PARTIAL
verdict:     NONE

changed:
  - docs/finance/financial-methodology.md — scope note (~1266-1275) extended to name the new subsection; new "### Direct-held ETF branch classification (US-39.1)" subsection appended after the ETF look-through subsection (before "## Risk Contribution and Concentration")
  - docs/contracts/exposure-fields.md:222-227 — enumeration prose now lists "fmp_etf_sector_weighting_confirmed" as a fourth classification_source value; heading now cites US-39.1 alongside US-37.1
  - docs/tech-debt-register.md:186 — narrowed: keyword-substring sector classifier clause for the direct-held ETF branch marked RESOLVED (US-39.1); futures-reference-data clause and category's own keyword derivation left untouched, same "acceptable" framing
  - docs/product/current-product-state.md — Exposure-tab bullet (~65-87) extended with a direct-held-ETF-branch paragraph: FMP endpoint used, identity gate, 55% dominance threshold, Unclassified fallback, category unaffected

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order named verification: NONE (docs lane, no Bash tool granted per PROTOCOL.md §7)

contract_notes:
  - none — the one open contract note from 06-technical-plan.md (exposure-fields.md's enumeration prose needing the new literal) is landed by this pass, see `changed`

pack_corrections:
  - none

handoff:
  - test-engineer (T-39.1.6) still owes the two rewritten test_instrument_registry.py tests + new test_etf_sector_resolution.py module — 08-backend.md's 2 pre-identified failures are expected until T-39.1.6 lands
  - Epic 39 creation / epic-roadmap.md / story-index placement stays out of scope per this order's non_goals — deferred to the run's close-out docs dispatch after T-39.1.6 lands and gates pass

risks:
  - capabilities/docs.md flags any new methodology section as flag-for-human, judgment-call territory — order's DoD explicitly directed writing one anyway — see § Pack conflict: methodology section
  - docs/tech-debt-register.md:186's original prose named the wrong method (`get_sector`) as the keyword classifier T-39.1.4 actually removed — see § Stale row reference, pre-existing not introduced here

## Pack conflict: methodology section

`capabilities/docs.md`'s "Auto-update vs flag-for-human" section states any
new methodology section, or edit to an existing one, is flag-for-human —
formula phrasing, citation choice and edge-case framing are judgment calls.
This order's `definition_of_done` explicitly directed appending the new
"### Direct-held ETF branch classification (US-39.1)" subsection with exact
placement and content instructions sourced from `06-technical-plan.md`
§ T-39.1.5, itself downstream of the tech lead's design and the
human-confirmed `DOMINANCE_THRESHOLD = 55%` decision already recorded in the
story file's Context section. Per `PROTOCOL.md` § "When the order and your
capability pack disagree," a pack *convention* does not block an explicit
order — I wrote the section as directed (`status: PARTIAL` reflects this),
rather than silently complying without flagging it. A human should confirm
the new subsection's formula phrasing and edge-case framing before treating
it as fully settled, same as any other flagged methodology addition.

## Stale row reference, pre-existing not introduced here

`docs/tech-debt-register.md:186`'s original text names `get_sector`
(`registry.py:209-211`, a 3-line `"Other"` fallback method) as "the
keyword-substring sector classifier." The actual keyword-substring `sector`
logic T-39.1.4 removed lived in `classify_imported_instrument`'s ETF branch
(formerly `registry.py:246-292`) — a different method entirely. This
order's DoD instruction to narrow row 186 the way US-38.1 narrowed row 177
assumed the row's existing reference was accurate; I narrowed it as
directed because the underlying code fact (the keyword `sector = ...` chain
is gone, replaced by `resolve_etf_sector`) is independently verified true
against the landed code, regardless of which method name the row's
already-stale text pointed at. The stale location reference predates this
pass and was not introduced by it.
