REPORT 2026-08-24-etf-sector-classification-research/03
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order named verification: NONE (read-only RESEARCH order). Live FMP + yfinance calls made ad hoc via throwaway scripts, not a test command — full call list and raw responses in § Live evidence log.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - New FMP endpoint found: `/stable/etf/sector-weightings` (legacy `/api/v3/etf-sector-weightings/{symbol}`) — accurate, on-plan (HTTP 200), not `get_profile` — see § Central finding.
  - `fmp.py` needs a new client method (propose `get_etf_sector_weightings(symbol)`) — no existing method calls this endpoint — see § Recommendation.
  - SBIO needs a new `SymbolResolutionRule` in `app/core/symbols.py` (no bare "SBIO" candidate — it collides with a different US fund on FMP) — see § Live evidence log item 3.
  - Propose a new `ClassificationSource` literal (e.g. `"fmp_etf_sector_weighting_confirmed"`), distinct from `"fmp_identity_confirmed"` — see § Trust-class analysis.
  - Dominance-threshold design parameter (50-60% band) is data-backed but not finalized — tech-lead/story-author must set the exact number — see § Formulas.
  - `category` (Sector/Thematic/Broad Market/Bond/Commodity ETF) is NOT resolved by this data source and needs its own design decision — not answered by this brief — see § Open item: category.
  - Full methodology-doc section proposal (not applied) is in § Methodology-doc section proposal — mirrors the US-37.1/US-38.1 section shape.

risks:
  - Dominance threshold (proposed 50-60%) is a recommendation from 8 data points, not a formal calibration — flagged for tech-lead sign-off, not asserted as final.
  - FMP sector-weighting bucket strings (12 seen) spot-checked against the 11-entry SECTOR_TAXONOMY_MAP on this run's tickers only — fuller coverage audit is implementation-time work.
  - yfinance corroboration used `Ticker.funds_data.sector_weightings`, a less-stable yfinance surface than `Ticker.history` — re-verify it still exists at build time if this story is built.
  - `get_etf_holders`' 505-row SPY response was not itself re-verified against a second source — cited only to show it is structurally different from sector-weightings (constituents vs. aggregate).

