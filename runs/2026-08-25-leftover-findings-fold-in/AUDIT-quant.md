REPORT 2026-08-25-leftover-findings-fold-in/AUDIT
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   cd services/quant-engine && python -m pytest -k "combine_snapshot or exposure_source_status or trust_source" -v ; cd services/quant-engine && python -m pytest app/tests/test_exposure_engine.py -k "self_consistent" -v ; cd apps/desktop && npx vitest run runMetadataTrustSourceGuard
  result:    PASS
  detail:    2 passed (combine-snapshots route tests), 1 passed (exposure self-consistency characterization), 3 passed (frontend trust-source guard). All landed tests are sound and pass — the FAIL verdict below is from independent recomputation finding a math defect the landed test suite does not cover, not from a failing test.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - FINDING 1 (MATERIAL) routes to backend-engineer: statement_importer.py double-counts positions/NAV when account_id fails to parse on either combined snapshot. See § Finding 1.
  - FINDING 1 is newly reachable via the ordinary add_snapshot flow, not just the old edge-case multi-file-upload path — see § Finding 1 "impact" for why that raises its priority.
  - FINDING 2 (MATERIAL) routes to docs-engineer or quant-research: financial-methodology.md has no section for combine_imported_snapshots' multi-statement merge (NAV selection, TWR compounding). See § Finding 2.
  - Both findings are in statement_importer.py, pre-existing code this epic reused — the epic's own new code (route, schema, App.tsx wiring) is correct, independently verified end-to-end in § US-40.2 verification.

risks:
  - Finding 1 requires account_id parsing to fail on at least one side (an unparsed IBKR PDF, or a Freedom24/ESPP/CSV regex/column miss) — not the tested path, since every existing fixture sets account_id explicitly.
  - I judged Finding 1 MATERIAL not CRITICAL specifically because it did not fire in run_all_tests.py's green run — flagging that judgment call explicitly for the human to weigh.
  - I did not attempt to fix either finding — per this order's non_goals and the gates.md rule that only the owning lane fixes what a finding names.

