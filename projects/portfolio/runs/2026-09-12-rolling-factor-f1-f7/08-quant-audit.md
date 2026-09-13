REPORT 2026-09-12-rolling-factor-f1-f7/08
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   cd services/quant-engine && pytest app/tests/test_analytics.py -k "rolling_loadings or factor_model" -v
  result:    PASS
  detail:    8 passed, 212 deselected in 7.67s. anchor: 5 fresh factor-model builds against the shipped engine (290d/16 proxies; 290d with XLE+XLU dropped; 150d; 100d; 40d), each paired with a line-by-line replication of the shipped badge resolver. Also ran the card's vitest file: 7 passed.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - FINDING 1 confirmed fixed for the case it named — model `partial` from a missing proxy now badges with the factors named. Closed. see § FINDING 1 — confirmed fixed
  - FINDING 3 confirmed fixed — the window-level `partial` test is honestly relabeled, and no other test in the repo treats that value as a live engine state. Closed.
  - FINDING 4 (MATERIAL, new, blocking) is a frontend fix in RollingFactorLoadingsCard.tsx:218 — gate model-level `partial` on the selected window's own `missing_factors`, not on model status. see § FINDING 4
  - FINDING 4's companion test change: RollingFactorLoadingsCard.test.tsx:106 currently pins the false tooltip as expected; it must invert to assert no badge. see § FINDING 4
  - FINDING 4 is a first-round finding on new behaviour introduced by CR-1, not a third round on FINDING 1 — the ledger's `Rounds` count should start at 1 for it.

risks:
  - The generic fallback tooltip becomes unreachable under FINDING 4's expected fix, because a non-empty `missing_factors` always populates an entry for all three windows. Removing it, rather than keeping it defensive, is the implementer's call.
  - Badge precedence (window-level checked before model-level, per 06-frontend.md § risks) is untested. Both branches render identical `Degraded` text, so only the tooltip differs; not a finding, but no test pins the order.

---

## Orchestrator brief

- Verdict: **FAIL**, on one new MATERIAL finding introduced by CR-1's fix. Both round-1 findings in scope are confirmed fixed.
- FINDING 1 (round-1 CRITICAL): **fixed and closed.** Reproduced case B against the shipped engine — model `partial`, all windows `ok`, badge now renders with the missing factors named ("energy, utilities"). Verified against the shipped .tsx, not the report's claim.
- FINDING 3 (round-1 MATERIAL): **fixed and closed.** The test at `RollingFactorLoadingsCard.test.tsx:80` now names itself a defensive branch and cites the unreachability proof. Repo-wide grep: no other test treats `windows[].status == "partial"` as live.
- FINDING 4 (MATERIAL, **new, blocking**): model `partial` also fires on short history alone, with every proxy present. At 100-274 shared observations the 20d and 60d fits are complete and seasoned, yet both now show `Degraded` with a tooltip claiming factor proxies are missing. Measured, not inferred.
- FINDING 4's fix is two lines and one test inversion — gate on `missingFactorKeysForWindow?.length`, not on `modelTrustStatus`. Exact expected in the section.
- The new test at `RollingFactorLoadingsCard.test.tsx:106` **pins** the false tooltip as correct, so this ships locked in unless FINDING 4 is routed.
- Not re-litigated, per the order: F7, and FINDING 2 (docs enum, lands with the close-phase docs dispatch).
- Sections below: **FINDING 1 — confirmed fixed**, **FINDING 3 — confirmed fixed**, **FINDING 4**, **Reproduction**.
- FINDING 4 blocks close-out. One lane, frontend + test.

---

## FINDING 1 — confirmed fixed

Checked against the shipped `RollingFactorLoadingsCard.tsx:206-222`, then reproduced
end to end.

- `modelTrustStatus` (line 206) reads `statistical_factor_model.status`; the two new
  branches at 218 and 220 degrade on model-level `partial` and
  `degraded_unverified_return_basis`.
- The `partial` branch carries a distinct tooltip (`modelPartialTooltip`, lines
  211-213), not the return-basis one — the distinct-tooltip half of the DoD.
- Round-1 case B, re-run against the shipped engine: 290 days, XLE and XLU histories
  absent → `model.status = partial`, `windows = [(20,ok),(60,ok),(252,ok)]`,
  `insufficient_history` carries `['energy','utilities']` for all three windows.
  Badge resolution now yields `Degraded` with the tooltip naming
  "Energy, Utilities" (labels resolved through `factorRegistryByKey`, raw key as
  fallback). Round 1's no-badge outcome is gone.
- Label lookup is safe on an unmapped key: `factorRegistryByKey[key]?.label ?? key`.

The badge is on the correct rung. A fit missing 2 of 16 proxies is `degraded`, not
`withheld` — a number is published and it is usable, with a stated limitation.
Nothing was collapsed into `unavailable`.

## FINDING 3 — confirmed fixed

- `RollingFactorLoadingsCard.test.tsx:71-85`: the case is now titled "renders a
  Degraded badge for the defensive window-level partial branch (not a reachable
  engine state)", with a comment citing `risk.py:1107` vs `:1644-1648` and
  05-quant-audit.md § FINDING 3. That is an accurate description of what it tests.
