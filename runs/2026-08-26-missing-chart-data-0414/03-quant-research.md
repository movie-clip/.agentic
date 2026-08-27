REPORT 2026-08-26-missing-chart-data-0414/03
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   cd services/quant-engine && python -m pytest app/tests/test_analytics.py -k "withheld or publishable or disclosure" -v
  result:    PASS
  detail:    8 passed, 207 deselected in 1.82s

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Proposed field: `PerformancePoint.withheld_reason: str | None` (backend `app/schemas/reconciliation.py:510-515`), mirrored as `PerformanceSeriesPoint.withheld_reason?: string | null` in `types.ts:556-562` — see § Field proposal for the exact computation site and classifier.
  - Single-source-of-truth mechanism: extract a new `_withheld_return_cause(state: DailyPortfolioState) -> str | None` helper in `performance.py`, called from both `replay_disclosures()` (run-level string, existing) and `build_true_performance_series()`'s per-state loop (new per-point field) — see § Field proposal.
  - Story-author: the field is populated **iff** `not state.return_is_publishable`; it is explicitly silent about the two other, unrelated causes of a null `portfolio_return_pct` (whole-basis suppression, zero-prior-value gap) — an AC must not describe it as "explains every null point," see § Scope of what the field explains.
  - Pre-existing methodology-doc defect found while grounding this research, unrelated to whether this story proceeds: `docs/finance/financial-methodology.md:2436-2443` states the pre-US-34.8 rule (reconciliation_adjustment withholds a day) verbatim, contradicting the corrected section at the same doc's lines 565-638 and the shipped code/tests — see § Methodology doc status. Needs a `docs` lane fix independent of this story.
  - Same stale framing also sits in a code comment at `dashboard_history_engine.py:504-505` ("withheld... because the state carries a material reconciliation adjustment") — cosmetic (does not affect behaviour) but worth fixing in the same pass as the doc correction, since it is the same drift.
  - Open question for tech-lead, not decided here: `replay_disclosures()`'s `reconciliation_adjustment` branch (`performance.py:225-229`) is unreachable under current `return_is_publishable` semantics (confirmed empirically, § Classification branches) — worth deleting as part of extracting the shared classifier, or worth leaving with a comment. Flagged, not resolved, since removing it is arguably outside this order's non-goal ("do not propose changing the withholding classification logic").

risks:
  - The DoD's "two-branch classification logic" framing describes `replay_disclosures()`'s source text, not its live behaviour — only one branch is reachable today (§ Classification branches). A classifier built against the "two branches" framing would reimplement a branch that never fires, and could misattribute cause on the one future date where both conditions coincide.
  - Did not check whether `risk.py`'s drawdown/VaR series or `drift_engine.py` — the two other candidates 01-scout flagged as unconfirmed — need the same field; out of scope per this order's inputs (Dashboard chart only). Those series omit withheld days from the array entirely rather than emitting a null point, so a per-point `withheld_reason` may not even be the right shape there — flagged, not investigated.
  - `withheld_return_impact_pct` (`performance.py:265-295`) and `PerformanceSummary` were read for context but are unaffected by this proposal — not re-verified beyond confirming they don't share the classification logic in a way that would drift.

## Orchestrator brief
- Decision: per-date classification is per-`DailyPortfolioState` only — no cross-date context needed. Verified empirically (§ Classification branches), not just read.
- Decision: `replay_disclosures()`'s two written branches are NOT two live causes — only `unbacked_cash_flow` materiality withholds a return today; `reconciliation_adjustment` never does (US-34.8). The delivery brief's "two-branch" framing is stale.
- Decision: proposed field is `PerformancePoint.withheld_reason: str | None`, computed in `build_true_performance_series`'s existing per-state loop via a new shared classifier — see § Field proposal.
- Decision: additive-only holds — `withheld_return_dates`/`withheld_return_reason` unchanged, new field coexists.
- Decision: this is guardrail-3/4 (trust/disclosure honesty) territory, not guardrail-1 (no formula changes) — a small methodology-doc addition is warranted, not a new formula section. See § Methodology doc status.
- Finding, not asked for but load-bearing: `docs/finance/financial-methodology.md:2436-2443` is stale and self-contradicts the doc's own lines 565-638 — pre-existing defect, needs a `docs` fix regardless of this story's fate.
- Sections below: § Classification branches · § Field proposal · § Scope of what the field explains · § Additive-only confirmation · § Test-suite consistency · § Methodology doc status · § Metrics inventory · § Open questions

