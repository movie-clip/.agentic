REPORT 2026-08-25-leftover-findings-fold-in/11
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   python scripts/run_all_tests.py
  result:    PASS
  detail:    Backend 911 passed. Frontend 40 files / 354 tests passed. tsc --noEmit clean. Dead-code gate (ruff+vulture+knip) clean. dashboardGoldens.ts unmodified (confirmed via git diff/status).

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Ready for docs-engineer close-out per run.md's own "next" plan. § Close-out items below is the authoritative punch list — 6 items, all non-blocking.
  - run.md ledger bookkeeping: mark the T-40.1.3-T-40.2.2a-backend types.ts contract_note (Open table line 68) ABSORBED, not OPEN.
  - It is superseded by T-40.2.2b's own decision (line 73, already ABSORBED): no named type needed, inline {snapshots} chosen instead.
  - Same bookkeeping applies to the 03-quant-research contract_note (line 54) and the 04-stories picker-date finding (line 56) — both superseded by 05-technical-plan's own ABSORBED entries answering the same open questions.
  - run.md's Rounds table still shows both AUDIT-quant findings at "round 1 of 2" with no closure marker, even though 10-quant-reaudit.md's verdict is PASS — ledger bookkeeping only, not a re-open.

risks:
  - The working tree carries a second, unrelated body of uncommitted changes predating this run (see § Unrelated uncommitted diff) — does not block this verdict, flagged for close-out/human awareness.
  - Backend count (911) is 3 higher than T-40.1.4-T-40.2.3-test.md's own reported 908 — those 3 tests belong to the unrelated diff above, not a gap in this epic's own coverage.

