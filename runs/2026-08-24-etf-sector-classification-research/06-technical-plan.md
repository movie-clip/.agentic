REPORT 2026-08-24-etf-sector-classification-research/06
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order named verification: NONE (design/planning artifact; read-only order, no code touched)

contract_notes:
  - schemas/instruments.py — ClassificationSource gains a new literal "fmp_etf_sector_weighting_confirmed"; backend-internal only — see § Contract
  - docs/contracts/exposure-fields.md:225-226's provenance prose needs the new literal name added — no new table row (still backend-internal)

pack_corrections:
  - none

handoff:
  - see § Orchestrator brief below for the lane-routable index

risks:
  - `weightPercentage`'s raw JSON type (float vs. "NN.NN%" string) wasn't captured verbatim in the research log — § T-39.1.4's `_coerce_weight` defends both shapes, verify at build time
  - two EXISTING tests in test_instrument_registry.py pin the exact defect this story removes — see § T-39.1.6, easy to miss if only the story's own test-plan bullets are read

## Orchestrator brief
- Contract: one new `ClassificationSource` literal `"fmp_etf_sector_weighting_confirmed"` (schemas/instruments.py) — see § Contract.
- Reuse: `equity_sector_resolution.py` is the STRUCTURAL template (single `get_company_profile` call, no manual candidate loop) — see § Reuse. `resolve_etf_sector` is a new, separate function/module.
- registry.py:246-292's `sector = "Broad Market"` default (line 247) and every keyword `sector = ...` assignment in the elif chain (252-281) are DELETED; `category` assignments in that SAME chain are untouched byte-for-byte — see § registry.py wiring.
- Two EXISTING tests (`test_enriched_etf_description_round_trips_to_broad_market_sector`, `test_etf_branch_ignores_market_data_and_makes_no_fmp_call`) pin the pre-fix behavior and MUST be rewritten, not just supplemented — see § T-39.1.6.
- Lane order: T-39.1.1 (schema) → T-39.1.2 (symbols.py) + T-39.1.3 (fmp.py/market_data.py) in parallel → T-39.1.4 (resolution + registry wiring) → T-39.1.5 (docs) + T-39.1.6 (tests) in parallel, all backend-engineer except T-39.1.5/T-39.1.6 — see § Lane sequence.
- Sections below: § Contract · § Reuse · § T-39.1.2 SBIO rule · § T-39.1.3 FMP client method · § T-39.1.4 resolve_etf_sector · § registry.py wiring · § T-39.1.5 docs pointers · § T-39.1.6 test design (the two existing-test fixes) · § Lane sequence · § Decisions · § Risks

---

## § Contract

`services/quant-engine/app/schemas/instruments.py:22`, current:

```python
ClassificationSource = Literal["static", "fmp_identity_confirmed", "unavailable"]
```

New (T-39.1.1), final literal value confirmed as the research brief's proposal, no objection found in story/DoD:

```python
ClassificationSource = Literal["static", "fmp_identity_confirmed", "fmp_etf_sector_weighting_confirmed", "unavailable"]
```

Extend the docstring comment above it (lines 12-21) with one more bullet:
`"fmp_etf_sector_weighting_confirmed" = resolved via FMP's ETF sector-weightings endpoint for a direct-held ETF, accepted only because the statement ISIN and the FMP profile ISIN matched AND the top sector bucket's share of total weight cleared DOMINANCE_THRESHOLD. Deliberately distinct from "fmp_identity_confirmed": the equity tier resolves via a direct string mapping, this tier via a weight-vector dominance rule — collapsing them loses the traceability distinction guardrail 2 exists to preserve (US-39.1).`

No other schema change. `Instrument.sector` stays `str | None` (unchanged). No new field, no route/response-shape change — `classification_source` is already backend-internal, not serialized to the client (confirmed at `docs/contracts/exposure-fields.md:222-236`, same note as the equity tier). `docs/contracts/exposure-fields.md:225-226`'s prose (not a table row) needs the new literal name added to its enumeration — a docs-engineer edit (T-39.1.5), not a contract-shape change.

## § Reuse

Named, not decorative:

- **Structural template**: `app/instruments/equity_sector_resolution.py`'s `resolve_equity_sector(imported, market_data)` — specifically its SHAPE: one `market_data.get_company_profile(imported.symbol)` call (not a manual per-candidate loop), a try/except around it, then the identity gate via `normalize_isin`. Do **not** copy the research brief's raw pseudocode literally — it manually loops `resolve_symbol_candidates(symbol, kind="quote")` and calls `get_company_profile(candidate)` per candidate. That is not how the equity branch actually works and duplicating it here would double-apply candidate resolution (see § Decisions #1 for why the single-call shape is correct and sufficient).
- **Taxonomy map**: import the existing public `SECTOR_TAXONOMY_MAP` from `equity_sector_resolution.py` (not a copy) and build a local `_NORMALIZED_...` casefold dict from it in the new module, using the exact same two-line idiom `equity_sector_resolution.py:62-64` already uses. Do not reach into `equity_sector_resolution.py`'s private `_NORMALIZED_SECTOR_TAXONOMY_MAP` (underscore-prefixed, module-private).
- **Identity primitive**: `app.services.instrument_identity.normalize_isin` — same import, same call shape as the equity branch. No second ISIN-comparison implementation.
- **Symbol resolution**: `app.core.symbols.resolve_symbol_candidates` / `canonicalize_symbol` — already used by every `MarketDataService` method; the new `get_etf_sector_weightings` method (T-39.1.3) reuses them the same way `get_company_profile` does, independently (§ T-39.1.3).
- **Import-cycle pattern**: `registry.py`'s existing LOCAL import of `resolve_equity_sector` inside `classify_imported_instrument` (registry.py:302-304) exists to break a real cycle (registry → equity_sector_resolution → instrument_identity → registry). The new `etf_sector_resolution.py` has the identical cycle (it also imports `instrument_identity`), so its import into `classify_imported_instrument` must be local too — copy the same comment.
- **Aggregation seam**: `analytics/overview.py`'s `instrument.sector or UNCLASSIFIED_SECTOR_LABEL` (already documented at `financial-methodology.md:1404-1424`) needs **no code change** — it already treats any `None` sector as `"Unclassified"`, regardless of which branch produced the `None`. AC11 is satisfied by `resolve_etf_sector` returning `None` on every failure path; nothing downstream needs to know it came from the ETF branch specifically.
- **Test fixture**: `app.tests.fixtures.FakeMarketData` — extend it (T-39.1.6), do not create a parallel fake class (§ T-39.1.6).

## § T-39.1.2 — SBIO `SymbolResolutionRule`

`services/quant-engine/app/core/symbols.py`, add to `DEFAULT_SYMBOL_RULES` (after the `CIBR` entry, `symbols.py:61`), following the exact `SEMI`/`CIBR` no-bare-candidate shape:

```python
# SBIO (statement: Invesco NASDAQ Biotech UCITS ETF, LSE, ISIN
# IE00BQ70R696) -> SBIO.L on FMP/Yahoo. Deliberately NO bare "SBIO"
# candidate: on FMP that symbol is a DIFFERENT US-listed security (ALPS
# Medical Breakthroughs ETF, isin US00162Q5936 -- confirmed live,
# 03-quant-research.md Live evidence log item 3). Same wrong-fund trap as
# SEMI/CIBR/DFND. No US proxy is defined -- none was requested by this
# story and none is needed for the identity gate to fail closed.
SymbolResolutionRule(canonical_symbol="SBIO", quote_candidates=("SBIO.L",), history_candidates=("SBIO.L",), holdings_candidates=("SBIO.L",), aliases=("SBIO.L",)),
```

No `proxy_candidates` — the story does not request a US-listed proxy fallback for SBIO (unlike SEMI/CIBR/DFND, which have one); omit it rather than inventing one, since an absent tuple already defaults to `()` per the dataclass.

Effect: `resolve_symbol_candidates("SBIO", kind="quote")` now returns `["SBIO.L"]` only (previously `["SBIO"]`, no rule existing). Both `MarketDataService.get_company_profile("SBIO")` and the new `get_etf_sector_weightings("SBIO")` (§ T-39.1.3) will each independently resolve only to `SBIO.L` — the bare, wrong-security candidate is never attempted in production once this rule exists. AC4's "identity gate rejects the wrong-security candidate" is therefore exercised at the **unit level** (a mocked `market_data` returning the wrong ISIN for a bare-symbol lookup, § T-39.1.6), not by observing production candidate-looping — see § Decisions #2.

## § T-39.1.3 — FMP sector-weightings client method

**`FmpClient`** (`services/quant-engine/app/clients/fmp.py`), new method placed after `get_profile` (fmp.py:349-350), same one-line `_get(...)` delegation shape:

```python
def get_etf_sector_weightings(self, symbol: str) -> list[dict[str, Any]]:
    return self._get(
        "etf-sector-weightings",
        "etf/sector-weightings",
        {"symbol": symbol},
        ttl_seconds=self.profile_ttl_seconds,
    )
```

- Path `"etf/sector-weightings"` resolves against `self.base_url` (`https://financialmodelingprep.com/stable`, `settings.py:33`) → the live-verified, on-plan `/stable/etf/sector-weightings` endpoint (03-quant-research.md § Live evidence log item 2, HTTP 200, not 402/404).
- New cache namespace `"etf-sector-weightings"` (distinct from `"profile"`), reusing `profile_ttl_seconds` (30 days) — fund sector composition changes on the same multi-week/month cadence as a company profile's sector field, same reasoning `financial-methodology.md:1436-1448` already records for `get_company_profile`.
- No bespoke error handling inside this method — `_get`'s existing 401/404/402/403/stale-cache/negative-cache machinery applies unchanged, same as every other `_get`-backed method on this client.

**`MarketDataService`** (`services/quant-engine/app/services/market_data.py`), new method placed immediately after `get_company_profile` (market_data.py:503-523), same candidate-loop shape:

```python
def get_etf_sector_weightings(self, symbol: str, symbol_overrides: dict[str, list[str]] | None = None) -> list[dict]:
    requested_symbol = canonicalize_symbol(symbol)
    for candidate in resolve_symbol_candidates(requested_symbol, symbol_overrides, kind="quote"):
        was_cached = self._will_be_served_from_cache(
            "etf-sector-weightings", "etf/sector-weightings", {"symbol": candidate}, self.client.profile_ttl_seconds
        )
        try:
            rows = self.client.get_etf_sector_weightings(candidate)
        except MarketDataAuthError:
            raise
        except Exception:  # noqa: BLE001
            continue
        if rows:
            self.last_fetch_meta[requested_symbol] = {"type": "etf-sector-weightings", "resolved_symbol": candidate, "cached": was_cached}
            return rows
    return []
```

Returns a plain `list[dict]` (empty list, not `None`, when no candidate has coverage) — matches `get_company_profile`'s pattern of "no tuple, just the payload" rather than `get_etf_holdings`' `(resolved_symbol, rows)` tuple shape, because nothing downstream needs the resolved symbol back out (unlike `get_etf_holdings`, which needs it for `holdings_history.record_snapshot`).

## § T-39.1.4 — `resolve_etf_sector` resolution logic

New module: `services/quant-engine/app/instruments/etf_sector_resolution.py`, mirroring `equity_sector_resolution.py`'s file shape (module docstring, taxonomy import, one public function).

```python
"""Identity-gated FMP sector-weighting resolution for direct-held ETFs
outside the static registry (US-39.1, T-39.1.4).

Resolution order for a direct-held ETF classify_imported_instrument's ETF
branch does not already resolve via INSTRUMENT_DEFINITIONS: identity-gate
the security (statement ISIN vs. FMP company-profile ISIN, same mechanism
as the equity branch), then read a DIFFERENT FMP field for the theme
(etf/sector-weightings' dominant sector bucket, not the profile's own
`sector` field -- confirmed unreliable for ETFs, 03-quant-research.md
Live evidence log item 1). A dynamically-resolved sector is accepted only
when the top bucket's share of total reported weight clears
DOMINANCE_THRESHOLD. Every other outcome -- lookup failure, no/empty
profile, ISIN mismatch or missing evidence, empty/zero-weight response,
below-threshold top share, an unmapped sector bucket -- resolves to no
classification (None, "unavailable"). Never a fallback guess, and
specifically never "Broad Market" (see registry.py's ETF branch, where
that literal used to be the unconditional default).

Truth class: snapshot analytics, mirroring the equity dynamic tier -- never
"verified" (guardrail 3).

Identity gate reuses instrument_identity.normalize_isin, same as
equity_sector_resolution.py -- no second, divergent ISIN-comparison
implementation.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from app.instruments.equity_sector_resolution import SECTOR_TAXONOMY_MAP
from app.schemas.imports import ImportedInstrument
from app.schemas.instruments import ClassificationSource
from app.services.instrument_identity import normalize_isin

if TYPE_CHECKING:
    from app.services.market_data import MarketDataService

# Human-confirmed 2026-08-24 -- see docs/product/stories/US-39.1-.../ Context
# "DOMINANCE_THRESHOLD = 55% -- resolved" for the evidence table. A fraction,
# not a percentage -- scale-invariant against whether FMP's raw weights are
# reported on a 0-100 or 0-1 basis, since only the RATIO top/total is used.
DOMINANCE_THRESHOLD = 0.55

_NORMALIZED_ETF_SECTOR_TAXONOMY_MAP: dict[str, str] = {
    key.strip().casefold(): value for key, value in SECTOR_TAXONOMY_MAP.items()
}


def _coerce_weight(value: object) -> float | None:
    """Defensive numeric coercion for one sector-weightings row's weight
    field. Live evidence (03-quant-research.md) rendered values as plain
    numbers (e.g. 37.4); this endpoint's raw JSON type was not captured
    verbatim, and FMP's legacy v3 surface is known to return a percentage
    as a "NN.NN%" string on some routes -- both shapes are handled here so
    a format difference degrades to "excluded from this weight vector"
    rather than crashing the import. None/non-numeric -> None."""
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip().rstrip("%")
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number


def resolve_etf_sector(
    imported: ImportedInstrument,
    market_data: "MarketDataService",
) -> tuple[str | None, ClassificationSource]:
    """Resolve one direct-held ETF's sector via FMP's sector-weightings
    endpoint, gated by ISIN identity match and a dominance-threshold
    aggregation over the reported weight vector.

    Returns (mapped_sector, "fmp_etf_sector_weighting_confirmed") only when
    ALL of: the statement ISIN and FMP profile ISIN are present and equal
    (AC3/AC4/AC5); the sector-weightings response is non-empty with a
    positive total weight (AC9); the top bucket's share of total weight is
    >= DOMINANCE_THRESHOLD (AC6/AC7); and the top bucket's sector string is
    present in SECTOR_TAXONOMY_MAP (AC8). Returns (None, "unavailable") for
    every other outcome, including any lookup exception (AC10).
    """
    try:
        profile = market_data.get_company_profile(imported.symbol)
    except Exception:  # noqa: BLE001 -- mirrors resolve_equity_sector's fail-safe pattern; AC10
        return None, "unavailable"

    if not profile or not profile.get("isin"):
        return None, "unavailable"

    statement_isin = normalize_isin(imported.isin)
    profile_isin = normalize_isin(profile.get("isin"))
    if not statement_isin or not profile_isin or statement_isin != profile_isin:
        return None, "unavailable"  # mismatch (AC4) or no evidence either side (AC5) -- collapsed, same as US-37.1

    try:
        weights = market_data.get_etf_sector_weightings(imported.symbol)
    except Exception:  # noqa: BLE001 -- AC10
        return None, "unavailable"

    if not weights:
        return None, "unavailable"  # AC9: empty response

    weighted_rows = [
        (row.get("sector"), _coerce_weight(row.get("weightPercentage")))
        for row in weights
        if isinstance(row, dict)
    ]
    usable_rows = [(sector, weight) for sector, weight in weighted_rows if weight is not None]
    total = sum(weight for _, weight in usable_rows)
    if total <= 0 or not usable_rows:
        return None, "unavailable"  # AC9: zero/degenerate total weight

    top_sector, top_weight = max(usable_rows, key=lambda row: row[1])
    top_share = top_weight / total
    if top_share < DOMINANCE_THRESHOLD:
        return None, "unavailable"  # AC6/AC7: genuinely diversified/mixed-theme -- never "Broad Market"

    if not top_sector:
        return None, "unavailable"

    mapped_sector = _NORMALIZED_ETF_SECTOR_TAXONOMY_MAP.get(top_sector.strip().casefold())
    if mapped_sector is None:
        return None, "unavailable"  # AC8: unmapped bucket, e.g. "Cash & Others" -- never passed through raw

    return mapped_sector, "fmp_etf_sector_weighting_confirmed"
```

Every edge case in the DoD maps to a concrete `return` above: no ISIN (either side) → the `statement_isin`/`profile_isin` guard; empty weights response → `if not weights`; zero-sum weights → `total <= 0`; below-threshold → `top_share < DOMINANCE_THRESHOLD`; unmapped bucket → `mapped_sector is None`; lookup exception → the two `except Exception` blocks. No branch returns a string that is not either a taxonomy-mapped sector or `None`.

## § registry.py wiring

`services/quant-engine/app/instruments/registry.py:246-292`, current ETF branch:

```python
        if instrument_type == "ETF" or listing_exchange == "LSEETF" or "UCITS" in description_upper or "ETF" in description_upper or "ETC" in description_upper:
            sector = "Broad Market"
            category = "ETF"

            if listing_exchange == "LSEETF" or "UCITS" in description_upper:
                category = "UCITS ETF"
            if "COMMOD" in description_upper or ...:
                sector = "Commodities"
                category = "Commodity UCITS ETF" if category == "UCITS ETF" else "Commodity ETF"
            elif ...   # (9 more elif branches, each sets BOTH sector AND category)

            return _instrument(
                f"imported-etf-{symbol.lower()}", symbol, description, "etf",
                sector, category, resolved_currency, exchange=imported.listing_exchange,
            )
```

Required edit — **remove every `sector = ...` statement from this block (the line-247 default AND all 9 elif-branch assignments), leave every `category = ...` statement byte-identical (same conditions, same strings, same order)**, then compute `sector` independently via the new opt-in dynamic gate, mirroring the equity branch's own shape immediately below it (registry.py:294-306):

```python
        if instrument_type == "ETF" or listing_exchange == "LSEETF" or "UCITS" in description_upper or "ETF" in description_upper or "ETC" in description_upper:
            category = "ETF"

            if listing_exchange == "LSEETF" or "UCITS" in description_upper:
                category = "UCITS ETF"
            if "COMMOD" in description_upper or "GOLD" in description_upper or "SILVER" in description_upper or "PRECIOUS" in description_upper:
                category = "Commodity UCITS ETF" if category == "UCITS ETF" else "Commodity ETF"
            elif "AEROSPACE" in description_upper or "DEF" in description_upper:
                category = "Thematic UCITS ETF" if category == "UCITS ETF" else "Thematic ETF"
            elif "INFORMATION TECHNOLOGY" in description_upper or "INFO TECH" in description_upper or " IT SECTOR" in description_upper:
                category = "Sector UCITS ETF" if category == "UCITS ETF" else "Sector ETF"
            elif "SEMIC" in description_upper or "SEMICONDUCT" in description_upper:
                category = "Thematic UCITS ETF" if category == "UCITS ETF" else "Thematic ETF"
            elif "FINANCIAL" in description_upper:
                category = "Sector UCITS ETF" if category == "UCITS ETF" else "Sector ETF"
            elif "HEALTH CARE" in description_upper or "HEALTHCARE" in description_upper:
                category = "Sector UCITS ETF" if category == "UCITS ETF" else "Sector ETF"
            elif "BIOTECH" in description_upper:
                category = "Sector UCITS ETF" if category == "UCITS ETF" else "Sector ETF"
            elif "TREAS" in description_upper or "TRBD" in description_upper or "BOND" in description_upper:
                category = "Bond UCITS ETF" if category == "UCITS ETF" else "Bond ETF"
            elif ("NASDAQ" in description_upper and "100" in description_upper) or "QQQ" in description_upper:
                category = "Thematic UCITS ETF" if category == "UCITS ETF" else "Thematic ETF"
            elif "S&P500" in description_upper or "S&P 500" in description_upper:
                category = "Broad Market UCITS ETF" if category == "UCITS ETF" else "Broad Market ETF"

            # ETF branch (US-39.1): opt-in FMP resolution, gated by `market_data`
            # being supplied -- same shape as the equity branch below. Without
            # it, no lookup is attempted and this ETF gets no classification.
            # The pre-US-39.1 "Broad Market" keyword-fallthrough default is
            # gone: it asserted a fund's *intent* (index-tracking) with no
            # evidence behind it.
            sector: str | None = None
            classification_source: ClassificationSource | None = None
            if market_data is not None:
                # Local import: breaks a real import cycle (registry ->
                # etf_sector_resolution -> instrument_identity -> registry).
                from app.instruments.etf_sector_resolution import resolve_etf_sector

                sector, classification_source = resolve_etf_sector(imported, market_data)

            return _instrument(
                f"imported-etf-{symbol.lower()}",
                symbol,
                description,
                "etf",
                sector,
                category,
                resolved_currency,
                exchange=imported.listing_exchange,
                classification_source=classification_source,
            )
```

Notes on this exact edit:
- `category`'s 10 branches (the initial default at the top plus the 9 `elif`s) are **unchanged in condition, order and string value** — only the interleaved `sector = ...` lines are deleted. This is what "category derivation stays completely untouched" means operationally: same behavior, same lines for `category`, but decoupled from `sector` because `sector` is no longer a byproduct of the same keyword match.
- `classification_source=classification_source` is a **new** keyword argument on this `_instrument(...)` call — the current ETF-branch call omits it entirely (defaults to `None` inside `_instrument`'s own signature). Passing it through is required for AC6/AC11 (a dynamically-resolved sector needs its provenance recorded, same as the equity branch).
- `classify_imported_instrument`'s function-level `market_data` parameter already exists (it is the equity branch's own parameter, `registry.py:237`) — the ETF branch is simply the second reader of the same parameter. No signature change to `classify_imported_instrument` itself.
- `attach_snapshot_metadata` (registry.py:320-371) needs **no change** — it already threads `market_data` through to every `classify_imported_instrument(...)` call site (lines 347, 351), and its static-registry short-circuit (line 338, `if instrument is not None`) already guarantees AC1 (a static hit never reaches this branch at all — see § Reuse).

## § T-39.1.5 — docs pointers (docs-engineer, not designed further here)

- `docs/finance/financial-methodology.md` — new `### Direct-held ETF branch classification (US-39.1)` subsection, placed after `### ETF look-through constituent classification (US-38.1)` (currently ends ~line 1519, "Contract rule" bullets below it). Update the top-of-section "Scope note" (lines 1266-1275) to name this new subsection as covering the direct-held ETF branch, alongside the equity-only and look-through-only scope notes already there. Mirror the equity section's structure: resolution-order code block, identity-gate rationale (can point back at "The identity gate, and why it is load-bearing" rather than re-deriving it), a sector-taxonomy note (reusing the SAME table, `equity_sector_resolution.py`'s `SECTOR_TAXONOMY_MAP` — no new table needed, cross-reference the existing one), and a `classification_source` bullet for the new literal (mirrors lines 1370-1402's shape). Draft prose already exists at `03-quant-research.md` § Methodology-doc section proposal — usable as a starting point, not applied verbatim (it predates the human-confirmed `DOMINANCE_THRESHOLD = 55%` and the final field-name decisions in this plan).
- `docs/contracts/exposure-fields.md:222-236` — add the new literal name to the enumeration prose (line 225-226's `"static"`, `"fmp_identity_confirmed"`, `"unavailable"`, or `None` list becomes four values, not three). No new table row (still backend-internal, same as today).
- `docs/tech-debt-register.md:186` — narrow the row the same way US-38.1 narrowed row 177: the keyword-classifier clause for the ETF branch is now resolved; the row's separate futures-reference-data clause (`tick_size`/`point_value`/`multiplier`) stays untouched, same row, same "acceptable" framing.
- `docs/product/current-product-state.md` — add the direct-held ETF branch's new resolution mechanism (currently undocumented per the delivery brief's "Already covered" finding).
- Epic/roadmap/story-index placement (Epic 39 creation, `epic-roadmap.md`) is explicitly out of this ticket's scope per the work order's non_goals — the human's/docs-engineer's close-out action, not named further here.

## § T-39.1.6 — test design

**New module** `services/quant-engine/app/tests/test_etf_sector_resolution.py`, mirroring `test_equity_sector_resolution.py`'s structure section-for-section (AC-labeled `# ──` banners, `_imported()` helper, `pytest.mark.parametrize` for the taxonomy-map regression). Needs a market_data fake exposing BOTH `get_company_profile` **and** `get_etf_sector_weightings` — extend `app.tests.fixtures.FakeMarketData` (do not add a second fake class):

```python
# In FakeMarketData.__init__, new params:
    sector_weightings: dict[str, list[dict]] | None = None,
    raise_for_weightings: set[str] | None = None,
# ...
    self.sector_weightings = sector_weightings or {}
    self.raise_for_weightings = raise_for_weightings or set()
    self.weightings_calls: list[str] = []

# New method, same recording/raise_for shape as get_company_profile:
    def get_etf_sector_weightings(self, symbol: str) -> list[dict[str, Any]]:
        self.weightings_calls.append(symbol)
        if symbol in self.raise_for_weightings:
            raise RuntimeError(f"FMP boom for {symbol}")
        return self.sector_weightings.get(symbol, [])
```

Required coverage (per the story's own test plan, each maps to a concrete assertion against `resolve_etf_sector`): static fast path is out-of-scope here (covered in test_instrument_registry.py, below); identity-match + above-threshold success; **SBIO-collision-prevented, standalone** — mock `get_company_profile("SBIO")` returning the wrong ISIN (`US00162Q5936`, live-verified value) against a statement ISIN of `IE00BQ70R696`, assert `(None, "unavailable")` and that `get_etf_sector_weightings` was never called (the weights fetch must not happen before identity clears); ISIN mismatch (generic); no-ISIN-evidence (both sides, parametrized like the equity module's `test_missing_isin_evidence_either_side_yields_no_classification`); dominance-threshold pass at exactly 55% and just above; dominance-threshold fail just below 55% (assert the result is `"unavailable"`, not `"Broad Market"` — an explicit `!=` assertion, mirroring `test_unmapped_fmp_sector_string_never_passed_through_raw`'s `assert sector != "..."` pattern); unmapped bucket (e.g. `"Cash & Others"`); empty weights list; zero-total-weight (all rows weight `0`); lookup exception on `get_company_profile`; lookup exception on `get_etf_sector_weightings` (a **second, distinct** exception case the equity module doesn't need, since the equity branch has no second network call).

**`test_instrument_registry.py` — two EXISTING tests must be rewritten, not left alongside new ones:**

1. `test_enriched_etf_description_round_trips_to_broad_market_sector` (lines 114-136). It calls `classify_imported_instrument(enriched)` with **no** `market_data` argument and asserts `sector == "Broad Market"`. Under the new logic, no `market_data` means the dynamic gate is never entered (`market_data is not None` is `False`), so `sector` stays `None` — the same "no lookup attempted" outcome the equity branch already has for this case. Rewrite the assertion to `classified.sector is None` and `classified.classification_source is None`; `category` stays `"ETF"` unchanged (no keyword matched, category's own default is untouched). Rename the test (it no longer "round trips to Broad Market") and update its docstring — it was pinning US-14.3's now-removed default.
2. `test_etf_branch_ignores_market_data_and_makes_no_fmp_call` (lines 182-195). Its entire premise — "the ETF branch ignores market_data entirely" — is exactly what this story reverses. With `market_data` supplied and `_SpyMarketData()` configured with no responses (profile defaults to `None`), the new `resolve_etf_sector` **will** call `get_company_profile("ZZZ2")`, get `None` back, and resolve to `(None, "unavailable")`. Rewrite to assert: `market_data.calls == ["ZZZ2"]` (no longer `[]`), `classified.sector is None`, `classified.classification_source == "unavailable"`, and `classified.category == "Sector UCITS ETF"` unchanged (the `"FINANCIAL"` keyword branch still fires for category, independent of sector). Rename away from "ignores_market_data" — add a new, separate test alongside it for the case the old name described (a symbol with NO static registry hit and NO `market_data` supplied at all → `market_data` stays `None`-typed, dynamic gate never entered, `classification_source is None`) if that case isn't already covered by test 1's rewrite.

New wiring tests to add (mirroring `test_equity_branch_with_market_data_and_isin_match_resolves_fmp_sector` / `..._isin_mismatch_...`, registry.py:212-239), proving `classify_imported_instrument`'s ETF branch delegates to `resolve_etf_sector` — not re-testing the resolver's own logic: AC1 (a static-registry ETF symbol, e.g. `SPY`, never reaches `classify_imported_instrument` at all when routed through `attach_snapshot_metadata` — already implied by the existing `test_static_registry_equity_never_calls_fmp_even_when_market_data_supplied`-style test; add the ETF-symbol equivalent), AC2 (an uncurated ETF WITH `market_data` DOES attempt the dynamic lookup — the corrected test 2 above already proves this), one identity-match success case through the full registry wiring.

**`test_analytics.py`** (aggregation coverage, AC11) — add one case alongside the existing equity "Unclassified" tests (~lines 400-476, symbols `ZZZ9`/`GHOST1`): a direct-held ETF with no static-registry hit and either no `market_data` or a failed dynamic lookup, asserting it appears in `sector_allocation`/`sector_position_breakdown` under `UNCLASSIFIED_SECTOR_LABEL`, with its weight counted in the total — same pattern, ETF instead of equity input.

**Regression breadth**: run the full `SEMI`/`CIBR`/`DFND`-style parametrized symbol-rule tests if any exist in `test_symbols.py` or similar, to confirm the new `SBIO` rule doesn't collide with an existing key — check `symbols.py`'s `rule_index` build (it is keyed by `all_keys()`, i.e. canonical + aliases) for a duplicate `"SBIO"` or `"SBIO.L"` key before adding.

## § Lane sequence

Ordered per the story's own ticket order, confirmed correct — contracts before consumers, tests last:

1. **T-39.1.1** (backend-engineer) — schema literal. Unblocks everything else; trivial, no dependencies.
2. **T-39.1.2** (backend-engineer) and **T-39.1.3** (backend-engineer) — independent of each other (symbols.py vs. fmp.py/market_data.py, disjoint files), can be built in either order or combined into one backend work order. Both are prerequisites for T-39.1.4.
3. **T-39.1.4** (backend-engineer) — depends on T-39.1.1-3. New module + registry.py wiring, § T-39.1.4 and § registry.py wiring above.
4. **T-39.1.5** (docs-engineer) and **T-39.1.6** (test-engineer) — both depend on T-39.1.4 being real code to document/test against; independent of each other, dispatchable in parallel.

Given the small surface (three small, disjoint file edits before the one real logic module), T-39.1.1-3 are plausibly a single backend-engineer work order rather than three separate dispatches — that consolidation call belongs to the orchestrator, not this plan; the boundaries above are written so it can be split either way without ambiguity.

## § Decisions

Decisions made in this plan that an engineer must not re-derive independently:

1. **`resolve_etf_sector` makes ONE call to `get_company_profile(imported.symbol)`, not a manual per-candidate loop.** The research brief's raw pseudocode loops `resolve_symbol_candidates` manually — that duplicates candidate-resolution logic `get_company_profile` already owns and is inconsistent with how `resolve_equity_sector` actually works today. Mirror the equity branch's actual code, not the brief's pseudocode.
2. **AC4's "gate rejects the wrong candidate" is proven at the unit level (mocked market_data), not via production candidate-looping.** Once the T-39.1.2 rule exists, `get_company_profile("SBIO")` only ever tries `SBIO.L` in production — the bare-ticker wrong-security candidate is structurally unreachable, not merely gated. The identity-gate mechanism is still exercised (generically, same as any ISIN mismatch) with SBIO's real recorded ISINs as the test's specific values.
3. **`ClassificationSource` literal is `"fmp_etf_sector_weighting_confirmed"`**, verbatim, per the research brief's proposal — no objection surfaced in the story or this review.
4. **`DOMINANCE_THRESHOLD = 0.55`** (a fraction), defined once in the new `etf_sector_resolution.py` module — not duplicated, not read from settings/config (mirrors how the equity branch's own constants are plain module-level values, not configuration).
5. **`get_etf_sector_weightings` returns a plain list, not a `(resolved_symbol, rows)` tuple** — nothing downstream needs the resolved symbol back out, unlike `get_etf_holdings`.
6. **`category` derivation is edited only to remove the interleaved `sector = ...` lines** — every `category = ...` line, condition and string value in the existing elif chain is unchanged. See § registry.py wiring for the literal before/after.
7. **The two existing tests that pin the pre-fix behavior are rewritten, not left as false regressions.** See § T-39.1.6.

## § Risks

- `_coerce_weight`'s string-vs-numeric defense in § T-39.1.4 is written against the research brief's rendered evidence, not a raw JSON dump — flagged already in this report's own `risks` section above; backend-engineer should confirm the real shape at implementation time (this project's test suite is network-free, so this is a one-off manual check, not something a regression test can pin either way without a live call).
- `category`'s decoupling from `sector` in registry.py (§ registry.py wiring) is a real code edit, not a no-op — although every string and condition is preserved, review should diff the two functions carefully rather than trusting "category is untouched" as a description of the diff; it means untouched in *value*, not that the file region is unedited.
