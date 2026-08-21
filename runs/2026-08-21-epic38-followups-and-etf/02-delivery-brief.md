REPORT 2026-08-21-epic38-followups-and-etf/02
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only placement brief

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - new epic proposed: Epic 38, 2 stories (A: ETF look-through, B: diagnostics) — see § Placement, § Stories
  - open decision: epic title wording — see § Open decisions
  - open decision: whether Story A needs a quant-analyst RESEARCH pass before ticketing — see § Open decisions
  - finding 4 (methodology section) verdict: no ticket needed, record as closed note — see § Already covered
  - finding 1 count correction: 5 methods / 6 call sites, not "4 other methods" as US-37.2 stated — see § Stories (Story B)

risks:
  - re-read risk.py:1031-1099,1613-1677 and market_data.py:275-545 myself, beyond scout's citations, to ground Story A and correct Story B's method count
  - findings 1 and 2 have no tech-debt-register row, only narrative mentions in US-37.2 — flagged for docs-engineer to add rows at close-out

## Orchestrator brief

- verdict: new epic, two stories — placement matches the human's pre-decided split
- epic: PROPOSED — Epic 38 (next sequential after Epic 37, the highest existing)
- Story A: PROPOSED — ETF look-through sector exposure stops guessing from a hardcoded ETF-ticker proxy list and stops silently landing on "Other"
- Story B: PROPOSED — market-data cache diagnostics report true hit/miss everywhere, the cache-key formula has one source of truth, not two
- blocks dispatch: epic title wording (cosmetic); whether Story A needs a quant-analyst RESEARCH pass first (see Open decisions) — nothing else blocks story-author drafting
- sections below: Placement · Stories · Sequence · Open decisions · Already covered

## Placement

**Precedent: Epic 37 itself**, not a folded-in Backlog story or a reopened Epic 24. Epic 37's own PRD states the operating convention directly: *"The human decided this fix should not reopen that closed epic — it ships under its own new, dedicated, single-story epic number instead."* Epic 37 is now itself `Status: Completed`, all stories `Done`, and the roadmap carries no "reopened" state — stories get appended to an epic only while it is still open (US-37.2 was filed under Epic 37 *while Epic 37 was still active*, explicitly because its three findings came from "US-37.1's own audit and test lanes, not new scope"). That precondition no longer holds: Epic 37 is closed, and today's four findings are being folded in from a *separate* recon pass (this run), after close-out, not from a lane still working inside the epic.

Given that, the closed-epic precedent (Epic 37 succeeding Epic 24) is the closer analog than the open-epic precedent (US-37.2 inside Epic 37), and it points to a new epic number: **Epic 38**.

This is not epic inflation under `product.md`'s test — a one-story epic needs a reason beyond "needs somewhere to live," but this is a **two-story** epic, the same shape Epic 37 itself ended up being, with one story (A) substantial and design-bearing (extending the US-37.1 dynamic-classification pattern into a second code path) and the other (B) a bundle of three precisely-diagnosed, already-scoped defects — the same bundling shape US-37.2 used. Two vertical, independently valuable stories under one epic reads as a coherent unit of work, not a single request wearing an epic's clothes.

**This is my call, stated for the human to override:** an alternative reading is defensible — since none of these four findings are *new* discoveries (all four were already named, in writing, by Epic 37's own stories/PRD as explicitly out of scope or as a noticed-but-unscoped risk), one could argue this is "Epic 37, continued" and should carry an Epic-37-adjacent number or even go straight to Backlog stories with no epic. I did not choose that path because (a) Story A is not a small bugfix — it is a second design-bearing slice of the same problem class Epic 37 solved for direct equities, sized similarly to US-37.1 itself, and (b) `product.md`'s "Epics get created mid-flight" guidance treats a lane's own carried finding as producer input for new-epic/new-story/debt-register triage, and the closed-epic precedent above answers that triage as new-epic.

## Stories

### Story A — ETF look-through sector exposure stops guessing and stops silently landing on "Other"

**Value:** A researcher looking at the Exposure tab's look-through sector breakdown (or the Risk tab's factor exposures, which are computed from the same sector totals — `build_factor_exposures` reads `lookthrough_sector_exposure`) currently sees ETF constituents that don't resolve through the registry get sorted into a sector guessed from which *proxy ETF ticker* happened to source them (e.g. anything sourced via `"XLF"` becomes `"Financials"`, regardless of what the underlying holding actually is), with a final silent fallback to `"Other"` — the exact fabrication-by-omission problem Epic 37 fixed for direct equity holdings, still live here. After this story, ETF look-through sector exposure gets a real, identity-gated classification when one is safely resolvable, and a distinct "Unclassified" disclosure (not "Other") when it is not.

