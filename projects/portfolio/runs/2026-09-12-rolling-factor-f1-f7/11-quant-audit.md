REPORT 2026-09-12-rolling-factor-f1-f7/11
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd services/quant-engine && pytest app/tests/test_analytics.py -k "rolling_loadings or factor_model" -v
  result:    PASS
  detail:    8 passed, 212 deselected in 7.46s. Card vitest also run: 7 passed. anchor: known-answer degenerate cases, 6 fresh factor-model builds against the shipped engine (290d/16 proxies, 290d/14, 150d, 100d, 40d, 10d), 18 badge evaluations via a line-by-line replication of the shipped resolver, plus a hand-derived contradiction proof of the window-`partial` predicate.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - FINDING 4 confirmed fixed. Short-history-only fits (150d/100d/40d, all 16 proxies) now render no badge on any window. Closed. see § FINDING 4 — confirmed fixed
  - FINDING 1 confirmed not regressed. The missing-proxy case still badges Degraded naming Energy, Utilities, on all three windows. see § FINDING 1 and 3 — not regressed
  - FINDING 3 confirmed not regressed. `windows[].status == "partial"` remains structurally unreachable; proof re-derived from the two threshold predicates. see § FINDING 1 and 3 — not regressed
  - The inverted test at RollingFactorLoadingsCard.test.tsx:115 is falsifiable — reverting line 216 to `modelTrustStatus === 'partial'` makes that fixture render Degraded and the test fail.
  - No findings opened. Nothing blocks close-out from the quant gate.

risks:
  - One narrow tooltip-precedence change from CR-3, not a finding: when a proxy is missing AND the return basis is unverified, the 252d window's tooltip now names the missing factors instead of the return basis. see § Tooltip precedence
  - Both branches in that case render `Degraded`, so the trust rung is correct and nothing is collapsed; only the stated cause differs, and no test pins the order.
  - `modelPartialTooltip` (RollingFactorLoadingsCard.tsx:211) still carries a `?? ''` fallback that would emit "missing sufficient history for: ." — unreachable under the gate at :216, but it is latent dead branching rather than removed.

---

## Orchestrator brief

- Verdict: **PASS**. Round 3 clears the finding-family; no escalation to the human is needed.
- FINDING 4 (round-2 MATERIAL, blocking): **fixed and closed.** Re-measured against the shipped engine, not the fix reports — cases F/G/C now render no badge on any window.
- FINDING 1 (round-1 CRITICAL): **not regressed.** Case B still badges Degraded naming "Energy, Utilities", on all three windows.
- FINDING 3 (round-1 MATERIAL): **not regressed.** Window-level `partial` remains unreachable; the test still describes itself as defensive.
- The engine writes one global `missing_factors` list identically to every emitted window entry (risk.py:1115), which is why per-window gating loses no missing-proxy case. Measured, not assumed.
- The new test is falsifiable against the exact regression it names — checked by reverting the predicate mentally against the fixture at portfolioFixtures.ts:974.
- No new findings opened. One non-blocking tooltip-precedence note in `risks`.
- Not re-litigated, per the order: F7, and FINDING 2 (docs enum).
- Sections below: **FINDING 4 — confirmed fixed**, **FINDING 1 and 3 — not regressed**, **Tooltip precedence**, **Reproduction**.
- Nothing blocks dispatch. The quant gate is clear for this slice.

---

## FINDING 4 — confirmed fixed

The shipped resolver at `RollingFactorLoadingsCard.tsx:216` now reads:

```
: (missingFactorKeysForWindow?.length ?? 0) > 0
    ? <TrustBadge type="degraded" tooltip={modelPartialTooltip} />
```

which is FINDING 4's `expected` verbatim. `modelTrustStatus` is no longer consulted
for the `partial` branch; it survives only on line 218 for
`degraded_unverified_return_basis`, which is correct and was not in scope.