## Classification branches

`replay_disclosures()` (`performance.py:207-235`) is *written* with two `if` branches over `states`:

1. `reconciliation_adjustment` cause (lines 225-229) — fires if any withheld state carries a truthy `reconciliation_adjustment`.
2. `unbacked_cash_flow` cause (lines 230-234) — fires if any withheld state carries a truthy `unbacked_cash_flow`.

But `withheld` (line 220) is built from `not state.return_is_publishable`, and that property (`app/schemas/reconciliation.py:588-629`) is, as of US-34.8, driven **exclusively** by `unbacked_cash_flow` materiality:

```python
if not self.unbacked_cash_flow:
    return True                      # reconciliation_adjustment plays no part
if not self.total_portfolio_value:
    return False
share = abs(self.unbacked_cash_flow) / abs(self.total_portfolio_value)
return share <= REPLAY_UNBACKED_CASH_MATERIAL_SHARE
```

`reconciliation_adjustment` is set **only** on the terminal state (`app/engine/portfolio_state.py:908` — one assignment site, one state). So branch 1 can fire only if the terminal state is *also* independently withheld by branch 2's condition on the same date — a coincidence, not a second cause. On every date where branch 1's condition is true today, `return_is_publishable` is true (the date is not in `withheld` at all), so branch 1's `any(...)` is evaluated over an empty-by-construction subset and never contributes a sentence. This is confirmed three ways, not asserted:

- **Code reading**: the property's own docstring (`reconciliation.py:590-592`) states "False only when the state carries a material unbacked cash flow," and separately documents (line 598-601) that a reconciled terminal day is *publishable*, not withheld.
- **Test**: `test_withheld_days_are_named_with_only_the_causes_that_fired` (`test_analytics.py:8512-8549`) asserts `"accounting" not in reason` with the comment "the reason still names the terminal reconciliation, which no longer withholds any day (US-34.8)."
- **Independent recompute against the live fixture** (`app/tests/test_analytics.py::_us313_ib2026_history`, IB2026 statement): every one of the 4 currently-withheld dates has `reconciliation_adjustment=None`; the one state with a non-null `reconciliation_adjustment` (2026-08-11, the terminal date, `-19.98`) has `unbacked_cash_flow=0.0` and `return_is_publishable=True`. A from-scratch classifier gating solely on `unbacked_cash_flow` materiality reproduces `run_metadata.withheld_return_dates` exactly: `['2026-04-14', '2026-04-17', '2026-06-12', '2026-07-17']`.

**Answer to the DoD's question**: yes, classification is fully per-`DailyPortfolioState` — no cross-date context is needed. The classifying signal (`unbacked_cash_flow`, `total_portfolio_value`, and the constant `REPLAY_UNBACKED_CASH_MATERIAL_SHARE`) all live on, or are computable from, the single state object, exactly as the delivery brief assumed. What the delivery brief got wrong is the *number* of live causes: one today, not two — the second branch in `replay_disclosures()` is dead code under current semantics, not a second classification path a per-date field needs to reproduce.

## Field proposal

**Name & type**: `PerformancePoint.withheld_reason: str | None` (backend), `PerformanceSeriesPoint.withheld_reason?: string | null` (TS mirror, matching the optional-but-always-serialized pattern already used for `portfolio_return_trust` / `window_start_date` on the sibling `DashboardRangeMetrics` type, `types.ts:541,553`).

**Where computed**: inside `build_true_performance_series` (`performance.py:298-359`), in the existing per-`state` loop (line 320 `for state in daily_states:`) — the exact site the DoD pointed at. No new plumbing: `state` is already in scope there with every field the classifier needs.

**Classifier — single source of truth**: extract a new module-level helper,

