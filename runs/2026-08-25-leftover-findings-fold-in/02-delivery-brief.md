REPORT 2026-08-25-leftover-findings-fold-in/02
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
  - 1 new epic + 2 stories proposed (not literally "1 story" as asked) — see § Stories and § Open decisions
  - open decision: epic placement/title — see § Placement
  - open decision: 1 story vs 2 stories — the human's literal ask vs my INVEST-driven recommendation — see § Open decisions
  - open decision: include the 2 extra prior-run leftovers (RecordingMarketData gap, dead market_data param)? — see § Open decisions
  - open decision: confirm the pre-existing tech-debt-register/epic-roadmap backlog stays out of scope — see § Open decisions
  - item 2 (source_status staleness) needs a quant-analyst RESEARCH pass before story-author drafts anything — see § Stories, Story 1
  - already covered check: none of the 4 in-scope items have an existing tech-debt-register.md row or epic-roadmap Open-items entry — see § Already covered

risks:
  - I took 01-scout's file:line re-confirmations on trust rather than re-reading every cited line myself — scout's report shows direct grep/read evidence per item, not bare assertion
  - I did independently verify the one scout claim that would change a verdict if wrong (contract doc for run_metadata.source_status) — grepped exposure-fields.md myself, see Story 1
  - I did not re-open the Epic 34/36/37/38/39 PRDs line-by-line; placement rests on epic-roadmap.md's own slice-log prose, per this project's "roadmap is the authority" convention