## Orchestrator brief
- US-40.1 (trust-classification fix): PASS on every DoD check — contract-doc note verified word-for-word against exposure_engine.py, regression test's regex verified to catch a hypothetical violation (both by tracing and by its own built-in sanity-check test cases), consumer census independently re-run (zero non-test reads of Exposure's run_metadata.source_status/.confidence today), duplication finding correctly routed to tech-debt (not silently fixed). No findings on this half. See § US-40.1 verification.
- US-40.2 (combine-snapshots reuse): route calls combine_imported_snapshots verbatim (confirmed by reading imports.py:49-56) — zero duplicated merge logic, engineering design is sound. Frontend wiring, argument order, sequential-add-chain accumulation, and the AC3 degraded-combination disclosure path were all independently traced/hand-computed and confirmed CORRECT. See § US-40.2 verification.
- FAIL verdict is from a math defect independently reproduced in the REUSED function itself (not the epic's new code): `combine_imported_snapshots`'s account-id-based position/NAV merge silently double-counts a same-account combine when account_id fails to parse on either input — reproduced numerically twice (both-None and one-None cases). See § Finding 1 (MATERIAL).
- Second finding: the multi-statement merge formulas (NAV selection, TWR compounding) that feed the documented cash-anchor rule have no financial-methodology.md section at all — a genuine guardrail-2 traceability gap, pre-existing but newly load-bearing via this epic's new reachable path. See § Finding 2 (MATERIAL).
- No CRITICAL findings — nothing currently displayed to a user is provably wrong today (the bug requires a specific parse failure not present in tested statements); both findings are MATERIAL ("correct in the normal case, wrong/unhandled at an edge" and "doc and code disagree" respectively).
- Sections below: § US-40.1 verification, § US-40.2 verification, § Finding 1, § Finding 2, § Anchors used.

---

## US-40.1 verification

**Contract-doc note vs. code (anchor: code-reading, direct).** `docs/contracts/exposure-fields.md:38`'s inserted sentence claims `run_metadata.source_status.lookthrough_resolution`, `run_metadata.source_status.benchmark_holdings`, and `run_metadata.confidence` are "always live/per-render, recomputed on every `build_exposure_result` call... redundant re-derivations of `availability`'s own classification." Read `exposure_engine.py` directly: `build_exposure_result` (:45-123) calls `_build_exposure_source_status` (:83-88, defined :131-149) and `_combine_exposure_confidence` (:89, defined :263-271) unconditionally on every invocation, and `_build_exposure_availability` (:59-64, defined :165-215) independently recomputes the identical three-way `lookthrough_status`/`lookthrough_resolution` classification over the identical inputs (`total_market_value`, `lookthrough_constituents`, `uncovered_positions`) one call apart. The doc's claim is accurate, line-for-line.

**Regression test (anchor: constructed violation case, traced).** `runMetadataTrustSourceGuard.test.ts`'s `FORBIDDEN_ACCESS_REGEX = /\brun_metadata\??\.(source_status|confidence)\b/` scans every non-test `.ts`/`.tsx` file under `features/portfolio`. I traced a hypothetical violation — a future `SomeCard.tsx` containing `const trust = result.run_metadata.source_status.benchmark_holdings` — against the regex by hand: `\brun_metadata` matches the word boundary before `run_metadata`, `\??` optionally matches nothing (no `?.`), `\.` matches the literal dot, `(source_status|confidence)` matches `source_status`, `\b` closes on the trailing word boundary before `.` — the line matches, the test fails, and reports `file:line`. The test file also carries its own explicit sanity-check case (`'const status = analysis.run_metadata.source_status.benchmark_holdings'` asserted `true` at line 95) that verifies exactly this construction — confirming the test's own self-check is not vacuous.

**Consumer census (anchor: independent, exhaustive re-grep, non-test).** Re-ran the grep this epic's own research (`03-quant-research.md`) ran, independently: `grep -rn "run_metadata" apps/desktop/src` (full output reviewed). Findings: `BenchmarkPositioningCard.tsx:80` reads only `.reproducibility.benchmark_symbol` (unaffected, correctly live-by-design). `DashboardPanel.tsx:141` passes `result?.run_metadata` (typed `DashboardHistoryRunMetadata`, a different backend type entirely) into `ReplayDisclosuresCard` — read that component's full head (`ReplayDisclosuresCard.tsx:1-40`) and confirmed via `grep -n "source_status\|confidence"` (zero hits) that it never reads either field; it reads `ReplayCashAnchor`/`ReplayQuantityWithholding` fields instead. `PerformanceBenchmarkCard.tsx:96-101` and `RiskSummaryCard.tsx:57` read `DashboardHistoryRunMetadata`/`DiagnosticsRunMetadata` fields (`return_basis_contract`, `section_trust`), not Exposure's `run_metadata.source_status`/`.confidence`. Zero non-test hits on `run_metadata.source_status` or `run_metadata?.confidence`/`run_metadata.confidence` (off the Exposure shape) anywhere in `apps/desktop/src`. This independently confirms the prior research's census rather than merely trusting it.

**Duplication finding disposition.** Confirmed by direct reading: `_build_exposure_source_status.lookthrough_resolution` (:137-144) and `_build_exposure_availability.lookthrough_status` (:181) are two separately-written three-way conditionals over identical inputs, never sharing a helper — genuine duplication, correctly NOT fixed in this slice (routing to tech-debt-register per the design doc's disposition is right: fixing it touches `exposure_engine.py`'s classification logic itself, which per project.md guardrail 1 needs its own quant-research pass, out of proportion to a doc-only story).

No findings on US-40.1. Every DoD item for this half is satisfied.

## US-40.2 verification

**Route calls `combine_imported_snapshots` verbatim (anchor: code-reading, direct).** `app/api/routes/imports.py:49-56`:
```python
@router.post("/combine-snapshots", response_model=ImportedPortfolioSnapshot)
def combine_snapshots(request: CombineImportedSnapshotsRequest) -> ImportedPortfolioSnapshot:
    try:
        return combine_imported_snapshots(request.snapshots)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
```
No re-implementation, no inlined subset, identical error-mapping pattern to the existing `import_interactive_brokers_statement` route. `CombineImportedSnapshotsRequest` (`app/schemas/imports.py:120-121`) is a pure one-field wrapper (`snapshots: list[ImportedPortfolioSnapshot]`), no new nested types. Zero duplicated financial-merge logic — the design's central claim is correct.

**Order independence (anchor: code-reading + hand trace).** `combine_imported_snapshots` (`statement_importer.py:66-73`) immediately does `ordered = sorted(snapshots, key=_snapshot_sort_key)` before anything else — the caller's input order is discarded and re-derived from each snapshot's own min/max ledger/position dates. So App.tsx sending `[baseImportedHistorySnapshot, nextAnalysis.snapshot]` in that specific order is cosmetic; the function is order-independent by construction. Confirmed, not just asserted.

**Sequential-add-chain accumulation (anchor: hand-computed 3-statement case, external anchor).** Wrote an independent script (not the design doc's prose, an executable degenerate case) building three synthetic single-account snapshots A (Jan, TWR 5%), B (Feb, TWR 3%), C (Mar, TWR 2%), each with account_id="U1" and distinct source_path/ledger entries, and combined them exactly the way `App.tsx`'s add_snapshot branch would (`combine(A,B)` then `combine(combine(A,B), C)`):
```
AB statements: ['A.pdf', 'B.pdf']           AB TWR: 8.15   (expected (1.05*1.03-1)*100 = 8.15)
ABC statements: ['A.pdf', 'B.pdf', 'C.pdf']  ABC TWR: 10.313 (expected (1.05*1.03*1.02-1)*100 = 10.313)
ABC positions: [('AAPL', 20.0)]              (expected 20, the latest-only holding, not 10+15+20=45)
ABC starting_nav: 1000.0                     (expected 1000, the earliest statement's own value)
ABC ending_nav: 4000.0                       (expected 4000, the latest statement's own value)
ABC ledger entry count: 3                    (expected 3, one per statement, none dropped or duplicated)
```
Every value matched hand-computed expectations exactly. `_collect_statements` (`:117-127`) reads each input's full `.statements` list (not just its own `.statement`), so a chain of combines genuinely accumulates the full history, confirming the design doc's "full accumulated history, not just the immediate parent" claim by direct execution, not by re-reading the doc's prose.

**AC3 degraded-combination path, end to end (anchor: code-reading, full chain traced).** `_validate_compatible_snapshots` (`statement_importer.py:130-133`) raises `ValueError("Cannot combine statements with different base currencies")` on a currency mismatch → route maps it to HTTP 400 (`imports.py:53-56`) → `combineImportedSnapshots` adapter (`portfolioAnalysisAdapter.ts:173-189`) checks `!response.ok` and throws `Error(payload?.detail ?? ...)` → App.tsx's inner `try/catch` (`App.tsx:789-794`) catches it, sets `combinedHistorySnapshot = null` and calls `setImportError(...)`, then falls through (no `throw`) to `saveImportedSnapshotNode(...)` and `restoreImportedWorkspaceFromPersistedState(...)`. Read `applyDashboardSession` (`App.tsx:328-334`) directly: it calls `setAnalysis`/`setExposureAnalysis`/`setExposureFactorModel`/`setLastImportedFileNames`/`setRestoredSession` only — never `setImportError` — and `restoreImportedWorkspaceFromPersistedState`'s full body (`:341-467`, read in full) never calls `setImportError` either, even though it builds a local `composeDashboardSession({..., importError: null, ...})` — that local field is silently unused by `applyDashboardSession`. So the message set in the inner catch survives untouched through the rest of the function and is what `DashboardPanel` renders. Confirmed end to end by reading the real code, not the test's mocked chain.

**TS request shape (anchor: code-reading).** `combineImportedSnapshots` (`portfolioAnalysisAdapter.ts:173-189`) POSTs `{ snapshots }` where each element is the frontend's `ImportedSnapshot` (`types.ts:14-49`). The TS type is loosely typed on two fields (`ledger_entries`/`instruments: Array<unknown>`) rather than mirrored field-for-field, but since these objects are never hand-constructed by the frontend — they are round-tripped JSON originally produced by the backend (`analyze-upload`'s response, or a prior `combine-snapshots` response) — the loose typing does not cause a serialization mismatch; confirmed by reading `nextAnalysis.snapshot`'s origin (the `analyze-upload` route's own `ImportedBootstrapResponse.snapshot`, itself an `ImportedPortfolioSnapshot.model_dump()`).

