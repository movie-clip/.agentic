REPORT 2026-08-21-dynamic-sector-classification/05
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only design pass; no code changed

contract_notes:
  - Instrument gains classification_source: Literal["static","fmp_identity_confirmed","unavailable"] | None — schema owner is T-37.1.1, see § Contract
  - Instrument is backend-internal (never serialized to the client) — no TS mirror or exposure-fields.md row needed for classification_source itself, see § Contract
  - PortfolioOverview.sector_allocation / sector_position_breakdown gain a new valid string value "Unclassified" — no type change, TS types.ts unchanged, see § Contract
  - docs/contracts/exposure-fields.md sector rows (top_sectors, sector_hhi, sector_allocation) need a note documenting the new "Unclassified" bucket — T-37.1.3
  - docs/finance/financial-methodology.md needs a new "Sector/Industry Classification — Source and Resolution" section — T-37.1.3

pack_corrections:
  - none

handoff:
  - Full contract, reuse map, lane split and settled decisions are in the body below — see § Contract, § Reuse, § Lanes, § Decisions, § Risks
  - T-37.1.1 must promote instrument_identity._normalized_isin to a public normalize_isin — see § Reuse
  - T-37.1.4 must add an autouse conftest fixture mocking app.analytics.overview.MarketDataService, mirroring the existing per-engine pattern — see § Risks (test isolation)
  - No frontend ticket — confirmed after reading ExposurePanel.tsx, see § Frontend confirmation

risks:
  - overview.py:50's dead get_sector() fallback branch is left unchanged (still returns literal "Other") for the "no instrument object at all" case — see § Decisions (nullability wiring)
  - ISIN-mismatch and no-coverage collapse to the same classification_source="unavailable" — internal distinction only survives in code comments/logs, see § Decisions (open decision 3)
  - Widening the profile cache TTL to 30 days makes a transient empty FMP response equally sticky for 30 days — see § Decisions (open decision 4)
  - Whether docs/IB2026.csv's INTU/PANW/VICI/SPCX are open positions in the committed dashboardGoldens.ts snapshot as of today is unconfirmed — see § Risks (goldens)

## Orchestrator brief

- Decision: classification_source lives on `Instrument` only (backend-internal, never serialized) — no TS type change, no frontend ticket. See § Contract, § Frontend confirmation.
- Decision: `sector=None` stays honestly nullable at `Instrument`/domain level; converted to a non-null `"Unclassified"` sentinel string exactly at the `overview.py` aggregation seam, because `sector_allocation`/`sector_position_breakdown` are string-keyed dicts that cannot carry `None`. See § Contract.
- Decision: FMP dependency is opt-in via a keyword-only `market_data` param threaded through `attach_snapshot_metadata` → `classify_imported_instrument`, defaulting to `None` (no FMP attempt) — this keeps risk.py's two unrelated callers (which only read `.asset_class`, never `.sector`) at zero added I/O. Only `overview.py` opts in. See § Contract, § Reuse.
- Decision: ISIN-mismatch and no-coverage both resolve to `classification_source="unavailable"` (collapsed, per DoD's allowed pragmatic choice) — see § Decisions #3.
- Decision: widen `get_profile()`'s cache TTL to a new dedicated 30-day setting (`fmp_profile_cache_ttl_seconds`) instead of a persisted record for v1 — see § Decisions #4.
- New module: `app/instruments/equity_sector_resolution.py` (taxonomy map + `resolve_equity_sector`) — see § Reuse, § Resolution logic.
- Lane split unchanged from the story: T-37.1.1, T-37.1.2 → backend-engineer (sequential); T-37.1.3 → docs-engineer; T-37.1.4 → test-engineer. No frontend lane. See § Lanes.
- Sections below, in order: Contract; Reuse; Resolution logic (pseudocode); Lanes; Decisions (all 4 open decisions settled); Frontend confirmation; Risks.
- Nothing here blocks dispatch. No AC conflicts with this repo's guardrails or existing code found.

---

## Contract

Field-by-field, backend → frontend.

### `Instrument` (backend-internal domain model, `app/schemas/instruments.py`) — NOT serialized to the client

| Field | Type (new) | Nullability | Notes |
|---|---|---|---|
| `sector` (existing) | `str \| None` (declaration unchanged) | genuinely nullable now | equity branch of `classify_imported_instrument` returns `None`, not `"Other"`, when nothing resolves it |
| `classification_source` (new) | `Literal["static", "fmp_identity_confirmed", "unavailable"] \| None` | nullable | `None` = this story's resolution mechanism was not invoked on this instrument (static-dict hits via `get_instrument()` outside `attach_snapshot_metadata`'s merge branch, the ETF branch, futures, the no-imported-instrument catchall — all untouched, out of scope). Never `"verified"` — that word is reserved for `verified_total_return`'s narrower, distinct meaning (guardrail 3). |

