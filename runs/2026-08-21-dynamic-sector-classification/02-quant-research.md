REPORT 2026-08-21-dynamic-sector-classification/02
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   Live `FmpClient.get_profile()` calls (services/quant-engine, real FMP_API_KEY present) for the 4 real equities this statement currently sends to "Other" (INTU, PANW, VICI, SPCX) + 9 static-registry equities to enumerate FMP's sector taxonomy; cache dir inspected before/after (data/raw/fmp-cache, gitignored) to confirm zero prior profile calls ever made for an equity
  result:    PASS
  detail:    all 4 confirmed non-empty sector+industry+ISIN; taxonomy diff found (5 of 11 GICS sector strings differ from project's canonical list); one live ticker (DFNS) reproduced the project's documented "wrong-fund" collision trap — see body

contract_notes:
  - exposure-fields.md's sector rows are labeled `current-state-truth`/`engine-derived` with no per-instrument provenance today — see § Trust-class analysis
  - financial-methodology.md has no section on how sector classification is sourced at all, independent of F-A — see § Methodology-doc gap

pack_corrections:
  - none

handoff:
  - Reuse `MarketDataService.get_company_profile()`, not raw `FmpClient.get_profile()`, to inherit symbol-candidate resolution — see § Recommended resolution logic
  - `instrument_identity.py`'s evidence-gated ISIN-match pattern (US-19.1/19.2) is the precedent to reuse for the FMP identity check — see § Identity risk
  - Sector-taxonomy mapping table (FMP string → project string) is fully specified for all 11 real GICS sectors — see § Sector taxonomy normalization
  - `get_profile()` shares the 300s `quote` cache TTL — too short for a fact that changes on a multi-year cadence — see § Caching recommendation
  - `"Other"` is documented as one of 16 legitimate sector values in the fmp-data skill, not a null marker — see § No-coverage handling

risks:
  - Live verification hit production FMP; results cached at data/raw/fmp-cache/profile-*.json (gitignored, 300s TTL) — stale by the time this is read
  - SPCX resolved to a live NASDAQ common-stock FMP profile; SpaceX is not known to be publicly traded — possible FMP data-quality anomaly, not chased further
  - ETF-side FMP `sector` (checked incidentally) looks unreliable as a constituent proxy (SPY/GRID both "Financial Services") — F-B territory, not cleared by this brief
  - `get_company_profile`'s `last_fetch_meta[...]["cached"]` is hardcoded `True` regardless of actual cache status (market_data.py:474) — noticed, not investigated, not part of F-A

## Orchestrator brief

- Decision: trusting FMP `sector` directly for the equity branch is defensible ONLY when gated by an ISIN identity check + a taxonomy-mapping table — never bare. See § Recommended resolution logic, § Identity risk, § Sector taxonomy normalization.
- Decision: US-14.3's "don't bypass the registry" call does not transfer as a blanket precedent — its reasoning was Freedom24/description-only and pre-dates any identity-safety analysis; F-A has zero fallback today so "no regression" doesn't apply. See § Does the US-14.3 precedent transfer.
- Decision: `"Other"` as silent categorical value is a guardrail-4 problem — recommend it become an explicit null/unavailable state, not a string. See § No-coverage handling.
- Decision: existing `/profile` HTTP cache (300s TTL) is not sufficient on its own; recommend either a longer, dedicated TTL or a persisted classification record — flagged as a should, not a hard block. See § Caching recommendation.
- Live-verified (not assumed): 4 real equities in this exact statement (INTU, PANW, VICI, SPCX) all get clean FMP sector+industry+ISIN today. See § Live verification.
- Critical, previously-unknown finding: FMP's sector taxonomy differs from this project's canonical list on 5 of 11 real GICS sectors — a mapping table is mandatory, not optional. See § Sector taxonomy normalization.
- Critical, previously-unknown finding: a live symbol-collision reproduction (DFNS) confirms the project's known "wrong-fund" trap (DFND/CIBR/SEMI) is a real, current risk for any bare-ticker FMP profile lookup, not just history/quote lookups. See § Identity risk.
- Sections below, in order: Problem framing; Concept & academic grounding; Live verification; Recommended resolution logic; Identity risk; Sector taxonomy normalization; Trust-class analysis; Caching recommendation; Does the US-14.3 precedent transfer?; No-coverage handling; Methodology-doc gap; Metrics / fields inventory; Tech-debt overlap.
- Nothing here blocks dispatch; all six of the producer's open decisions are answered across those sections.

---

## Problem framing

A portfolio researcher looking at the Exposure tab's sector donut / top-sector
cards cannot trust the "Other" bucket to mean anything: today it silently
absorbs every equity the ~90-entry static `INSTRUMENT_DEFINITIONS` dict doesn't
happen to name, with **zero** attempt at classification — not even the
keyword-substring heuristic the ETF branch gets. A researcher holding INTU,
PANW, VICI or SPCX today (all real positions in the bound statement) sees them
folded into "Other" alongside anything genuinely unclassifiable, and cannot
tell "the classifier didn't try" from "the classifier tried and failed" from
"this position genuinely defies sector classification." This corrupts every
sector-level aggregate downstream: `top_sectors`, `sector_hhi`,
`top_sector_weight`. The FMP company-profile client that would fix this is
**already wired, already called at import time, and already receives a clean
`sector` field** — it is discarded by a narrower story (US-14.3) that never
had this code path in view. A fix here enables the researcher to trust the
Exposure tab's sector composition for any new equity they buy, not just the
~90 already hand-curated.

## Concept & academic grounding

**Provider-sourced categorical classification vs. curated reference data vs.
keyword inference** — three distinct sourcing strategies for the same
categorical fact (an equity's GICS-style sector), not three different
concepts. All three currently coexist in this codebase for *ETFs*
(`classify_imported_instrument`'s ETF branch keyword-matches; the static dict
curates the rest); equities get only the second, and only for the ~90 in the
static dict.

**GICS (Global Industry Classification Standard)**, jointly maintained by MSCI
and S&P Dow Jones Indices, is the de facto standard this project's own sector
taxonomy already approximates (`"Technology"`, `"Financials"`, `"Health
Care"`, `"Energy"`, `"Consumer Discretionary"`, `"Consumer Staples"`,
`"Industrials"`, `"Materials"`, `"Real Estate"`, `"Utilities"`,
`"Communication Services"` — 11 sectors, matching GICS's 11 top-level
sectors exactly in count and near-exactly in name). FMP's own `sector` field
is *also* a GICS-style classification, sourced from the issuer's own
disclosed SIC/GICS mapping — but, confirmed live (§ Sector taxonomy
normalization below), FMP's string values are not verbatim GICS sector names
either; they are FMP's own house style, which happens to diverge from this
project's house style on 5 of 11 sectors.

Citations:
- MSCI/S&P Global, *Global Industry Classification Standard (GICS) Methodology*
  (2023 revision) — the industry-standard 11-sector taxonomy both FMP's and
  this project's sector strings approximate.
- Financial Modeling Prep, `/stable/profile` endpoint documentation — the
  concrete source of the `sector`/`industry`/`isin`/`exchange`/`country`
  fields this brief verified live.

**Known pitfalls, specific to this integration (not generic GICS caveats):**
1. A single company can be legitimately reclassified between sectors over
   time (e.g., Meta was Technology under some providers' pre-2018 mappings,
   Communication Services under GICS's 2018 revision) — a provider-sourced
   value is a **snapshot**, not an immutable fact; see § Caching
   recommendation.
2. **Ticker collision across exchanges is not hypothetical here — it is a
   documented, recurring failure mode this exact codebase has hit three times
   before** (DFND, CIBR, SEMI — see code comments in `app/core/symbols.py`
   lines 33-51) and was reproduced live in this research pass for a fourth
   symbol (DFNS) that has no existing guard rule. A bare-symbol `/profile`
   lookup silently returns an unrelated security's sector when the ticker
   happens to also exist on a different exchange. See § Identity risk.
3. GICS/FMP sector is a **company-level** attribute; it says nothing about a
   multi-segment conglomerate's true revenue mix (e.g. Amazon: "Consumer
   Cyclical" per FMP, despite AWS being a large and separately meaningful
   cloud/technology revenue segment). This is a known, accepted GICS
   limitation, not something this brief proposes to fix.

## Live verification

**What I checked, and how**, per this order's requirement to verify against
real data rather than assume:

1. **Confirmed the equity gap is real for this exact statement.** Ran
   `InstrumentRegistry.classify_imported_instrument()` against every
   `Financial Instrument Information` / `Stocks` row in `docs/IB2026.csv` not
   already in `INSTRUMENT_DEFINITIONS` (12 rows). 8 are ETFs mislabeled
   "Stocks" by IB (IB's own `Type` field says `ETF`, correctly routed to the
   ETF branch already). **4 are real equities and all 4 land in `sector=
   "Other"` today**: `INTU` (Intuit), `PANW` (Palo Alto Networks), `VICI`
   (Vici Properties — a REIT), `SPCX` (Space Exploration Technologies Corp.).
2. **Confirmed zero equity has ever received a live FMP profile call in this
   environment.** `data/raw/fmp-cache/` contained zero `profile-*.json` files
   before this pass — consistent with F-A (the enrichment path that calls
   `get_company_profile` is Freedom24-only, and this statement is an IB
   import).
3. **Live-called `FmpClient.get_profile()` for the 4 equities** (real
   `FMP_API_KEY`, this environment has one configured). All 4 returned
   non-empty `companyName`, `sector`, `industry`, and `isin`:

   | symbol | FMP sector | FMP industry | FMP isin | matches IB statement's `Security ID`? |
   |---|---|---|---|---|
   | INTU | Technology | Software - Application | US4612021034 | yes, exact |
   | PANW | Technology | Software - Infrastructure | US6974351057 | yes, exact |
   | VICI | Real Estate | REIT - Diversified | US9256521090 | yes, exact |
   | SPCX | Industrials | Aerospace & Defense | US84615Q1031 | yes, exact |

   This directly answers the producer's open decision #2 for the equity path:
   FMP does return usable, non-empty sector data for the real "Other"
   population in this statement, and its `isin` field is a byte-exact match
   to what `interactive_brokers_csv.py` already captures as
   `ImportedInstrument.isin` (from IB's `Security ID` column) — the
   disambiguation mechanism in § Identity risk is not hypothetical plumbing,
   it is already-captured data sitting unused.
4. **Confirmed a no-coverage case exists and degrades to empty, not an
   error.** `get_profile("ACOMO")` (a real, already-registered Dutch equity,
   Euronext-listed) returned `[]` when queried by bare ticker — FMP's
   `/profile` endpoint does not resolve this non-US listing under its plain
   symbol. This is the concrete "no FMP coverage" edge case the DoD asked
   for: it fails closed (empty list), not with a fabricated or wrong value.
5. **Reproduced the project's documented "wrong-fund" collision live**, on a
   symbol not yet covered by an existing guard rule — see § Identity risk.
6. **Did not** verify FMP's ETF-side sector reliability rigorously (F-B is
   out of scope) — the two ETF profiles pulled incidentally (SPY, GRID) both
   returned `"Financial Services"` (the fund sponsor's own business
   classification, not the fund's thematic sector), which is a strong
   negative signal for F-B specifically but is **not** load-bearing for this
   brief's F-A recommendation.

## Recommended resolution logic

Not a numeric formula — a classification-resolution order, since the input
here is categorical. Written as logic so the edge cases are explicit, per
this order's DoD.

```text
classify_equity(imported: ImportedInstrument) -> (sector: str | None, source: str):

  1. Static lookup (existing, unchanged):
     if normalize_symbol(imported.symbol) in INSTRUMENT_DEFINITIONS:
         return (static_entry.sector, "static")
     # This step already runs before classify_imported_instrument is
     # reached (attach_snapshot_metadata calls get_instrument() first) —
     # nothing here changes.

  2. Provider lookup, identity-gated (NEW):
     profile = MarketDataService.get_company_profile(imported.symbol)
     # MUST go through MarketDataService, not FmpClient directly — this
     # reuses the existing candidate-resolution machinery in
     # app/core/symbols.py (proxy/suffix handling) instead of a second,
     # divergent implementation. Duplicating symbol resolution is exactly
     # the class of defect this project's quant gate hunts for.

     if profile is None or not profile.get("sector"):
         fall through to step 3          # no coverage, or empty sector string

     fmp_sector_raw = profile["sector"]
     mapped_sector = SECTOR_TAXONOMY_MAP.get(fmp_sector_raw)
     if mapped_sector is None:
         fall through to step 3          # FMP sector string not in the known
                                          # mapping (new/renamed FMP sector) —
                                          # never pass an unmapped string
                                          # through raw; see § taxonomy table

     statement_isin = normalize_isin(imported.isin)
     profile_isin   = normalize_isin(profile.get("isin"))

     if statement_isin and profile_isin:
         if statement_isin == profile_isin:
             return (mapped_sector, "fmp_verified")     # identity confirmed
         else:
             fall through to step 3      # WRONG SECURITY — do not use this
                                          # value at all; see § Identity risk
     else:
         fall through to step 3          # no evidence either way — see
                                          # note below on this being a
                                          # deliberately conservative default

  3. No classification available:
     return (None, "unavailable")        # NOT the string "Other" — see
                                          # § No-coverage handling
```

**Edge cases, stated explicitly (never resolved with a fallback value):**

| Case | Resolution |
|---|---|
| `imported.symbol` in static dict | step 1, unchanged, no FMP call — fast path preserved |
| FMP has no profile for the symbol at all (no coverage) | step 2 falls through to step 3 → `unavailable`, never a guess |
| `profile.sector` is `""` or missing | treated identically to "no profile" — never coerced to a truthy default |
| `profile.sector` is a string not in the taxonomy map (FMP adds/renames a sector) | falls through to step 3 — never passed through raw as an ad-hoc 12th sector bucket that would silently fragment `sector_hhi` |
| both ISINs present and match | `fmp_verified` — highest-confidence automated source |
| both ISINs present and **mismatch** | do not use the FMP value at all — this is the "wrong security" case (§ Identity risk), distinguishing it from "no data" matters for guardrail 4 |
| ISIN missing on either side (no evidence) | conservative default: treat as unconfirmed, fall through — **a named, explicit choice**, not a silent one; see rationale below |
| FMP raises (timeout, 5xx, rate limit) | caught and swallowed exactly like `instrument_enrichment.py`'s existing `except Exception` pattern — falls through to step 3, never propagates, never blocks the import |
| symbol already resolves via keyword inference today (ETFs only) | unaffected — this logic is additive to the equity branch, which has no keyword step to preserve |

**Why "no ISIN evidence → don't trust it" is the recommended default, not
"trust it anyway":** every genuine collision this codebase has hit
(DFND, CIBR, SEMI, and the newly-reproduced DFNS) involves a **non-US-listed**
instrument colliding with an unrelated US-listed one on the bare ticker. IB
and Freedom24 — the two importers that would ever reach this branch for a
non-static equity — both already capture ISIN on every instrument line (§
Live verification confirmed byte-exact matches for all 4 real cases). An
equity that legitimately lacks ISIN evidence is the unusual case, not the
common one, so the conservative default costs little in practice while
closing off the exact failure mode this project has paid to discover three
times already.

## Identity risk

**This is the load-bearing finding in this brief.** `app/core/symbols.py`
already documents, in comments, three prior incidents where a bare-ticker
FMP lookup silently resolved to the wrong security:

> `# DFND = iShares Global Aerospace & Defence UCITS ETF (LSE, GBP). ... Do
> NOT map to DFNS.L/DFEN.DE/DFNG.L — those are VanEck Defense, a DIFFERENT
> fund.`
> `# SEMI ... Deliberately NO bare "SEMI" candidate: on FMP that symbol is a
> DIFFERENT US-listed security (2026-06-30 quote 40.58 vs the held line's
> 17.998 GBP, 2.25×; Epic 31 F-5).`
> `# CIBR ... Deliberately NO bare "CIBR" candidate: on FMP that symbol is
> the US-listed sister fund (a different security — the DFND wrong-fund
> lesson).`

I reproduced this class of failure live, on a symbol with **no existing
guard rule** (`DFNS`, which appears in this exact statement as "VANECK
DEFENSE ETF", LSE, ISIN `IE000YYE6WK5`):

```
FmpClient.get_profile("DFNS") -> companyName="T3 Defense Inc.", isEtf=False,
                                  sector="Industrials", isin=<a different ISIN>
```

`DFNS` is an ETF (F-B territory, not F-A directly), but the mechanism is
identical and directly relevant to F-A: any equity not yet in the static
dict, listed on a non-US exchange, whose bare ticker happens to also name an
unrelated US-listed security, is exposed to exactly this trap the moment the
equity branch starts calling `get_company_profile`. None of the 4 real F-A
cases in this statement hit it (all 4 are genuinely US-listed, NASDAQ/NYSE,
and their ISINs match cleanly) — but the code path does not know that in
advance, and the failure mode is silent and confident, not an error.

**This is exactly why "trust FMP's sector field directly" cannot be
unconditional.** The existing mitigation pattern in this codebase for
exactly this class of risk is `app/services/instrument_identity.py`
(US-19.1/19.2): an evidence-gated ISIN comparison — "skipped when either
side lacks an ISIN; absent evidence is never a pass or a failure" — currently
used only to flag mismatches between a statement and the **static registry's**
own recorded ISIN. **The same evidence-gating logic is the correct mechanism
to gate FMP-sourced sector**, comparing the statement's ISIN against the
FMP profile's `isin` field instead of against the registry's. Reuse the
pattern, not a new one — this project's quant/tech-debt findings repeatedly
flag duplicated inference logic as the recurring defect class here.

## Sector taxonomy normalization

**Confirmed live, not assumed.** FMP's `sector` string values differ from
this project's canonical 11-value GICS-equivalent list
(`.claude/skills/fmp-data/SKILL.md`, "Sector values used in this codebase")
on 5 of 11 sectors:

| Project canonical value | FMP value (confirmed live) | Confirmed via |
|---|---|---|
| `Health Care` | `Healthcare` | NVO |
| `Financials` | `Financial Services` | BRK-B |
| `Consumer Discretionary` | `Consumer Cyclical` | AMZN |
| `Consumer Staples` | `Consumer Defensive` | PG |
| `Materials` | `Basic Materials` | LIN |
| `Technology` | `Technology` | INTU, PANW, ASML — exact match |
| `Energy` | `Energy` | EQNR — exact match |
| `Industrials` | `Industrials` | CAT, SPCX — exact match |
| `Real Estate` | `Real Estate` | VICI — exact match |
| `Utilities` | `Utilities` | NEE — exact match |
| `Communication Services` | `Communication Services` | META, GOOGL — exact match |

**This mapping table is mandatory, not optional.** Passing `profile["sector"]`
through unmapped would silently create parallel near-duplicate sector buckets
in every downstream aggregate — `top_sectors`, `sector_hhi`,
`top_sector_weight` — where "Healthcare" and "Health Care" fragment what
should be one bucket, corrupting concentration math without any error or
visible symptom. A wrong-but-plausible HHI is exactly the degenerate-case
failure guardrail 1 exists to prevent. Any FMP sector string not in this
table (new or renamed on FMP's side) must fall through to `unavailable`, not
pass through raw as a 12th ad hoc value (see § Recommended resolution logic,
edge case table).

## Trust-class analysis

Per output field, per this project's two overlapping trust vocabularies —
the four truth classes (broker truth / snapshot analytics / synthetic
history / persisted import) and the verified/degraded/withheld/unavailable
ladder, plus the card-level label convention (`current-state-truth` /
`engine-derived`) actually used in `exposure-fields.md` for sector fields
today.

**`sector` (existing field, `Instrument.sector: str | None`, feeds
`top_sectors`, `sector_hhi`, `top_sector_weight`, `lookthrough_sector_exposure`)**

- Truth class: **snapshot analytics** — derived from current holdings
  metadata + external reference data, no return history involved. This does
  not change with F-A.
- Card-level label: unchanged, still `current-state-truth` — F-A does not
  make the sector field returns-derived or historical.
- **Per-instrument classification confidence, however, genuinely varies now**
  in a way the current flat card label does not distinguish, and guardrail 4
  exists precisely so this isn't collapsed:
  - static dict hit → curated / human-verified — highest confidence
  - FMP-sourced + ISIN-confirmed (`fmp_verified` in the logic above) —
    automated, but identity-confirmed; second tier
  - FMP-sourced without identity confirmation — **not recommended for use at
    all** under the conservative default (§ Recommended resolution logic);
    if a future revision chooses the looser option, this tier must carry its
    own explicit, lower label — never silently merged with `fmp_verified`
  - no source resolves it → `sector = None`, not `"Other"` (§ No-coverage
    handling)
- **Caution on vocabulary**: do not literally reuse the word `verified` for
  the FMP-confirmed tier — that word already has a specific, narrower meaning
  elsewhere in this codebase (return-basis verification, e.g.
  `verified_total_return`). Reusing it for a categorical, non-returns fact
  risks exactly the truth-class mixing guardrail 3 forbids. A distinct name
  (e.g. a `classification_source` enum) is the schema owner's call, not
  mine, but the naming collision is a real risk worth flagging now.
- Nullability: **must become nullable in the honest sense** — today it is
  typed `str | None` but the equity branch never actually returns `None`,
  always the string `"Other"`. Recommend the field start actually using its
  existing nullability rather than a string standing in for absence.
- Withheld vs. unavailable, precisely: the ISIN-mismatch case (§ Identity
  risk) is subtly closer to **withheld** than **unavailable** under the
  ladder's own definitions ("withheld = have it, don't trust it" vs.
  "unavailable = don't have it") — the resolver *does* receive a sector
  string from FMP, and specifically distrusts it. Whether that distinction
  needs its own exposed state or can collapse to `unavailable` at the
  field level (since nothing downstream currently consumes a `withheld`
  sector) is a schema-owner call; I flag it so it is a deliberate choice, not
  an accidental collapse.

## Caching recommendation

**Not sufficient as-is.** `get_profile()` shares the `quote` cache namespace
and TTL (`fmp_quote_cache_ttl_seconds`, default 300 seconds) — the same
5-minute TTL used for live bid/ask quotes. A company's sector classification
changes on a multi-year cadence (GICS reclassifications, M&A), not a
5-minute one. Two concrete consequences:

1. **Repeated imports within a session re-fetch identical data needlessly**
   — every re-import more than 5 minutes after the last one re-hits FMP for
   every non-static symbol, even though the answer essentially never
   changes. Wasteful, not incorrect.
2. **More importantly for guardrail 1**: a re-import that happens to land
   just after cache expiry, combined with any transient FMP data hiccup
   (§ Live verification's `ACOMO` case showed `/profile` can legitimately
   return empty for a symbol it resolved cleanly before), could cause the
   *same* equity to classify differently across two runs of the same
   statement — a `current-product-state.md`-tracked Exposure number
   silently changing between two runs of an unchanged import, with no audit
   trail explaining why.

Recommendation: at minimum, move `get_profile()` off the `quote` TTL onto
something closer to the `history` tier (86400s) or longer — sector doesn't
need same-session freshness. Better: persist the **resolved classification
decision** itself (symbol, mapped sector, source tier, resolved-at,
ISIN-match evidence) as an explicit record, not just rely on the ephemeral
HTTP cache — this makes a sector's provenance auditable independent of
cache TTL and survives a `manage_cache.py clear`. This is a **should**, not
a hard block — the HTTP-cache-only approach is a workable v1 if the TTL is
at least widened — but given F-A's output feeds a shipped-state-tracked
UI surface, I recommend against leaving it on the 5-minute quote TTL. Exact
persistence shape (new field, new table, versioned record) is the tech
lead's call, not mine.

## Does the US-14.3 precedent transfer?

**No, not as a blanket "don't use FMP's sector field" rule — but its
reasoning contains something worth keeping.**

US-14.3's stated reason was narrow and structural, not principled:
*"The helper populates `description` and `instrument_type` only. ... We do
not bypass the registry's classification logic."* No safety or trust
analysis was recorded — the story's own "Out of scope" section gives the
real justification: *"Users get the same bug (some sectors → 'Other') that
existed before this story — no regression."* That framing is airtight for
US-14.3's actual scope (Freedom24, feeding the *same* keyword classifier that
was already doing an OK job for well-described positions) — but it does not
hold for F-A, where the status quo is not "an existing classifier doing
imperfect work," it is **zero classification, ever, for any importer**.
"No regression" cannot be the bar when there is nothing to regress from.

What *should* transfer from US-14.3 is the **"one code path" instinct**, just
applied differently: rather than building a second, independent classifier
that trusts FMP's field wholesale, the recommendation in this brief (§
Recommended resolution logic) folds FMP-sourced classification into the
*same* `classify_imported_instrument` resolution method as a new, ranked
input — static dict first, FMP (identity-gated) second, unavailable last.
That preserves "one method, one code path" while actually answering the
question US-14.3 left open rather than reasserting its conclusion in a
different context.

**Direct answer to producer open decision #6**: the "don't bypass" call does
not settle F-A. F-A is a materially different code path (general, all
importers, currently a hard-coded `"Other"` with no classifier at all) from
the one US-14.3 scoped (Freedom24-only, feeding an *existing* keyword
classifier). Trusting FMP's sector field directly is defensible for F-A —
conditioned on the identity gate and taxonomy mapping this brief specifies —
in a way it may not have been worth the complexity for US-14.3's narrower,
lower-stakes case.

## No-coverage handling

**Direct answer to producer open decision #5.** Today, `"Other"` is not a
residual/absence marker — it is documented as one of 16 legitimate values in
`.claude/skills/fmp-data/SKILL.md`'s "Sector values used in this codebase"
list, indistinguishable in the data model from a position genuinely
classified as (say) `"Materials"`. GICS itself has no "Other" sector; this
project invented the bucket to give the field *some* string when nothing
classified the position. That is precisely the shape of problem guardrail 4
targets: a silent label standing in for "we don't know," presented with the
same confidence as a real answer.

**Recommendation**: when no source (static, FMP-identity-confirmed) resolves
a value, `sector` should become an explicit `None`/unavailable state, not the
string `"Other"`. The UI can still render an "Unclassified" bucket for
display purposes — that is a presentation choice, not a data-model one — but
the underlying field should stop asserting a categorical fact it does not
have. This is a nullability/schema decision for the schema owner to execute,
not mine to specify in field-name terms, but the underlying guardrail-4
call — "Other" as a bare string is fabrication-adjacent and should stop —
is the recommendation this research pass is making explicitly, per the DoD's
direct ask on this point.

## Methodology-doc gap

Independent of F-A: `docs/finance/financial-methodology.md` has **no section**
describing how sector/industry classification itself is sourced or resolved
— only how sector *exposure* (an aggregate over already-classified holdings)
is computed (`§Sector exposure vs. factor loading`, which treats the
per-holding classification as a given input). US-14.3 explicitly declared
"no methodology change... not an analytics change" for its own scope, which
was true for that story (it changed the *description* field, not the sector
value). It is not true for F-A: F-A is precisely a new sector-value source.
Guardrail 2 ("every UI metric maps to one engine formula and one code path")
is not fully met for `sector` today regardless of F-A, since the
*classification mechanism itself* — keyword substrings for ETFs, static
lookup for the ~90 known symbols — has no documented rule a reader could
check the code against. Recommend a new short methodology-doc section
("Sector/Industry Classification — Source and Resolution") covering the
resolution order in § Recommended resolution logic once a story implements
it; not drafted here per this order's non-goals (no story text).

## Metrics / fields inventory

One row per field this brief's recommendation implies. Exact naming is the
schema owner's call — these are research-level candidate names, not a
locked contract.

| Field | Type | Logic reference | Trust / truth class | Nullable? | Notes |
|---|---|---|---|---|---|
| `sector` (existing) | `str \| None` | § Recommended resolution logic | snapshot analytics; card-level `current-state-truth` unchanged | **yes — must actually use it** | today typed nullable but never returns `None` for equities; "Other" stands in for absence |
| `classification_source` (candidate, new) | enum: `static \| fmp_verified \| unavailable` (+ optionally a fourth tier if the looser no-ISIN-evidence option is chosen later) | § Recommended resolution logic, § Identity risk | orthogonal to the truth-class ladder — a provenance/confidence tag for a categorical fact, not a returns-basis rung | no — always resolvable, `unavailable` is itself a valid value | do not literally reuse `verified` (see naming caution, § Trust-class analysis) |
| `industry` (candidate, new — optional) | `str \| None` | not specified by this brief; FMP returns it alongside `sector` at no extra cost | same as `sector` | yes | out of scope to require — noted because it's free from the same call, a story-scoping decision, not mine |

## Tech-debt overlap

Confirms the producer's brief: `docs/tech-debt-register.md`'s
`instruments/registry.py:45-48,180-261` entry ("the keyword classifier is
the fragile part") names the *existing* ETF-branch fragility, not F-A's gap
directly — F-A's equity branch has no classifier to be fragile, it has none
at all. Closing F-A does not resolve that tech-debt entry (still epic-24,
still open); it is a separate, adjacent fix. Not proposing scope changes
here per this order's non-goals.
