REPORT 2026-08-21-epic38-followups-and-etf/03
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only research; no code executed beyond reading source

contract_notes:
  - docs/contracts/exposure-fields.md:207-209 (lookthrough_sector_exposure rows) does not yet document an "Unclassified" bucket the way lines 216-219 (sector_allocation-derived rows) already do — needs the same treatment once Story A ships
  - docs/tech-debt-register.md:177 cites risk.py:1485-1499,1537-1549 for the two hardcoded-list functions; current line numbers are 1613-1627 and 1665-1677 — drifted, needs correcting at close-out

pack_corrections:
  - none

handoff:
  - concrete aggregation rule, worked example, and methodology-doc amendment are in § Proposed aggregation rule and § Draft methodology-doc section below, ready for story-author/docs-engineer
  - companion recommendation (curate XLF/XLV/IBB/ITA/PPA/BIL/VGSH/DBC into INSTRUMENT_DEFINITIONS) is in § Companion recommendation — verified these 8 tickers are NOT in registry.py today, unlike SPY/VUAA/SLV/IEF/ISLN/SGLD/ICOM which are
  - open question for design/story-author on MIN_SECTOR_WEIGHT (0.05%) suppression applying to "Unclassified" — see § Open decision: suppression threshold

risks:
  - I recommend NOT literally reusing resolve_equity_sector() as a function call per constituent (it would pay for a wasted get_company_profile network/cache call whose result is always discarded) — see § Why "reuse" means the principle, not the call, for the reasoning; flagging in case story-author/tech-lead expected a literal call-site reuse
  - the per-source fund-category override (Thematic/Sector/Bond/Commodity ETF with a curated .sector) is pre-existing, unaffected by this research, and must not be conflated with the two hardcoded-list functions in scope — see § What is NOT in scope, to prevent an implementer widening the change

## Orchestrator brief

- decision: partial-resolution rule is per-source-slice, not per-constituent — each source's value classifies independently; unresolved slices land in "Unclassified" (US-37.1's `UNCLASSIFIED_SECTOR_LABEL`), nothing pro-rated, nothing dropped — § Proposed aggregation rule
- decision: no new dynamic FMP+identity-gate tier for look-through constituents — they carry no statement ISIN (only a bare ticker from FMP's own ETF-holdings feed), so tier-2 identity evidence structurally does not exist — § Why constituents cannot reuse the ISIN gate literally
- decision: all three named fallback sites (both hardcoded-list functions, the ungated `get_company_profile` call) resolve to the same fix — delete the guess, land in Unclassified — § Explicit treatment of the three fallback sites
- companion finding (not requested, load-bearing): 8 of the hardcoded list's ETF tickers (XLF/XLV/IBB/ITA/PPA/BIL/VGSH/DBC) are NOT curated in `INSTRUMENT_DEFINITIONS` at all — curating them is how the legitimate fund-category labels survive removal — § Companion recommendation
- open, not resolved here: whether "Unclassified" should be exempt from the existing `MIN_SECTOR_WEIGHT` (0.05%) display-suppression filter, since `overview.py`'s own Unclassified precedent has no such floor — § Open decision: suppression threshold
- sections below, in order: Problem framing · Current mechanism, traced · Why constituents cannot reuse the ISIN gate literally · Proposed aggregation rule · Worked example · Explicit treatment of the three fallback sites · What is NOT in scope · Companion recommendation · Trust-class analysis · Open decision: suppression threshold · Draft methodology-doc section · Metrics inventory

---

## Problem framing

`build_lookthrough_sector_exposure` (`risk.py:1031-1076`) and `_build_shared_sector_overlap`
(`risk.py:1630-1662`, feeding the ETF-overlap-pair card) both need a sector label for
every dollar of look-through market value, but a look-through *constituent* — a
company discovered by unpacking an ETF's holdings via
`market_data.get_etf_holdings(...)` — is identified only by a bare ticker string
(`row["asset"]`) from FMP's own ETF-holdings endpoint. Unlike a directly-held
equity (US-37.1), there is no broker-statement ISIN backing that identity.

Today, when the static registry (`InstrumentRegistry.get_instrument`) does not
resolve a constituent's own sector, both functions fall back to a **hardcoded
ETF-ticker → sector keyword match** (`_infer_sector_from_sources`,
`_infer_sector_from_resolved_pair`), defaulting to the literal `"Other"` (or, in
`_build_shared_sector_overlap`, to an **ungated live FMP `get_company_profile`
call** with no identity check at all, also defaulting to `"Other"`). This is the
same fabrication-by-omission problem Epic 37 fixed for direct equities, still
live in the look-through path. This research establishes the rule for what
happens to sector totals when only some of an ETF's constituents resolve.

## Current mechanism, traced

`build_lookthrough_sector_exposure` operates on `LookThroughConstituent` records
(`schemas/reconciliation.py:105-110`): one record per underlying symbol, carrying
`effective_market_value` (its total look-through value across every sourcing
ETF/direct position) and `sources: list[LookThroughSource]` — one entry per
ETF (or direct position) that contributed value to it, each with
`source_market_value`, `source_weight`, `resolved_via` (the source ETF's
resolved ticker).

For each constituent (`risk.py:1036-1062`):
1. `default_sector` = `registry.get_instrument(constituent.symbol).sector` if the
   constituent's own symbol is in the static registry, **else**
   `_infer_sector_from_sources(constituent.sources)` (hardcoded keyword match on
   `resolved_via`, defaulting to `"Other"`).
2. For each `source` in `constituent.sources`: the slice's value
   (`source_market_value * source_weight`) is attributed to `default_sector`,
   **unless** the sourcing instrument is a curated Thematic/Sector/Bond/Commodity
   ETF with its own `.sector` set in the static registry — then that slice uses
   the *fund's own* curated sector instead (e.g. a bond fund's holdings are
   classified `"Fixed Income"` by fund category, not by attempting an
   equity-style GICS lookup on a bond). **This per-source fund-category override
   is legitimate, pre-existing, and unaffected by this research** — see
   § What is NOT in scope.