## Orchestrator brief
- Verdict PASS. Full epic (US-40.1 T-40.1.1-4, US-40.2 T-40.2.2a/b+40.2.3, CR-1 fix 07/08/09, re-audit 10) composes correctly; run_all_tests.py green.
- CR-1 integration confirmed clean by direct code read (not by trusting reports): `_validate_compatible_snapshots`'s new account-identity ValueError and the pre-existing currency-mismatch ValueError both funnel through the SAME unedited `except ValueError -> HTTPException(400)` in imports.py, the SAME adapter throw in portfolioAnalysisAdapter.ts, and the SAME App.tsx `catch { setImportError(...) }` block (App.tsx:788-795) — no special-casing needed, none was added. See § CR-1 integration trace.
- Per-ticket DoD cross-check against 05-technical-plan.md: all 7 tickets' deliverables verified present in the actual tree, matching the plan's specifics (file:line citations checked, not just report prose). No undeclared deviations found. See § DoD cross-check.
- Contract alignment: schema (imports.py) <-> route <-> TS type (types.ts's ImportedSnapshot) <-> App.tsx usage all consistent; router registration confirmed (one `router` object, already included via main.py:19, no new include_router needed). No BLOCKING findings.
- 6 non-blocking close-out items remain, all correctly deferred (not silently skipped) across the ticket reports — full list with exact status in § Close-out items. None require another engineering round; all are docs-engineer or tech-debt-register bookkeeping.
- Sections below: § CR-1 integration trace, § DoD cross-check, § Contract alignment, § Close-out items, § Unrelated uncommitted diff.

---

## CR-1 integration trace

Read the current tree directly at each hop, not the reports' claims of it:

1. `statement_importer.py:130-147` (`_validate_compatible_snapshots`) — two independent raise sites, both `ValueError`: the pre-existing base-currency check (:131-133) and CR-1's new account-identity check (:141-147, "at least one statement has no parsed account identifier..."). Both run in the same function, same call, no ordering dependency that matters to the caller.
2. `app/api/routes/imports.py:49-56` (`combine_snapshots` route) — unedited by CR-1 (confirmed: 07-backend.md's own `changed` list names only `statement_importer.py`). `except ValueError as exc: raise HTTPException(status_code=400, detail=str(exc))` catches both raise sites identically — the route cannot and does not distinguish which ValueError fired.
3. `portfolioAnalysisAdapter.ts:173-189` (`combineImportedSnapshots`) — `if (!response.ok)` throws `Error(payload?.detail ?? 'Combine imported snapshots failed')` for any non-2xx, both cases included.
4. `App.tsx:788-795` — the `try { combinedHistorySnapshot = await combineImportedSnapshots(...) } catch { combinedHistorySnapshot = null; setImportError(...) }` block has no error-type discrimination; it treats every rejection identically, both the pre-existing currency-mismatch case and CR-1's new account-identity case.
5. `applyDashboardSession`/`restoreImportedWorkspaceFromPersistedState` (App.tsx:328-334, called at :807 after the catch) — read directly, confirmed it never calls `setImportError`, so the message set in step 4 survives to render in `DashboardPanel`'s `<p className="error">`.

Net: CR-1's fix required zero changes outside `statement_importer.py` to integrate with AC3's degradation channel — the channel was already generic. This confirms 07-backend.md's own "no route/schema change needed" claim (§ Route mapping) by independent trace, not by re-reading that claim.

One judgment call worth surfacing to the human even though it does not block: the AC3 message text (App.tsx:793) says "for example, a differing base currency" — a specific example that predates CR-1 and does not mention the new account-identity failure mode. This is accurate (the message is generic, "for example" signals non-exhaustive), just not as specific as it could be for the new case. Not a BLOCKING or SHOULD_FIX finding — the message is truthful and the badge/disclosure requirement (AC3) is met — but worth a follow-up polish if the human wants the message to name both cases explicitly.

## DoD cross-check

Checked each ticket's actual landed code against 05-technical-plan.md's own specification (not against the ticket report's paraphrase of it):

- **T-40.1.1**: docs/contracts/exposure-fields.md:38's inserted sentence — read directly, text matches 05-technical-plan.md § T-40.1.1's specified sentence verbatim (including the `CR-1-frontend.md` cross-reference, which is a DIFFERENT CR-1 than this epic's own — a pre-existing, already-landed 2026-08-24 fix, correctly distinguished by name).
- **T-40.1.2**: `variantLabels.ts` — `resolveNodeImportDate`/`formatVariantNodeLabel`/`formatWorkingDraftLabel` read directly; matches the design's reuse-`buildNodePath`'s-shape instruction and the `.slice(0, 10)` truncation convention.
- **T-40.1.3**: `frozen_market_data.py` — `RecordingMarketData.get_company_profile`/`get_etf_sector_weightings` read directly; matches `MarketDataService`'s real two-arg-with-`symbol_overrides` signatures per the plan's explicit instruction (not `FakeMarketData`'s narrower shape). `to_payload()` extended with the two new sorted-dict keys as specified.
- **T-40.1.4**: regression tests exist (`runMetadataTrustSourceGuard.test.ts`, `variantLabels.test.ts`, `test_exposure_engine.py`'s characterization test) and pass.
- **T-40.2.2a**: `CombineImportedSnapshotsRequest` schema and `/combine-snapshots` route read directly; matches the plan's exact shape (pure wrapper, verbatim reuse of `combine_imported_snapshots`, identical error-mapping to `import_interactive_brokers_statement`).
- **T-40.2.2b**: `App.tsx`'s `add_snapshot` branch (:783-808) read directly; matches the plan's snippet field-for-field, including the "no prior replay data -> adopt the new statement's own snapshot alone" fallback and the try/catch degradation.
- **T-40.2.3**: `test_routes.py`'s two new route tests read directly; correctly scoped as thin-wrapper checks (not re-testing merge math, which `test_importer.py` already covers) per the plan's own instruction.
- **CR-1 (07/08/09/10)**: covered in § CR-1 integration trace above; 10-quant-reaudit.md's PASS independently re-verified the math, out of this order's non_goals to re-check.

No undeclared deviations found anywhere in this cross-check.

## Contract alignment

- `app/schemas/imports.py`'s `ImportedPortfolioSnapshot` fields (`statement`, `statements`, `statement_totals`, `instruments`, `cash_balances`, `positions`, `ledger_entries`) line up 1:1 by name with `types.ts`'s `ImportedSnapshot` (types.ts:14-49). `ledger_entries`/`instruments` remain loosely typed as `Array<unknown>` on the TS side — pre-existing looseness (not introduced by this epic), safe because the frontend never hand-constructs these objects, only round-trips backend JSON (confirmed by AUDIT-quant.md's own trace, independently re-confirmed here by reading `types.ts` directly).
- `main.py:4,19` — `imports` router imported and `include_router(imports.router)` called once; the new `/combine-snapshots` route rides the same router object (prefix `/portfolios/import`), no missing registration.
- No published/already-consumed field was altered by any lane in this epic — every schema change in this diff is additive (`CombineImportedSnapshotsRequest` is new; `ImportedPortfolioSnapshot` itself is untouched).
- No duplicated formula introduced: the new route calls `combine_imported_snapshots` verbatim, zero re-implementation (confirmed by direct read of imports.py:49-56 against statement_importer.py:66-98).

## Close-out items

All six are correctly deferred by the lanes that found them (none silently dropped), none blocking:

1. `docs/contracts/` has no entry yet for `POST /portfolios/import/combine-snapshots` — confirmed absent by grep across all `docs/contracts/*.md`. Docs-engineer's call on which file (dashboard-fields.md or a new import-fields.md), per 05-technical-plan.md.
2. `docs/tech-debt-register.md` has no entry yet for the dead `market_data` param in `_build_shared_sector_overlap` (risk.py:1654, call site risk.py:1531) — confirmed absent by grep. Named in 05-technical-plan.md § T-40.1.3 and 02-delivery-brief.md § Stories Item 4.
3. `docs/tech-debt-register.md` also has no entry yet for the `_build_exposure_source_status`/`_build_exposure_availability` duplication (exposure_engine.py:137-144 vs :181) — confirmed absent by grep. Named in 05-technical-plan.md § Duplication finding disposition; needs a quant-research pass before any fix, per project.md guardrail 1.
4. `financial-methodology.md`'s new "Multi-Statement Snapshot Merge" section is missing 10-quant-reaudit.md's Finding 3 (MINOR) sentence about a null-TWR input nulling the whole compound rather than partial-compounding — confirmed absent by reading the current section text (lines ~2263-2344). Non-blocking per the re-audit's own verdict.
5. `app/tests/fixtures.py`'s docstring doesn't note that `statement_totals` fixtures must set `cash_total`/`stock_total` explicitly (ending_nav is derived from their sum, not read directly) — 08-test.md's own "fixtures gotcha," minor test-hygiene note only.
6. `docs/IB2026.pdf` and `docs/U8516450_20260101_20260408.pdf` are absent from this checkout, silently no-op'ing several golden multi-statement combine tests in `test_importer.py` (early `return` on missing file) — pre-existing test-infra gap, not introduced by this epic, flagged by 10-quant-reaudit.md and independently confirmed here (`ls docs/*.pdf` shows neither file present). Worth a tech-debt-register row so it stops being invisible.

Standard end-of-slice docs work (epic-roadmap.md status flip, current-product-state.md inventory update, story-file status flips for US-40.1/US-40.2) is expected at close-out and not itself a gap — not listed as a numbered item above since it is not a finding, just the normal close-out job.

## Unrelated uncommitted diff

`git status`/`git diff --stat` show 10 modified files touched by none of this epic's 9 dispatch reports: `App.tsx` (a hunk distinct from the add_snapshot branch), `BenchmarkPositioningCard.tsx`, a new `BenchmarkPositioningCard.test.tsx`, `DashboardPanel.test.tsx`, `importedBootstrapMapper.ts`, `portfolioWorkspaceStorage.ts`/`.test.ts`, `workspaceTypes.ts`, `portfolioFixtures.ts`, `import_bootstrap.py`, `import_engine.py`, `import_engine_composer.py`. HEAD is commit `59387c7` ("39"), dated 2026-08-24 18:50 — before this run started (2026-08-25 11:04). This is the "2026-08-24 fix (`CR-1-frontend.md`)" that T-40.1.1's own inserted doc sentence cross-references (a prior, already-audited epic's CR fix for `benchmark_overlap_status`, distinct from this epic's own CR-1 for Finding 1). It sits uncommitted per the project's "no agent commits" rule. `run_all_tests.py` is green with it included, and it shares no files with this epic's 24-file diff, so it does not affect this verdict — but the human's next commit will bundle both epics' work together unless split first.
