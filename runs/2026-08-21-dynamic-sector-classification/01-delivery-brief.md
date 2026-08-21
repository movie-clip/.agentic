REPORT 2026-08-21-dynamic-sector-classification/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only recon order; no verification command named

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Trigger case (SBIO) is factually wrong for the top-level sector path — verify against IB2026.csv before writing any story, see § Trigger-case correction
  - Two tech-debt-register entries (registry.py sector classifier, risk.py look-through inference) are open and squarely in scope — see § Already covered
  - US-14.3 (Done) already made and recorded the "don't use FMP's own sector field" call — see § Prior recorded decision
  - Quant RESEARCH mode is required before any story is written — see § Open decisions

risks:
  - FMP /profile's actual sector/industry coverage for ETFs (vs equities) is unverified — a live-API question for the audit, not asserted here
  - Equity branch always returning "Other" is confirmed by code reading + one concrete IB2026.csv trace (SBIO), not run against every equity in the statement

## Orchestrator brief

- Verdict: **new epic, PROPOSED** — not a defect, not fully covered, not "known-open, do nothing." No epic is active, so no collision with in-flight work.
- Trigger case (SBIO → "Other") is **empirically wrong** for the live sector path — verified by running the real importer against `docs/IB2026.csv`. See § Trigger-case correction. Do not seed a story from it as stated.
- Real gap, narrower than the user's framing: equities get zero dynamic classification ever; ETF look-through constituents get zero dynamic classification; FMP already returns `sector` via an already-wired call the product deliberately discards (US-14.3). See § Findings.
- Two open tech-debt-register entries (epic-24, unresolved) are directly in scope — fold into this epic's audit, don't track separately. See § Tech-debt overlap.
- Prior recorded decision (US-14.3) narrowed scope to Freedom24-only, ETF-only, and explicitly declined to use FMP's `sector` field — surfaced, not overridden. See § Prior recorded decision.
- DoD requirement: **quant RESEARCH mode required** before any story is drafted — six unresolved questions. See § Open decisions.
- Shape recommendation (not a ticketed plan): audit-first story, findings-first pattern. See § Proposed shape.
- Sections below, in order: DELIVERY BRIEF, Trigger-case correction, Findings, Prior recorded decision, Tech-debt overlap, Open decisions, Proposed shape.

---

## DELIVERY BRIEF

**verdict:** New epic — PROPOSED (`epic-3?-dynamic-sector-industry-classification`, number TBD by the human at ticketing time)

**epic:** No epic is currently active (`docs/product/epic-roadmap.md`, updated 2026-08-20: "No epic is active... next epic unscoped"). This does not collide with in-flight work. It is not a fit for any *closed* epic's remaining scope either — Epic 26 (currency), Epic 30 (exposure FX/valuation correctness), Epic 34 (Dashboard trust states) all touch adjacent surfaces but none owns sector/industry classification.

**rationale:** The request is real and not fully covered, but it is **not the defect the trigger case claims**, and it is **not a green-field capability** either — a partial, deliberately-scoped dynamic mechanism already shipped (US-14.3) and two tech-debt items already name the fragile half of it. The honest first move is an audit that corrects the framing and quantifies the actual "Other" exposure across the paths that really lack any dynamic lookup, before any fix is scoped — consistent with this project's findings-first house pattern (Epics 33/34/35/36) and with the fact that nobody today can say how big this problem actually is in dollar/weight terms.

---

## Trigger-case correction

I ran the real pipeline against `docs/IB2026.csv` rather than trusting the trigger's claim:

```
metadata sector: Health Care   category: Sector UCITS ETF
get_sector() fallback: Other
imported instrument: symbol=SBIO description='INVESCO NASDAQ BIOTECH'
                      listing_exchange='LSEETF' instrument_type='ETF'
```