3. A small reconciliation remainder (float drift between
   `effective_market_value` and the summed sourced value) is added to
   `sector_totals[default_sector]`.

`_build_shared_sector_overlap` (the ETF-overlap-pair card) does the analogous
thing for symbols shared between two ETFs: static registry first, then
`_infer_sector_from_resolved_pair` (same hardcoded-keyword shape), then — the
one case with **no fallback keyword match at all** — an **ungated**
`market_data.get_company_profile(symbol)` call read directly for `sector`,
defaulting to `"Other"` (`risk.py:1654-1655`). This is the fallback site named in
the order as having "no ISIN identity check at all today" — confirmed: no
identity gate of any kind guards it.

## Why constituents cannot reuse the ISIN gate literally

US-37.1's gate (`resolve_equity_sector`, `equity_sector_resolution.py:67-96`)
matches the **statement's own ISIN** (`ImportedInstrument.isin`, broker-supplied)
against the FMP profile's ISIN. A look-through constituent has no
`ImportedInstrument` and no statement ISIN — its only identity claim is the
ticker string FMP's own `/etf-holdings` endpoint reported. Verified: neither
`market_data.py`'s `get_etf_holdings`/`get_etf_holdings_for_date` nor the
underlying `fmp.py` client surfaces an ISIN or CUSIP on a holdings row — only
`asset` (ticker), `name`, `weightPercentage`.

So for a look-through constituent, calling `get_company_profile(ticker)` and
trusting its `sector` is asking FMP "what sector is this ticker" using an
identity FMP itself already supplied — a same-provider round trip. In the quant
capability pack's own terms this is `anchor: provider-self-consistent`, not
independent evidence, **regardless of any cross-check invented against FMP's own
ETF-holdings row** (matching `get_company_profile`'s returned ticker/name back
against the holdings row's `asset`/`name` only catches an FMP-internal
inconsistency between its own endpoints, not a wrong-security assignment against
broker truth). Inventing a weaker, ticker-only "confirmation" tier and labeling
it as if it were comparable to `fmp_identity_confirmed` would be exactly the
"second, divergent trust check" Epic 37's PRD says not to build.