No findings on US-40.2's own new code (route, schema, App.tsx wiring). The FAIL verdict below is entirely about the pre-existing `combine_imported_snapshots` internals this design correctly chose to reuse rather than re-implement.

## Finding 1

```
FINDING 1
severity:   MATERIAL
where:      services/quant-engine/app/services/statement_importer.py:243-253 (_latest_snapshot_by_account) and :256-280 (_merge_terminal_positions), :177-230 (_merge_statement_totals) — reached via the new POST /portfolios/import/combine-snapshots route (app/api/routes/imports.py:49-56), which is now App.tsx's add_snapshot path (App.tsx:789-794)
claim:      combine_imported_snapshots merges two same-account statements by replacing (latest-wins), not accumulating, terminal positions/NAV/cash — the semantic add_snapshot needs (statement N+1's holdings supersede statement N's, they must not be summed).
actual:     independently reproduced with an executable script against the real functions (not a mock): two single-account snapshots, base (Jan, AAPL qty 10, ending_nav 2000) and new (Feb, AAPL qty 15, ending_nav 3000).
            - With account_id="U1234567" on BOTH (the tested, normal case): combined positions = [('AAPL', 15.0)] (correct, latest wins), ending_nav = 3000.0 (correct).
            - With account_id=None on BOTH: combined positions = [('AAPL', 10.0), ('AAPL', 15.0)] — TWO position rows for the same account/symbol instead of one — and ending_nav = 5000.0 (2000+3000 summed).
            - With account_id="U1234567" on the base but None on the newly-uploaded statement only (the more realistic failure mode — one statement's account-id parse fails, not both): identical double-counted result — positions [('AAPL',10.0),('AAPL',15.0)], ending_nav = 5000.0.
            Root cause: _latest_snapshot_by_account (:243-253) buckets any snapshot with a falsy account_id into fallback_snapshots and returns it as an ADDITIONAL terminal snapshot rather than deduping it against the other input by account. This logic is correct and intentional for genuinely different accounts (verified via test_importer.py's test_three_broker_combine_ib_ff_espp, which legitimately sums IB+Freedom24+ESPP holdings — three real accounts). It is wrong for the same account with an unparseable id, and the function cannot distinguish the two cases.
impact:     a researcher who adds a statement whose account_id fails to parse — e.g. an IBKR PDF where the "Account " line's value doesn't start with "U" (interactive_brokers.py:93-96's exact match condition), a Freedom24/ESPP statement whose "Client ID"/"participant" regex misses (freedom24.py:89, espp.py:53), or a CSV import missing an "Account" column (interactive_brokers_csv.py:191) — would see their combined portfolio's holdings and ending NAV silently inflated (in this example, exactly doubled) with no error and no degradation disclosure. This combined snapshot's starting_nav/ending_nav feed PortfolioStateEngine's cash anchor (`base_cash = starting_nav − opening_positions_value`, financial-methodology.md:2232-2235) and terminal-state reconciliation (portfolio_state.py:891-897), so the corruption propagates into the replayed TWR the Dashboard displays for that history — a plausible-looking wrong number, the exact failure mode the pack calls "the worst possible outcome — it will never be questioned."
expected:   combine_imported_snapshots should not silently sum same-account positions when account_id can't be confirmed distinct. Candidate fix: extend _validate_compatible_snapshots (or a new check) to require account_id to be present and equal (or explicitly the same known-single-account case) before the position-replace path applies, and raise ValueError otherwise — routing through the already-wired AC3 degradation channel (HTTP 400 → setImportError) rather than guessing by summation. This needs the owning lane's design judgment, not a lane fix in passing.
```