`overview.py::build_portfolio_overview` (the function that feeds the Exposure tab's `current_state_concentration.top_sectors` / sector donut, per `docs/contracts/exposure-fields.md`) calls `InstrumentRegistry.attach_snapshot_metadata()` **first**, which routes SBIO through `classify_imported_instrument()`. That function keyword-matches the broker's own free-text description ("INVESCO NASDAQ BIOTECH") against a fixed list of substrings and hits `"BIOTECH"` → sector = `"Health Care"`. **SBIO is correctly classified as Health Care today, on this exact statement.** It only falls to `"Other"` if you call the *other*, static-only method (`get_sector()`) directly — which `overview.py` does NOT do here (it only falls back to `get_sector()` when `attach_snapshot_metadata` produces no sector at all).

This matters for scoping: SBIO is not a counter-example to fix, it's a case that happens to work because its broker description contains a lucky keyword. That's the actual shape of the problem — fragile, not absent, for ETF-shaped instruments.

## Findings

**F-A (equities get zero dynamic classification, ever).** `InstrumentRegistry.classify_imported_instrument()`'s non-ETF branch (`registry.py:256-265`) unconditionally returns `sector="Other"` for any equity not in the ~90-entry static `INSTRUMENT_DEFINITIONS` dict — there is no keyword inference, no FMP call, nothing, regardless of how rich the broker's description is. This is a real, structural gap the trigger case didn't surface (SBIO is an ETF) but is the more consequential one for "any unrecognized... company ticker."

**F-B (ETF look-through constituents get zero dynamic classification).** `build_lookthrough_sector_exposure()` (`analytics/risk.py:1031-1038`) — the engine that unpacks an ETF into its real underlying holdings for the look-through sector view — calls `registry.get_instrument()` (static-dict-only, no description fallback, no FMP) and falls back to `_infer_sector_from_sources()`, a second, separate hardcoded proxy-ticker keyword list (`["XLF"]→Financials`, etc. — tech-debt-register `risk.py:1485-1499,1537-1549`). Any underlying constituent stock not in the static dict lands in `"Other"` here regardless of what happens at the top level.

**F-C (FMP already returns sector data the product discards by design).** `FmpClient.get_profile()` → `MarketDataService.get_company_profile()` is already wired and already called at import time (`app/services/instrument_enrichment.py::enrich_imported_instruments`, shipped in US-14.3). The FMP profile payload it receives already carries a `sector` field (visible in that story's own test fixtures, e.g. `{"companyName": "XYZ World Corp", "sector": "Technology", ...}`). **The enrichment helper deliberately discards `sector` and only keeps `companyName`/`isEtf`**, feeding the enriched description back into the same keyword classifier described in F-A/F-B rather than trusting FMP's own categorical field directly. This is a recorded decision, not an oversight — see next section.

## Prior recorded decision

`docs/product/stories/US-14.3-freedom24-fmp-enrichment.md` already built a slow-path FMP lookup for unrecognized symbols and explicitly scoped it narrower than what this request asks for:

- **"Sector overrides" is explicitly Out of Scope**: *"The helper populates `description` and `instrument_type` only. The existing `classify_imported_instrument` in `InstrumentRegistry` does the description-keyword → sector inference. We do not bypass the registry's classification logic."* No reason beyond "one code path" is recorded — worth asking the human whether that reasoning should still hold once FMP's `sector` field is table stakes for solving F-A.
- **Freedom24-only, explicitly**: *"IB and ESPP parser enrichment [is out of scope]. IB statements already populate richer descriptions natively... Adding enrichment there is a follow-up only if a real bug surfaces."* The trigger case is an IB import — this decision is exactly why IB-imported unknowns get no FMP round-trip today, independent of F-A.
- **Residual "Other" outcome accepted as no-regression**: *"Users get the same bug (some sectors → 'Other') that existed before this story — no regression."*

Per the product pack's convention, this is surfaced rather than silently reopened: **has the "IB doesn't need it" premise changed?** The evidence says no in general (IB descriptions are usually richer) but yes specifically for the equity path (F-A), where richness of description doesn't matter because the classifier never looks at it for non-ETF instruments.

## Tech-debt overlap

`docs/tech-debt-register.md`, both tagged `epic-24`, neither marked `RESOLVED` (unlike sibling entries on the same lines that are):

- `instruments/registry.py:45-48,180-261` — *"Hardcoded instrument reference data... plus a keyword-substring sector classifier (`get_sector` fallback chain ~209-242). Reference data is acceptable... the keyword classifier is the fragile part."* (low severity, med effort)
- `analytics/risk.py:1485-1499,1537-1549` — *"Sector inference from hardcoded proxy-ticker lists... Duplicated across two functions; overlaps the `InstrumentRegistry` sector source of truth."* (med severity, med effort)

Epic 24 (closed) evidently did not act on either. These are not "new findings" — they are the same fragility this request is pointing at, already catalogued and open. A new epic here should close them as part of its scope rather than leave them duplicated in two places.

## Open decisions

Per this work order's DoD, flagging explicitly: **this touches trust classification (guardrail 3/4) for a dynamically-sourced categorical attribute, so quant-analyst RESEARCH mode is required before `story-author` drafts anything.** Sector/industry isn't a formula, but assigning it a trust rung and deciding how it should degrade sector-dependent computed metrics (sector HHI, sector concentration weights, look-through sector exposure, the factor-tilt sector composition) is exactly the class of decision this project routes to quant research, not to the tech lead. Specifically unresolved:

1. **Should a provider-sourced (FMP `sector`) classification carry a different trust rung than a curated `INSTRUMENT_DEFINITIONS` entry?** Today sector carries no trust label at all — it's presented as flat fact regardless of source. Introducing a dynamic, un-curated source raises the question this project's guardrail 4 exists for.
2. **Data source**: reuse the already-wired `MarketDataService.get_company_profile()` (FMP `/profile`, already cached), or something else? Nobody has verified FMP actually returns non-empty `sector`/`industry` for ETFs specifically (vs. equities) — the one shipped test fixture for an ETF (`XYZE`, US-14.3) is a mock, not a live-API observation. This is a factual question for the audit/research pass, not something to assume.
3. **Scope**: equities only (F-A, the bigger structural gap), ETF look-through constituents (F-B), or both? They are different code paths with different callers.
4. **Caching policy**: the FMP client already caches `/profile` responses; is that sufficient, or does a dynamically-resolved sector need its own persistence/versioning given it can change the number in `current-product-state.md`-tracked cards between runs?
5. **No-coverage fallback**: when FMP has no profile for a symbol at all (delisted, thinly covered, non-US), does it stay `"Other"`, or does it become an explicit `unavailable`/`withheld` trust state rather than a silent bucket label? (Today `"Other"` reads as a real sector name, not an absence — arguably itself a small fabrication-adjacent smell worth the audit naming.)
6. **Does the US-14.3 "don't bypass the registry's keyword classification" decision still hold**, now that the ask is explicitly to trust FMP's own field? Epic placement and this reversal are the owner's call, not mine to make in this brief.

## Proposed shape

Following this project's findings-first pattern (Epics 33-36): **first story = audit**, not a fix. It would: (a) correct the trigger framing the way this brief does, (b) quantify actual `"Other"` exposure in dollars/weight across the real portfolio for both F-A and F-B paths (not just the SBIO anecdote), (c) empirically check what FMP's `/profile` actually returns for a sample of currently-"Other" equities and ETFs (live-API check, the kind `fmp-data` skill and quant-research would run), (d) fold in the two open tech-debt entries as findings rather than a separate cleanup, (e) hand quant-analyst the six open decisions above before any fix story is drafted. Not a plan the human is meant to ticket as-is — a shape for review.

**invest note:** this is exactly the "if nobody can tell how big it is, the honest first story is an investigation" case — Estimable is the criterion this proposal is weakest on, deliberately, until the audit runs.

**Epic-inflation check:** this is not a one-story epic proposed to give a request somewhere to live — the audit alone will very likely spawn 2+ closing stories (F-A fix, F-B fix, each with its own trust-labeling AC once research settles the open decisions), matching the Epic 34/35 shape rather than the Epic 16 quick-win shape. If the audit comes back smaller than expected, "fold into Backlog as a single story" remains available — that call belongs to whoever reviews the audit's findings, not to this brief.

**sequence:** (1) Quant-analyst RESEARCH pass on the six open decisions above — must precede story drafting per guardrail 3/4. (2) Audit story (`US-<epic>.1`), findings-first, produces F-1..F-n in the epic PRD including the two folded-in tech-debt items. (3) Closing stories, one per surviving finding, sequenced by the audit's own risk-first read (not predictable from this brief).

**already_covered:** US-14.3 (Done, Epic 14) is partial prior art — Freedom24-only, ETF-shaped-only, deliberately does not use FMP's `sector` field; surfaced above, not silently reopened. Tech-debt register `registry.py:45-48,180-261` and `risk.py:1485-1499,1537-1549` (epic-24, open) name the same fragility already; fold in rather than duplicate. Not covered anywhere: giving unrecognized equities or look-through constituents a dynamic sector source at all.