Re-measured against the shipped `app.analytics.risk`, the three false-signal cases
are gone: at 150, 100 and 40 shared observations with all 16 proxies present, no
window renders a badge. The 20d and 60d fits that carry 125/75 and 75/25 non-null
points are now unbadged, which is honest — they are complete, 16-of-16 fits. The
252d window, which has zero points, keeps the empty-state panel ("Not enough
history for 252d rolling factor loadings", line 331) and no longer also claims to
be a degraded estimate. That was the guardrail-4 half of the finding: an
`insufficient_history` window is no longer collapsed into `degraded` at the
presentation layer.

**Why per-window gating loses nothing.** `_build_insufficient_history`
(`risk.py:1113-1129`) computes `missing_factors` **once**, globally, from
`DEFAULT_FACTOR_DEFINITIONS` minus `active_factors`, then writes that same list
into every entry it emits. So a genuinely missing proxy is never visible on one
window and invisible on another. FINDING 4's `expected` asserted this; case B
below confirms it empirically (all three windows carry
`['energy', 'utilities']`).

**The test is falsifiable.** `RollingFactorLoadingsCard.test.tsx:115` drives the
base fixture, whose `insufficient_history` is
`[{window_days: 252, ..., missing_factors: []}]` with model `status: 'partial'`
(`portfolioFixtures.ts:955, :974`), and forces the 60d window to `'ok'`. Under the
shipped predicate no entry matches the 60d window, so no badge — the assertion
passes. Under the pre-CR-3 predicate `modelTrustStatus === 'partial'` the model
status is `'partial'`, so `Degraded` would render and `queryByText` would be
non-null. The test therefore fails on exactly the regression it is written to
catch, rather than passing vacuously.

## FINDING 1 and 3 — not regressed

**FINDING 1.** Case B re-run against the shipped engine: 290 daily states, XLE and
XLU histories absent. `model.status = partial`, all three windows `ok`,
`insufficient_history` carries `['energy','utilities']` for 20d, 60d and 252d.
The shipped resolver yields `Degraded` on all three windows with the tooltip
naming "Energy, Utilities" — labels resolved through `factorRegistryByKey`, with
the raw key as a safe fallback (`factorRegistryByKey[key]?.label ?? key`,
line 210). This is the outcome FINDING 1 asked for, and CR-3's narrowing did not
take it away. Rung is still `degraded`, not `withheld`: a 14-of-16 fit publishes a
usable number with a stated limitation.

**FINDING 3.** The claim is that `windows[].status == "partial"` cannot be
produced by the engine. Re-derived from the two predicates rather than re-read:

- `_build_window_summaries` (`risk.py:1107`) emits `partial` only when
  `len(common_dates) < WINDOW_MIN_OBSERVATIONS[window]` **and** `valid_points` is
  non-empty.
- `_build_rolling_factor_loadings` (`risk.py:1647`) appends a bare point whenever
  `index + 1 < min_observations`, with `min_observations =
  WINDOW_MIN_OBSERVATIONS.get(window, window)` — the same constant, compared
  against the same quantity.

A non-null point requires `index + 1 >= MIN` for some index, i.e.
`len(common_dates) >= MIN`. The `partial` branch requires `len(common_dates) <
MIN`. The two are contradictory, so `partial` is unreachable by construction, not
merely unobserved. The empirical sweep agrees: across n = 10, 40, 100, 150 and 290
no window ever reported `partial`. The test at line 80 still names itself a
defensive branch and cites the unreachability proof, which remains an accurate
description of what it pins.

## Tooltip precedence

Not a finding, recorded so it is visible. CR-3 moved the missing-factors check
ahead of the model-level return-basis check in the ternary chain. Measured case:
150 states, XLE/XLU dropped, close-only rows (no `adjClose`), after
`apply_return_basis_status_to_factor_model`:

```
model.status = degraded_unverified_return_basis
windows      = [(20,'degraded_unverified_return_basis'),
                (60,'degraded_unverified_return_basis'),
                (252,'insufficient_history')]
insufficient_history missing_factors = ['energy','utilities'] on all three windows

  @20d   shipped: window-return-basis          pre-CR-3: window-return-basis
  @60d   shipped: window-return-basis          pre-CR-3: window-return-basis
  @252d  shipped: "missing: Energy, Utilities" pre-CR-3: model-return-basis
```

Only the 252d window changes, and only in the tooltip text. Both render
`Degraded`, so the trust rung is unchanged and nothing is fabricated or collapsed.
The new text is arguably more actionable but omits the return-basis caveat, which
the 20d and 60d windows still surface. It is out of this order's scope and not
blocking; it is the same precedence gap 08-quant-audit.md already recorded in
`risks`, now with one concrete instance attached.

## Reproduction

Offline, against the shipped `app.analytics.risk`, sockets disabled. Daily states
with a linear value path; 16 factor proxies as distinct sine series (the shape
`test_analytics.py:4880` uses). The badge column replicates the **shipped**
resolver at `RollingFactorLoadingsCard.tsx:204-220` line for line, evaluated per
window.

| case | n | proxies | model.status | windows (20/60/252) | badge 20d | badge 60d | badge 252d |
|---|---|---|---|---|---|---|---|
| A | 290 | 16 | `ok` | ok / ok / ok | none | none | none |
| B | 290 | 14 | `partial` | ok / ok / ok | **Degraded** (Energy, Utilities) | **Degraded** (same) | **Degraded** (same) |
| F | 150 | 16 | `partial` | ok / ok / insufficient | none | none | none |
| G | 100 | 16 | `partial` | ok / ok / insufficient | none | none | none |
| C | 40 | 16 | `partial` | ok / insufficient / insufficient | none | none | none |
| H | 10 | 16 | `insufficient_history` | insufficient ×3 | none | none | none |

Non-null point counts, confirming the unbadged fits are real rather than empty:
case F has 125 points at 20d and 75 at 60d; case G has 75 and 25; case A has 265,
215 and 15. Cases C (60d, 252d) and H (all) have zero points and render the
empty-state panel, correctly with no badge.

Rows F, G and C are FINDING 4's three failing cases and are now clean. Row B is
FINDING 1 and is unchanged. Row H is a degenerate case added this round — below
`FACTOR_MODEL_MIN_SHARED_OBSERVATIONS`, the engine takes the early return at
`risk.py:1329` and the card shows the empty state with no badge, which is the
correct unavailable-not-degraded outcome.