## Orchestrator brief
- VERDICT: a reliable dynamic source EXISTS — not `get_profile` (confirmed unreliable, fresh evidence), but FMP's separate `/stable/etf/sector-weightings` endpoint, live-verified accurate on 8 tickers and on-plan.
- Central question answered: BOTH layers are real. Epic 37's identity-gate pattern is reusable AND required (SBIO ticker-collision proven live), but insufficient alone — the fix is identity-gate the SECURITY, then read a DIFFERENT FMP field (sector-weightings, not `sector`) for the THEME.
- Human's proposed shape (static curation first, dynamic FMP fallback second) is CONFIRMED WORKABLE — same 3-tier shape as Epic 37, swap which field tier 2 reads, add a dominance-threshold aggregation step.
- Second-provider corroboration obtained: yfinance's `funds_data.sector_weightings` independently matches FMP's numbers closely (satisfies pack's `anchor: second-provider` bar) — but yfinance cannot serve as the identity gate itself (no ISIN field).
- New open design parameter, not settled here: the dominant-sector threshold (data suggests 50-60%) and the separate `category` sub-classification.
- Sections below: Live evidence log · Central finding · Formulas, with edge cases · Trust-class analysis · Open item: `category` · Metrics inventory (one row per affected field) · Methodology-doc section proposal (draft — not applied) · Recommendation summary

## Live evidence log

All calls made live against this project's own FMP client/settings (`services/quant-engine/.env`'s `FMP_API_KEY`, 32-char key present) and the real yfinance package already in `requirements.txt`. No test suite was touched (`pytest.ini`'s `--disable-socket` does not apply here — these were standalone scripts, not pytest).

**1. `get_profile` / `/profile` — reproducing the Epic 37/38 "unreliable for ETFs" finding, fresh.**

Called `FmpClient.get_profile(symbol)` for SBIO, SPY, XLF, GRID, QQQ, ICLN:

| Symbol | `sector` | `industry` |
|---|---|---|
| SBIO | Financial Services | Asset Management |
| SPY | Financial Services | Asset Management |
| XLF | Financial Services | Asset Management |
| GRID | Financial Services | Asset Management - Global |
| QQQ | Financial Services | Asset Management |
| ICLN | Financial Services | Asset Management - Global |

Every one of 6 ETFs spanning biotech, broad-market, financial-sector, tech-thematic and clean-energy-thematic funds returns the identical `sector`/`industry` pair — this is FMP's fund-sponsor/vehicle classification (an ETF is an "asset management" product), not a thematic answer, for any ETF. This reproduces and extends the SPY/GRID finding cited in both PRDs' non-goals with fresh, broader evidence.

**2. Endpoint discovery — probing for an ETF-specific classification endpoint.**

Probed candidate paths (`httpx` direct calls, both `stable` and legacy `v3` bases) for SPY:

| Path | Status | Result |
|---|---|---|
| `stable/etf/info?symbol=SPY` | 200 | ETF metadata (name, description, isin, AUM, expense ratio, holdingsCount) — **no sector field** |
| `stable/etf-info?symbol=SPY` | 404 | does not exist |
| `stable/etf/sector-weightings?symbol=SPY` | **200** | **top-line sector-weighting breakdown — 12 buckets, thematically accurate** |
| `stable/etf-sector-weightings?symbol=SPY` | 404 | does not exist (hyphenated form is wrong) |
| `stable/etf/country-weightings?symbol=SPY` | 200 | country breakdown, not sector-relevant |
| `stable/etf/holdings?symbol=SPY` | 402 | **restricted on this plan** — individual constituent list not served on `stable` |
| `v3/etf-sector-weightings/SPY` | 200 | same data as the `stable` path, legacy form |
| `v3/etf-info?symbol=SPY` | 200 | empty `[]` — v3 form not populated |
| `v3/etf-country-weightings/SPY` | 200 | same country data |

`/stable/etf/sector-weightings` (or its legacy v3 twin `/api/v3/etf-sector-weightings/{symbol}`) is the endpoint the work order asked to find: distinct from `get_profile`, distinct from `get_etf_holders` (which returns 505 individual constituent rows for SPY — confirmed live, `NVDA` weight 7.979% as top holding — a different granularity entirely), and reachable on this project's current FMP plan (HTTP 200, not 402).

**3. Sector-weightings data quality, and the SBIO ticker-collision hazard — both confirmed live.**

`stable/etf/sector-weightings` top sectors, sorted by weight:

| Symbol | Top sectors (weight %) |
|---|---|
| SBIO | Healthcare 100 |
| SPY | Technology 37.4, Financial Services 12.24, Communication Services 9.91, Consumer Cyclical 9.57 |
| XLF | Financial Services 98.12, Technology 1.63, Industrials 0.24 |
| GRID | Industrials 58.37, Utilities 13.81, Technology 10.54, Basic Materials 8.58 |
| QQQ | Technology 60.27, Communication Services 11.99, Consumer Cyclical 10.29 |
| ICLN | Utilities 41.36, Energy 30.02, Industrials 22.39, Technology 2.83 |
| XLV | Healthcare 99.23, Technology 0.59, Cash & Others 0.18 |
| IBB | Healthcare 100 |

Every known-sector-pure fund (SBIO, XLF, XLV, IBB) resolves cleanly to its real theme. Broad and multi-theme funds (SPY, GRID, ICLN) show a genuinely spread distribution — correctly reflecting that they are not single-sector funds. Weights sum to ~100% per symbol (float noise only, e.g. a `1.42e-14` "Cash & Others" row). Nonexistent tickers (`ZZZZNOTREAL`) and non-ETF tickers (`AAPL`) both return `[]` cleanly (HTTP 200, empty body) — same fail-closed shape this codebase's `_get()` already handles everywhere else.

**But this SBIO 100%-Healthcare result is for the WRONG SECURITY.** `get_profile("SBIO")` returned `isin: "US00162Q5936"`, `companyName: "ALPS Medical Breakthroughs ETF"` — a US-listed fund. The statement's actual SBIO holding (`docs/IB2026.csv`, per `01-scout.md`) is `"INVESCO NASDAQ BIOTECH"`, `listing_exchange: LSEETF`, ISIN `IE00BQ70R696`. These are two different securities that happen to share a bare ticker — exactly the collision class `app/core/symbols.py`'s DFND/SEMI/CIBR comments already document and guard against (bare-ticker traps to a wrong US fund). SBIO currently has **no** `SymbolResolutionRule` in `symbols.py`.

Tried `SBIO.L` as the candidate instead: `get_profile("SBIO.L")` returns `isin: "IE00BQ70R696"`, `companyName: "Invesco NASDAQ Biotech UCITS ETF"`, `exchange: "LSE"` — an **exact ISIN match** to the statement. `stable/etf/sector-weightings?symbol=SBIO.L` returns the same `Healthcare 100` result — this time for the *correct* security, reached only through the identity-matched candidate, not the bare ticker. `get_profile("SBIO.L")`'s `sector` field is still `"Financial Services"` — confirming the unreliability is specific to that field, not to the candidate resolution.

This is direct, live proof that the identity-gate pattern (statement ISIN vs. FMP profile ISIN, requiring the correct exchange-suffixed candidate) is not optional here: without it, a coincidentally-plausible-looking sector answer (100% Healthcare, for a US biotech fund with a similar name) would have published silently for the wrong security. The two funds happen to agree on theme here by luck; nothing guarantees that in general — the same collision risk the DFND/SEMI/CIBR incidents already document for equities.

**4. Second-provider corroboration — yfinance's `funds_data.sector_weightings`.**

`yfinance` (already a dependency, `yfinance_client.py`) exposes `Ticker(symbol).funds_data.sector_weightings` (a dict of 11 GICS-style sector keys, fractional weights) and `Ticker(symbol).info["category"]` (a Morningstar-style fund category string). Called for SBIO, SPY, XLF, GRID:

| Symbol | Yahoo `funds_data.sector_weightings` (top) | Yahoo `info["category"]` |
|---|---|---|
| SBIO | healthcare: 1.0 (100%) | "Health" |
| SPY | technology: 0.374 (37.4%) — matches FMP to 3 decimals | "Large Blend" |
| XLF | financial_services: 0.9812 (98.12%) — matches FMP exactly | "Financial" |
| GRID | industrials: 0.6645 (66.45%), utilities: 0.1876, technology: 0.115 | "Infrastructure" |

SBIO, SPY and XLF match FMP's sector-weightings closely (SPY and XLF near-exact to 2-4 decimal places). GRID is directionally consistent (Industrials dominant, Utilities second, Technology third on both providers) but not numerically identical (Yahoo: 66.45/18.76/11.5 vs. FMP: 58.37/13.81/10.54) — plausibly different data vintage or underlying-holdings snapshot date between providers. This is a genuine `anchor: second-provider` corroboration per the quant capability pack's audit discipline (two independent vendors agreeing is stronger evidence than either alone), not `anchor: provider-self-consistent`.

Also confirmed `yf.Ticker("SBIO.L")` independently resolves to `longName: "Invesco NASDAQ Biotech UCITS ETF"` (matching the correct security) with `sector_weightings: {healthcare: 1.0}` — same correct answer as FMP's identity-matched candidate.

`Ticker.isin` for `SBIO.L` returned `"-"` (unpopulated) — **yfinance does not reliably expose ISIN**, so it cannot itself serve as the identity-gate mechanism. This explains, rather than merely restates, why `yfinance_client.py` today has no profile/identity method at all (§ pack note): even if one were added, it has no evidence to gate on. Yahoo can corroborate a sector answer FMP already produced; it cannot independently confirm the security's identity.

## Central finding

The delivery brief's Open Decision #2 asked the exact right question: is this "no identity evidence exists" (Epic 38's shape) or "the identified thing's data source lies" (a different problem)? The live evidence shows it is **neither alone — it is both, layered, and they require two separate fixes**:

