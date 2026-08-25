REPORT 2026-08-24-etf-sector-classification-research/02
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only producer order, no verification command named

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - verdict: new epic (PROPOSED, "Epic 39") — see § Placement
  - premise correction needed: SBIO is "Health Care" today, not "Unclassified" — see § Orchestrator brief
  - quant-analyst RESEARCH required before story-author drafts anything — see § Open decisions
  - dedupe: tech-debt-register.md:186 is a superset (2 clauses); this scopes only its keyword-classifier clause — see § Already covered
  - 5 open decisions for the human — see § Open decisions

risks:
  - took on trust: fmp.py has no ETF-specific profile/sector-weighting endpoint — scout's grep claim (01-scout.md), not re-verified by me
  - "new epic" rests on reading Epic 37/38's stated placement precedent (roadmap.md:79-89,116-122) at face value, not re-derived independently

## Orchestrator brief
- verdict: NEW EPIC (PROPOSED) — 1 story, RESEARCH-gated before drafting
- premise correction: SBIO resolves to sector="Health Care" today (keyword match on
  "BIOTECH" in its description), NOT "Unclassified" — the user's stated symptom is
  wrong, but the underlying concern (fragile, unscalable, non-identity-gated) is real
- epic: PROPOSED, no existing epic fits — nearest precedent is Epic 37 (sibling, not host)
- 1 story (PROPOSED, unticketed): direct-held ETF sector classification hardened
  beyond keyword-substring matching — story count may grow to 2 once RESEARCH names
  a feasible data source; this brief does not fix the count
- blocks dispatch: quant-analyst RESEARCH pass (data-source feasibility) must run
  before story-author drafts anything — see § Open decisions #2
- sections below: Placement · Stories · Sequence · Open decisions · Already covered

## Placement

