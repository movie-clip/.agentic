REPORT 2026-09-12-rolling-factor-f1-f7/05
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   cd services/quant-engine && pytest app/tests/test_analytics.py -k "rolling_loadings or factor_model" -v
  result:    PASS
  detail:    8 passed, 212 deselected in 6.66s. anchor: constructed degenerate cases - 5 independent factor-model builds run against the shipped engine (290d full; 290d with 2 proxies dropped; 40d; 12d; empty), plus a construction-level proof read from risk.py. Not a methodology-doc re-read.

contract_notes:
  - `statistical_factor_model.status` producible set is five values, not four — `unavailable` is emitted at `diagnostics_engine.py:604`. The close-phase `dashboard-fields.md` row specified in 01-design.md § Doc contract row would document a wrong enum. see § FINDING 2
  - `windows[].status` producible set is two values in practice — `ok` and `degraded_unverified_return_basis`; `insufficient_history` when the series is empty. `partial` is unreachable. see § FINDING 3
  - `RollingFactorLoadingPoint.alpha` removal is contract-safe: pydantic ignores an extra `alpha=` kwarg, so no caller can break on it.

pack_corrections:
  - none

handoff:
  - FINDING 1 (CRITICAL) is a frontend fix in `RollingFactorLoadingsCard.tsx` — badge must also consider `factorModel.statistical_factor_model.status`, not `selectedWindowSummary.status` alone. see § FINDING 1
  - FINDING 1 needs a tooltip wording decision for model-level `partial` (missing factor proxies ≠ short history) — owner or design, not an engineer's guess.
  - FINDING 2 must reach the docs lane before it writes the contract row, or the row ships a false enum.
  - FINDING 3: `RollingFactorLoadingsCard.test.tsx:57-61` asserts a window status the engine cannot emit — informational for the test lane, not a blocker.
  - F7 verified clean and needs no further work — evidence in § F7 verification.

risks:
  - Model-level `unavailable` renders the empty-state copy "Not enough history for 60d rolling factor loadings", which names the wrong cause. That copy is F10's territory and an explicit non_goal here; flagged, not litigated.
  - 01-design.md § F7 states no rolling intercept is computed. An intercept *is* fitted (`coefficients[0]`, risk.py:1672 offsets factor keys by +1); it is deliberately never surfaced. Imprecise, but does not change the removal verdict.
  - Window `partial` and `degraded_unverified_return_basis` collapse into one literal in the degrade overlay (risk.py:773-776). Moot today given FINDING 3, but it would silently drop the short-history reason if `partial` ever became reachable.

---

## Orchestrator brief

- Verdict: **FAIL**, on one CRITICAL. F7 (`alpha` removal) is clean and closed; F1 is fixed for one of the engine's two reachable degrade signals and misses the other.
- FINDING 1 (CRITICAL): `statistical_factor_model.status == "partial"` — emitted whenever any of the 16 factor proxies has no history — leaves every `windows[].status` at `"ok"`, so the card renders a 14-of-16-factor fit with **no badge**. Reproduced, numbers in the section.
- FINDING 2 (MATERIAL): the producible enum is `{ok, partial, insufficient_history, degraded_unverified_return_basis, unavailable}` — five, not the four 01-design.md asserts. `unavailable` comes from `diagnostics_engine.py:604`, a file outside that pass's reading.
- FINDING 3 (MATERIAL): `windows[].status == "partial"` is **unreachable by construction** — proof in the section. The shipped `partial` badge branch is dead against real engine data, and the test that covers it can never fail for the right reason.
- The `degraded_unverified_return_basis` path — the original F1 — is correctly surfaced, correct rung, correct tooltip. Verified end to end.
- Sections below: **Findings** (FINDING 1-3, each with numbers), **F7 verification**, **What verified clean**, **Reproduction**.
- FINDING 1 blocks close-out. FINDING 2 blocks the close-phase docs dispatch only.

---

## Findings