- The unreachability claim still holds against the shipped `risk.py`:
  `_build_window_summaries` (1107) yields `partial` only when
  `len(common_dates) < WINDOW_MIN_OBSERVATIONS[window]` **and** a non-null point
  exists, while `_build_rolling_factor_loadings` (1644) emits only bare points below
  that same threshold. Re-confirmed in this pass's sweep: no n produces `partial`.
- Repo-wide grep for `'partial'` across `apps/desktop/src`: the other hits are
  `BenchmarkPositioningCard`, `DrawdownAnalyticsCard`, `StressScenariosCard`,
  `ExposurePanel`, `DriftBenchmarkPanel` and `App.test.tsx` — all different fields
  with their own producible `partial`. No other test misrepresents
  `windows[].status == "partial"`.
- The pre-existing "no badge" test (line 62) was correctly updated: it now forces
  `status: 'ok'` and `insufficient_history: []`, which is a reachable engine state
  (measured case A). It does not manufacture an impossible one to stay green.

## FINDING 4

```
FINDING 4
severity:   MATERIAL
where:      apps/desktop/src/features/portfolio/RollingFactorLoadingsCard.tsx:218
            (tooltip text at :213); test pinned at RollingFactorLoadingsCard.test.tsx:106
claim:      The card asserts, via the badge on the section header next to the selected
            window's coverage line, that the displayed fit is degraded because "One or
            more of the model's factor proxies lack sufficient price history; this fit
            omits them."
actual:     `statistical_factor_model.status` is `partial` whenever
            `insufficient_history` is non-empty (risk.py:1364), and
            `_build_insufficient_history` (risk.py:1119) appends an entry when
            `available_observations < required` **OR** `missing_factors` — the two
            causes are indistinguishable in the status alone. Measured, 150 shared
            observations, all 16 proxies present:
              model.status         = "partial"
              windows              = [(20,'ok'),(60,'ok'),(252,'insufficient_history')]
              insufficient_history = [(252, required 275, available 149, missing [])]
              20d non-null points  = 125,  60d non-null points = 75
            The 20d and 60d fits are complete: 16 of 16 factors, past
            WINDOW_MIN_OBSERVATIONS. Yet on the default 60d window the card renders
            `Degraded` with the generic tooltip above. No proxy is missing and nothing
            is omitted from that chart. Same at n=100 and n=40.
impact:     Two false signals in the regime that covers any portfolio with less than
            roughly 13 months of shared history — the common case, and the default
            view. (a) The researcher is told factor proxies are absent from a fit that
            has all 16, and will look for lines that are not missing or discount
            loadings that are sound. (b) On the 252d window, which has zero data
            points and renders the empty-state panel, the badge says `degraded` —
            a window with no series is not a degraded estimate. Round 1 verified the
            engine never degrades `insufficient_history`; this reintroduces exactly
            that collapse at the presentation layer. Guardrail 4.
expected:   Gate the model-level `partial` branch on the selected window's own missing
            factors rather than on model status:
              : (missingFactorKeysForWindow?.length ?? 0) > 0
                  ? <TrustBadge type="degraded" tooltip={modelPartialTooltip} />
            This is exact, not conservative: when a proxy is genuinely missing,
            `_build_insufficient_history` writes the same non-empty `missing_factors`
            to an entry for **every** window (measured, case B), so no
            missing-proxy case loses its badge. Short-history-only windows keep the
            empty-state panel and no badge, which is what they had before CR-1.
            The generic fallback at :213 then has no reachable caller.
            RollingFactorLoadingsCard.test.tsx:106 must invert to assert
            `queryByText('Degraded')` is null for that fixture.
```

## Reproduction

Offline, against the shipped `app.analytics.risk`. 290/150/100/40 daily states, 16
factor proxies as distinct sine series (the shape `test_analytics.py:4880` uses).
Badge column is the shipped resolver at `RollingFactorLoadingsCard.tsx:214-222`
replicated line for line, evaluated per window.

| case | proxies | model.status | windows (20/60/252) | insufficient_history | badge @60d | tooltip |
|---|---|---|---|---|---|---|
| A — 290d | 16 | `ok` | ok / ok / ok | `[]` | none | — |
| B — 290d | 14 | `partial` | ok / ok / ok | all 3, missing `[energy, utilities]` | **Degraded** | names Energy, Utilities |
| F — 150d | 16 | `partial` | ok / ok / insufficient | `[(252, 275, 149, [])]` | **Degraded** | **generic — false** |
| G — 100d | 16 | `partial` | ok / ok / insufficient | `[(252, 275, 99, [])]` | **Degraded** | **generic — false** |
| C — 40d | 16 | `partial` | ok / insufficient / insufficient | `[(60,…,[]), (252,…,[])]` | **Degraded** | **generic — false** |

Case B is round-1 FINDING 1, now correct. Cases F, G and C are FINDING 4: a complete
20d/60d fit badged as degraded for a cause that does not exist. In case C the 60d
window has 0 non-null points and shows the empty-state panel *and* the badge.

Non-null point counts per window confirm the fits are real where the badge claims
omission: case F has 125 points on 20d and 75 on 60d, all 16 factors present.

The repo's own frozen fixture is this shape — `portfolioFixtures.ts:974` carries
`insufficient_history: [{window_days: 252, required 275, available 60,
missing_factors: []}]` with `status: 'partial'` — which is why the new test at
`RollingFactorLoadingsCard.test.tsx:106` passes while asserting the false tooltip.