`classification_source` is set in exactly two places, both touched by this story:
1. `_merge_known_instrument_metadata` (registry.py, static-dict-known hit during snapshot attach) → `"static"`.
2. `classify_imported_instrument`'s equity branch (registry.py, the code this story extends) → `"fmp_identity_confirmed"` or `"unavailable"`, only when a `market_data` instance was supplied.

Everywhere else (ETF branch, `attach_snapshot_metadata`'s no-imported-instrument catchall, futures/static entries reached via any OTHER path than the merge branch) leaves `classification_source=None` — this is a deliberate, minimal-blast-radius choice, not an oversight: don't fabricate a provenance claim about a code path this story didn't touch or verify.

`Instrument` never crosses the API boundary today (confirmed: no `Instrument`-shaped type in `apps/desktop/src/features/portfolio/types.ts`; `ExposureResult.snapshot.instruments` is the separate, unrelated `ImportedInstrument` — raw broker-parsed data, pre-classification). **No TS type change is required for `classification_source`.**

### `PortfolioOverview` (`app/schemas/reconciliation.py`) — IS serialized, reaches `ExposureResult`

`sector_allocation: list[dict[str, float | str]]` and `sector_position_breakdown: dict[str, list[dict[str, float | str]]]` — **type declarations unchanged.** The dict values stay `str`/`float`, never `None`. This is not a workaround; it is the correct seam: these structures are string-keyed aggregates that cannot represent `None`, and `ExposurePanel.tsx` already renders any string label generically (confirmed, see § Frontend confirmation). A new module-level constant in `overview.py`:

```python
UNCLASSIFIED_SECTOR_LABEL = "Unclassified"
```

is used as the bucket key/value wherever `Instrument.sector` resolves to `None` (or empty string, defensively) at the point `overview.py` builds `sector_totals`/`sector_position_breakdown`. It is a new, distinct, honestly-labeled bucket — never `"Other"`, never dropped from the weight total (see § Contract — aggregation wiring below). `ExposureCurrentStateConcentration.top_sectors` / `sector_hhi` / `top_sector_weight` (`exposure_engine.py`) need **zero code change**: they already iterate the *full* `overview.sector_allocation` list for concentration math (`exposure-fields.md` line 126's "computed over the full sector allocation set" invariant), so `"Unclassified"` automatically participates once `overview.py` emits it as a real bucket.

**TS types (`apps/desktop/src/features/portfolio/types.ts` lines 62-63, 1213-1228): unchanged.** `sector: string` already accepts a new literal value with no shape change.

### Aggregation wiring (`overview.py:46-51`, the exact fix)

Current (the bug):
```python
sector = instrument.sector if instrument and instrument.sector else instrument_registry.get_sector(position.symbol)
```
`instrument.sector` is currently always a truthy string (including `"Other"`), so the `else` branch is dead code today. Once the equity branch can return `None`, this ternary reactivates the `else` branch and calls `get_sector()`, which re-tries the *static-only* lookup and returns its own literal `"Other"` — silently re-coercing the exact case this story exists to fix.

New:
```python
if instrument is not None:
    sector = instrument.sector or UNCLASSIFIED_SECTOR_LABEL
else:
    sector = instrument_registry.get_sector(position.symbol)  # unchanged, defensive-only
```
`instrument` is populated for every position by `attach_snapshot_metadata` (confirmed by reading it in full — its final catch-all branch guarantees an entry even when no imported-instrument record exists), so the `else` branch is provably unreachable today and stays that way — it is **not** touched or repurposed, because `get_sector()` is a separate, independently-tested public method (`test_instrument_registry.py::test_unknown_symbol_falls_back_to_other` pins its own `"Other"` contract directly) and changing its contract is out of this story's scope. This is a named, accepted residual inconsistency — see § Risks.

## Reuse

Named specifically, per file:

- **`MarketDataService.get_company_profile(symbol)`** (`app/services/market_data.py:459`) — call this, never `FmpClient.get_profile()` directly. It already inherits `app/core/symbols.py`'s candidate-resolution machinery (proxy/suffix handling), which a second implementation would have to duplicate.
- **`instrument_identity.py`'s `_normalized_isin` helper (line 40-45)** — **promote it to public**: rename to `normalize_isin`, drop the leading underscore, update its 2 internal call sites in that module. Import it from the new resolution module. Reuse means importing this one function and the evidence-gating *principle* ("skip when either side lacks an ISIN; absent evidence is never a pass or a failure") — it does **not** mean calling `detect_instrument_identity_mismatches()` itself, which has a different shape (scans an entire snapshot's registry-known holdings for mismatches; this story needs a single-instrument comparison against an FMP profile's ISIN, not the registry's).
- **`instrument_enrichment.py`'s fail-safe pattern (`_enrich_one`, line 75-78)** — mirror its bare `try: ... except Exception: return instrument` shape exactly. This is a deliberate choice to swallow *everything* including `MarketDataAuthError` (which `get_company_profile()` itself re-raises for OTHER callers per US-35.1) — see § Decisions for why that divergence is intentional here.
- **`app/core/symbols.py`** — not called directly; reused transitively via `get_company_profile()`.
- **The existing conftest.py per-engine `MarketDataService` mock pattern** (`_mock_exposure_engine_market_data`, `_mock_dashboard_history_engine_market_data`, `_mock_diagnostics_engine_market_data`, `_mock_risk_engines_market_data`) — T-37.1.4 must add a matching `_mock_overview_engine_market_data` fixture patching `app.analytics.overview.MarketDataService`. Without it, `build_portfolio_overview`'s new internal `MarketDataService()` construction breaks the "network-free by design" test guarantee the moment a real `FMP_API_KEY` happens to be present in a dev's local `.env` (this environment has one).

## Resolution logic

New module: `services/quant-engine/app/instruments/equity_sector_resolution.py`.

```python
from app.schemas.instruments import ClassificationSource  # Literal["static","fmp_identity_confirmed","unavailable"]
from app.services.instrument_identity import normalize_isin  # promoted, see § Reuse

SECTOR_TAXONOMY_MAP: dict[str, str] = {
    "Technology": "Technology",
    "Energy": "Energy",
    "Industrials": "Industrials",
    "Real Estate": "Real Estate",
    "Utilities": "Utilities",
    "Communication Services": "Communication Services",
    "Healthcare": "Health Care",
    "Financial Services": "Financials",
    "Consumer Cyclical": "Consumer Discretionary",
    "Consumer Defensive": "Consumer Staples",
    "Basic Materials": "Materials",
}
# Source: 02-quant-research.md § Sector taxonomy normalization (live-verified, all 11 GICS-style sectors).

def resolve_equity_sector(
    imported: ImportedInstrument,
    market_data: MarketDataService,
) -> tuple[str | None, ClassificationSource]:
    try:
        profile = market_data.get_company_profile(imported.symbol)
    except Exception:  # noqa: BLE001 — mirrors instrument_enrichment.py's fail-safe pattern; AC8
        return None, "unavailable"

    if not profile or not profile.get("sector"):
        return None, "unavailable"

    mapped_sector = SECTOR_TAXONOMY_MAP.get(profile["sector"])
    if mapped_sector is None:
        return None, "unavailable"  # unmapped FMP sector string — never pass through raw, AC6

    statement_isin = normalize_isin(imported.isin)
    profile_isin = normalize_isin(profile.get("isin"))
    if statement_isin and profile_isin and statement_isin == profile_isin:
        return mapped_sector, "fmp_identity_confirmed"

    return None, "unavailable"  # mismatch (AC4) or no evidence either side (AC5) — collapsed, see § Decisions #3
```

`classify_imported_instrument`'s equity branch (registry.py:256-265) becomes:

```python
def classify_imported_instrument(
    self,
    imported: ImportedInstrument,
    currency: str | None = None,
    *,
    market_data: MarketDataService | None = None,
) -> Instrument:
    ...  # ETF branch unchanged, ignores market_data entirely
    sector, source = (
        resolve_equity_sector(imported, market_data) if market_data is not None else (None, None)
    )
    return _instrument(..., sector, "Equity", ..., classification_source=source)
```

`attach_snapshot_metadata` gains a matching keyword-only `market_data: MarketDataService | None = None`, threaded only into the equity-branch call sites (lines 289, 293). `_merge_known_instrument_metadata` (line 184-198) adds one line: `updates["classification_source"] = "static"`.

`overview.py::build_portfolio_overview(snapshot)` — **signature unchanged** (still just `snapshot`). Internally:
```python
from app.services.market_data import MarketDataService
...
market_data = MarketDataService()
metadata = instrument_registry.attach_snapshot_metadata(snapshot, market_data=market_data)
```
This mirrors `exposure_engine.py`'s existing `market_data = MarketDataService()` pattern and requires **no change to any caller of `build_portfolio_overview`** (`exposure_engine.py`, all 4 test call sites, `export_dashboard_goldens.py`). `risk.py`'s two `attach_snapshot_metadata(snapshot)` calls (lines 611, 1463) stay as-is — default `market_data=None` — zero new FMP calls there, confirmed both call sites only read `.asset_class` from the returned metadata, never `.sector`.

## Lanes

Ordered, per the story's own ticket split (unchanged):

1. **T-37.1.1 — backend-engineer.** `app/schemas/instruments.py` (add `ClassificationSource`, `classification_source` field), new `app/instruments/equity_sector_resolution.py`, `app/instruments/registry.py` (equity branch + `_merge_known_instrument_metadata` + signatures), `app/services/instrument_identity.py` (promote `normalize_isin`). Verification: `cd services/quant-engine && pytest app/tests/test_instrument_registry.py app/tests/test_instrument_identity.py -q`.
2. **T-37.1.2 — backend-engineer**, after T-37.1.1 lands. `app/analytics/overview.py` (aggregation fix + `UNCLASSIFIED_SECTOR_LABEL` + internal `MarketDataService()` construction), `app/core/settings.py` (`fmp_profile_cache_ttl_seconds`, default `2592000`), `app/clients/fmp.py` (`get_profile()` uses the new TTL instead of `quote_ttl_seconds`). Verification: `cd services/quant-engine && pytest app/tests/test_analytics.py app/tests/test_fmp_client.py -q`.
3. **T-37.1.3 — docs-engineer**, after T-37.1.1/T-37.1.2. New `financial-methodology.md` § "Sector/Industry Classification — Source and Resolution" (resolution order, taxonomy table, identity gate, `classification_source` semantics, explicit note that F-B/ETF look-through is untouched). `exposure-fields.md` sector rows: document the `"Unclassified"` bucket value and that `classification_source` is backend-internal (not currently serialized). No verification command (docs-only).
4. **T-37.1.4 — test-engineer**, can start once T-37.1.1's module signatures exist; full suite per the story's test plan, plus: the `_mock_overview_engine_market_data` conftest fixture (§ Reuse), the dedicated taxonomy-divergence regression test, and `statement_truths.py::IB_SECTOR_EXAMPLES` additions for INTU/PANW/VICI/SPCX **only if** they are open positions in the golden's snapshot (verify against the committed `docs/IB2026.csv` before adding — see § Risks). Verification: `python scripts/run_all_tests.py`.

No frontend lane — see § Frontend confirmation.

## Decisions

**1. Provenance field/enum naming.** `Instrument.classification_source: Literal["static", "fmp_identity_confirmed", "unavailable"] | None`. Not `"fmp_verified"` or any `*verified*` value — reserved for `verified_total_return`'s distinct meaning (guardrail 3). `"fmp_identity_confirmed"` names the actual mechanism (AC3's own language) rather than a generic confidence word.

