REPORT 2026-08-24-etf-sector-classification-research/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only recon order, no verification command named

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - SBIO IS in `docs/IB2026.csv` (lines 84,165,244,437-438,764): held position, 5 units, listing_exchange `LSEETF`, instrument_type `ETF`, description "INVESCO NASDAQ BIOTECH", ISIN IE00BQ70R696.
  - SBIO is NOT in `InstrumentRegistry.INSTRUMENT_DEFINITIONS` (registry.py:56-173) — no curated entry, unlike XLF/XLV/IBB/SLV/IEF etc.
  - Because instrument_type=="ETF", `attach_snapshot_metadata` (registry.py:346-348) routes SBIO through `classify_imported_instrument`'s ETF branch (registry.py:246-292), not the equity branch and not the risk.py look-through path — those are the two paths US-37.1/US-38.1 fixed; this is a third, untouched path.
  - Traced live: description "INVESCO NASDAQ BIOTECH" contains no "UCITS"/"ETF"/"ETC" substring but instrument_type=="ETF" alone enters the branch; listing_exchange=="LSEETF" sets category to "UCITS ETF"; the "BIOTECH" in description_upper elif (registry.py:270-272) then matches, so SBIO currently lands as sector="Health Care", category="Sector UCITS ETF" — NOT "Unclassified" and NOT "Other" today.
  - This "Health Care" label is produced entirely by keyword substring-matching on the ETF's own free-text description inside `classify_imported_instrument` (registry.py:246-282) — no FMP/market-data call is made for the ETF branch at all, ever (market_data param is only consulted in the equity branch, registry.py:301).
  - If SBIO's description had not contained a recognized keyword, the ETF branch's fallthrough default is sector="Broad Market" (registry.py:247-248) — a silently wrong label, not "Unclassified"/"Other" — this fallthrough is the latent failure mode for any uncurated ETF whose name text doesn't hit one of the ~10 hardcoded elif keywords.
  - `docs/tech-debt-register.md:186` already tracks this exact mechanism, still open: "instrument_registry.py:45-48,180-261 ... keyword-substring sector classifier (get_sector fallback chain ~209-242) ... the keyword classifier is the fragile part" — tagged epic-24, never marked RESOLVED.
  - This is distinct from tech-debt-register.md:177 (F-B), which US-38.1 marked RESOLVED — that row was risk.py's look-through proxy-ticker-list functions (`_infer_sector_from_sources`/`_infer_sector_from_resolved_pair`), now deleted; registry.py's ETF-branch keyword matcher was never touched by that fix.
  - Epic 37 PRD non-goal (epic-37-...md:58-61) and Epic 38 PRD non-goal (epic-38-...md:56-61) both explicitly scope out "ETF-side FMP sector reliability" / "re-deriving ETF-level sector classification from FMP directly," citing FMP's `sector` field returning the fund sponsor's own classification for both SPY and GRID (e.g. "Financial Services") rather than a thematic one — see § Prior art below for exact wording.
  - current-product-state.md:83-87 documents this as the still-open "narrower remainder of tech-debt-register.md's F-B row" but only in the context of the look-through path (US-38.1) — it does not mention the direct-holding ETF-branch keyword matcher in registry.py at all, so that mechanism is undocumented in current-product-state.md.
  - No row in epic-roadmap.md's "Open items" (lines 14-52) names this direct-held-ETF-ticker gap specifically; the only live tracking is tech-debt-register.md:186 (general) and the F-B narrower-remainder note (look-through-specific, not this).
  - INSTRUMENT_DEFINITIONS already curates ~40 ETFs with real sector/category (XLF, XLV, IBB, ITA, PPA, BIL, VGSH, DBC added by US-38.1; SLV, ICOM, SGLD, ISLN, IEF, GLD, TLT, AGG, BND, SPY, VOO, IVV, VTI, VT, VEA, VWO, QQQ, VNQ, plus UCITS variants DFND, IAUP, IDFN, VDST, COPX, CIBR, SXRV, VUAA, BTEC, IUFS, IUHC, IUIT, SEMI) — SBIO is simply an uncurated ETF that the same manual-curation treatment could cover for itself, but manual curation does not scale to "any arbitrary ETF ticker" a future statement might hold.
  - Client methods already wired: `fmp.py` `get_profile(symbol)` (line 349-350, the flagged-unreliable-for-ETFs sector field), `get_etf_holders(symbol)` (line 376, used for look-through only), `get_sp500_constituents`, `get_screener_results(...,sector=,is_etf=)` (line 467+). No ETF-specific profile/category/sector-weighting endpoint (e.g. FMP's etf-info or sector-weighting endpoints) is implemented anywhere in fmp.py.
  - `yfinance_client.py` has no ETF metadata/sector method at all — only `get_historical_price_light` for UCITS price fallback (per docstring at line 4).
  - No test fixture or golden file references SBIO or an analogous uncurated-ETF scenario anywhere under `services/quant-engine/app/tests/` — only the bound statement (`docs/IB2026.csv`) and its derived goldens (`apps/desktop/src/test/dashboardGoldens.ts`, `services/quant-engine/app/scripts/golden_market_data.json`) contain the string "SBIO".
  - `Instrument.classification_source` (schemas/instruments.py:22) is `Literal["static","fmp_identity_confirmed","unavailable"] | None` — the ETF branch never sets it (registry.py's `_instrument()` calls in the ETF branch pass no classification_source, defaulting to None), so even SBIO's current "Health Care" label carries no provenance/trust marker distinguishing it from a curated static entry.

risks:
  - none

## Orchestrator brief
Traced SBIO end-to-end: it is a held ETF position (docs/IB2026.csv), uncurated
in INSTRUMENT_DEFINITIONS, and today lands as sector="Health Care" purely via
a keyword-substring match ("BIOTECH" in its free-text description) inside
`classify_imported_instrument`'s ETF branch (registry.py:246-292) — a third
code path, never touched by Epic 37 (equity branch) or Epic 38 (risk.py
look-through). It is not "Unclassified"/"Other" today, but the mechanism is
fragile and undocumented: an ETF whose name lacks a recognized keyword
silently defaults to "Broad Market" instead. This exact mechanism is already
tracked, open, in tech-debt-register.md:186 (distinct from the now-RESOLVED
F-B row at line 177). Both Epic 37 and Epic 38 PRDs/stories explicitly scoped
out "re-deriving ETF-level sector from FMP directly," citing SPY/GRID both
returning "Financial Services" from FMP's own sector field — see handoff
bullets for exact citations. No dedicated ETF-profile/category/sector-
weighting client method exists in fmp.py or yfinance_client.py today.