**Slice:** In scope — the three fallback sites in `analytics/risk.py` that produce a sector for a look-through constituent when the registry's direct `instrument.sector` lookup does not resolve: `_infer_sector_from_sources` (lines 1613–1627, hardcoded ETF-ticker→sector proxy list), `_infer_sector_from_resolved_pair` (lines 1665–1677, the same pattern for paired-ETF overlap), and the raw, **un-gated** `market_data.get_company_profile(symbol)` fallback inside `_build_shared_sector_overlap` (line 1654) that reads FMP's `sector` field directly with no ISIN identity check at all — a second live instance of exactly the ungated-lookup risk Epic 37's identity gate exists to close, distinct from the two hardcoded-list functions but touching the same code path. Nearest thing deliberately out: re-deriving *ETF-level* sector classification from FMP directly (Epic 37's PRD already found this unreliable — FMP's `sector` field for an ETF ticker returns the fund sponsor's own classification, e.g. both SPY and GRID return `"Financial Services"`, not a thematic category) — this story is about the **constituent-level** fallback, not inventing a new ETF-level source.

**Depends on:** none structurally, but reuses US-37.1's identity-gated resolution machinery (`equity_sector_resolution.py::resolve_equity_sector`, the ISIN-gate pattern) rather than inventing a second, divergent trust check — the design pass should treat that reuse as close to mandatory, per Epic 37 PRD's own stated principle ("not a second, divergent trust check").