**2. `sector` nullability wiring.** `Instrument.sector` becomes genuinely `None`-valued at the domain layer (registry.py's equity branch). It is converted to the non-null `"Unclassified"` string sentinel exactly once, at the `overview.py` aggregation seam, because the aggregate structures (`sector_allocation`, `sector_position_breakdown`) are string-keyed and cannot hold `None`, and because the frontend already renders any string label with zero special-casing. `overview.py:50`'s dead `get_sector()`-reCoercion path is neutralized by branching on `instrument is not None` rather than `instrument.sector` truthiness (full detail in § Contract). `get_sector()` itself is untouched — out of scope, independently pinned by its own test.

**3. ISIN-mismatch vs. no-coverage.** **Collapsed** to the same exposed outcome: `sector=None`, `classification_source="unavailable"`. Rationale: nothing downstream consumes a finer-grained `withheld` state today (confirmed — no field in this codebase's trust vocabulary distinguishes "checked and distrusted" from "never checked" for a categorical fact like sector), and inventing a 4th enum value nothing reads would itself be the kind of untraceable addition guardrail 1 warns against. The distinction is preserved in code structure only: `resolve_equity_sector`'s mismatch branch is a separate, explicitly-commented `return` statement (see § Resolution logic) distinct from the no-coverage/no-evidence branches, so a future story can split them without re-deriving the logic.

**4. Caching.** Pragmatic v1, not the persisted-record option: add `fmp_profile_cache_ttl_seconds: int = Field(default=2592000)` (30 days) to `Settings`, and change `FmpClient.get_profile()` (line 328-329) to use it instead of `self.quote_ttl_seconds`. `get_profile()` already writes to its own `"profile"` cache namespace (distinct from `"quote"`), so this is a ~4-line change with an existing, disk-backed (`JsonFileCache`) cache doing the work — no new persistence layer, no schema/table. Rejected the persisted-classification-record option for v1 because the DoD names it a "should," and the existing namespace-separated HTTP cache already closes both concrete risks the research brief named (redundant re-fetch waste; cross-run flip-flop from mid-session expiry) at a fraction of the implementation cost. A persisted, auditable classification record remains available as a clean follow-on story.

**Additional decision not in the story's 4 (a design-pass finding, not scope creep — required for T-37.1.1 to be buildable at all):** the FMP dependency is threaded through `classify_imported_instrument`/`attach_snapshot_metadata` as an **opt-in keyword-only `market_data` parameter**, defaulting to `None` (no attempt, `classification_source=None`). Without this, extending `classify_imported_instrument`'s equity branch unconditionally would also activate FMP calls from `risk.py`'s two unrelated `attach_snapshot_metadata` callers (`build_lookthrough_exposure`, `build_etf_overlap_pairs`), which only ever read `.asset_class` from the result and never `.sector` — adding real network latency to the Stress/Drawdown/VaR routes for a value nothing consumes there. Only `overview.py` opts in.

**Also settled: `MarketDataAuthError` handling.** `resolve_equity_sector`'s bare `except Exception` (mirroring `instrument_enrichment.py`) swallows `MarketDataAuthError` too, even though `get_company_profile()` deliberately re-raises it for other callers (US-35.1: "a configuration failure is not a fact about this symbol"). This is an intentional, named divergence: AC8's text is unconditional ("any reason... never blocks or crashes an import"), and the story explicitly mandates mirroring `instrument_enrichment.py`'s pattern, which already makes this same choice for the exact same import-time-enrichment class of call.

## Frontend confirmation

**No frontend ticket — confirmed, story's call stands.** Read `ExposurePanel.tsx` in full for the Top Sectors section (lines 297-314) and `types.ts` (lines 1213-1228, 62-63). Rendering is fully generic: `topSectors.map(item => ...)` renders `item.name` / `item.weight` / `item.market_value` for whatever strings the engine returns, with no special-casing for `"Other"` or any other literal anywhere in the component. A new `"Unclassified"` bucket label requires zero component code change and zero TS type change (both `sector_allocation` and `ExposureConcentrationItem.name` stay `string`). No trust badge is required by any AC — AC9 requires only that the bucket be disclosed under a distinct name and counted in the weight total, both satisfied purely on the backend (§ Contract).

## Risks

- **`overview.py:50`'s residual dead branch.** `get_sector()`'s own `"Other"` fallback stays reachable in theory when `metadata.get(position.symbol)` returns `None` — a case that, per a full read of `attach_snapshot_metadata`, cannot currently occur (every position gets an entry). Left as pre-existing, out-of-scope behavior; not hardened further by this story.
- **ISIN-mismatch/no-coverage collapse (Decision 3)** means a future "why is this Unclassified" debugging session has no field-level signal distinguishing "FMP has never heard of this symbol" from "FMP returned a different security's sector" — only code comments/logs. Acceptable per the DoD's own allowance, but worth the human knowing this is a real, if minor, traceability gap.
- **30-day profile cache TTL (Decision 4)** makes a transient empty/no-coverage FMP response (confirmed live during research: `ACOMO` returned `[]` on a previously-working symbol) sticky for up to 30 days before the next natural re-attempt. `manage_cache.py clear` remains the only forced-refresh path. If this proves painful in practice, the persisted-record option the research brief named is the clean fix.
- **Goldens.** `docs/IB2026.csv`-based dashboard goldens today show a `sector_allocation` bucket set with no `"Other"` entry and no `Real Estate`/`Industrials` buckets that would obviously correspond to VICI/SPCX — meaning either those symbols are closed (not open) positions as of the golden's as-of date, or they're absorbed into a bucket I didn't fully trace. T-37.1.4 must re-verify which of INTU/PANW/VICI/SPCX are actually open positions in the current golden snapshot before adding `statement_truths.py::IB_SECTOR_EXAMPLES` pins for them — do not assume the research brief's live-verification result (run against a possibly-different `docs/IB2026.csv` state) still matches.
- **Taxonomy map completeness beyond the 11 verified sectors.** The map covers exactly the 11 GICS-style sectors the research brief live-verified. Any 12th FMP sector string (new/renamed on FMP's side, or a sector this project's static registry has never held, e.g. a sector GICS reclassified since 2023) falls through to `"Unclassified"` correctly by construction (AC6), but is untested beyond the dedicated regression test's 5 pinned divergent pairs — genuinely hard to test further without live FMP access to discover new drift.