```python
def _withheld_return_cause(state: DailyPortfolioState) -> str | None:
    """The one reason THIS state's return is withheld, or None if it is
    publishable. Called both by replay_disclosures() (run-level summary,
    deduplicated across dates) and build_true_performance_series() (per-point
    field) so the two surfaces read one classification, not two.
    Today there is exactly one live cause (US-34.8: reconciliation_adjustment
    no longer withholds a return). If a future cause is added to
    return_is_publishable, add its branch here — and only here.
    """
    if state.return_is_publishable:
        return None
    return (
        "a holding whose reconstructed quantity was withheld traded that day, "
        "moving cash with no position behind it in market value"
    )
```

`replay_disclosures()` would call this once per state to build its deduplicated, ordered `causes` list instead of its current two inline `any(...)` checks — same run-level output, same test assertions, but sourced from the one function the per-point field also calls. This is presented as a design option for tech-lead, not decided here (see § Open questions on the dead branch).

**Value for a non-withheld date**: `None` — never a "no reason" string, never an empty string. This falls out of the classifier by construction (`if state.return_is_publishable: return None`) and was verified against the one edge case in the current fixture that specifically tests it (§ Scope of what the field explains, immaterial-unbacked-cash rows).

## Scope of what the field explains

`portfolio_return_pct is None` at a given point has **three** distinct causes in `build_true_performance_series`, not one:

1. **Whole-series basis suppression** (line 333): `portfolio_return_basis_contract not in _PUBLISHING_PORTFOLIO_BASES` — every point in the series is null, for a reason that has nothing to do with any individual date's state.
2. **Zero-denominator gap** (`_time_weighted_daily_return`, line 363): `previous_state.total_portfolio_value == 0` — a genuine "no claimable return" case, per the existing comment at lines 322-327, unrelated to `current_state.return_is_publishable`.
3. **State-level withholding** (line 367): `not current_state.return_is_publishable` — the cause this story is about.

The proposed field is gated on cause 3 only (`not state.return_is_publishable`), which is deliberate and correct — cause 3 is the only one that is actually a per-date, state-carried fact; causes 1 and 2 are a run-level scalar and an adjacent-pair comparison respectively, and inventing a per-point explanation for them from a single state would be exactly the "fabricate a plausible-looking value for a case the data doesn't support" failure mode the pack warns against.

**Consequence for the story's AC**: it must not read "every null point on the chart gets an inline reason." It should read something closer to "every point whose date is in `withheld_return_dates` gets an inline reason naming that date's specific cause" — narrower, honest, and matching what the field can actually promise. On the *current* IB2026 fixture this distinction is invisible (empirically confirmed: all 4 null `portfolio_return_pct` dates in `performance_series` are exactly the 4 state-withheld dates, no basis-suppression or zero-value nulls present on this statement) — but the field's contract must not rely on that coincidence holding for every future statement.

**Edge case, verified numerically**: two dates in the current fixture (2026-06-10, 2026-06-23) carry nonzero-but-immaterial `unbacked_cash_flow` (share 0.0004 and 0.00009, both below `REPLAY_UNBACKED_CASH_MATERIAL_SHARE = 0.001`). `return_is_publishable` is `True` on both, `portfolio_return_pct` is non-null on both, and the proposed classifier correctly returns `None` on both — confirming the field is gated on the materiality-adjusted boolean, not on `unbacked_cash_flow != 0` directly, which would have been the naive (and wrong) implementation.

## Additive-only confirmation

