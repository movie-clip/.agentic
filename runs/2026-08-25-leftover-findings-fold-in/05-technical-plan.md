REPORT 2026-08-25-leftover-findings-fold-in/05
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only DESIGN order; no verification command applies. `python scripts/detect_deadcode.py --strict` was run read-only to settle T-40.1.3's dead-param question (see § T-40.1.3) — confirmed clean/no findings, not a code change.

contract_notes:
  - docs/contracts/exposure-fields.md:38 (end of the existing "distinct truth class" bullet) gains the sibling sentence specified in § T-40.1.1 — no schema change, doc-only.
  - US-40.2 needs a NEW backend schema (`CombineImportedSnapshotsRequest`, app/schemas/imports.py) + route (`POST /portfolios/import/combine-snapshots`) — see § US-40.2 design.
  - The contract doc covering the diagnostics/dashboard-history imported-replay path (docs-engineer's call, likely dashboard-fields.md) needs a new entry once T-40.2.2a lands.

pack_corrections:
  - none

handoff:
  - Full lane-by-lane design for both stories' 7 tickets is below. Orchestrator dispatches directly from § Lane sequence.
  - T-40.2.1 (tech-lead DESIGN) is fulfilled BY this report — do not dispatch it separately, dispatch T-40.2.2a/b and T-40.2.3 against § US-40.2 design.

risks:
  - US-40.2's design adds a backend schema/route the order's DoD assumed was unneeded ("client-side per the story's own framing") — I did not comply silently, see § US-40.2 design, "Why not a pure client-side merge" for the reasoning.
  - This deviation needs the human/producer to confirm or override before T-40.2.2a is dispatched — it trades a small new backend surface against duplicating ~250 lines of NAV/TWR/ledger-merge logic client-side.
  - T-40.1.3's dead-param sub-item: a live `detect_deadcode.py --strict` run confirms it does NOT fire on `_build_shared_sector_overlap`'s param — routes to tech-debt-register.md, not a code removal. See § T-40.1.3.
  - The picker freeze-date source is resolved with high confidence (see § T-40.1.2), but no currently-live code path produces a `kind: 'variant'` node (only test fixtures use it today) — the ancestor-walk fallback is defensive, not proven necessary by a live example.

## Orchestrator brief
- Picker freeze-date data source resolved: `node.portfolioSnapshot.importedMeta.importedAt` (client-persisted, non-optional, present on every workspace node) — NOT the engine's `ExposureRunReproducibilityMetadata` (would need an engine call per picker node). See § T-40.1.2.
- US-40.1's run_metadata fix (T-40.1.1): doc-only sentence at exposure-fields.md:38 + a new source-scanning regression test file `apps/desktop/src/features/portfolio/runMetadataTrustSourceGuard.test.ts`. No schema, no engine behavior change. See § T-40.1.1.
- T-40.1.3 housekeeping: `RecordingMarketData` gets 2 new delegating methods (backend-engineer, real code change). The dead `market_data` param is CONFIRMED not caught by `detect_deadcode.py --strict` today → routes to tech-debt-register.md, not removed here. See § T-40.1.3.
- Duplication finding (`_build_exposure_source_status` vs `_build_exposure_availability`): NOTED, NOT TICKETED — fixing it touches core exposure-classification logic and needs quant-lane involvement per project.md guardrail 1; out of proportion to this doc-only story. Route to tech-debt-register.md. See § Duplication finding disposition.
- US-40.2 (T-40.2.1, fulfilled here): recombination happens by reusing the backend's existing, tested `combine_imported_snapshots` (statement_importer.py:66-98) through a new thin route, NOT a client-side TS port. Splits T-40.2.2 into 40.2.2a (backend-engineer, new schema+route) and 40.2.2b (frontend-engineer, App.tsx wiring) — sequenced, 2a before 2b. See § US-40.2 design.
- AC3 degradation channel reuses the EXISTING `importError`/`dashboardSession.importError` → `DashboardPanel` `<p className="error">` plumbing — confirmed by reading `applyDashboardSession` (App.tsx:328-334): it does not touch `importError`, so a `setImportError(...)` call before `restoreImportedWorkspaceFromPersistedState` is not clobbered. No new prop/component needed.
- Sections below: § T-40.1.1, § T-40.1.2, § T-40.1.3, § T-40.1.4, § Duplication finding disposition, § US-40.2 design, § Lane sequence.

---

## T-40.1.1 — contract-doc note + regression test for `run_metadata.source_status`/`.confidence`

**Lane:** backend-engineer (doc edit) + test-engineer (regression test), or one lane doing both — either split works, no shared file conflict since the doc edit and the new test file are disjoint.

**Contract-doc edit.** `docs/contracts/exposure-fields.md` — insert immediately after the existing "distinct truth class from `ExposureResult`'s own path" bullet (currently ends at line 38, right before the blank line and "Important rules:" at line 39):

> **`run_metadata.source_status.lookthrough_resolution`, `run_metadata.source_status.benchmark_holdings`, and `run_metadata.confidence` are excluded from this freeze and must never be read as a trust source.** They are always live/per-render values, recomputed on every `build_exposure_result` call (`exposure_engine.py:79-91`), and are redundant re-derivations of `availability`'s own classification (`:131-149` vs `:165-215` independently compute the same three-way status from the same inputs). A node whose `availability`/`lookthrough`/`market_overlap` are frozen at import must never have its trust badge sourced from `run_metadata.source_status.*` or `run_metadata.confidence` — that would silently combine a frozen-vintage number with a live-vintage trust label, the exact defect class the 2026-08-24 fix (`CR-1-frontend.md`) closed for `benchmark_overlap_status`. `run_metadata.reproducibility.*` is unaffected by this note — it is genuinely live/per-render by design (e.g. `benchmark_symbol` tracks the currently-selected benchmark) and must stay that way. Enforced by a permanent regression test, not a one-time grep — see `apps/desktop/src/features/portfolio/runMetadataTrustSourceGuard.test.ts`.

No `app/schemas/exposure.py` edit — the fields, their types and their docstrings are unchanged; this is a consumption-discipline note, not a schema change. (The schema-edit-reminder hook does not fire, since no file under `app/schemas/` changes.)

**Regression test (AC5).** New file, since no existing file does source-scanning: `apps/desktop/src/features/portfolio/runMetadataTrustSourceGuard.test.ts`. Shape (mirrors the spirit of `BenchmarkPositioningCard.test.tsx`'s CR-1 pattern — "confirmed via repo-wide grep," made permanent and automated rather than a one-time manual check):

- Use Node's `fs`/`path` (available in vitest's default environment) to recursively list every `.ts`/`.tsx` file under `apps/desktop/src/features/portfolio`, excluding `*.test.ts`/`*.test.tsx`.
- For each file's contents, assert no line matches `/run_metadata\??\.(source_status|confidence)\b/` — this targets property ACCESS (`run_metadata.source_status`, `run_metadata?.confidence`), not object-literal construction (`source_status: {...}` as a key) or type declarations (`source_status: ExposureRunSourceStatus`), so it will not false-positive on `types.ts`'s own `ExposureRunMetadata` type definition (which lives in this same directory) or on any fixture object literal.
- On a match, fail with the offending file path and line number in the assertion message, so a future violation is immediately actionable (mirrors AC5's "not a one-time grep" requirement — this makes the grep step itself the enforcement).
- Test files are deliberately excluded from the scan: `BenchmarkPositioningCard.test.tsx`'s own fixture constructs `run_metadata: { source_status: { ... } }` as an object literal for the CR-1 regression — not a violation, but excluding test files entirely keeps the scanner simple rather than relying on the access-vs-construction regex distinction to save it.

**Backend regression (test plan's first bullet).** Extend `test_exposure_engine.py` (matches its existing `test_exposure_engine_*` naming convention) with one characterization test that calls `build_exposure_result(...)` once and asserts `run_metadata.source_status.lookthrough_resolution`/`run_metadata.confidence` and `availability.lookthrough_status`/`.lookthrough_confidence`/`.benchmark_overlap_confidence` are computed from the same call (i.e., pins today's self-consistency-within-one-call property so a future edit that decouples them — e.g. making one path async or optional — is caught). This is a pin, not new behavior; no assertion should change if nothing changes.

**Traces to:** AC4, AC5, AC6.

## T-40.1.2 — freeze-date signal in the snapshot picker

**Lane:** frontend-engineer.

**Resolved data source (the order's own open question).** Use `node.portfolioSnapshot.importedMeta.importedAt` — a client-persisted field on `PortfolioSnapshot` (`workspaceTypes.ts:28`, non-optional). Confirmed by reading the full node-creation/merge chain:
- `createWorkspaceFromImport` (`portfolioWorkspaceStorage.ts:102-103`) sets it from the fresh import.
- `saveImportedSnapshotNode` (`:334`) sets `node.createdAt`/`source.importedAt` from `input.portfolioSnapshot.importedMeta.importedAt` — same field, always present.
- `overlayImportedSnapshot` (`portfolioSnapshot.ts:151-154`, add_snapshot's merge path) updates it to the newly-imported statement's `importedAt` on merge — a reasonable "most recent capture" semantic, not a fabrication.
- `clonePortfolioSnapshot` (`portfolioSnapshot.ts:88-90`, used by `createDraftFromNode` for the working draft) deep-clones the field unchanged, so a draft/variant built on top of a base node inherits the base's date without extra plumbing.

This is why the engine's `ExposureRunReproducibilityMetadata.input_imported_at` (the brief's other candidate) is wrong for this job: it is only computed by `build_exposure_result` for the snapshot currently being analyzed, not for every node the picker enumerates — using it would mean running the engine per picker option, which is not how `snapshotOptions` is built today (`App.tsx:875-878`, a synchronous map over `workspaceNodes`).

**Implementation.** `variantLabels.ts`:
- Add `resolveNodeImportDate(node: PortfolioNode, nodes: PortfolioNode[]): string | null` — reuse `buildNodePath`'s existing `nodeById`/parent-walk shape: check `node.portfolioSnapshot?.importedMeta?.importedAt` first; if absent, walk `parentId` the same way `buildNodePath` does, returning the first ancestor's date found; return `null` if the chain has no snapshot/date anywhere (this is the AC3 "no date" case — a node with no import behind it at all, e.g. `formatWorkingDraftLabel`'s `activeNode === null` early return, which must keep returning `'Working Draft · base'` unchanged). Format as `importedAt.slice(0, 10)` (YYYY-MM-DD) — this is the codebase's existing convention for ISO-date truncation, already used by `extractStatementEndDate` (`App.tsx:64`), not a new formatter.
- `formatVariantNodeLabel`: after building the joined path, append `` ` (${date})` `` when `resolveNodeImportDate(...)` is non-null; unchanged (no suffix) when null.
- `formatWorkingDraftLabel`: no change needed beyond what `formatVariantNodeLabel` already gives it — it delegates to `formatVariantNodeLabel(activeNode, nodes)` for the non-null-`activeNode` branch (line 24), so the date suffix appears automatically once that function is updated. Its `!activeNode` early return (line 23, `'Working Draft · base'`) stays untouched — this is AC3's literal "renders exactly as it does today" case.

**Traces to:** AC1, AC2, AC3.

## T-40.1.3 — housekeeping: test-infra fold-in

**Lane:** backend-engineer.

**`RecordingMarketData` gap (real code change).** `services/quant-engine/app/scripts/frozen_market_data.py:131-198`. Add two methods mirroring the existing four's delegate-and-capture shape (e.g. `get_historical_prices` at `:140-154`), matching `MarketDataService`'s real signatures (`market_data.py:503`, `:525` — both take `symbol_overrides: dict[str, list[str]] | None = None`, unlike `FakeMarketData`'s narrower two-arg version; the story explicitly says match the real service, not the fake):

```python
def get_company_profile(self, symbol: str, symbol_overrides: dict[str, list[str]] | None = None) -> dict | None:
    profile = self._inner.get_company_profile(symbol, symbol_overrides)
    self._profiles[canonicalize_symbol(symbol)] = profile
    return profile

def get_etf_sector_weightings(self, symbol: str, symbol_overrides: dict[str, list[str]] | None = None) -> list[dict]:
    rows = self._inner.get_etf_sector_weightings(symbol, symbol_overrides)
    self._sector_weightings[canonicalize_symbol(symbol)] = rows
    return rows
```

Add `self._profiles: dict[str, dict | None] = {}` and `self._sector_weightings: dict[str, list[dict]] = {}` to `__init__` (`:135-137`), and extend `to_payload()` (`:191-198`) with two more keys (e.g. `"profiles"`, `"sector_weightings"`) built the same sorted-dict way as `"fetch_meta"`.

**Scope boundary (state explicitly, don't let this creep):** `FrozenMarketData` (the replay side, `:48-129`) is unaffected — the module docstring (`:14`, "duck-types the four `MarketDataService` methods the golden path consumes") stays accurate, because nothing in the current dashboard-golden generation path calls `resolve_etf_sector`/`get_company_profile`/`get_etf_sector_weightings` yet. This ticket only closes the recording-side gap so a *future* story touching `resolve_etf_sector` in the golden-refresh workflow doesn't have to fix this first; it does not wire replay support, because there is no current consumer to replay for.

**Dead `market_data` param — CONFIRMED not to fire, routes to tech-debt-register, not a code change here.** I ran `python scripts/detect_deadcode.py --strict` read-only (ruff + vulture + knip) against the current tree: clean, zero findings. Direct code reading confirms the param IS genuinely unreferenced in `_build_shared_sector_overlap`'s body (`risk.py:1648-1687` — only `registry`, `sector_cache`, `shared_symbols`, `left_holdings`, `right_holdings`, `left_resolved`, `right_resolved` are used); vulture's default `--min-confidence 80` simply doesn't flag unused function *parameters* the way it flags unused locals/functions. Per the story's own disposition rule ("if `detect_deadcode.py --strict` confirms it fires... or routes to `docs/tech-debt-register.md` if it does not"), this is a **docs-engineer close-out handoff**, not a T-40.1.3 code change: `docs/tech-debt-register.md` gets an entry naming `risk.py:1654` (`market_data: HoldingsMarketData` parameter), noting it's dead (confirmed by direct reading, not caught by the automated gate), and pointing at the single call site (`risk.py:1531`) which would also need its `market_data` argument dropped in the same pass whenever this is picked up.

**Traces to:** no AC — housekeeping only, per the story.

## T-40.1.4 — tests

**Lane:** test-engineer.

Delivers: the backend characterization test named in § T-40.1.1, the new `runMetadataTrustSourceGuard.test.ts` scanner, and a new `apps/desktop/src/features/portfolio/variantLabels.test.ts` (no existing file — confirmed via glob) covering:
- a base node's label includes its `importedMeta.importedAt` date, truncated to YYYY-MM-DD;
- a variant/draft node built on the base still carries the same date (via `clonePortfolioSnapshot`'s unchanged-`importedMeta` behavior, or via the ancestor-walk fallback if a future `kind: 'variant'` node is constructed without its own snapshot);
- a node with no import date anywhere in its chain renders with no date suffix (AC3), and `formatWorkingDraftLabel(null, nodes)` still returns exactly `'Working Draft · base'`.

**Traces to:** AC1-AC6 (full story coverage, both halves).

## Duplication finding disposition

**NOTED, NOT TICKETED.** `_build_exposure_source_status`'s `lookthrough_resolution` (`exposure_engine.py:137-144`) and `_build_exposure_availability`'s `lookthrough_status` (`:181`) independently reimplement the identical three-way conditional over the identical inputs; `run_metadata.confidence` is a pure recombination of `availability`'s own two confidence fields. This is real duplication (same shape as the `US-34.8` `risk.py` case the pack names), but fixing it means editing `exposure_engine.py`'s classification logic itself — under project.md's "any change touching `analytics/`, a formula, a weighting, a return basis, or a trust classification must go through the quant lane," this needs a quant-research pass of its own, which is a larger, separate lift than a doc-only, zero-behavior-change story. Folding it into T-40.1.1 would blur a pure-documentation ticket with a behavior-adjacent refactor. Route to `docs/tech-debt-register.md` (docs-engineer close-out), same disposition as item 4.

## US-40.2 design (fulfills T-40.2.1)

**What actually needs combining.** `historySource.importedHistorySnapshot` is `ImportedSnapshot` (`types.ts:14-49`) — the raw broker-truth object (`statement`, `statements[]`, `positions[]` with `as_of_date`, `ledger_entries[]`, `instruments[]`, `cash_balances[]`, `statement_totals`), NOT `PortfolioOverview` (the story text's loose paraphrase). It is what `runImportedDiagnosticsEngine`/`runImportedDashboardHistory` (`portfolioAnalysisAdapter.ts:155-205`) POST to `/api/engines/diagnostics/run-imported` and `/api/engines/dashboard-history/run-imported` to reconstruct synthetic history — `ledger_entries` and per-position `as_of_date` are load-bearing for that reconstruction, so a lossy/partial combine would produce wrong historical numbers, not just a cosmetic gap. This is squarely a guardrail-1 (financial accuracy) surface, not a data-plumbing one.

**Reuse point: `combine_imported_snapshots` already exists and does exactly this.** `services/quant-engine/app/services/statement_importer.py:66-98` (plus its 8 helper functions, `:101-347`) already combines a `list[ImportedPortfolioSnapshot]` into one: per-account terminal positions/cash (latest-dated snapshot wins per account), concatenated+deduped statements and ledger entries, and correctly-compounded `statement_totals` (including geometric TWR compounding, not naive summing). It's used today by `import_statements` (`:55-63`) when a user uploads *multiple files in one analyze-upload request* — the same "combine two statements" problem, just currently only exercised when both statements arrive in one request. `_validate_compatible_snapshots` (`:130-133`) already raises `ValueError` on incompatible base currencies — this is an existing, ready-made hook for AC3's degradation case.

**Why not a pure client-side merge (the order's DoD assumed "client-side," flagging the deviation).** The two objects to combine here do NOT both arrive in one backend request — one is the *existing* node's already-persisted `ImportedSnapshot` (client-side IndexedDB state, possibly itself an already-combined chain result), the other is the *newly-uploaded* statement's fresh `ImportedSnapshot` from this analyze-upload response. Porting `combine_imported_snapshots`'s ~250 lines (NAV/TWR compounding, per-account terminal-position dedup, ledger-entry dedup-by-composite-key) to TypeScript would be a second, unaudited implementation of financial merge math — the exact "duplicated formula" pattern the architecture pack calls out as invisible to individual lanes and a BLOCKING finding at integration. A thin backend endpoint that accepts the two already-parsed `ImportedSnapshot` JSON payloads and calls the existing, tested function directly avoids that: **zero new merge logic**, one new wrapper schema, one new route.

**Design: new backend endpoint, reusing `combine_imported_snapshots` verbatim.**
- `app/schemas/imports.py`: add `CombineImportedSnapshotsRequest(BaseModel): snapshots: list[ImportedPortfolioSnapshot]` (a pure wrapper — no new field types; `ImportedPortfolioSnapshot` is the existing schema already mirrored 1:1 as TS `ImportedSnapshot`).
- `app/api/routes/imports.py`: add `@router.post("/combine-snapshots", response_model=ImportedPortfolioSnapshot)` on the SAME `router` object (prefix `/portfolios/import`, already registered in `main.py:19` — no new `include_router` call needed). Body: `try: return combine_imported_snapshots(request.snapshots) except ValueError as exc: raise HTTPException(400, detail=str(exc))` — identical error-mapping pattern to `import_interactive_brokers_statement` (`imports.py:37-46`).
- `portfolioAnalysisAdapter.ts`: add `combineImportedSnapshots(snapshots: ImportedSnapshot[], apiUrlOptions?): Promise<ImportedSnapshot>`, POSTing `{ snapshots }` to `/api/portfolios/import/combine-snapshots`, mirroring `runImportedDiagnosticsEngine`'s exact fetch/error-check shape (`:155-163`, `:147-153` for the `!response.ok` → throw pattern).

**Client-side orchestration (still genuinely client-side — this is the part the story called "client-side recombination"): `App.tsx`'s `processImportedFiles`, `add_snapshot` branch (currently `:767-795`).**
```ts
const baseSource = getEffectiveNodeImportSource(baseNode, workspaceNodes, activeWorkspace)   // already computed, :780
const mergedHistoryContext = mergeHistoryContext(getNodeHistorySource(baseSource)?.historyContext ?? null, importedViews.historyContext)  // unchanged, :781
const baseImportedHistorySnapshot = canUseImportedReplay(baseSource) ? baseSource.historySource.importedHistorySnapshot : null
let combinedHistorySnapshot: ImportedSnapshot | null = nextAnalysis.snapshot   // no prior replay data → adopt the new statement's own snapshot alone (still strictly better than today's `null`, and honest: there is nothing to combine)
if (baseImportedHistorySnapshot) {
  try {
    combinedHistorySnapshot = await combineImportedSnapshots([baseImportedHistorySnapshot, nextAnalysis.snapshot])
  } catch {
    combinedHistorySnapshot = null
    setImportError('Added statement could not be combined with the existing imported history (for example, a differing base currency) — this snapshot keeps the merged positions but not full replay history.')
  }
}
```
then pass `importedHistorySnapshot: combinedHistorySnapshot` into the EXISTING `saveImportedSnapshotNode(...)` call (`:783-792`) in place of today's literal `null` at `:789`. **No other file changes.** `workspaceTypes.ts`'s `ImportedHistorySource` 3-way union, `historySource.ts`'s `buildImportedHistorySource`, and `saveImportedSnapshotNode` (`portfolioWorkspaceStorage.ts:301-326`) already fully support this — `saveImportedSnapshotNode` already threads `importedHistorySnapshot` straight through to `buildImportedHistorySource`, which already produces `kind: 'imported_replay'` on non-null and `kind: 'none'` on null. The story's own framing assumed this union "needs reconciling" (US-40.2's Context section) — it does not; that was the one piece of good news this design pass found.

**AC3 disclosure channel: reuse, don't add.** `setImportError(...)` before `await restoreImportedWorkspaceFromPersistedState(...)` is not clobbered — confirmed by reading `applyDashboardSession` (`App.tsx:328-334`): it calls `setAnalysis`/`setExposureAnalysis`/`setExposureFactorModel`/`setLastImportedFileNames`/`setRestoredSession` only, never `setImportError`. `dashboardSession.importError` (rendered by `DashboardPanel` as `<p className="error">`, `App.tsx:858` + `DashboardPanel.tsx:155`) reads the live `importError` state directly every render (`App.tsx:324`), so the message set above survives the subsequent restore call and renders. No new prop, no new component.

**Sequential-add-chain correctness (test plan's 4th bullet).** Each `add_snapshot` node's `importedHistorySnapshot` is already the FULLY combined snapshot of every prior statement in the chain (not just the immediate parent), because `combine_imported_snapshots` is given `[baseImportedHistorySnapshot, newSnapshot]` where `baseImportedHistorySnapshot` is itself already the accumulated result of the previous step, and `_collect_statements` (`statement_importer.py:117-127`) reads each input's full `.statements` list, not just its terminal state. If an earlier link in the chain degraded (AC3 fired, that node has `kind: 'history_context'`, no `importedHistorySnapshot`), the next add_snapshot correctly falls through to "adopt the new statement's own snapshot alone" (the `baseImportedHistorySnapshot` branch above is `null` via `canUseImportedReplay`) — this is intentional, not a gap: the prior degradation was already disclosed at the point it happened, and fabricating a merge with data that's no longer available would violate AC3's own no-fabrication clause.

**Ticket split (T-40.2.2 becomes two lanes — the story named one, this design needs two):**
- **T-40.2.2a (backend-engineer):** `app/schemas/imports.py` (new request schema) + `app/api/routes/imports.py` (new route) per above. Verification: `cd services/quant-engine && pytest`.
- **T-40.2.2b (frontend-engineer):** `portfolioAnalysisAdapter.ts` (new adapter fn) + `App.tsx`'s `add_snapshot` branch, per above. Depends on 40.2.2a's route existing (or a mocked fetch in the interim — frontend-engineer's call). Verification: `cd apps/desktop && npx vitest run && npx tsc --noEmit`.

**T-40.2.3 (test-engineer) gains a backend slice.** In addition to the story's own frontend test plan (add_snapshot preserves history; replace-mode regression; degraded-combination case; sequential-add-chain regression — all still apply verbatim against this design), add one backend test for the new route: 2-snapshot combine happy path returns `combine_imported_snapshots`'s own result (thin wrapper — the merge logic itself is already covered by `statement_importer.py`'s existing tests, not re-tested here), and the incompatible-currency case returns HTTP 400 with the `ValueError`'s message.

**Contract/schema answer for the order's DoD.** US-40.1: confirmed no schema change (quant research's finding holds). **US-40.2: a schema change IS needed** — one new request schema, one new route — which is the one place this plan disagrees with the order's "client-side" framing; see risks for the explicit flag.

**Traces to:** AC1 (T-40.2.2a/b), AC2 (T-40.2.2a/b), AC3 (T-40.2.2b's catch branch + disclosure), AC4 (unchanged replace branch — verified by reading `:797-802`, untouched by this design).

## Lane sequence

1. **T-40.1.1** (backend-engineer doc edit, parallel-safe with everything else) + **T-40.1.3** (backend-engineer, `frozen_market_data.py` only — no file overlap with T-40.1.1).
2. **T-40.1.2** (frontend-engineer, `variantLabels.ts`) — independent of 1, can run in parallel.
3. **T-40.2.2a** (backend-engineer, new schema+route) before **T-40.2.2b** (frontend-engineer, `App.tsx` + adapter) — 2b's `combineImportedSnapshots` call needs 2a's route to exist for real (or an explicit mock, frontend-engineer's call if run out of order).
4. **T-40.1.4** and **T-40.2.3** (test-engineer) after their respective implementation lanes land — both can be one lane doing both stories' tests, or two separate dispatches; no file overlap between them.
5. Close-out (docs-engineer, out of this order's scope): tech-debt-register.md entries for the dead `market_data` param (T-40.1.3) and the duplication finding; the new combine-snapshots route's contract-doc entry (US-40.2).

Every lane's own close-out gate is `python scripts/run_all_tests.py`; no agent commits.