## Orchestrator brief
- verdict: new story work, existing-epic-pattern but NEW epic (not an existing one) — see § Placement
- epic: PROPOSED — no active epic exists today (epic-roadmap.md: "No epic is active" as of Epic 39's 2026-08-24 close)
- 2 stories PROPOSED (deviates from the human's literal "1 story" ask — flagged, not silently overridden): Story 1 bundles items 1+2 (stale-import trust-signal completeness), Story 2 is item 3 alone (add_snapshot fidelity)
- item 4 (risk.py market_data kwarg) recommended OUT of both stories — confirmed inert today, routes to tech-debt-register or a ticket-of-opportunity, not its own story
- blocks dispatch: human must confirm epic title/placement, the story-count deviation, and the 3 scope-inclusion questions in § Open decisions before story-author drafts anything
- sections below: Placement · Stories · Sequence · Open decisions · Already covered

## Placement

**Verdict: new epic**, sibling to **Epic 38 — Sector-Classification Follow-Through: ETF Look-Through & Diagnostic Integrity** (closed 2026-08-24), not a reopening of Epic 39 (closed same day these findings were carried) or any other closed epic.

The precedent match is close to exact. Epic 38's own roadmap description: *"Seeded by a post-close recon pass over Epic 37 that folded in four findings, none of which were new discoveries — all four were already named, in writing, by Epic 37's own stories/PRD as explicitly out of scope or as a noticed-but-unscoped risk... Ships as its own new, dedicated two-story epic rather than reopening the now-closed Epic 37, per the same placement precedent Epic 37 itself used against Epic 24."*

Every one of the 4 in-scope items here is the same shape: each was explicitly named and explicitly deferred (not newly discovered) during the 2026-08-24-sbio-still-unclassified-bug run — 3 as `finding`-kind CARRIED rows in that run's own `run.md § Open`, the 4th named directly in this order's own scope from 01-scout's prior-run handoff. None have a tech-debt-register.md row or an epic-roadmap Open-items entry (checked — see § Already covered), so nothing here is "already tracked," consistent with a fresh epic rather than an addition to an existing tracked backlog.

Epic 37→38→39 also establishes the specific house convention this project uses when a same-day-adjacent finding surfaces right after a close: **new epic, every time**, never a reopen — even Epic 39 (closed the same day as this run's origin) followed that rule against Epic 38. Reopening Epic 39 or Epic 38 to house these findings would break a pattern this project has now applied three times running.

I am not proposing "Epic 40" reuse the Epic 38 title — the pack requires framing correction, not restatement of the reporter's words. A working title: **"Snapshot Trust & Fidelity Follow-Through"** — the unifying thread across items 1–3 is not "leftover bugs" but "does the app tell the researcher, and does it preserve, what a frozen/imported snapshot actually contains" — trust-signal completeness (items 1, 2) and data fidelity (item 3) are two faces of the same underlying property. Epic title is the human's call per the pack's "when you do propose a new epic, say who decides" rule — this is a proposal, not a settled name.

## Stories

### Story 1 (PROPOSED) — "The researcher can tell when a snapshot's trust signals reflect frozen import data, not a live recomputation"

value: Today two places silently misrepresent frozen data as current: the snapshot picker labels a base-import node just `"base"` with no date, and `run_metadata.source_status.lookthrough_resolution`/`.confidence` recompute live on every engine run even for a frozen snapshot — the exact class of bug Finding 1 already fixed once (CR-1, `getBenchmarkTrust`) for a different field. This story closes both remaining instances of that class so a researcher never mistakes a frozen number for a live one, anywhere the app currently gets this wrong.

slice: In — (a) thread the already-computed `imported_at`/`snapshot_as_of_date` (present today in `ExposureRunReproducibilityMetadata`, `exposure_engine.py:156-162`, just not surfaced to the picker) into the snapshot-picker label (`variantLabels.ts`, `App.tsx:876-877`); (b) fix `_build_exposure_source_status`/`_build_exposure_availability` (`exposure_engine.py:131-149`, `:165-209`) to read from frozen state instead of recomputing live, in the same shape CR-1 used for the frontend consumer. Out: any change to `add_snapshot`'s data loss (Story 2); item 4's `risk.py` kwarg (recommended out entirely, see § Open decisions).

depends_on: none — independent of Story 2, no shared function per 01-scout's blast-radius check.

invest: **Small is the weak axis.** (a) is a small, well-scoped frontend change with a design choice (where exactly the date appears, what format) but no schema change. (b) is a backend trust-semantics fix that touches `ExposureRunSourceStatus`/`ExposureRunMetadata` (contract doc: confirmed `docs/contracts/exposure-fields.md`, independently grepped, not just relayed from scout) and — per guardrail 1 — needs a quant-analyst RESEARCH pass before design, because it changes what a trust-state field is honestly allowed to claim. Bundling a frontend label change with a backend trust-methodology fix into one story is defensible as *one coherent value statement* (mirrors how Finding 1's own CR-1 spanned schema + frontend in one fix), but it does mean this story cannot be "one PR, one small diff" — see § Open decisions for whether the human wants it split further.

**Quant RESEARCH needed:** yes, for the (b) half. Reasoning: `run_metadata.source_status` is a trust-classification field (guardrail 1: "any change touching ... a trust classification must go through the quant lane"), and it is explicitly the same bug class as the already-audited Finding 1 (`AUDIT-quant.md` in the 2026-08-24 run) — quant-analyst should confirm the fix direction (freeze the field vs. stop surfacing it as a trust signal, both floated by 01-scout) before design starts, exactly as happened for Finding 1's CR-1. The (a) half (UI label) needs no quant pass — it surfaces an already-computed date, no formula or trust-state logic involved — tech-lead DESIGN is sufficient there.

### Story 2 (PROPOSED) — "Adding a new snapshot to a portfolio no longer discards its imported history"

value: Today, using `add_snapshot` mode instead of `replace` silently drops the imported-history payload (`App.tsx:789` passes `importedHistorySnapshot: null`, vs. `:801` on the replace path) — a researcher who adds a snapshot rather than replacing loses reproducibility data the replace path keeps. This story makes `add_snapshot` behave like `replace` from the researcher's point of view: no silent data loss based on which import mode was chosen.

slice: In — client-side recombination of the two `PortfolioOverview`-shaped objects (existing snapshot + newly imported one) so `add_snapshot` preserves both, feeding `portfolioWorkspaceStorage.ts:301-324` (`saveImportedSnapshotNode`). Out: any change to `replace` mode (already correct); items 1/2/4.

depends_on: none formally, but see § Sequence for a soft dependency on Story 1.

invest: **Small and Estimable are the weak axes.** This has been explicitly excluded from scope twice already (02- and 03-technical-plan in the 2026-08-24 run), each time because the recombination logic wasn't designed — "needs client-side recombination of two PortfolioOverview-shaped objects, not designed here" is 03-technical-plan's own carried note. That means the honest estimate today is "unknown until tech-lead DESIGN produces the recombination contract" — this story's first ticket is effectively a design ticket, not an implementation one. No quant-analyst pass needed (no formula/methodology involved, this is a data-merge problem, not a computation).

### Item 4 — risk.py market_data kwarg (RECOMMENDED: not a story)

`risk.py:612`/`:1483` call `registry.attach_snapshot_metadata(snapshot)` without the `market_data` kwarg `attach_snapshot_metadata` (`registry.py:325-330`) accepts and would thread into sector classification. Confirmed inert today — only `.asset_class` is read downstream at those call sites, never `.sector`. Per this project's product pack: *"Pure technical enablement with no user-visible change... it is a ticket inside a story that delivers something"* — with no story currently consuming the sector data this would enable, this is not independently valuable, and per this project's express-lane rule it is not express-eligible either (`analytics/` is a hard express disqualifier regardless of size). Recommendation: `docs/tech-debt-register.md` entry, or a ticket-of-opportunity folded into Story 1 or 2 only if a lane already touching that file's metadata plumbing notices it's a one-line addition — not a standalone story or a mandatory scope item. See § Open decisions.

## Sequence

1. **Story 1 first.** Soft dependency on nothing, but establishes the "frozen state, read once, not recomputed" pattern for `run_metadata` that Story 2's recombination design may want to reuse or at minimum be consistent with — a `PortfolioOverview` object being merged in Story 2 carries its own `run_metadata`, so having Story 1 already settle "what does a frozen snapshot's metadata correctly look like" narrows Story 2's design space rather than leaving it to invent its own answer. Also lower-risk and better-understood (mirrors an already-shipped fix pattern), so it banks value while Story 2's design ticket is still being worked.
2. **Story 2 second.** Needs its own tech-lead DESIGN ticket before implementation sizing is even possible; sequencing it second means that design work isn't blocking Story 1's faster, lower-risk delivery.

## Open decisions

- **Epic title and placement.** I recommend a new epic, sibling to Epic 38, working title "Snapshot Trust & Fidelity Follow-Through" — confirm, or provide a different title. (Placement itself — new epic, not a reopen — has strong 3-epic precedent per § Placement; the title is the softer part of this decision.)

- **1 story vs 2 stories.** The user asked for exactly 1 story. My INVEST read is that items 1+2 can honestly share one story (same trust-signal-honesty value statement, same shape as the already-shipped Finding 1 fix) but item 3 is a structurally distinct problem (data loss/recombination, not a trust-label problem) whose own design has already been deferred twice for being non-trivial — forcing it into the same story as 1+2 would produce a single PR touching a frontend label, a backend trust-classification fix requiring its own quant RESEARCH pass, and an undesigned client-side data-merge, which is not one reviewable slice. I am recommending 2 stories under the 1 epic and flagging this explicitly rather than silently complying with "1 story" or silently overriding it — the human should confirm 2 stories, or explicitly direct that all 3 items go into a single (large, multi-ticket) story despite the INVEST cost.

- **Include the 2 extra prior-run leftovers scout found but that were not in the original "3 points"?**
  - RecordingMarketData missing `get_company_profile`/`get_etf_sector_weightings` (`frozen_market_data.py:131-186`) — a test-infra gap affecting the golden-refresh workflow for any future story touching `resolve_etf_sector`. Not user-visible; recommend tech-debt-register or a ticket-of-opportunity on whichever future story next needs it, not a slot in this epic.
  - Dead `market_data` param in `_build_shared_sector_overlap` (`risk.py:1648-1687`) — recommend checking `detect_deadcode.py --strict` first; if it fires, this is express-lane-eligible dead-code removal per the project's own express-lane rule and doesn't need a story or this epic at all. If it does not fire (unused-param false negative), route to tech-debt-register instead.
  - Recommendation for both: exclude from this epic. Confirm.

- **Is the large pre-existing tech-debt-register.md/epic-roadmap.md Open-items backlog out of scope?** Yes, recommended — it is a long-standing, separately-tracked, non-blocking backlog (US-26.3/26.4, Epic 34's deliberately-left-open findings, Epic 35's closed framing note, Epic 36's 4 close-out carries, 6 live dependency advisories) with no connection to the 2026-08-24-sbio run this fold-in originates from, and 01-scout independently confirmed none of the 4 in-scope items appear in it. Folding it in would be a scope expansion well beyond "the 3 points and leftover tasks from that run" — flagging per this order's non-goals, not silently excluding it. Confirm exclusion.

- **Item 4 disposition** — tech-debt-register entry vs. ticket-of-opportunity vs. a 3rd (tiny) story, if the human disagrees with my "not a story" read. See § Stories, Item 4.

## Already covered

None of the 4 in-scope items (or the 2 extra leftovers) have an existing `tech-debt-register.md` row or `epic-roadmap.md` Open-items entry — 01-scout checked this explicitly and I did not find reason to re-open that check; the roadmap's Open-items section (lines 15-53) and the tech-debt-register's open rows (01-scout's catalogue) cover a materially different, older set of items (currency-risk follow-up, Epic 34's deliberately-open findings, dependency-vulnerability advisories, Epic 36 integration carries — none overlapping in file or concern with any of items 1-4). This is a genuinely fresh fold-in, not a duplicate of tracked work.