Confirmed: `withheld_return_dates` (`dashboard_history.py:306`) and `withheld_return_reason` (`dashboard_history.py:307`) are unchanged in meaning, unchanged in computation (`replay_disclosures()`'s public return shape is untouched even if its internals are refactored to share the new classifier), and continue to exist alongside the new per-point field. Nothing about the run-level summary note on `PerformanceBenchmarkCard.tsx` (lines 249-258, per 01-scout) or `ReplayDisclosuresCard.tsx` needs to change for this field to ship. No strong reason found to deprecate the flat string — it remains the correct source for a run-wide "N days excluded" summary, which a per-point field cannot replace (a chart tooltip cannot show a summary before the user has hovered any point). Not flagging a deprecation question; the two are complementary, as the order anticipated.

## Test-suite consistency

`test_withheld_days_are_named_with_only_the_causes_that_fired` (`test_analytics.py:8512-8549`) and the other 7 tests selected by the order's verification command all pass (8 passed, 207 deselected). The specific assertion load-bearing for this proposal — `len(metadata.withheld_return_dates) == 4` and only the unbacked-cash sentence fires — was independently reproduced by direct recomputation against `_us313_ib2026_history()` in this session (§ Classification branches), not merely re-read. The proposed field's value on all 4 dates would be the identical unbacked-cash-flow sentence, since all 4 share the one live cause on this statement — consistent with what the suite already asserts about the run-level string. No existing test would need to change for the field to be added (it is a new, additive field with no interaction with the assertions above); a new test asserting `withheld_reason` is non-null exactly on `withheld_return_dates` and null elsewhere (including the two immaterial-unbacked dates) is the natural regression pin — a test-lane concern, not authored here.

## Methodology doc status

**This is guardrail-3/4 (trust semantics / truth-class honesty) territory, not guardrail-1 (formula) territory** — confirmed by reading, not taken from the order's framing. `return_is_publishable` itself is unchanged by this proposal; nothing here computes a new return, a new trust rung, or a new numeric quantity. The risk this field carries is a *disclosure-honesty* risk (attributing the wrong cause to a gap), which is exactly the failure class guardrail 4 names ("never fill a plausible value") applied to text rather than a number.

**A small doc addition is warranted, not a new formula section**: `docs/finance/financial-methodology.md`'s existing withholding discussion (the corrected section at lines 565-638) should gain a short note that the withholding cause is surfaced at two granularities — run-level (`withheld_return_reason`) and per-date at the exact point (`PerformancePoint.withheld_reason`) — both derived from one shared classifier, so a future editor adding a second cause updates one function rather than two independently.

**Separately, and found only while grounding this research — a pre-existing defect, unrelated to whether this story proceeds**: `financial-methodology.md:2436-2443` states, verbatim, "no return is published for a day whose `|reconciliation_adjustment|` exceeds `REPLAY_RECONCILIATION_TOLERANCE`. The day is WITHHELD" — this is the **pre-US-34.8 rule**. It directly contradicts the same document's own corrected section 60+ lines later ("Withholding remains for the other cause: a day whose cash moved with no position behind it (US-33.2) has no corrected value available... [reconciliation_adjustment] creates one, so the day's return is computed" — lines 607-624), and contradicts the shipped code and the regression test cited above. The same stale framing also appears in a code comment at `dashboard_history_engine.py:504-505`. This is a `CRITICAL`-class doc-vs-code discrepancy under the quant-audit gate's own rubric (a specification that disagrees with itself and with the code it specifies), surfaced here because I read the doc section this order named as authoritative and it is wrong — not something I am authorized to fix (no Write access, and it is outside this order's scope), so it is handed off for a `docs` lane fix.

## Metrics inventory

| Field | Type | Computed by | Nullability | Trust class |
|---|---|---|---|---|
| `PerformancePoint.withheld_reason` | `str \| None` | `_withheld_return_cause(state)` (proposed, in `performance.py`, called from `build_true_performance_series`'s per-state loop) | `None` whenever `state.return_is_publishable` is `True`; non-null text whenever it is `False`. Never populated for the other two null-`portfolio_return_pct` causes (basis suppression, zero-prior-value) — see § Scope. | Not a numeric trust rung — disclosure metadata attached to an already-published withholding decision (`return_is_publishable`, itself `verified` broker-truth-derived per US-33.2/34.8). Same class as the existing `withheld_return_reason` string it is the per-date sibling of. |

## Open questions

- Whether to actually delete `replay_disclosures()`'s now-provably-dead `reconciliation_adjustment` branch (lines 225-229) as part of extracting the shared classifier, versus leaving it in place with a comment noting it is currently unreachable. Deleting it is arguably within this story's "how an already-computed classification gets surfaced" mandate (it's the same disclosure-text function); arguably outside the letter of the order's non-goal ("do not propose changing the withholding classification LOGIC"). Flagged, not resolved.
- Whether the doc correction at `financial-methodology.md:2436-2443` should land as its own immediate `docs`-lane fix now (it is a live, user-facing-adjacent correctness defect in the spec of record) or be bundled into this story's close-out docs pass. Either is defensible; the defect itself is not optional to leave uncorrected.
