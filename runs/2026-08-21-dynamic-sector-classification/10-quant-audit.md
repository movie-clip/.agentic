REPORT 2026-08-21-dynamic-sector-classification/10
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   independent recomputation (see § Independent verification log) — no pytest run per non_goals
  result:    PASS
  detail:    anchor: external (live FMP re-call, fresh ticker sample) for the taxonomy map; anchor: methodology-doc for wiring/edge-case checks; anchor: independent hand-derivation for HHI/weight-sum invariant — see body for all commands and numbers

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - FINDING 1 fix: registry.py:337-346's catch-all Instrument hardcodes sector="Other" — see § Findings
  - FINDING 1 fix direction: route that catch-all through None/UNCLASSIFIED_SECTOR_LABEL, not a literal
  - FINDING 2 fix candidate: normalize FMP sector string casing/whitespace before the taxonomy lookup

risks:
  - No open position in docs/IB2026.csv exercises the live fmp_identity_confirmed path end-to-end
  - INTU/PANW/VICI/SPCX are closed round-trips per the statement's own Open Positions section, not held
  - Test lane correctly used synthetic fixtures instead — coverage-shape observation, not a defect
  - MarketDataAuthError is deliberately swallowed by resolve_equity_sector, per the design doc's own call
  - A misconfigured FMP_API_KEY would silently degrade every non-static equity with zero disclosure
  - That tradeoff is pre-existing and documented, not new to this audit — surfaced for visibility only

## Orchestrator brief