**The identity gate's own logic already answers this.** AC5 of US-37.1 states:
"when either the statement or the FMP profile lacks an ISIN … the FMP-sourced
sector is not used." A look-through constituent structurally has no statement
ISIN, for every constituent, on every run — so AC5's branch is not an edge case
here, it is the *only* reachable outcome. Reusing the gate's **principle**
(missing identity evidence ⇒ no classification, never a guess) is what "reuse,
not a second check" means in this context — not a literal per-constituent call
into `resolve_equity_sector`.

### Why "reuse" means the principle, not the call

`resolve_equity_sector` calls `get_company_profile` *before* checking ISINs
(`equity_sector_resolution.py:79-93`) — the network/cache fetch happens
unconditionally, and the ISIN check only decides whether to *use* the result.
Calling it per look-through constituent with a synthetic `isin=None` would
therefore fetch and discard a profile for every unresolved constituent on every
run — paying FMP-call/cache cost for an outcome knowable in advance without any
lookup. The correct implementation shape is not "call `resolve_equity_sector`
with no ISIN," it is "apply static-registry tier 1 only, and treat tier 2 as
structurally inapplicable" — same outcome, no wasted call. This is an
implementation note for the design pass, not a new mechanism: it does not
introduce any classification outcome `resolve_equity_sector` itself could not
already produce.

## Proposed aggregation rule

```text
For each LookThroughConstituent c (unchanged iteration shape):

  registry_sector = InstrumentRegistry().get_instrument(c.symbol)?.sector
  default_sector  = registry_sector if registry_sector else UNCLASSIFIED_SECTOR_LABEL
                    (was: registry_sector else _infer_sector_from_sources(...) or "Other")

  For each source in c.sources (UNCHANGED — per-source-slice attribution stands):
    source_value  = source.source_market_value * source.source_weight
    source_sector = default_sector
    if source_instrument is a curated Thematic/Sector/Bond/Commodity ETF
       with its own .sector set:                      # UNCHANGED, see scope note
      source_sector = source_instrument.sector
    sector_totals[source_sector] += source_value        # UNCHANGED

  remainder handling UNCHANGED (goes to default_sector, i.e. Unclassified when
    unresolved)

_build_shared_sector_overlap, per shared symbol (mirrors the same rule):
  sector = registry_sector if registry_sector else
           (proxy_sector if proxy_sector else UNCLASSIFIED_SECTOR_LABEL)
           (was: ... else _infer_sector_from_resolved_pair(...) else
                 live get_company_profile(symbol) read, "Other" default)
  proxy_sector itself continues to mean only "a curated fund-category match" —
  see § Companion recommendation for what makes proxy_sector resolve at all
```

**What changes, precisely:** the *only* thing that changes is what a
constituent's/shared-symbol's sector resolves to when the static registry (and,
for `_build_shared_sector_overlap`, the curated-fund-category `proxy_sector`)
do not resolve it. It was a hardcoded ticker-keyword guess, or an ungated live
FMP call, both defaulting to `"Other"`. It becomes `UNCLASSIFIED_SECTOR_LABEL`
("Unclassified", reused from `app/analytics/overview.py:13`, not a new string
or a new bucket-mechanism). The per-source-slice attribution loop, the
fund-category override, and the remainder-reconciliation mechanic are all
**unchanged** — this is a substitution at the leaf resolution step, not a
restructuring of the aggregation.