1. **Identity absence/collision is real here too** (Epic 37's shape). SBIO's bare ticker resolves to a different security on FMP entirely. An identity gate (statement ISIN vs. FMP profile/etf-info ISIN, via the correctly-suffixed candidate) is required, exactly as it is for equities — confirmed live, not hypothetical.
2. **Data quality is also real, but narrower than the PRDs' non-goals framed it.** `get_profile`'s `sector` field lies for ETFs — confirmed on 6/6 fresh tickers. But that is a property of **that one field**, not of FMP as a provider. A different, adjacent FMP endpoint (`etf/sector-weightings`) reads real thematic composition correctly for the same securities, live-verified and corroborated by a second provider.

So identity-gating a wrong field would indeed accomplish nothing (the delivery brief's concern is valid against `get_profile` alone) — but identity-gating the **security**, then reading a **different, correct field** from that now-confirmed security, is a real fix. Both Epic 37/38 PRDs' non-goals are accurate as written (they only tested `get_profile`) and do not cover this endpoint — it was never investigated by either epic.

## Formulas, with edge cases

Proposed resolution order for the direct-held ETF branch (mirrors `equity_sector_resolution.py`'s shape):

```text
resolve_etf_sector(imported, market_data) -> (sector: str | None, classification_source):

  1. Static registry lookup (unchanged): if symbol is a curated
     INSTRUMENT_DEFINITIONS entry, return (curated_sector, "static").

  2. Identity-gated dynamic lookup, opt-in (market_data supplied):
     for candidate in resolve_symbol_candidates(symbol, kind="quote"):
         try:
             profile = market_data.get_company_profile(candidate)  # existing method
         except Exception:
             continue
         if not profile or not profile.get("isin"):
             continue
         if normalize_isin(imported.isin) != normalize_isin(profile["isin"]):
             continue                                    # wrong security, never proceed
         # identity confirmed for this candidate
         weights = market_data.get_etf_sector_weightings(candidate)  # NEW method
         if not weights:
             return (None, "unavailable")
         total = sum(row["weightPercentage"] for row in weights)
         if total <= 0:
             return (None, "unavailable")                # degenerate: no usable weights
         top = max(weights, key=lambda row: row["weightPercentage"])
         top_share = top["weightPercentage"] / total
         if top_share < DOMINANCE_THRESHOLD:              # e.g. 0.50-0.60 — see below
             return (None, "unavailable")                 # genuinely diversified/mixed-theme
         mapped = SECTOR_TAXONOMY_MAP.get(top["sector"].strip().casefold())
         if mapped is None:
             return (None, "unavailable")                 # unmapped bucket, e.g. "Cash & Others"
         return (mapped, "fmp_etf_sector_weighting_confirmed")   # NEW classification_source value
     return (None, "unavailable")                          # no candidate cleared the gate
  else:
     return (None, None)                                  # no lookup attempted, same as equity branch

  3. Nothing resolved -> instrument.sector = None -> "Unclassified" at the overview.py aggregation seam.
```

Edge cases, and why each is `None`/`"unavailable"` rather than a fallback value:

| Case | Correct behaviour | Why |
|---|---|---|
| No candidate's ISIN matches the statement's (ticker collision, e.g. bare "SBIO") | `unavailable` | Confirmed live — a plausible-looking sector for the wrong security is worse than no answer. |
| Statement has no ISIN captured (`imported.isin` is `None`) | `unavailable` | Same as equity AC5 — gate cannot clear without evidence on both sides. |
| `etf/sector-weightings` returns empty `[]` | `unavailable` | Confirmed live for a nonexistent/non-ETF symbol; also the shape for any ETF with no FMP sector-weighting coverage. |
| Sum of weights is zero | `unavailable` | Protects the `top_share` division; not observed live but must be handled defensively. |
| Top sector's share is below `DOMINANCE_THRESHOLD` (genuinely diversified fund) | `unavailable`, **never** `"Broad Market"` | See "Do not repeat the keyword matcher's mistake" below. |
| Top sector string not in `SECTOR_TAXONOMY_MAP` (e.g. `"Cash & Others"`) | `unavailable` | Mirrors the equity branch's existing rule — never pass an unmapped string through raw. |
| FMP lookup raises (network/plan error) | `unavailable` | Mirrors `resolve_equity_sector`'s `except Exception` -> `unavailable` (AC8). |

**Do not repeat the keyword matcher's mistake.** The current ETF branch's fallthrough default is `sector = "Broad Market"` (`registry.py:247-248`) when no keyword hits — the exact silently-wrong behaviour this epic exists to remove (`01-scout.md`, confirmed). A below-threshold dynamic result must **not** default to `"Broad Market"` either, even though it is tempting by analogy (SPY genuinely is diversified). `"Broad Market"` is a claim about a fund's *intent* (index-tracking, not sector-focused) that a weight vector alone cannot establish — GRID (58% Industrials, clearly a thematic infrastructure fund) and ICLN (41%/30%/22% across three sectors, clearly a thematic clean-energy fund) are both diversified in the same numeric sense as SPY but are not broad-market funds. Collapsing "below threshold" into `"Broad Market"` would mislabel exactly these. The honest answer below threshold is `unavailable` / `"Unclassified"`, matching this project's existing edge-case discipline (never resolve with a plausible fallback).

**`DOMINANCE_THRESHOLD` is a data-backed proposal, not a finalized number.** Evidence table:

| Symbol | Top-sector share | Should resolve to a single sector? |
|---|---|---|
| SBIO, XLV, IBB, XLF | 98-100% | Yes — unambiguous |
| QQQ | 60.3% | Yes — matches this fund's *existing* static curation (`"Technology"`, `INSTRUMENT_DEFINITIONS`), useful as a calibration anchor |
| GRID | 58.4% | Borderline |
| ICLN | 41.4% | No — should stay unresolved |
| SPY | 37.4% | No — should stay unresolved (also already statically curated as `"Broad Market"`, unaffected either way) |

A threshold in the **50-60%** band separates the unambiguous cases from SPY/ICLN cleanly and keeps QQQ's known-correct answer reachable if it were ever uncurated; GRID sits in the borderline zone and the exact cutoff decides it either way. Naming the precise number is a tech-lead/story-author design call informed by this table, not something this brief finalizes.

## Trust-class analysis

Per-field, following this project's `verified > degraded > withheld > unavailable` ladder and the four truth classes:

- **Truth class: snapshot analytics** — same class as the existing equity dynamic tier (`equity_sector_resolution.py`'s docstring: "a classification derived from current market data at snapshot/import time, not broker truth"). Never `verified` — that word is reserved elsewhere per the doc's existing guardrail-3 note.
- **`Instrument.sector` (str | None)** — nullable. `"static"` tier: always present when curated. Dynamic tier: present only when identity-gated AND above the dominance threshold; otherwise `None`, surfaced as `"Unclassified"` at the `overview.py` aggregation seam (existing mechanism, unchanged).
- **`Instrument.classification_source`** — propose a **new** literal, e.g. `"fmp_etf_sector_weighting_confirmed"`, added to the existing `Literal["static", "fmp_identity_confirmed", "unavailable"] | None`. Recommend against reusing `"fmp_identity_confirmed"` verbatim: that literal's own docstring defines it as "the FMP lookup resolved it... a direct sector string" — the ETF path resolves via a structurally different mechanism (a weight-vector dominance rule, not a direct string mapping), and collapsing two different formulas under one provenance label loses exactly the traceability distinction guardrail 2 (one metric, one code path) exists to preserve. This is a naming recommendation for tech-lead/story-author, not a mandate.
- **Backend-internal only**, matching the existing equity pattern — not currently serialized to the client (same as `"fmp_identity_confirmed"` today, per `schemas/instruments.py`'s comment and the exposure-fields contract doc).

## Open item: `category`

`classify_imported_instrument`'s current ETF branch sets both `sector` **and** `category` (e.g. `"Sector ETF"` vs `"Thematic ETF"` vs `"Bond ETF"`) from the same keyword match. `etf/sector-weightings` data answers "what sector" but does **not** answer "is this a sector fund, a thematic fund, or a bond/commodity fund" — that is a fund-structure judgment (XLF/XLV are official S&P sector-SPDR products; GRID/ICLN are thematic despite also having a dominant sector) that a sector-weighting vector alone cannot make. This brief does not resolve `category`'s dynamic-tier design — flagging it explicitly rather than silently defaulting it to something plausible, per this lane's own edge-case discipline. Story-author/tech-lead must decide: leave `category` a generic dynamic-tier label (e.g. `"Dynamically Classified ETF"`), infer it heuristically from the threshold band, or scope `category` out of this epic entirely and leave the keyword matcher's category logic in place until a follow-up.

## Metrics inventory (one row per affected field)

| Field | Type | Nullability | Trust class | Source when present | Source when absent |
|---|---|---|---|---|---|
| `Instrument.sector` (ETF branch) | `str \| None` | nullable | snapshot analytics | static curation, or identity-gated FMP `etf/sector-weightings` dominant bucket ≥ threshold | `None` -> `"Unclassified"` at `overview.py` |
| `Instrument.classification_source` (ETF branch) | new `Literal` value, `\| None` | nullable | n/a (provenance, not itself a value) | `"static"` or proposed `"fmp_etf_sector_weighting_confirmed"` | `"unavailable"` (gate failed / below threshold / unmapped) or `None` (mechanism not invoked on this path) |
| `Instrument.category` (ETF branch) | `str` | required today (keyword default) | unresolved by this brief | unchanged / out of scope | see § Open item: category |

## Methodology-doc section proposal (draft — not applied)

Mirrors the shape of `## Sector/Industry Classification — Source and Resolution (US-37.1)` and its `### ETF look-through constituent classification (US-38.1)` subsection. For the eventual implementer/docs lane, not applied to `financial-methodology.md` by this report:

```markdown
### Direct-held ETF sector classification (US-39.x, proposed)

The scope note under "Sector/Industry Classification" above excluded direct-held
ETF classification, deferring it to `classify_imported_instrument`'s ETF branch
(`registry.py:246-292`), a keyword-substring matcher on the broker's free-text
description. This subsection covers its replacement.

**Why `get_company_profile`'s `sector` field is not used here.** Live-verified
(2026-08-24) against 6 ETFs spanning distinct themes (SBIO, SPY, XLF, GRID,
QQQ, ICLN): FMP's general profile `sector` field returns the fund-sponsor/
vehicle classification for every ETF ("Financial Services" / "Asset
Management"), never a thematic answer. This confirms and extends the SPY/GRID
finding Epic 37 and Epic 38 both recorded as a non-goal. Do not extend the
equity branch's resolution order to ETFs by reusing this field.

**Resolution order (ETF branch):**

  1. Static registry lookup (unchanged): a curated `INSTRUMENT_DEFINITIONS`
     entry always wins -> `("static", curated_sector)`.
  2. Identity-gated dynamic lookup (opt-in, `market_data` supplied):
     for each symbol candidate (`resolve_symbol_candidates`, exchange-suffix
     aware — required for UCITS listings, e.g. `SBIO.L`, not bare `SBIO`):
       a. Fetch `get_company_profile(candidate)`; require the candidate's
          `isin` to equal the statement's `isin` (same identity gate as
          equities, `normalize_isin`). No match on any candidate -> unavailable.
       b. On identity match, fetch `get_etf_sector_weightings(candidate)`
          (`/stable/etf/sector-weightings`, live-verified accurate and
          on-plan). Take the top-weighted sector bucket.
       c. If the top bucket's share of total weight is below
          `ETF_SECTOR_DOMINANCE_THRESHOLD` (proposed 0.50-0.60, calibration
          in `03-quant-research.md` § Formulas): unavailable — a diversified
          or multi-theme fund is not silently relabeled `"Broad Market"`.
       d. Map the top bucket's sector string through `SECTOR_TAXONOMY_MAP`
          (reused from the equity branch). An unmapped bucket (e.g.
          `"Cash & Others"`) -> unavailable.
       e. -> `(mapped_sector, "fmp_etf_sector_weighting_confirmed")`.
  3. Nothing resolved -> `sector = None` -> `"Unclassified"` at the
     `overview.py` aggregation seam, same contract as the equity branch.

**Trust class:** snapshot analytics, never `verified`, mirroring the equity
dynamic tier.

**Second-provider corroboration (not a production data path):** yfinance's
`Ticker.funds_data.sector_weightings` independently matches FMP's weights
closely on every ETF tested 2026-08-24. Cited as feasibility evidence for this
section, not wired as a runtime fallback — yfinance exposes no ISIN, so it
cannot itself pass the identity gate.

**`category`** (Sector/Thematic/Broad Market/Bond/Commodity ETF) is not
resolved by sector-weighting data and is out of scope for this subsection —
see the research brief's § Open item: category.
```

## Recommendation summary

1. A reliable dynamic source **exists**: FMP's `/stable/etf/sector-weightings` (legacy `v3/etf-sector-weightings/{symbol}`), live-verified accurate and on-plan.
2. It requires the **same identity-gate pattern as Epic 37** (statement ISIN vs. FMP profile ISIN, via exchange-suffixed candidates) — confirmed necessary, not optional, by the live SBIO ticker-collision case.
3. The human's proposed shape — static curation first, identity-gated dynamic fallback second — is **confirmed workable**, unchanged from Epic 37's three-tier shape; only the field tier 2 reads, and the aggregation step (dominance threshold) are new.
4. `classification_source` needs a **new literal** (recommend `"fmp_etf_sector_weighting_confirmed"`), not reuse of `"fmp_identity_confirmed"`.
5. Two design parameters are **open, not settled by this brief**: the exact dominance threshold (data supports 50-60%) and the `category` field's dynamic-tier treatment (unresolved by any data source found here).
6. SBIO specifically needs a new `SymbolResolutionRule` (`SBIO.L` candidate, no bare `"SBIO"`) before any dynamic lookup can reach the correct security — the identity gate makes the mechanism *safe* without this rule (it fails closed to `unavailable`), but the rule is what makes it *resolvable*.
