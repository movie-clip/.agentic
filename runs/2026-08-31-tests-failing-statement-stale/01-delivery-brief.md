REPORT 2026-08-31-tests-failing-statement-stale/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only order; no verification command specified

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - verdict: no ticketed story — routine documented maintenance (testing-architecture.md#statement-refresh-workflow) — see § Placement
  - dedupe: no open story or roadmap item for an IB2026 refresh exists by design — see § Already covered
  - open decision: human's one-commit choice (probe_engine hardening + statement refresh together) is a traceability concern worth reconsidering — see § Open decisions
  - scope watch: a new Aug-28 holding with no FMP coverage or a wrong-fund ticker collision would exceed a pin update — see § Open decisions

risks:
  - verdict inherits run.md § Diagnosis's claim that engine and methodology are unchanged and probe_engine is not implicated; the order's non_goals say take the diagnosis as given, so I did not re-open it
  - confirmed directly via git: statement_truths.py unmodified; IB2026.csv + dashboardGoldens.ts + golden_market_data.json modified/staged alongside four mcp_server files (server.py, probing.py, testing.py, test_mcp_tools.py)

## Orchestrator brief

- verdict: **Not a ticketed story.** Routine, pre-documented maintenance — the statement-refresh workflow in `docs/architecture/testing-architecture.md#statement-refresh-workflow`, which is the shipped deliverable of Epic 28 / US-28.3.
- epic: Epic 28 — IBKR CSV Importer & Statement-Refresh Resilience (**closed**). This work is the workflow Epic 28 built, not new scope under it. No new story anywhere.
- roadmap authority: `docs/product/epic-roadmap.md` snapshot (updated 2026-08-28) — Epics 41 and 42 active; no statement-refresh item in the open-items list.
- 0 stories proposed. The fix (re-pin `statement_truths.py`, add instrument-registry entries for new symbols, commit the five artifacts together) is steps 3–5 of the documented workflow and runs DESIGN → build → gates with no story file.
- gates still apply: `quant-audit` REQUIRED is correct — re-pinned TWR (4.77%→5.51%), terminal market value and currency split are guardrail-1 financial reference truth. A gate running does not imply a story.
- prior decision check: US-33.4 adopted the 2026-08-11 statement *as a story*, but only because it was entangled with an Epic 33 engine fix and had to re-derive pins against a changed engine. Adopting Aug-28 with an unchanged engine reverses no recorded decision — US-28.3 and US-33.4's own slice log establish that a plain refresh is a no-story chore.
- blocks dispatch: nothing. Two things for the human to weigh, neither blocking: the combined-commit traceability concern, and the new-instrument-coverage scope watch.
- sections below: Placement · Stories · Sequence · Open decisions · Already covered

## Placement

**Precedent epic: Epic 28 — IBKR CSV Importer & Statement-Resilience** (`docs/product/prd/epic-28-ibkr-csv-importer.md`, roadmap line ~1215). Epic 28 exists precisely so that swapping `docs/IB2026.csv` for a fresh export is *not* a story every few weeks. Its charter, quoted from the roadmap: "the IB statement file is replaced with a fresh broker export every few weeks, so exact-number pins break on every refresh". US-28.3 delivered the one-command workflow, the single `statement_truths.py` pin module, and the `test_statement_refresh.py` swap-simulation meta-test that proves a refresh fails *only* the documented pin set.

This request is that workflow being exercised. It is **not** a sibling of US-33.4 ("Adopt the 2026-08-11 statement as the golden fixture"), even though the surface looks identical:

- US-33.4 lived inside Epic 33, whose subject was a structural replay defect (opening-position roll-back summing quantities across a share split). The pins there had to be **re-derived against a fixed engine**, and the adoption surfaced five structural tests wrongly pinning statement truths plus an unbacked-cash fabrication. That is story-shaped work.
- The Aug-28 refresh, per `run.md` § Diagnosis, touches no engine code, no formula, no schema, no methodology doc. All 41 failures trace to `statement_truths.py` still pinning the Aug-11 export. `test_statement_refresh.py::test_committed_statement_yields_zero_truths_diffs` failing is the workflow's own "you skipped step 3" signal firing exactly as designed.

Against `capabilities/product.md` "What is a story here, and what is not": this is **pure technical enablement with no user-visible change** — the researcher sees no new capability, no new metric, no changed trust state. The portfolio *data* moves (that is the point of a refresh), but the product does not. That is the definition of not-a-story in this project.

## Stories

None proposed.

The work is the documented workflow, executed as maintenance:

  outcome:    the committed suite is green again against the 2026-08-28 IB export
  value:      none user-visible — fixture/pin realignment; the researcher's numbers were already correct, the *tests* lagged the swapped input
  slice:      re-pin `statement_truths.py` (period, position/instrument counts, per-currency split, pinned positions, replay-universe size, terminal-value assertions); add InstrumentRegistry entries for any brand-new Aug-28 holdings; regenerate + commit `IB2026.csv` + `golden_market_data.json` + `dashboardGoldens.ts` + `statement_truths.py` + registry entries together. Deliberately out: any engine, formula, schema or methodology change — if one is needed, this stops being a refresh.
  depends_on: none — `run.md` records `refresh_statement.py` already run and goldens regenerated/staged; the remaining steps need no FMP key or network
  invest:     n/a (no story)

If the network's convention requires a tracking artifact for gate provenance, the honest form is a **slice-log entry on Epic 28** ("2026-08-28 — statement refreshed Aug-11 → Aug-28, pins re-derived, no engine change"), matching how US-33.4's refresh was slice-logged — not a US-28.4 story file.

## Sequence

Single track, already partly done. Documented workflow order (testing-architecture.md steps 3–5):

1. Re-pin `statement_truths.py` from `diff_statement_truths` / `test_statement_matches_truths_module` output — **first**, because every other failing cluster (test_analytics, test_ledger_replay_audit, test_portfolio_state, test_exposure_engine, test_currency_conversion) is downstream of these pins.
2. Add registry entries for brand-new Aug-28 symbols — parallel-safe with (1); gated by `test_registry_isin_integrity.py` against the statement's own ISINs.
3. Full suite green, then `quant-audit` (re-pinned TWR / terminal value / currency split are financial reference truth), then `integration` + `review`.
4. Human commits.

No risk-first reordering applies — there is no plan to invalidate.

## Open decisions

Two items for the human. Neither blocks dispatch.

- **The one-commit choice mixes two unrelated changes.** `run.md` records the decision: probe_engine/MCP hardening (`server.py`, `tools/probing.py`, `tools/testing.py`, `test_mcp_tools.py`) and the statement refresh (`IB2026.csv`, `golden_market_data.json`, `dashboardGoldens.ts`, `statement_truths.py`, registry) land in **one** commit because the working tree is already all-staged together. This project's whole premise is per-number traceability, and its commit/PR machinery is story-structured. A single commit means a future "when did the pinned TWR become 5.51%?" bisect lands on a commit that also rewrote the MCP probe layer — neither change gets a clean diff boundary. Both changes are non-`.md`, so both need the same green suite regardless; splitting into two commits costs nothing and neither has a ticketed story to bind them. Recommendation: two commits. The human has already decided one; this is a flag, not an override.

- **Do the Aug-28 new holdings all have clean FMP coverage?** Step 4 of the workflow (registry entries for new symbols) is normally in-scope maintenance. But if a new Aug-28 holding has *no* FMP coverage, or hits a wrong-fund ticker collision (the `CIBR US` vs `CIBR.L` UCITS class the workflow doc explicitly warns about; precedent: `SEMI` bare-symbol fallback became its own story, US-31.4, in Epic 31), that specific sub-item is a trust/availability question bigger than a pin update and may need its own placement pass. Scout / tech-lead DESIGN should confirm the new-symbol set is clean before treating the whole thing as routine.

## Already covered

**No open story or roadmap item for an IB2026 statement refresh exists — by design.**

Searched:
- `docs/product/epic-roadmap.md` — full-text for `statement.refresh`, `refresh_statement`, `IB2026`, `statement_truths`, `re-pin`, `statement refresh`. Every hit is historical: Epic 28 (workflow creation), Epic 31 US-31.2/31.4/31.5 (replay-path fixes), Epic 33 US-33.4 (the 2026-08-11 adoption). The snapshot's "Open items" list (US-26.3/26.4, Epic 34 F-1a/F-10/F-12, Epic 36 carries, dependency-advisory findings) contains nothing statement-related.
- `docs/product/stories/README.md` — same terms. Only US-28.1/28.2/28.3 and US-33.4, all Done.
- `git log -- docs/IB2026.csv` — two commits: `d6faacb` (Epic 28, CSV committed) and `3fe699a "update statements"`, 2026-08-12 (the Aug-11 export; pins re-derived in `91bb0b7`, Epic 33). The Aug-28 swap is the third and is uncommitted.
- `git log -- services/quant-engine/app/tests/statement_truths.py` — `c61695a` (US-28.3, created) and `91bb0b7` (US-33.4, re-homed 5 structural pins). Unmodified since.

Not a repeat of a chore that has a standing ticket: there is no standing ticket, because US-28.3 deliberately made this a no-story command-plus-checklist. `test_statement_refresh.py` is the mechanical record that the chore was run correctly — it replaces a story.

Nothing here is deliberately-open being reopened. US-33.4's status as a story was a consequence of Epic 33's engine fix, not a precedent that every refresh is a story; its own slice log states structural tests "must not fail on a refresh", i.e. a clean refresh touches only the pin module.