**Partial resolution answer (the order's central question):** an ETF's
look-through value splits across whatever sectors its individual constituents'
slices resolve to. A slice with a resolvable sector counts toward that sector.
A slice that cannot be resolved counts, at its full weight, toward
`"Unclassified"` — never redistributed pro-rata across the resolved sectors
(that would fabricate confidence about the unresolved slice), never dropped
from `total_market_value` or the weight denominator (that would silently
shrink the portfolio, the same violation US-30.5a's base-currency rule
forbids for FX). One ETF can therefore legitimately appear split across a real
sector and `"Unclassified"` in the same response.

## Worked example

Illustrative, not live data. ETF `XYZ`, $10,000 look-through value, two
constituents: `AAPL` (60% weight inside XYZ, curated `sector="Technology"`)
and `OBSCURECO` (40% weight inside XYZ, not in the static registry, `XYZ`
itself not a curated Thematic/Sector/Bond/Commodity fund):

```text
AAPL:      effective_market_value = $6,000
           default_sector = "Technology" (static registry hit)
           source_sector  = "Technology" (XYZ not a fund-category override)
           sector_totals["Technology"] += $6,000

OBSCURECO: effective_market_value = $4,000
           default_sector = "Unclassified" (no registry hit, XYZ not curated)
           source_sector  = "Unclassified"
           sector_totals["Unclassified"] += $4,000

Result: Technology 60% ($6,000), Unclassified 40% ($4,000).
Total ($10,000) and weight sum (100%) both reconcile — nothing dropped.
```

Under the CURRENT code, `OBSCURECO`'s slice would resolve via
`_infer_sector_from_sources(["XYZ"])` — none of the hardcoded tokens match
`"XYZ"` — landing in `"Other"`, indistinguishable from a genuinely-attempted-
and-failed classification and from any other miscellaneous residual the system
already uses `"Other"` for elsewhere (e.g. `InstrumentRegistry.get_sector()`'s
own defensive-only fallback). The fix does not change the 60/40 split; it
changes the second bucket's label from a silent, ambiguous `"Other"` to an
honest, distinctly-named `"Unclassified"`.

A second, more insidious current-behavior case: if `OBSCURECO` had instead been
sourced via `SPY` (`resolved_via = "SPY"`), `_infer_sector_from_sources` returns
`"Broad Market"` — **not a GICS sector**, and not the constituent's own sector
either. It is a guess standing in for "sourced from a diversified index fund,
real sector unknown," but it *looks* like a deliberate classification rather
than an admission of ignorance — the "plausible-looking number in a degenerate
case" failure mode the quant capability pack calls the worst outcome, because it
never gets questioned. This also becomes `"Unclassified"` under the proposed
rule.

## Explicit treatment of the three fallback sites

1. **`_infer_sector_from_sources` (risk.py:1613-1627).** Delete. Its only call
   site (`risk.py:1038`, `default_sector` fallback) becomes
   `UNCLASSIFIED_SECTOR_LABEL`. Confirmed single call site — no other caller in
   production code.
2. **`_infer_sector_from_resolved_pair` (risk.py:1665-1677).** Delete. Its only
   call site (`risk.py:1642`, `proxy_sector` in `_build_shared_sector_overlap`)
   becomes `None` in effect once deleted — the caller's own fallback (below)
   then applies. Confirmed single call site.
3. **The ungated `market_data.get_company_profile(symbol)` call
   (risk.py:1654-1655, inside `_build_shared_sector_overlap`).** Delete the
   call entirely — do not replace it with a gated version. § Why constituents
   cannot reuse the ISIN gate literally establishes that no identity evidence
   exists to gate it *with*; a live FMP call here can only ever be
   provider-self-consistent, which the quant capability pack already treats as
   insufficient for a published classification. The function's `sector = ...
   else: profile = market_data.get_company_profile(symbol); sector =
   str((profile or {}).get("sector") or "Other")` branch becomes `sector =
   UNCLASSIFIED_SECTOR_LABEL`. This also means the `market_data:
   HoldingsMarketData` parameter may become unused by
   `_build_shared_sector_overlap` — an interface simplification for whoever
   implements, not a decision this brief makes.

All three sites converge on the same replacement value and the same reasoning;
none needs separate treatment beyond deleting the guess.

## What is NOT in scope

The **per-source fund-category override** — `source_instrument.asset_class ==
"etf" and source_instrument.category in {"Thematic ETF", "Sector ETF", "Bond
ETF", "Commodity ETF", ...} and source_instrument.sector` — is a *different*
mechanism from the three fallback sites above: it reads a **curated, static
registry** field (the same trust tier as US-37.1's tier 1, no identity gate
needed because it is human-reviewed data), not a live lookup or a hardcoded
keyword guess. It already correctly classifies value sourced from ETFs like
`SLV`, `ICOM`, `SGLD`, `ISLN`, `IEF` (all curated in `INSTRUMENT_DEFINITIONS`
with real `sector`/`category` values — verified in `registry.py`). This
research does not touch it, and an implementer must not conflate it with the
two hardcoded-list functions being removed — doing so would regress correctly-
resolved fund-category labels that have nothing to do with the fabrication
problem this research addresses.

## Companion recommendation

Verified against `registry.py`: of the tickers referenced by the two hardcoded-
list functions, `SPY`, `VUAA`, `SLV`, `IEF`, `ISLN`, `SGLD`, `ICOM` **are**
curated in `INSTRUMENT_DEFINITIONS` (so removing the hardcoded lists does not
affect value sourced through them — the legitimate fund-category override
already covers them, except SPY/VUAA which are curated `"Broad Market"`
category, deliberately outside the override's whitelist, correctly not
sector-substituted). But **`XLF`, `XLV`, `IBB`, `ITA`, `PPA`, `BIL`, `VGSH`,
`DBC` are not present anywhere in `registry.py`** — confirmed by direct grep,
zero matches. Removing the hardcoded-list fallback, with no companion action,
means any constituent value sourced *only* through one of these eight funds
moves from a guessed label (`"Financials"`, `"Health Care"`, `"Defense"`,
`"Fixed Income"`, `"Commodities"`) to `"Unclassified"` — correct per this
research's rule, but a visible, sizeable shift if any of these funds are
material in the bound statement.

**Recommendation for the design pass:** curate these eight tickers into
`INSTRUMENT_DEFINITIONS` with their real `sector`/`category` (mirroring how
`SLV`/`ICOM`/`SGLD`/`ISLN`/`IEF` are already curated) as a companion change to
Story A. This is the *correct* way to preserve the legitimate fund-category
labels — through the same static, human-reviewed tier US-37.1 already
established as trustworthy without an identity gate — rather than through the
divergent, hardcoded, un-synced pattern-matcher being removed. This is a data
addition (eight dict entries), not a new resolution mechanism, and is
explicitly **not** a decision this research makes on the schema owner's behalf;
it is named here because it is the direct, load-bearing consequence of the
rule above, not an optional nice-to-have. Whether it ships inside Story A or as
a fast-follow is the design pass's / story-author's call.

## Trust-class analysis

| Output | Truth class | Trust level | Basis |
|---|---|---|---|
| `LookThroughSectorExposure.sector` resolved via static registry (constituent's own symbol, or fund-category override) | snapshot analytics | resolved (curated) | human-reviewed `INSTRUMENT_DEFINITIONS` entry — same tier as US-37.1's `"static"` |
| `LookThroughSectorExposure.sector = "Unclassified"` | snapshot analytics | unresolved, honestly disclosed | no source resolved a sector; value is counted, never dropped, never guessed |
| `EtfOverlapPair.sector_overlap[].sector` (shared-symbol case) | snapshot analytics | resolved (curated) or `"Unclassified"`, same rule as above | mirrors `build_lookthrough_sector_exposure` |
| `FactorExposurePoint` sector-tilt fields reading `sector_weights.get(<label>, 0.0)` (`build_factor_exposures`, `risk.py:1079-1099`) | snapshot analytics (derived from the same sector totals) | unchanged mechanically, but `"Defense"`/`"Fixed Income"`/`"Commodities"` tilts will read `0.0` for any weight that moves to `"Unclassified"` post-fix, until/unless the companion recommendation is applied | these factor labels are keyed directly on the removed hardcoded strings for XLF/XLV/IBB/ITA/PPA/BIL/VGSH/DBC-sourced value — see § Companion recommendation |

No output in this research crosses into `synthetic` or `verified` — sector
exposure remains snapshot analytics throughout (current holdings, no return
history), consistent with the existing methodology doc's classification. No
new `classification_source` value is introduced; this research recommends
*not* extending that enum to look-through constituents (they have no
`ImportedInstrument`/ISIN to carry provenance for in the first place) — a
constituent either resolves via the static registry (same evidentiary basis as
`"static"`) or does not.

## Open decision: suppression threshold

`build_lookthrough_sector_exposure`'s existing `MIN_SECTOR_WEIGHT = 0.0005`
(0.05%) filter (`risk.py:1064-1067`) suppresses any bucket — including a small
`"Unclassified"` bucket under the proposed rule — from the returned list
entirely (weight still counted in the denominator, just not itemized).
`overview.py`'s own `"Unclassified"` precedent (US-37.1, the pattern this
research is asked to reuse) has **no equivalent floor** — every sector,
however small, is always itemized. This is a genuine inconsistency between the
two Unclassified implementations if left as-is, though it predates this
research (the filter already suppresses small *real* sectors the same way) and
is not one of the three named fallback sites. Flagged for the design pass /
story-author to decide explicitly — exempting `"Unclassified"` from the filter
would match the `overview.py` precedent and guardrail 4's disclosure bias;
leaving it as-is is defensible for genuinely negligible residuals but should be
a stated choice, not an accidental carry-over.

## Draft methodology-doc section

For `docs/finance/financial-methodology.md`, as an amendment appended to the
existing `## Sector/Industry Classification — Source and Resolution (US-37.1)`
section (not a new top-level section — this is the same classification
concept, extended to a second code path the existing section explicitly
scoped out). Ready for docs-engineer to apply verbatim at close-out; not
applied to the doc by this research order.

```markdown
### ETF look-through constituent classification (Story A)

The scope note above excluded ETF look-through constituent classification.
This subsection covers it.

A look-through constituent's identity is a bare ticker sourced from
`MarketDataService.get_etf_holdings(...)` (FMP's own ETF-holdings feed) — there
is no broker-statement ISIN backing it, unlike a directly-held equity. The
identity-gate mechanism above (statement ISIN vs. FMP profile ISIN) therefore
has no applicable input for a look-through constituent: AC5's "missing ISIN
evidence on either side" branch is not an edge case here, it is the only
reachable outcome. Look-through constituent classification accordingly has
only two tiers, not three:

1. Static registry lookup (`InstrumentRegistry.get_instrument(symbol).sector`),
   unconditional — same tier as direct-equity classification's `"static"` tier,
   unaffected by this section.
2. Nothing resolved → `UNCLASSIFIED_SECTOR_LABEL` ("Unclassified",
   `app/analytics/overview.py:13`) — no dynamic FMP lookup is attempted for a
   look-through constituent, at any point, because the identity evidence a
   dynamic lookup would need to be trustworthy structurally does not exist for
   this input.

Per-source-slice attribution (each ETF/direct position contributing to one
constituent's value is classified independently) is unchanged and unaffected:
a constituent partially sourced from a fund whose own category is curated
(e.g. a Bond/Commodity/Sector/Thematic ETF with its own `.sector` set) has that
slice classified by the *fund's* curated sector, not by attempting an
equity-style lookup on a non-equity holding. This fund-category override
predates and is unaffected by Story A.

Consequence: `LookThroughSectorExposure` and `EtfOverlapPair.sector_overlap`
totals may split a single ETF's look-through value across a real sector and
`"Unclassified"` in the same response — this is the honest outcome of partial
resolution, not an error state, and mirrors the direct-equity Unclassified
bucket's own contract rules (never dropped from the weight total, never merged
into `"Other"`).

Implementation:
- `services/quant-engine/app/analytics/risk.py` —
  `build_lookthrough_sector_exposure(...)`, `_build_shared_sector_overlap(...)`

Contract rule:
- a look-through constituent's sector is either curated (`"static"`-equivalent,
  via the static registry) or `"Unclassified"` — there is no dynamic,
  FMP-sourced tier for look-through constituents, because no identity evidence
  exists to gate one
```

## Metrics inventory

One row per field this research's rule affects (existing fields; no new field
proposed).

| Field | Nullable? | Trust level | Change from this research |
|---|---|---|---|
| `LookThroughSectorExposure.sector` (list item) | no — string, but may now be the literal `"Unclassified"` | resolved (static) or honestly-unresolved | unresolved value no longer guesses a label |
| `LookThroughSectorExposure.market_value` / `.weight` | no | unchanged — snapshot analytics | unaffected; totals still reconcile, just re-bucketed |
| `EtfOverlapPair.sector_overlap[].sector` | no — same "Unclassified" possibility | resolved (static) or honestly-unresolved | same fix, `_build_shared_sector_overlap` |
| `FactorExposurePoint` (Defense/Fixed Income/Commodities tilts) | no — numeric, defaults to `0.0` when the sector key is absent from `sector_weights` | unchanged mechanically | value may shift toward 0.0 unless § Companion recommendation ships alongside |