**INVEST weak spot — Estimable.** This is sized closer to US-37.1 (a full-stack, backend-weighted story with open decisions) than to a US-37.2-style ticket-bundle, but I have not sized it with a design pass, and it touches `analytics/risk.py`, a live formula. Per `project.md`'s lane-routing guardrail — *"Any change touching `analytics/`, a formula, a weighting, a return basis, or a trust classification must go through the quant lane"* — **this likely needs a quant-analyst RESEARCH pass before write-story**, not just a tech-lead DESIGN pass, because the "Unclassified" bucket's aggregation treatment for partial look-through resolution (what happens to the total when only some of an ETF's constituents resolve) is a genuine aggregation-rule question, not just a wiring choice. I am flagging this rather than deciding it — see Open decisions.

### Story B — Market-data cache diagnostics report the truth, and the cache-key formula has one home

**Value:** An engineer debugging cache behaviour (via `last_fetch_meta`/`get_last_fetch_meta`) currently gets a `cached` flag that lies for five of six call-site methods (`get_latest_quotes`, both branches of `get_historical_prices`, `get_direct_verified_benchmark_history`, `get_etf_holdings`, `get_etf_holdings_for_date`) — only `get_company_profile` was fixed, by US-37.2. After this story, every `MarketDataService` method that reports a `cached` flag reports the real per-call hit/miss state, the way `get_company_profile` already does, and the cache-key formula used to answer "is this a hit" is expressed once (in `fmp.py`), not re-derived a second time in `market_data.py`'s pre-check helper.

**Slice:** In scope — finding 1 (extend T-37.2.2's real-hit/miss fix to the remaining five methods) and finding 2 (fmp.py:184–187 is the canonical cache-key formula; `market_data.py`'s `_profile_will_be_served_from_cache()` helper at 460–483 currently re-derives an identical copy rather than calling into a shared method — US-37.2's own risk section already named "the clean fix belongs in fmp.py itself" as the right shape). **Correction to the source record:** US-37.2's "Out of scope" note named this as "4 other methods (`get_quote`, `get_historical_prices`, `get_etf_holdings`, `get_etf_holdings_for_date`)" — I re-read `market_data.py` directly and that list is off on two counts: there is no `get_quote` method (the actual name is `get_latest_quotes`), and it omits `get_direct_verified_benchmark_history` (line 412) entirely. The real count is **5 methods, 6 hardcoded call sites** (`get_historical_prices` has two: FMP branch line 350, yfinance-fallback branch line 371). Story-author should use this corrected list, not US-37.2's.

Nearest thing deliberately out: any change to what gets cached or for how long (TTL, persistence) — this is a diagnostic-accuracy fix only, reporting what already happens, mirroring T-37.2.2's own scope boundary.

**Finding 4 (methodology section review) — judged NOT to warrant its own AC/ticket here.** I independently re-read the shipped section (`financial-methodology.md:1257–1404`) against the code it documents: the resolution-order pseudocode matches `equity_sector_resolution.py::resolve_equity_sector` and `registry.py::classify_imported_instrument`'s actual equity branch; the 11-row sector-taxonomy table matches `SECTOR_TAXONOMY_MAP` in `equity_sector_resolution.py:39-51` exactly, key-for-key and value-for-value; the `classification_source` literal values (`"static"`, `"fmp_identity_confirmed"`, `"unavailable"`) match `ClassificationSource` in `app/schemas/instruments.py:48`. The section also explicitly self-scopes to direct-holding equities only and names the ETF look-through gap (Story A, above) as out of its own scope — so it does not overclaim. This reads as accurate, traceable documentation, not a provisional draft awaiting sign-off. I am recording this as a closed item with the verification trail above rather than a build ticket — see § Already covered.

**Depends on:** none — both findings (1, 2) are narrow, single-file/single-function fixes with no schema change, matching the shape `project.md`'s express-lane criteria describe (though routing that call belongs to whoever dispatches the tickets, per US-37.2's own note making the same observation about T-37.2.1/T-37.2.2).

**INVEST weak spot — Value.** Findings 1 and 2 are both internal/diagnostic (an engineer reading `last_fetch_meta`, not a researcher reading the Exposure tab) — there is no end-user-visible outcome here in the Dashboard/Exposure/Risk sense. I am keeping this as a story rather than routing it to the tech-debt register because `product.md`'s "not stories" carve-out is for *refactors and cleanups with no user-visible change*, and this is closer to *fixing a diagnostic that actively misreports* (matching how US-37.2 itself framed the identical `get_company_profile` fix as a story, not a debt-register row) — but this is a closer call than Story A's, and the human should treat "value" here as "diagnostic honesty for the engineers who maintain this system," consistent with guardrail 4's "never fabricate," applied to an internal signal rather than a UI number.

## Sequence

**A and B are independent — no hard dependency either direction.** They touch disjoint files (`analytics/risk.py` vs `services/market_data.py` + `clients/fmp.py`) and disjoint concerns (a sector-inference fallback vs. a cache-diagnostic flag). Recommended order: **B before A**, risk-first in a narrow sense — B is fully diagnosed (all four sub-parts already have file:line evidence and a named fix shape from prior lanes) and low-design-risk, so it can ticket and ship without waiting on a design/quant decision, while A's quant-routing question (see Open decisions) may take longer to resolve and could reshape A's scope. Shipping B first also means the corrected 5-method/6-site cache-diagnostic list (this brief's correction to US-37.2's undercount) is locked in before anything else touches that file. This is a soft-dependency-free ordering preference, not a hard gate — either could go first.

## Open decisions

- **Epic title wording.** I have not proposed final title text. A working title consistent with both stories: "Epic 38 — Sector-Classification Follow-Through: ETF Look-Through & Diagnostic Integrity." The human should confirm or replace this — epic titles in this project are read as the epic's one-line identity in the roadmap's completed-epic list.

- **Does Story A need a quant-analyst RESEARCH pass before story-author drafts it, or does tech-lead DESIGN suffice?** Story A changes an aggregation/fallback rule inside `analytics/risk.py`'s `build_lookthrough_sector_exposure` — a live, shipped formula that feeds both the Exposure tab's sector breakdown and the Risk tab's factor exposures (`build_factor_exposures` reads the same `lookthrough_sector_exposure` output). `project.md`'s guardrail-1 routing rule is explicit that any change touching `analytics/`, a formula, a weighting, or a trust classification goes through the quant lane. I judge this crosses that line (the "what happens when only some of an ETF's constituents resolve" question is a genuine aggregation-rule decision, not pure wiring reuse), but I am not the tech-lead and this is ultimately a design-pass call the human or orchestrator should confirm before dispatch, per this project's routing table.

- **Should docs-engineer add tech-debt-register rows for findings 1 and 2 at close-out?** Both currently exist only as narrative mentions inside US-37.2's own "Notes / decisions" and "Out of scope" sections, unlike finding 3 (F-B / ETF look-through), which already has a proper register row (`analytics/risk.py:1485-1499,1537-1549`, tagged `epic-24`). This is a docs-lane action at close-out, not something I can do read-only — flagging so it isn't silently skipped when Epic 38 is created.

## Already covered

- **Finding 3 (ETF look-through, F-B)** is already recorded — in the tech-debt register (`docs/tech-debt-register.md:177`, tagged `epic-24`), in Epic 37's PRD non-goals, in US-37.1 §"Out of scope"/§F-B, in US-37.2 §"Out of scope", and in `current-product-state.md:74-75` ("Does not cover ETF look-through constituents"). All five records agree it is real, unaddressed, and deliberately deferred — nothing here contradicts that; Story A is the first story to actually close it, not a duplicate filing.

- **Finding 4 (methodology section)** — see § Stories (Story B) above for the full verification trail. Verdict: accurate as shipped, no changes needed, no ticket warranted. Recorded here rather than as a build ticket.

- **Findings 1 and 2** are not duplicates of any existing story or register row — they exist only as narrative "noticed, not investigated" mentions inside US-37.2 (its own Notes/Out-of-scope sections), explicitly flagged there "for a human to decide whether it is worth its own follow-up." That decision is being made now, in this brief: yes, as Story B.

- **No overlap with the roadmap's "Open items" block** (`epic-roadmap.md` lines 12–50, read in full): US-26.3/US-26.4 (currency-risk), Epic 34's three deliberately-left-open findings, Epic 35's framing correction, Epic 36's four close-out carries, and the real dependency-vulnerability findings are all unrelated to these four findings. None of today's four items appear there yet — this brief is the first placement pass for them.
