REPORT 2026-09-09-risk-annualized-volatility/12
status:      DONE
verdict:     NONE

changed:
  - docs/finance/financial-methodology.md — AMENDED the existing "Annualized realized volatility" section (no new section); no new section added.
  - docs/finance/financial-methodology.md — added the Risk-tab publication floor: N = paired `risk_summary.observations`; N=0 → unavailable, 1..59 → withheld (never collapsed), ≥60 → published `synthetic`.
  - docs/finance/financial-methodology.md — added the zero-variance-at-floor → `0.00%` human ruling.
  - docs/finance/financial-methodology.md — added the `RISK_TAB_ANNUALIZED_VOL_MIN_OBSERVATIONS = 60` constant, distinguished from `MIN_DAILY_OBSERVATIONS` (20) and `WINDOW_MIN_OBSERVATIONS`.
  - docs/finance/financial-methodology.md — added the chi-square grounding with citations (02-quant-research § 2.4), and stated the Dashboard surface is unchanged/unfloored. Text matches quant-audit § A4's clause-by-clause check.
  - docs/contracts/risk-fields.md — NEW section "US-44.1 — Portfolio Annualized Volatility (Risk tab)" documenting the `risk_tab_volatility` object across backend type ↔ TS type ↔ UI surface (`AnnualizedVolatilityCard`).
  - docs/contracts/risk-fields.md — the new section's four fields: `annualized_volatility_pct` (float|None / number|null, non-null iff published), `trust` (synthetic|withheld|unavailable), `observations` (int), `minimum_observations` (int).
  - docs/contracts/risk-fields.md — new section also carries: a "Trust vocabulary extension" note that `withheld` extends the file preamble for this one figure; a note that the figure is sourced from the diagnostics engine, not a Risk-tab engine; a trust-state table; and verbatim withheld/unavailable/helper/tooltip copy pinned to `AnnualizedVolatilityCard.tsx`.
  - docs/contracts/risk-fields.md — updated the "UI rendering" section from "three Risk-tab cards" to "four" and recorded that `TrustBadge` was not extended.
  - docs/contracts/diagnostics-fields.md — CROSS-REFERENCE added in the `volatility_summary` block (~line 224): `risk_tab_volatility.annualized_volatility_pct` is the publication-gated Risk-tab view of `volatility_summary.portfolio_volatility_pct` — same source scalar, same code path, plus a 60-paired-observation floor; the `volatility_summary` field itself is unchanged.
  - docs/contracts/dashboard-fields.md — one-line note on the Portfolio Volatility row (line 237): the Dashboard figure has no minimum-observation floor (publishes from N ≥ 2, `0.00%` at N = 1); US-44.1 added the 60-paired-observation floor to the Risk-tab view only, this row is unchanged.
  - docs/product/current-product-state.md — inventory add under "### Risk": portfolio annualized volatility is now in shipped Risk-tab scope, with its 60 paired-observation publication floor and the withheld/unavailable distinction.
  - docs/product/stories/US-44.1-risk-tab-annualized-volatility.md — Status Backlog → Done; `Last updated:` stays 2026-09-09 (today).
  - docs/product/stories/US-44.1-risk-tab-annualized-volatility.md — replaced the "draft for human review / not approved" banner with a delivered-2026-09-09 note (gates PASS, 12 ACs confirmed, suite green).
  - docs/product/stories/US-44.1-risk-tab-annualized-volatility.md — converted the "Open decisions (block ticketing)" block to "Open decisions (resolved at delivery)", recording each of the four resolutions and keeping the original draft text beneath.

verification:
  command:   none
  result:    NOT_RUN
  detail:    Read-only doc reconciliation; no verification command in the work order and this lane has no Bash. Canonical suite was green at the review gate (11-review.md: run_all_tests.py exit 0, backend 1001 passed, frontend 369 passed).

Reconciliation scope: six doc files reconciled against the shipped diff (06-backend,
07-frontend, 08-test `changed:` lists plus `AnnualizedVolatilityCard.tsx` read
directly). No code, schema, test, or card file touched. All contract_notes from
lanes 04/05/06/07 landed; see below.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Every `contract_note` from every lane is absorbed. Methodology amendment (05, 06, 04) → financial-methodology.md. Diagnostics-fields.md cross-ref (05, 06, 04) → done. Current-product-state.md inventory (05, 06) → done.
  - risk-fields.md §US-44.1 new section absorbs contract notes 05, 06, 04 and 07's three copy pins.
  - The schema→TS mirror note (05, 06) was already discharged by the frontend lane (types.ts) and is documented in the new risk-fields.md section.
  - Card copy strings for the withheld and unavailable states are now pinned in TWO places — `AnnualizedVolatilityCard.test.tsx` (substring asserts) and `docs/contracts/risk-fields.md` §US-44.1 "Verbatim card copy". Any future copy edit must move both.
  - No story-index, `epic-roadmap.md`, or PRD file exists to reconcile: the planning corpus was deleted in commit ce9c97d and is intentionally staying deleted. `docs/product/stories/US-44.1-risk-tab-annualized-volatility.md` is the only product-doc record of this slice; there is no epic snapshot row or slice-log entry to write.
  - Pre-existing nit left for a future order, not added to docs/tech-debt-register.md: `_calculate_annualized_volatility` (`analytics/risk.py:2120`) uses a literal `sqrt(252)` while `VOLATILITY_ANNUALIZATION_DAYS = 252` exists in the same module.
  - That nit is same-value/cosmetic, untouched by US-44.1, and below the register's "current, actionable" bar (its 5 open items are all substantive), so it is flagged here rather than as a low-value row. Also noted by quant-audit § A1/risks.
  - `AnnualizedVolatilityCard.tsx:38` `formatPct` has an unreachable `value == null → '—'` branch (only called in the `trust === 'synthetic'` block where the backend guarantees non-null). Flagged as SHOULD_FIX by 07/09/10; it is a code nit, not a docs concern, so no doc records it.

risks:
  - The story-file edit went slightly past a bare status-field flip: I also replaced the "draft / not approved" banner and rewrote the "Open decisions (block ticketing)" block as recorded resolutions (original draft text preserved beneath). Both claims directly contradicted "delivered", so leaving them would have left the file asserting the slice was unapproved and unbuilt.
  - The risk-fields.md "UI rendering" section said "All three Risk-tab cards"; I changed it to "four" and added the TrustBadge-not-extended note. This reconciles shipped state (RiskPanel now hosts four cards per 07/10), not opportunistic tidying, but it is an edit outside the strict "new section" target.
  - The methodology amendment cites the academic sources by name (Casella & Berger, Kenney & Keeping, Figlewski, Danielsson & Zigrand) and also points at `2026-09-09-risk-annualized-volatility/02-quant-research.md § 2.4` for the worked confidence-interval tables, as the order specified. A run-dir path is less durable than an in-repo reference; if the run artifacts are ever pruned, the CI-width tables become unreachable from the doc.