## Finding 2

```
FINDING 2
severity:   MATERIAL
where:      docs/finance/financial-methodology.md (no section exists) vs. services/quant-engine/app/services/statement_importer.py:66-98, :177-230 (combine_imported_snapshots / _merge_statement_totals)
claim:      financial-methodology.md is "the canonical source of truth for every implemented formula" (CLAUDE.md, project.md guardrail 1) and documents the cash-anchor formula this merge feeds (`base_cash = starting_nav − opening_positions_value`, :2232-2235, sourced from app/engine/portfolio_state.py).
actual:     grepped the full doc for "combine", "multi-statement", and any starting/ending-NAV merge semantics — zero hits beyond the single-statement anchor rule. _merge_statement_totals (:177-230) computes, for a COMBINED (multi-statement) snapshot: starting_nav = the earliest statement's own starting_nav (:214-218); ending_nav/cash_total/stock_total = the latest (terminal, per-account) statement's own values (:204-212); time_weighted_return_pct = geometric compounding across each statement's own period return (`growth *= 1 + twr_i/100`, :192-198, verified correct by hand-computation in § US-40.2 verification). None of this derivation — which is exactly what feeds the documented cash-anchor formula whenever the anchored snapshot is a combined one, as it now routinely will be via add_snapshot — has a methodology-doc section.
impact:     a future engineer or auditor checking "how is starting_nav derived for an add_snapshot/combined history" has no specification to check the code against — this is precisely the guardrail-2 traceability gap the pack defines ("every UI metric maps to one engine formula and one code path... untraceable → do not ship"). It also means Finding 1's defect had no documented spec that would have caught it as a deviation — the merge logic has effectively been undocumented since it was written for the old multi-file-upload case, and this epic newly makes it reachable through the ordinary, expected add_snapshot workflow rather than an edge-case initial multi-file import.
expected:   financial-methodology.md should gain a section (near the existing cash-anchor rule at :2232) documenting combine_imported_snapshots' merge semantics: earliest-starting-NAV / latest-terminal-ending-NAV(per-account) / geometric TWR compounding, and explicitly state the account-identity assumption position-replace relies on — which Finding 1 shows is currently unsound when account_id is unparseable.
```