```
FINDING 1
severity:   CRITICAL
where:      apps/desktop/src/features/portfolio/RollingFactorLoadingsCard.tsx:205-210
claim:      01-design.md § F1 decision: the badge's trust source is
            `selectedWindowSummary.status` alone, because window- and model-level
            status "degrade identically today from the same return-basis check".
actual:     They do not. `build_statistical_factor_model` (risk.py:1364) sets
            model.status = "partial" whenever `insufficient_history` is non-empty,
            and `_build_insufficient_history` (risk.py:1115-1119) populates that list
            when ANY of the 16 factor proxies is missing — independently of
            observation count. `_build_window_summaries` (risk.py:1107) keys window
            status on `len(common_dates)` only, so every window stays "ok".
            Measured, 290 days of history, XLE and XLU histories absent:
              model.status   = "partial"
              windows        = [(20,'ok'),(60,'ok'),(252,'ok')]
              insufficient_history = [(20,['energy','utilities']), (60,...), (252,...)]
              60d latest r_squared = 0.5355  vs  0.5465 for the complete model
            `selectedWindowTrustStatus` is 'ok' → `trustBadge` is null → the card
            renders pixel-identical to a complete 16-factor fit.
impact:     The researcher reads loadings from a fit that silently omits 2 of 16
            factors — two lines simply absent from the chart, lower explanatory
            power, no indication — as a fully-specified model. A missing proxy
            history is an ordinary market-data gap, not an exotic case. This is the
            same defect the original FINDING 1 was raised for: an engine-computed
            degrade discarded at the last hop. Guardrail 4.
expected:   The badge derives from both levels, degrading on either:
            model.status ∈ {partial, degraded_unverified_return_basis} OR
            selectedWindowSummary.status ∈ {the same}. Model-level `partial` needs
            its own tooltip — the missing factors are named in
            `insufficient_history[].missing_factors` and should be surfaced.
```

```
FINDING 2
severity:   MATERIAL
where:      01-design.md § Status enum and treatment; services/quant-engine/app/services/diagnostics_engine.py:604
claim:      "No `unavailable` or `withheld` literal is ever produced for
            `statistical_factor_model.status` / `windows[].status`."
actual:     `build_unavailable_diagnostics_result` constructs
            `StatisticalFactorModel(status='unavailable', ..., windows=[])` at
            diagnostics_engine.py:604, on the no-history-context path
            (`run_diagnostics_engine`, missing history_start_date/history_end_date).
            It is the third construction site of this model; the design pass read
            only the two in risk.py. Producible set is therefore five:
            {ok, partial, insufficient_history, degraded_unverified_return_basis,
             unavailable}.
impact:     The close-phase docs order in § Doc contract row specifies the exact
            four-value enum to write into dashboard-fields.md, citing risk.py line
            ranges. Writing it verbatim publishes a contract that omits a
            reachable state — and this doc is the traceability artifact guardrail 2
            rests on.
expected:   The enum list corrected to five values before the docs row is written,
            citing diagnostics_engine.py:604 for the fifth. Card behaviour on this
            path is acceptable as shipped (no badge, no series, no number
            published) and needs no code change.
```

```
FINDING 3
severity:   MATERIAL
where:      services/quant-engine/app/analytics/risk.py:1107 vs :1644-1648;
            apps/desktop/src/features/portfolio/RollingFactorLoadingsCard.test.tsx:57-61
claim:      01-design.md § Status enum and treatment, and the shipped card branch at
            RollingFactorLoadingsCard.tsx:206, treat `windows[].status == "partial"`
            as a live state meaning "less than the full recommended history".
actual:     Unreachable by construction. `_build_window_summaries` yields "partial"
            only when `len(common_dates) < WINDOW_MIN_OBSERVATIONS[window]` AND at
            least one point in the series has a non-null factor value. But
            `_build_rolling_factor_loadings` (risk.py:1644-1648) emits a bare,
            all-null point for every index where `index + 1 < min_observations`,
            with the same `WINDOW_MIN_OBSERVATIONS[window]` threshold. So a
            non-null point exists only when the series already has ≥ min
            observations — exactly the "ok" condition. The two predicates are
            mutually exclusive. Confirmed numerically at n = 21, 23, 25, 26, 30
            common dates: status goes `insufficient_history` → `ok` at n=26 with
            zero `partial` in between, and the 20d series has 0 non-null points at
            n≤25 and 1 at n=26.
impact:     Two consequences. (a) The test at line 57 hand-sets `partial` on a
            fixture and passes — it verifies the branch, not the engine, and no
            engine regression can ever make it fail (gates.md § 2). (b) The
            close-phase contract row would document a phantom state while the
            reachable degrade signal — model-level `partial`, FINDING 1 — goes
            undocumented.
expected:   Keep the defensive branch. But name it as defensive, and do not
            document `windows[].status = "partial"` as a producible engine state
            until either risk.py:1107 or risk.py:1644 changes so that it is.
            The coverage FINDING 1 actually needs is a model-level `partial` case.
```

## F7 verification

`RollingFactorLoadingPoint.alpha` removal is **correct**. Re-derived from risk.py
rather than taken from 01-design.md or the prior audit:

- `_build_rolling_factor_loadings` has exactly two construction sites for
  `RollingFactorLoadingPoint`: risk.py:1648 (`date=date` only, the below-threshold
  bare point) and risk.py:1672-1677 (`date`, `r_squared`, `residual_vol`,
  `**values_map`).
