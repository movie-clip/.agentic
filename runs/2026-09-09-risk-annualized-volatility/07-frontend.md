REPORT 2026-09-09-risk-annualized-volatility/07
status:      DONE
verdict:     NONE

changed:
  - apps/desktop/src/features/portfolio/types.ts — added `RiskTabVolatilityTrust` (`'synthetic' | 'withheld' | 'unavailable'`) and `RiskTabAnnualizedVolatility` types mirroring the Pydantic models; added the required `risk_tab_volatility` field to `ImportedDiagnosticsSource` (its alias `DiagnosticsEngineResponse` is the only other TS shape mirroring `DiagnosticsResult`).
  - apps/desktop/src/app/App.tsx — threaded `diagnosticsAnalysis={diagnosticsAnalysis}` into `<RiskPanel>` (~line 912); no new fetch, no new adapter function.
  - apps/desktop/src/features/portfolio/RiskPanel.tsx — added the required `diagnosticsAnalysis: DiagnosticsEngineResponse | null` prop to `RiskPanelProps`; mounted `<AnnualizedVolatilityCard>` in `.risk-shell-stack` after `VarDistributionCard`, fed `diagnosticsAnalysis?.risk_tab_volatility ?? null`.
  - apps/desktop/src/features/portfolio/AnnualizedVolatilityCard.tsx — NEW prop-driven card (`{ volatility: RiskTabAnnualizedVolatility | null }`), no self-fetch, no WindowSelector. CardShell + TrustBadge, tokens only, `tabular-nums` figure. Renders the four states per plan 05 § 1.5 (loading / synthetic / withheld / unavailable).

verification:
  command:   cd apps/desktop && npx tsc --noEmit && npx vitest run src/features/portfolio
  result:    PASS
  detail:    tsc: 7 errors, all in T-44.1.3-owned test/fixture files, 0 in my 4 source files — 6x RiskPanel.test.tsx TS2741 missing new required 'diagnosticsAnalysis' prop; 1x src/test/portfolioFixtures.ts:994 TS2741 "Property 'risk_tab_volatility' is missing" (fixture-shape, exactly as the order predicted). vitest src/features/portfolio: 272 passed / 28 files, 0 failed (incl RiskPanel.test.tsx — vitest does not type-check, so the missing prop is undefined at runtime and the card renders LoadingState).

contract_notes:
  - docs/contracts/risk-fields.md — must match the card's withheld-state copy: title "Annualized volatility withheld"; detail "{observations} of {minimum_observations} paired portfolio and benchmark trading days available. An annualized volatility projected from fewer than {minimum_observations} paired trading days is not published here. Dashboard shows an unfloored estimate."
  - docs/contracts/risk-fields.md — the card's unavailable-state copy: title "Annualized volatility unavailable", detail "No paired portfolio and benchmark return history is available for this portfolio yet."
  - docs/contracts/risk-fields.md — methodology reference (AC 12): the synthetic-state helper cites financial-methodology.md §"Annualized realized volatility" and the "{minimum_observations} paired trading days" publication threshold.

pack_corrections:
  - none

handoff:
  - For T-44.1.3: `AnnualizedVolatilityCard` prop shape is `{ volatility: RiskTabAnnualizedVolatility | null }`. `null` -> `LoadingState` message "Computing annualized volatility…". Otherwise the render branches on `volatility.trust`.
  - For T-44.1.3: `trust === 'synthetic'` -> row "Portfolio volatility (annualized)" = `${annualized_volatility_pct.toFixed(2)}%` + `TrustBadge type="synthetic"` + methodology helper.
  - For T-44.1.3: `trust === 'withheld'` -> `EmptyState` title "Annualized volatility withheld" (no number, no badge); `trust === 'unavailable'` -> `EmptyState` title "Annualized volatility unavailable" (no badge). Distinct by title + detail copy.
  - For T-44.1.3: `RiskPanelProps` now REQUIRES `diagnosticsAnalysis: DiagnosticsEngineResponse | null`. The 6 `RiskPanel.test.tsx` render sites (lines 114, 127, 146, 167, 189, 209) each need the prop added — that is the sole cause of the 6 tsc TS2741 errors there.
  - For T-44.1.3: `src/test/portfolioFixtures.ts` diagnostics fixture (~line 994) needs `risk_tab_volatility` added to satisfy the now-required field; add `AnnualizedVolatilityCard.tsx` to `ALL_CARD_FILES` and `CARDS_WITH_BADGE` in `designSystem.audit.test.ts`. `dashboardGoldens.ts` did NOT surface under tsc — confirm during regen whether it constructs a full diagnostics shape.
  - I did NOT extend `TrustBadge` — union stays `'synthetic' | 'unavailable'`. Withheld/unavailable carry the distinction via distinct `EmptyState` copy alone (plan 05 § 2 Frontend last bullet; AC 10 satisfied). Reason: ~20 files import `TrustBadge`; the fallback is explicitly sanctioned.
  - RiskPanel now hosts four cards, not three — `RiskPanel.test.tsx` wording/assertions that say "all three cards" should become four.

risks:
  - Frontend pack says "`withheld` … always show their badge". I render no header badge in the withheld state (only `EmptyState` titled "…withheld"), which I judged renders the state visibly and matches plan 05 § 1.5. A reviewer wanting the badge needs the optional `TrustBadge` `'withheld'` union extension.
  - `verification.result` is recorded PASS against the order's lane-specific criterion ("tsc MUST be clean on your changed source files" + every remaining failure attributable to T-44.1.3). The raw `tsc --noEmit && vitest` command exits non-zero because of the 7 T-44.1.3-owned test/fixture errors; none are in my source.
  - `--font-section-title` (used by `StressScenariosCard.tsx` for its figure) is not defined in `styles.css` `:root`; I used the defined `--font-heading-sm` for the card's figure instead. Not touching the StressScenariosCard dead token — out of scope.
  - App state `diagnosticsAnalysis` is `null` until the Dashboard's diagnostics fetch resolves, and stays `null` if `analyzeExposureSnapshot` threw (scout risk). In that failure mode the card shows `LoadingState` indefinitely — there is no error branch on this prop because RiskPanel does not own the fetch.