## Anchors used

- **US-40.1 contract-doc note vs. code**: `anchor: methodology-doc`-equivalent — direct code-reading of `exposure_engine.py` against the doc's own claims (consistency check, not independent verification of a formula's correctness — there is no formula here, only a consumption-discipline claim, so code-reading is the correct and sufficient anchor for this half).
- **US-40.1 regression test**: `anchor: constructed violation case` — a hypothetical forbidden-access line traced by hand against the regex, plus the test file's own embedded sanity-check assertions (both a positive and negative case), which is an external anchor because it does not depend on the test having been written correctly — I re-derived what the regex would match independently.
- **US-40.1 consumer census**: `anchor: independent, exhaustive re-grep` — re-ran the same census from scratch rather than trusting `03-quant-research.md`'s prior result; results agree.
- **US-40.2 route wiring / order independence / AC3 disclosure chain**: `anchor: code-reading, direct` — traced actual execution path file-by-file (route → adapter → App.tsx → applyDashboardSession/restoreImportedWorkspaceFromPersistedState), not the design doc's prose.
- **US-40.2 sequential-add-chain / TWR compounding / position selection (Findings 1 and the passing checks in § US-40.2 verification)**: `anchor: closed-form/hand-computed case` — the pack's cheapest and strongest external anchor. Built minimal synthetic snapshots with hand-computable expected TWR (geometric product), NAV (earliest/latest selection), and position quantities (latest-wins), executed the real `combine_imported_snapshots` against them, and compared to the hand-derived expectation — this is genuine independent verification, not a consistency check against the same doc/design the code was built from.
- **Finding 2 (doc gap)**: `anchor: methodology-doc absence` — confirmed by direct grep of the full doc; this is the pack's explicit "no section exists" finding class, not a formula-correctness check.