- `values_map` (risk.py:1663-1667) is keyed by `factor_keys[factor]`, and
  `factor_keys` is built from `DEFAULT_FACTOR_DEFINITIONS` — the 16 factor keys.
  `alpha` is not among them, so `**values_map` can never carry it.
- Grep confirms no other module constructs the model. The only surviving `alpha`
  strings in `services/quant-engine/app/analytics/risk.py` are the two comment
  lines at 1352-1354 recording the Epic 23 decision.
- The field was therefore null for every point ever produced. Removing it deletes
  no value.
- An intercept *is* fitted inside each window — `values_map` indexes
  `coefficients[position + 1]`, so `coefficients[0]` is the intercept — and is
  deliberately not surfaced. This is consistent with the methodology's prohibition
  on labelling it `alpha`, and with `attribution-fields.md:16`. It does make
  01-design.md § F7's "no rolling-window intercept computed anywhere" imprecise;
  the *decision* is unaffected.
- Compatibility: `RollingFactorLoadingPoint(date='2024-01-01', alpha=0.1)`
  constructs without error and omits `alpha` from `model_dump()` — pydantic's
  default `extra='ignore'`. No caller can break on the removal.

Post-removal field list, read from `model_fields`: commodities,
consumer_discretionary, consumer_staples, credit, date, energy, financials, growth,
health_care, industrials, market, r_squared, rates_ief, rates_tlt, residual_vol,
small_cap, technology, utilities. No `alpha`.

## What verified clean

- **The original F1 path is genuinely fixed.** With close-only price rows,
  `apply_return_basis_status_to_factor_model` degrades model.status and all three
  window statuses to `degraded_unverified_return_basis` (measured), the card's
  second branch fires, and a `TrustBadge type="degraded"` renders with a tooltip
  that accurately names the cause. Rung assignment is right: this is the `degraded`
  rung of `verified > degraded > withheld > unavailable`, not `withheld`.
- **`insufficient_history` is never degraded.** `_degrade_status_for_unverified_return_basis`
  gates on `status in {"ok","partial"}`; measured mapping:
  ok→degraded, partial→degraded, insufficient_history→insufficient_history,
  unavailable→unavailable, degraded→degraded (idempotent). Correct — there is no
  series to mistrust, and `unavailable` is not collapsed into a degrade.
- **`insufficient_history` pairs with empty series.** The early return at
  risk.py:1332 yields empty `rolling_loadings_*d`, so the card routes to the
  empty-state panel and publishes no number. Confirmed at n=0 and n=12.
- **No `withheld`/`unavailable` collapse.** The two are distinct in this
  component: `unavailable` (FINDING 2's path) is a real state; nothing here is
  withheld, and nothing withheld was turned into unavailable.
- **`TrustBadge` extension is minimal and correct** — `'degraded'` added to the
  union and to `LABELS`, no new CSS, exactly the extension path the primitive's own
  docstring prescribes.
- **No duplicate status logic.** `_degrade_status_for_unverified_return_basis` is
  the single degrade implementation, shared by the reliability snapshot and the
  factor model. No second copy.

## Reproduction

Offline, no sockets, against the shipped `app.analytics.risk`. 290 daily states,
16 factor proxies as distinct sine series (the shape `test_analytics.py:4880` uses).

| case | model.status | windows[].status | 20d points |
|---|---|---|---|
| A — 290d, all 16 proxies | `ok` | ok / ok / ok | 289 |
| B — 290d, XLE + XLU absent | **`partial`** | **ok / ok / ok** | 289 |
| C — 40d | `partial` | ok / insufficient / insufficient | 39 |
| D — 12d | `partial` | insufficient ×3 | 11 |
| E — empty | `insufficient_history` | insufficient ×3 | 0 |
| B + close-only rows | `degraded_unverified_return_basis` | degraded ×3 | 289 |

Case B is FINDING 1: the only row where the model is degraded, a full series is
rendered, and the card shows nothing. 60d latest `r_squared` 0.5355 (B) against
0.5465 (A); the surviving factors' loadings are unchanged to 4dp, because
Gram-Schmidt orthogonalization drops the lower-priority factors last — so no
displayed *number* is wrong. The defect is that an incomplete model is presented
as a complete one.

Reachability sweep for window `partial`, n ∈ {21, 23, 25, 26, 30} common dates:
`insufficient_history` at every n ≤ 25 (0 non-null 20d points), `ok` at n = 26
(1 non-null point). No n produces `partial` — consistent with the construction
proof in FINDING 3.