- Verdict: FAIL — one MATERIAL finding, AC9/doc-contradicting. Taxonomy map, identity gate, trust labeling, and the aggregation seam's happy-path are all independently verified correct.
- FINDING 1 (MATERIAL): `attach_snapshot_metadata`'s pre-existing, untouched no-imported-instrument catch-all (`registry.py:337-346`) still hardcodes `sector="Other"`, which survives this story's fix (`instrument.sector or UNCLASSIFIED_SECTOR_LABEL` treats "Other" as truthy) and reaches the UI as the literal string this story exists to eliminate. Contradicts AC9 and the new methodology section's own "no fourth outcome" rule. Independently reproduced numerically — see § Findings.
- FINDING 2 (MINOR): `SECTOR_TAXONOMY_MAP.get(profile["sector"])` is a case-sensitive raw dict lookup with no defensive normalization (unlike the ISIN side, which normalizes). Fails safe today (falls to `unavailable`, never fabricates) but is untested against casing/whitespace drift — the exact edge case this order's DoD named. Not blocking.
- All 11 `SECTOR_TAXONOMY_MAP` entries independently re-verified against a **live, fresh** FMP sample (11 tickers none of which appear in the research brief's own verification set) — zero divergence. This is a genuine external anchor, not a doc-consistency check. See § Independent verification log.
- Identity gate, trust-classification honesty, and the "Unclassified" bucket's participation in `sector_hhi`/`top_sectors`/weight totals were independently re-derived (hand-written script, not the shipped tests) and matched the engine exactly, including a hand-computed HHI = 0.625 case. See § Independent verification log.
- Methodology doc's new § "Sector/Industry Classification — Source and Resolution" checked against the actual merged code, doc-as-spec direction: matches on every claim checked (resolution order, taxonomy table, opt-in wiring, `classification_source` values, caching TTL) — **except** the "Unclassified... never silently folded into any named sector including 'Other'" contract-rule claim, which Finding 1 falsifies on the untouched catch-all path.
- No duplicated ISIN-comparison or sector-taxonomy logic found elsewhere in the codebase; `risk.py`'s ETF look-through mechanism is a separate, pre-existing, keyword-based path, explicitly and correctly scoped out by the new doc section.
- Sections below, in order: Independent verification log; Findings; Trust-classification review; Edge cases exercised; Not re-derivable.

---

## Independent verification log

Every number below was produced by a script I wrote independently against the actual merged code (not by reading or trusting the shipped tests), per this lane's "re-derive, don't re-read" mandate.

**1. Taxonomy map — external anchor, live FMP, fresh ticker sample.**
Loaded `FMP_API_KEY` from `services/quant-engine/.env` and called FMP's `/stable/profile` endpoint directly via `curl` (bypassing the app entirely — a genuinely independent path), for 11 tickers **none of which appear in `02-quant-research.md`'s own live-verification set**:

```
PFE -> Healthcare            (map: Health Care)       ✓
GS  -> Financial Services    (map: Financials)         ✓
HD  -> Consumer Cyclical     (map: Consumer Discretionary) ✓
WMT -> Consumer Defensive    (map: Consumer Staples)   ✓
FCX -> Basic Materials       (map: Materials)          ✓
MSFT-> Technology            (map: Technology)         ✓
XOM -> Energy                (map: Energy)             ✓
GE  -> Industrials           (map: Industrials)        ✓
O   -> Real Estate           (map: Real Estate)        ✓
DUK -> Utilities             (map: Utilities)          ✓
DIS -> Communication Services(map: Communication Services) ✓
```

All 11 `SECTOR_TAXONOMY_MAP` entries (`equity_sector_resolution.py:39-51`) confirmed correct against live current FMP data, independent of the research brief's own sample. `anchor: external`.

**2. Weight-sum / HHI invariant — independent hand-derivation.**
Wrote a standalone script (not the shipped `test_analytics.py` test) building a 2-position snapshot (AAPL $300 static-registry hit, ZZZ9 $100 unclassified, FMP mocked to return no profile) and ran it through `build_portfolio_overview` + `_build_current_state_concentration`:

```
sector_allocation: Technology $300 (w=0.75), Unclassified $100 (w=0.25)
weight sum:        1.0
hand-computed HHI: 0.75^2 + 0.25^2 = 0.625
engine sector_hhi: 0.625                    -- exact match
engine top_sectors includes Unclassified;  engine top_sector_weight = 0.75
```
`anchor: closed-form hand computation`. Confirms "Unclassified" is never dropped from the weight total and is never double-counted or excluded from concentration math (DoD's explicit ask).

**3. Zero-weight position.** Same harness with a $0 ZZZ9 position: `Unclassified` bucket still appears (`weight=0.0`, `market_value=0.0`), weight sum still `1.0`, no division-by-zero. Correct.

**4. ISIN normalization edge cases.** `normalize_isin("   ")`, `normalize_isin("")`, `normalize_isin(None)` all return `None`; `normalize_isin("us0378331005")` returns `"US0378331005"` — confirmed directly, matches AC5's "no evidence either side" contract and the "both-blank-string" parametrized test's own claim.

**5. Casing/whitespace drift on the FMP `sector` string itself (not the ISIN).** `resolve_equity_sector` with `sector="technology"`, `"TECHNOLOGY"`, `" Technology"`, `"Technology "` (statement ISIN matching) all four produced `(None, "unavailable")` — the taxonomy lookup is case-sensitive and un-normalized, so any casing drift fails closed rather than resolving. Safe (never fabricates), but untested and undefended — see Finding 2.

**6. The no-imported-instrument catch-all — reproduced, contradicts AC9.** Built a snapshot with one position (`GHOST1`) and **zero** matching `ImportedInstrument` records (a data-completeness gap the project's own "Importer resilience rule" in `financial-methodology.md` documents as reachable via a malformed/dropped record). Ran it through `build_portfolio_overview`:

```
overview.sector_allocation == [{'sector': 'Other', 'market_value': 100.0, 'weight': 1.0}]
```

Confirmed via `git diff` that `registry.py:337-346` (the catch-all `Instrument(...)` construction with the literal `sector="Other"`) was **not modified** by this story's diff — it predates US-37.1 and was not in scope for T-37.1.1/T-37.1.2's changes, but it is reached through the exact seam (`overview.py`'s `instrument.sector or UNCLASSIFIED_SECTOR_LABEL`) this story rewired, and `"Other"` is truthy so `or UNCLASSIFIED_SECTOR_LABEL` never fires. See Finding 1.

**7. Real bound statement — confirmed the four "Other" equities are not open positions.** Ran the actual IBKR CSV importer against `docs/IB2026.csv` and diffed `snapshot.positions` symbols against `snapshot.instruments` symbols: zero positions lack a matching instrument record (Finding 1's catch-all is not reached by *this* statement). Separately confirmed via the statement's own `Open Positions` section that INTU, PANW, SPCX all show `Quantity=0` in Mark-to-Market (closed round trips) and VICI appears only in a dividend/withholding line, never in `Open Positions,Data,Summary,Stocks`. The technical plan's own flagged risk ("whether these four are open positions... unconfirmed") resolves to **no** — matching `statement_truths.py::IB_SECTOR_EXAMPLES`'s correct omission of all four and the test lane's correct choice to use a synthetic `ZZZ9` fixture instead of pinning these four.

## Findings

```
FINDING 1
severity:   MATERIAL
where:      services/quant-engine/app/instruments/registry.py:337-346 (attach_snapshot_metadata's
            no-imported-instrument catch-all), consumed by app/analytics/overview.py:56-58
claim:      docs/finance/financial-methodology.md § Sector/Industry Classification, "Contract rule":
            "an equity's sector is either curated, FMP-sourced and identity-confirmed, or
            unresolved — there is no fourth outcome, and an unresolved equity is disclosed as
            'Unclassified', never silently folded into any named sector including 'Other'."
            AC9 makes the identical claim ("never the string 'Other'").
actual:     For a position with no matching ImportedInstrument record at all, attach_snapshot_metadata
            falls through to a pre-existing (untouched by this story, confirmed via `git diff`)
            catch-all that constructs Instrument(..., sector="Other", category="Imported Position").
            Because "Other" is a truthy string, overview.py's new line
            `sector = instrument.sector or UNCLASSIFIED_SECTOR_LABEL` never reaches the
            UNCLASSIFIED_SECTOR_LABEL branch for this instrument. Independently reproduced:
            a snapshot with one position (GHOST1, no matching instruments entry) through
            build_portfolio_overview() yields sector_allocation ==
            [{'sector': 'Other', 'market_value': 100.0, 'weight': 1.0}] — the literal string
            this entire story exists to eliminate.
impact:     A researcher would see a real position folded into a bucket literally named "Other"
            in a codebase that just spent a story eliminating exactly that fabrication elsewhere —
            worse, this specific path is silent and looks identical to the pre-fix, fully-general
            bug the story report will claim is fixed. This path is reachable in practice: the
            project's own "Importer resilience rule" (financial-methodology.md) documents that a
            malformed/dropped statement record yields a position with no corresponding
            instrument record — precisely the condition this catch-all exists to handle.
expected:   Route this catch-all's sector through the same None-then-UNCLASSIFIED_SECTOR_LABEL
            path as every other unresolved case — either construct it with sector=None
            (classification_source stays None, consistent with the design doc's own stated intent
            for this branch) and let overview.py's existing `or UNCLASSIFIED_SECTOR_LABEL` handle
            it, or special-case it in overview.py. The design pass's own risk analysis (05-technical-
            plan.md § Risks, "overview.py:50's residual dead branch") examined only whether
            metadata.get(position.symbol) can be None (correctly found unreachable) and did not
            examine that the catch-all Instrument object it returns still carries the literal
            "Other" through the new truthy check — this is the actual gap, not the one the design
            pass flagged and accepted.
```

```
FINDING 2
severity:   MINOR
where:      services/quant-engine/app/instruments/equity_sector_resolution.py:74
            (SECTOR_TAXONOMY_MAP.get(profile["sector"]))
claim:      Implicit in AC6/AC7 and the methodology doc's taxonomy table: an FMP sector string
            is correctly mapped or correctly falls through to unresolved — no third outcome.
actual:     The taxonomy lookup is a raw, case-sensitive dict .get() with no normalization of the
            FMP string (contrast: the ISIN side normalizes via normalize_isin — upper + strip).
            Verified: resolve_equity_sector with profile sector values "technology", "TECHNOLOGY",
            " Technology", "Technology " (ISIN matching) all four fall through to
            (None, "unavailable") rather than resolving to "Technology". Live-checked 15 distinct
            FMP tickers across this audit and the research brief; all returned consistent Title
            Case today, so this has not yet manifested — but it is exactly the edge case this
            order's DoD named ("FMP returning a sector string with different casing/whitespace
            than the taxonomy map's keys") and it is untested.
impact:     Fails safe today (degrades a resolvable equity to Unclassified rather than fabricating
            a wrong sector or passing an unmapped string through) — not a guardrail violation. But
            a future FMP formatting change (provider-side casing/whitespace drift) would silently
            move previously-classified equities into "Unclassified" with no test catching the
            regression and no error surfaced, since the failure mode is identical in shape to
            genuine no-coverage.
expected:   Either a documented, deliberate decision that raw matching is intentional (acceptable
            if stated), or a normalized lookup (e.g. .strip() the FMP sector string, matching the
            ISIN side's discipline) plus a regression test pinning at least one casing-variant
            case. Not blocking — recommend as a should-fix alongside Finding 1.
```

## Trust-classification review

- `classification_source="fmp_identity_confirmed"` is set in exactly one `return` statement (`equity_sector_resolution.py:81`), gated by `statement_isin and profile_isin and statement_isin == profile_isin` — all three conditions truthy-checked, no path sets this value without both ISINs actually matching. Confirmed by reading every `return` in the function; no other call site sets this literal.
- `"unavailable"` never leaks downstream as a plausible-looking sector string: it is a `classification_source` value, never assigned to `Instrument.sector` itself (`sector` stays `None` on every `"unavailable"` return). `overview.py` converts `None` sector to the honestly-named `"Unclassified"` bucket, never to a value that could be mistaken for a real GICS sector — confirmed by grep, no code path assigns the literal string `"unavailable"` to any sector field.
- `"Unclassified"` is never confused with a real GICS sector name in aggregate math: `sector_hhi`/`top_sectors`/`top_sector_weight` (`exposure_engine.py:220-238`) iterate the full, unfiltered `overview.sector_allocation` list — no special-casing, confirmed by reading the function and by the independent HHI recomputation above (§ log item 2), which matched the engine's own output exactly with "Unclassified" included as a genuine bucket.
- `"static"` is set unconditionally on every static-registry hit (`_merge_known_instrument_metadata`), regardless of what else is merged — confirmed no branch skips it.
- `MarketDataAuthError` handling is a deliberate, named divergence documented in `05-technical-plan.md` § Decisions (swallowed like every other exception, unlike `get_company_profile`'s convention for other callers). Not a new finding — flagged in `risks` for visibility since it means a systemic auth misconfiguration is indistinguishable, at the field level, from "genuinely unclassifiable" for every affected equity.

## Edge cases exercised

| Case | Result | Matches DoD expectation |
|---|---|---|
| Empty ISIN both sides | `(None, "unavailable")` | yes |
| ISIN present one side only | `(None, "unavailable")` | yes |
| FMP sector casing/whitespace divergent from map key | `(None, "unavailable")` — fails safe, untested (Finding 2) | fails safe, not ideal |
| Zero-weight Unclassified position | Included as its own bucket, weight=0.0, total still 1.0 | yes |
| Weight total before/after an Unclassified bucket | Sums to 1.0 in both the 2-position and 1-position cases tested | yes |
| No-imported-instrument-record position | `sector="Other"` (literal) — **violates AC9** | **no — Finding 1** |
| ISIN match (case/whitespace-insensitive) | Resolves correctly via normalize_isin | yes |
| ISIN mismatch | `(None, "unavailable")`, never the FMP value | yes |
| FMP raises | `(None, "unavailable")`, no propagation, other symbols unaffected (per-call isolation) | yes |
| Unmapped FMP sector string | `(None, "unavailable")`, never passed through raw | yes |

## Not re-derivable

- Could not re-run `python scripts/run_all_tests.py` per this order's explicit `non_goals` (that verification already happened in T-37.1.4). All numbers above come from standalone scripts I wrote against the actual merged modules, not from the shipped test suite.
- Did not attempt to reproduce a fresh ticker-collision case beyond the research brief's DFNS finding — the identity gate's correctness is structural (verified by reading `resolve_equity_sector` and by the ISIN-mismatch test above), not dependent on finding a new collision; a mismatch of any kind, regardless of cause, resolves to `(None, "unavailable")`.
- No live network access was used against the real production FMP quota beyond the 11 read-only `/profile` calls in § Independent verification log item 1 — kept minimal and disjoint from the research brief's own sample by design.