**Nearest precedent: Epic 37 — Dynamic Equity Sector Classification.** Same shape —
a `tech-debt-register.md` row (there: `registry.py:45-48,180-261`, equity branch;
here: the same row's ETF-branch clause) seeding a dedicated classification epic that
replaces a hardcoded/fragile mechanism with an identity-gated dynamic one. Epic 38 is
the second-nearest precedent — it followed Epic 37 the same day as "its own new,
dedicated two-story epic rather than reopening the now-closed Epic 37" (roadmap.md:87-89),
explicitly citing that placement choice as reused from "the human's placement decision"
that created Epic 37 rather than reopening Epic 24.

That is a real, twice-applied house precedent in this project: **closed epics are not
reopened for follow-on classification work, even same-day, even on a near-identical
mechanism** — a new dedicated epic is created instead. Epic 38 closed 2026-08-24 (today).
Applying the same precedent a third time argues for a new epic here rather than a
fast-follow story appended to Epic 38.

Against epic inflation (pack § "Epic inflation"): a one-story epic needs a reason
beyond "this needs somewhere to live." Epic 16's precedent for a legitimate one-story
epic was "small, self-contained, no open design questions" — that does **not** describe
this request. This one has an open design question the scout's own findings surface:
whether an identity-gate (ISIN-confirmed, like Epic 37's equity path) is even usable
here, given FMP's ETF-level `sector` field itself returns the wrong kind of answer
(fund-sponsor classification, not thematic) even once identity is confirmed — see
§ Stories, `invest: Estimable`. That open question is exactly why Epic 37 justified
itself as dedicated rather than quick-win, and it justifies this one the same way.
**Verdict: propose it as a new epic, but epic placement is the owner's call — see
§ Open decisions #1.**

## Stories

### Story 1 (PROPOSED, unticketed): Direct-held ETF sector classification stops relying on keyword-substring matching

value: A researcher holding an uncurated ETF (e.g. SBIO) sees a sector label that is
either derived from real classification evidence or honestly marked unresolved —
never a silent match on whatever words happen to appear in the broker's free-text
description, and never a silently-wrong "Broad Market" default when no keyword hits.

slice: In — the direct-held ETF branch of `InstrumentRegistry.classify_imported_instrument`
(`registry.py:246-292`), the one code path neither Epic 37 (equity branch) nor Epic 38
(risk.py look-through) touched. Out (nearest deliberately-excluded neighbor) — the
futures reference-data clause of the same tech-debt row (`tick_size`/`point_value`/
`multiplier`, already deemed acceptable and documented in the `fmp-data` skill); the
look-through path Epic 38 already fixed; re-litigating whether FMP's general-purpose
`get_profile` sector field is reliable for equities (Epic 37 already answered that,
yes, with an identity gate — this is ETF-specific).

depends_on: quant-analyst RESEARCH output (data-source feasibility, whether an
identity-gate is reusable, trust-class design) — see § Open decisions #2. This is a
hard dependency, not sequencing convenience: story-author cannot write acceptance
criteria for "resolves via X" until RESEARCH names what X is or confirms none exists.

invest:
  - **Estimable — weak, deliberately.** Sizing depends entirely on what RESEARCH
    finds. If a reliable thematic ETF data source exists (dedicated FMP endpoint,
    Yahoo Finance, or fund-holdings-based inference), this is probably a story the
    same shape as US-37.1 (identity-gate + curated-fallback + Unclassified bucket).
    If no reliable source exists, the honest story is much smaller: stop the keyword
    matcher's silent guessing (fail to "Unclassified" like Epic 38 did for look-through,
    rather than "Broad Market"), with manual curation as the only path to a real label.
    Both are legitimate stories; RESEARCH decides which.
  - **Valuable — checked, not asserted.** The scout traced this against the actual
    held statement: SBIO is a real position (`docs/IB2026.csv`, 5 units), not a
    hypothetical. The failure mode (silent wrong "Broad Market" default for any
    uncurated ETF whose description text misses all ~10 keywords) is a real,
    demonstrated gap in a system whose stated premise is that every number is
    traceable — this is not a scale-dependent claim needing "many holdings" to matter.

## Sequence

Single proposed story; sequencing is between this epic and the RESEARCH pass that
gates it, not between multiple stories:

1. **quant-analyst RESEARCH** (hard dependency, blocks story-author) — evaluate FMP's
   dedicated ETF endpoints (not the general `get_profile` sector field, already proven
   unreliable for ETFs per both PRDs' non-goals) and Yahoo Finance's ETF metadata
   surface (currently zero ETF-sector methods in `yfinance_client.py` per scout) for a
   thematic classification signal; determine whether Epic 37's identity-gate pattern
   is reusable once/if a reliable source is named, or whether the problem is
   structurally different (see § Open decisions #2 for the exact question).
2. **Story 1** (this brief) — implementation, once RESEARCH names the approach.

This is risk-first by construction: the one thing that could invalidate the story's
shape entirely (does a usable data source even exist) is answered before any
acceptance criteria are drafted, per the pack's audit/research-first discipline for
work whose cause or approach is not yet named.

## Open decisions

- **#1 — Epic placement.** Propose as a new, dedicated epic (working title "Epic 39
  — Direct-Held ETF Sector Classification" or similar), following the Epic 37→38
  precedent of not reopening a closed epic for adjacent classification work. The
  human may instead choose to fold this into a future Epic 38 revisit if they judge
  the two-hours-old closure differently than that precedent suggests — this is the
  owner's call per the pack's "when you do propose a new epic, say who decides."

- **#2 — Is quant-analyst RESEARCH needed before story-author drafts anything, and
  what must it answer?** Recommend **yes**, for two independent reasons: (a) project
  guardrail 1 — this touches a trust classification (`classification_source`) and a
  live analytics path (`registry.py`'s classify function feeds Exposure-tab sector
  breakdowns), which the pack requires routing through the quant lane in research
  mode before any change; (b) the scout's own finding that this problem may not be
  the same shape as Epic 37's. Epic 37 solved "no identity evidence exists yet" for
  equities (ISIN-matched FMP lookup, once gated, was trustworthy). SBIO's ISIN
  (`IE00BQ70R696`) means identity evidence **does** exist for a direct-held ETF —
  but both PRDs' non-goals independently record that FMP's `sector` field itself
  returns the wrong kind of answer for ETFs generally (fund-sponsor classification,
  not thematic — SPY and GRID both return "Financial Services"). That means the
  blocker is not "no identity gate is possible" (Epic 38's problem, for constituents
  with no ISIN at all) — it is "the identified thing's own data source lies." RESEARCH
  must determine whether that is fixable via a different API (a dedicated
  ETF-sector-weighting/profile endpoint at FMP, distinct from `get_profile`; Yahoo
  Finance's ETF surface, currently unimplemented here) or whether no API answers this
  reliably, in which case the honest fix is disclosure (fail to "Unclassified") plus
  continued manual curation, not a new dynamic tier.

- **#3 — Scope boundary on `tech-debt-register.md:186`.** This brief's story targets
  only that row's keyword-classifier clause. The row's other clause (hardcoded futures
  reference data — `tick_size`/`point_value`/`multiplier`) is explicitly called
  "acceptable" in the same row and documented in the `fmp-data` skill. Confirm the
  epic should leave that clause untouched and, at close-out, split/narrow the row the
  same way US-38.1 narrowed F-B (row 177) rather than marking the whole row resolved.

- **#4 — Does RESEARCH mode also cover live-API reachability testing, or is that
  deferred to implementation time?** The work order for this brief explicitly excludes
  researching Yahoo/FMP endpoint behavior from producer scope. Whether the downstream
  quant-analyst RESEARCH dispatch is expected to make live calls to characterize
  endpoint reliability (as this project's PRDs do — e.g. citing SPY/GRID's actual
  returned values) or work from documentation alone is a scoping choice for that
  order, not settled here.

- **#5 — Does the eventual fix keep `INSTRUMENT_DEFINITIONS` manual curation as the
  first-choice path with a dynamic fallback (mirroring Epic 37's static-registry-first,
  identity-gated-fallback-second shape for equities), or does RESEARCH's finding
  change that shape?** Flagged for RESEARCH + tech-lead DESIGN to settle jointly;
  not a producer decision, but worth naming so the human knows it is still open.

## Already covered

`docs/tech-debt-register.md:186` already tracks this exact mechanism, open, tagged
`epic-24`: "Hardcoded instrument reference data (futures `tick_size`/`point_value`/
`multiplier`; ETF→sector defs) plus a keyword-substring sector classifier (`get_sector`
fallback chain ~209-242). Reference data is acceptable...; the keyword classifier is
the fragile part." (verified by direct read, `tech-debt-register.md:186`, not taken on
trust from the scout). This brief's proposed epic is **narrower than that row** — it
targets only the keyword-classifier clause, not the futures reference-data clause,
which the row itself already deems acceptable. It is not a new finding; it is the
still-open remainder of an already-recorded one.

This is distinct from `tech-debt-register.md:177` (F-B), which US-38.1 marked
RESOLVED (verified by direct read) — that row was `risk.py`'s look-through
proxy-ticker-list functions, a different code path (constituents inferred during
look-through overlap analysis, no ISIN available at all), now deleted. Row 177's own
text already flags a narrower open remainder ("ETF-side FMP sector reliability... out
of scope") — that remainder and row 186's keyword-classifier clause are naming the
same underlying FMP-unreliable-for-ETFs problem from two different code paths
(look-through vs. direct-held). A story here should close out row 186's
keyword-classifier clause the way US-38.1 closed row 177's main clause, and should
cross-reference row 177's still-open remainder rather than duplicate it.

No row in `epic-roadmap.md`'s "Open items" (lines 14-52, verified by direct read)
names the direct-held-ETF-ticker gap specifically — the only live tracking anywhere is
`tech-debt-register.md:186`. `current-product-state.md:83-87` (verified by direct
read) documents the look-through path's narrower remainder but does not mention the
direct-held ETF-branch keyword matcher in `registry.py` at all — that mechanism is
currently undocumented in the shipped-state inventory, a gap this epic's close-out
should also fix regardless of which implementation approach RESEARCH lands on.
