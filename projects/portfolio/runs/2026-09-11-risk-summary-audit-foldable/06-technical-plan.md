REPORT 2026-09-11-risk-summary-audit-foldable/06
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order's verification field was NONE (design pass, read-only). Plan derived from direct reads of trust_gate.py, diagnostics_engine.py, risk.py, RiskSummaryCard.tsx, dashboard-fields.md, financial-methodology.md, risk-fields.md and the two input reports.

contract_notes:
  - Fix 1 and Fix 2 each flip a `DiagnosticsRunMetadata`/response field from always-null to sometimes-populated; no field name, type or nullability declaration changes (already `float | None`), but the *reachable value space* changes.
  - That reachable-value-space change is exactly what dashboard-fields.md:238,242,287 and financial-methodology.md:1141-1149 currently mis-describe — backend must emit these doc corrections as its own contract_notes at close-out; docs-engineer applies them.
  - Fix 3 changes no schema field (`risk_contribution_path` keeps its name, type, and three enum values). Only the frontend's rendered string changes. Confirm in review that no backend change accompanied this fix — if one did, it was out of scope.
  - Fix 4 narrows `portfolio_volatility_pct`/`benchmark_volatility_pct`'s *practical* range at N=1 (0.0 is no longer reachable) but the declared type (`float | None`) does not change — both fields are already `Optional`.

pack_corrections:
  - none

handoff:
  - Backend lane: Fix 1, Fix 2, Fix 4 — see § Fix 1, § Fix 2, § Fix 4 below for exact edits.
  - Frontend lane: Fix 3 — see § Fix 3 below. No backend change required for Fix 3.
  - Docs lane: doc corrections listed per-fix below, dispatched after backend/frontend land (docs describe shipped behavior, not the reverse).
  - Test lane: new/changed coverage named per-fix below; also update the four pinned-null assertions test_routes.py:595-598, :1088-1089, :2546-2547, :2739 (audit's FINDING 1 citations) to assert real values under a verified-adjusted-close fixture, and the analogous relative-return pinned-null assertions for FINDING 2.

risks:
  - Neither input report found a test that exercises a diagnostics run with fully `verified_adjusted_close` benchmark+factor basis (03-quant-research.md risks). Fix 1/Fix 2 verification therefore needs a NEW fixture, not just relaxed assertions — flagged again here so the test lane does not treat this as a pure find-and-replace.
  - Fix 1 and Fix 2 are independent gates (different files, different call sites) but both terminate in the same `DiagnosticsResult` response and the same card render — sequence them together in one review pass so `showRelativeRisk`/drawdown-row coherence is checked once, not twice.
  - `docs/product/epic-roadmap.md` referenced by project.md's Sources-of-truth table does not exist in this repo (03-quant-research.md handoff) — not this order's concern, noted only so the docs lane isn't surprised.

## Orchestrator brief
- 4 fixes, all backend-owned except Fix 3 (frontend-only, no schema change).
- Fix 1 (backend): `allow_diagnostics_drawdown_outputs` — remove unconditional `False`, gate on `historical_sections_available` (always `True` at its only call site) → effectively always-pass in that path. See § Fix 1.
- Fix 2 (backend): `_allow_diagnostics_relative_return_outputs` — same pattern, diagnostics_engine.py. See § Fix 2.
- Fix 3 (frontend-only): `sectionTrustLabel`/label text in RiskSummaryCard.tsx — no schema change, string only. See § Fix 3.
- Fix 4 (backend): risk.py:507-508 — swap truthy-list guard for `len(...) >= 2`, matching `_calculate_beta`/`_calculate_correlation`. See § Fix 4.
- Sequence: Fix 1, Fix 2, Fix 4 can run in the SAME backend work order (same file family, same reviewer pass) since none touch each other's code; Fix 3 is a fully separate frontend order with no backend dependency. Docs order runs after backend+frontend land, consuming both sets of contract_notes at once.
- Sections below, by name: § Contract (all four fixes, field-by-field) · § Fix 1 — unwithhold diagnostics drawdown · § Fix 2 — unwithhold diagnostics relative return · § Fix 3 — relabel `risk_contribution_path` badge · § Fix 4 — null convention for portfolio/benchmark volatility at N<2 · § Reuse · § Decisions · § Risks (design-level).

## Contract

Fields affected, all inside `DiagnosticsResult` (the diagnostics engine response consumed by `RiskSummaryCard.tsx` — no route or type-shape change, only the value each field can now take):

| Field | Type (unchanged) | Old reachable values | New reachable values | Trust/withholding note |
|---|---|---|---|---|
| `drawdown_summary.current_drawdown_pct` | `float \| None` | always `None` | real value whenever `historical_sections_available` is `True` (already-computed `volatility_regime.snapshot.current_drawdown_pct`, subject to its own math-layer null handling) | drops the categorical gate; math-layer nulls (insufficient history, etc.) still apply and are the only remaining source of `None` |
| `drawdown_summary.max_drawdown_pct` | `float \| None` | always `None` | same as above | same |
| `relative_risk.active_return_pct` | `float \| None` | always `None` | passes through `build_relative_risk_summary`'s own output unmodified (real value whenever `paired_returns` non-empty) | math-layer null handling in `risk.py:744-770` is unchanged and now the only source of `None` |
| `relative_risk.information_ratio` | `float \| None` | always `None` | passes through unmodified — `None` only per its own documented edge cases (fewer than 2 paired returns, or `tracking_error == 0`) | same |
| `volatility_summary.portfolio_volatility_pct` | `float \| None` | `0.0` at N=1 (paired observations); `None` only at N=0 | `None` at N<2, matching `portfolio_beta`/`portfolio_correlation`/`r_squared` in the same `PortfolioRiskSummary` struct | no trust-rung change — this is a math-layer null-convention fix, not a withholding-policy fix |
| `volatility_summary.benchmark_volatility_pct` | `float \| None` | `0.0` at N=1 | `None` at N<2 | same |
| `run_metadata.section_trust.risk_contribution_path` | `Literal["verified_adjusted_close", "degraded_unverified_return_basis", "unavailable"]` | unchanged | unchanged | **not touched by any fix** — Fix 3 is a frontend label-text change only |
| RiskSummaryCard.tsx rendered string at the "Risk contribution basis" line | n/a (UI text) | `"Risk contribution basis: Verified"` when `risk_contribution_path === "verified_adjusted_close"` | scoped wording naming price-field provenance specifically (exact copy is the frontend lane's call within the constraint below) — must not read as an unqualified "Verified" claim over Factor HHI / Position HHI / top-N risk shares | UI-only; see § Fix 3 |

No field is added, removed, renamed, or retyped. This is why Fix 1/Fix 2/Fix 4 do not require a frontend companion change — `RiskSummaryCard.tsx` already renders `formatPct(dd.current_drawdown_pct)` etc. unconditionally; it will simply start rendering real numbers instead of `n/a` once the backend passes them through. Frontend engineer's job on Fix 1/2/4 is `- none`: verify (not build) that the existing render paths (lines 116-121, 149-157 of RiskSummaryCard.tsx) already handle non-null values correctly (they do — no `if (value === 0)` special-casing exists).

## Fix 1 — unwithhold diagnostics drawdown

**Owner: backend only. No schema/contract type change.**

File: `services/quant-engine/app/services/trust_gate.py:244-245`

Current:
```python
def allow_diagnostics_drawdown_outputs() -> bool:
    return False
```

Change to accept and return `historical_sections_available`, mirroring the parameter the sibling `build_diagnostics_section_trust` (same file, lines 217-228) already takes and mirroring the Risk-tab drawdown engine's "publish or unavailable, no withheld rung" policy (`docs/contracts/risk-fields.md:548`, cited in 03-quant-research.md § Recommended condition):

```python
def allow_diagnostics_drawdown_outputs(*, historical_sections_available: bool) -> bool:
    return historical_sections_available
```

Call site: `services/quant-engine/app/services/diagnostics_engine.py:339`

Current:
```python
    allow_drawdown_outputs = allow_diagnostics_drawdown_outputs()
```

Change to:
```python
    allow_drawdown_outputs = allow_diagnostics_drawdown_outputs(historical_sections_available=True)
```

(`historical_sections_available=True` is a hardcoded literal already used at the neighboring `build_diagnostics_section_trust` call, diagnostics_engine.py:308 — this function, `build_historical_diagnostics_result`, is only ever invoked on the available path; the unavailable path at diagnostics_engine.py:497-539 builds `DiagnosticsDrawdownSummary()` directly with its own defaults and never calls this gate at all, so no other call site needs updating.)

Net effect: the gate becomes a pass-through in the only place it is exercised. The math-layer null handling already in `volatility_regime`/`drawdown.py` (insufficient history, N<2, etc. — not touched by this fix) remains the sole source of `None` on these two fields going forward.

**Also update:** `allow_diagnostics_drawdown_outputs`'s new signature should carry a short comment explaining why it takes a parameter it always receives as `True` today — point at the dashboard sibling gate's dated-rationale-comment convention (trust_gate.py:136-161) so a future reader does not mistake the always-`True` call site for dead code. Do not add speculative future-conditioning logic; the parameter exists so the function's shape matches its sibling and so a future `historical_sections_available=False` caller (if one is ever added) is handled correctly by construction, not because any caller needs it today.

**Doc corrections (docs lane, after backend lands):**
- `docs/contracts/dashboard-fields.md:238` — "This Dashboard row is unchanged" language about Portfolio Volatility publication threshold is unaffected by Fix 1 (that's the Fix 4 paragraph); the Fix 1 paragraph is the **next** table row, `docs/contracts/dashboard-fields.md:238`'s "Current / Max Drawdown" row and note: "diagnostics' drawdown is a separate, unwithheld path" — this claim becomes TRUE after Fix 1 ships; verify the note's wording still matches (no "always null" caveat should be added, since it's genuinely fixed now) and add a cross-reference to `docs/contracts/risk-fields.md:548`'s "no withheld rung" policy per 03-quant-research.md's contract_notes, so both synthetic-drawdown surfaces are documented as following one policy.
- `docs/contracts/dashboard-fields.md:287` (Accuracy Rule 6) — "RiskSummaryCard sidesteps this by sourcing drawdown from the separate, unwithheld diagnostics path instead" — becomes accurate; no wording change needed beyond confirming it, unless review finds drift.
- No methodology.md change identified for Fix 1 — the underlying formula and its degenerate-case handling were already correctly documented; only the categorical gate was wrong.

**Test coverage (test lane):**
- New fixture: a diagnostics run with `historical_basis` producing `historical_sections_available=True` and enough paired history for `current_drawdown_pct`/`max_drawdown_pct` to be real, non-null values — 03-quant-research.md risks flags that no such fixture exists today.
- Update the four pinned-null assertions the audit cites: `test_routes.py:595-598`, `:1088-1089`, `:2546-2547`, `:2739` — these currently assert `drawdown_summary == {"current_drawdown_pct": None, "max_drawdown_pct": None}` unconditionally; after Fix 1 they must assert real values under the new fixture (or, if those specific tests exercise a genuinely-unavailable/insufficient-history scenario, confirm they still correctly assert `None` for THAT reason and are not merely pinning the old gate's behavior).
- `test_trust_gate.py`: 03-quant-research.md's grounding log (item 12) notes the existing test only pins object-identity of the US-43.3 relocation and never exercises either gate's boolean logic — add a direct unit test for `allow_diagnostics_drawdown_outputs(historical_sections_available=True/False)` returning `True`/`False` respectively.

## Fix 2 — unwithhold diagnostics relative return

**Owner: backend only. No schema/contract type change.**

File: `services/quant-engine/app/services/diagnostics_engine.py:187-188`

Current:
```python
def _allow_diagnostics_relative_return_outputs() -> bool:
    return False
```

`build_relative_risk_summary` (risk.py:744-770) already implements every edge case the methodology doc specifies (fewer than 2 paired returns → both null; `tracking_error == 0` → `information_ratio` null only) — per 03-quant-research.md FINDING 2 point 2, this categorical gate discards already-correct output. The recommended condition is to pass values through unmodified whenever historical sections are available — same shape as Fix 1:

```python
def _allow_diagnostics_relative_return_outputs(*, historical_sections_available: bool) -> bool:
    return historical_sections_available
```

Call site: `services/quant-engine/app/services/diagnostics_engine.py:326`

Current:
```python
    allow_relative_return_outputs = _allow_diagnostics_relative_return_outputs()
```

Change to:
```python
    allow_relative_return_outputs = _allow_diagnostics_relative_return_outputs(historical_sections_available=True)
```

Same rationale as Fix 1 for the hardcoded `True`: this function (`build_historical_diagnostics_result`) only runs on the available path.

`_apply_diagnostics_relative_return_output_policy` (diagnostics_engine.py:191-204) itself needs no change — it already does the right thing (`return relative_risk` unmodified) once `allow_relative_return_outputs` is `True`.

**Doc corrections (docs lane, after backend lands):**
- `docs/contracts/dashboard-fields.md:242` — the "rows omitted entirely... `n/a` per individually-null field otherwise" language is already roughly accurate post-fix (it describes math-layer nullability, which is now the only source of nulls) — confirm no further edit needed, or tighten wording if review finds it still implies the old unconditional-null behavior.
- `financial-methodology.md:1141-1149` ("Contract rule") — currently states these fields "carry the same trust/withholding semantics as `tracking_error_pct`." Per 03-quant-research.md FINDING 2 point 3, this was FALSE before Fix 2 (tracking_error_pct was never gated; IR/active_return were unconditionally gated) and becomes TRUE after Fix 2 ships (neither field is now categorically gated; both rely solely on math-layer nulls). Docs lane should re-read this section after the fix lands and confirm the "same semantics" claim now holds, updating only if drift is found — 03-quant-research.md is explicit that both the contract doc AND this methodology section must be corrected together if the owner had instead chosen option (b); since (a) was chosen, confirm rather than rewrite.

**Test coverage (test lane):**
- Reuse the Fix 1 verified-adjusted-close fixture (same run) to also assert `relative_risk.information_ratio`/`active_return_pct` are real, non-null values when `tracking_error_pct` is non-null and paired returns are sufficient.
- Add a case where `showRelativeRisk` (RiskSummaryCard.tsx:68, `tracking_error_pct != null`) is true AND `information_ratio`/`active_return_pct` are real numbers — this is the exact coherence case the card comment (lines 58-60) says it exists to protect, and per 01-quant-audit.md FINDING 2 it was never actually exercised.
- Add/update a unit test for `_allow_diagnostics_relative_return_outputs(historical_sections_available=True/False)`.

## Fix 3 — relabel `risk_contribution_path` badge

**Owner: frontend only. No backend change, no schema change.** `risk_contribution_path`'s field name, type, and enum values (`verified_adjusted_close` / `degraded_unverified_return_basis` / `unavailable`) all stay exactly as-is — this fix is contained entirely in `RiskSummaryCard.tsx`'s rendering.

File: `apps/desktop/src/features/portfolio/RiskSummaryCard.tsx`

Two candidate touch points, both in-scope for the frontend lane to choose between (pick one, do not do both):

1. `sectionTrustLabel` (lines 23-32) — change the `'verified_adjusted_close'` case's return value from `'Verified'` to something that names price-field provenance specifically, e.g. `'Adjusted-close basis: verified'` — but note this function's label also feeds the OTHER two `section_trust` fields it is NOT currently used for elsewhere on this card (it is only called once, line 64, for `risk_contribution_path`) — confirm via grep that no other caller exists before changing its return values, since a shared helper's output must stay correct for every caller.
2. The render line itself (line 95): `<p className="helper" ...>Risk contribution basis: {trust}</p>` — change the surrounding sentence instead of the word "Verified" itself, e.g. `Risk contribution basis (adjusted-close price provenance only): {trust}` — leaves `sectionTrustLabel` untouched, scopes the caveat to the sentence rather than the badge word.

Per audit FINDING 3's expected resolution ("a distinct label... scoped explicitly to price-field provenance, not overall trust"), either satisfies it. Recommend option 2 (touch the surrounding sentence, not the shared `sectionTrustLabel` function) since `sectionTrustLabel` is written as a generic three-state formatter and grep confirms it has exactly one call site today (line 64) but changing its return string couples a generic-sounding helper to this one specific caveat — the sentence-level fix keeps `sectionTrustLabel`'s vocabulary ("Verified"/"Degraded"/"Unavailable") reusable if a future card needs the same three states without the price-provenance caveat. Frontend lane may override this recommendation with reasoning in its own report if it finds a better shape; that is a declared deviation, not a violation (§ Design pass in the architecture pack).

Do NOT add `provenance.historical_basis` to this card as an additional field read — audit's "at minimum" alternative (surface `provenance.historical_basis` next to the badge) is a larger UI change (new data binding, new row) that the human's "relabel narrowly" decision (work order Fix 3 title) rules out; the work order is explicit this is a narrow relabel, not a provenance-surfacing feature.

**Test coverage (test lane):** update/add a Vitest assertion on the rendered "Risk contribution basis" text for the `verified_adjusted_close` case, confirming the new copy does not contain the bare word "Verified" without the price-provenance qualifier next to it.

**Doc corrections (docs lane):** `docs/contracts/dashboard-fields.md`'s "Risk contribution basis label" row (in the Risk Summary card table, the row with Notes = "plain-text label distinct from the Exposure-tab `TrustBadge` primitive") — update the Notes cell to state the label is scoped to price-field provenance, matching whatever exact copy the frontend lane ships.

## Fix 4 — null convention for portfolio/benchmark volatility at N<2

**Owner: backend only. No schema/contract type change** (`float | None` unchanged; `None` was already a legal value at N=0).

File: `services/quant-engine/app/analytics/risk.py:507-508`

Current:
```python
        portfolio_volatility_pct=round(_calculate_annualized_volatility(portfolio_samples) * 100, 2) if portfolio_samples else None,
        benchmark_volatility_pct=round(_calculate_annualized_volatility(benchmark_samples) * 100, 2) if benchmark_samples else None,
```

The guard `if portfolio_samples else None` is a truthy-list check (only catches N=0); `_calculate_annualized_volatility` itself (risk.py:2117-2120) internally returns `0.0` at `len(values) < 2`, so N=1 slips through as `0.0`. Every other call site of this same function in this file already guards with an explicit `len(...) >= 2` check before calling it (risk.py:750, :1177, :1669, :1890) rather than relying on its internal `0.0` fallback. Change to match that existing pattern, and to match `_calculate_beta`/`_calculate_correlation`'s `len < 2 → None` convention in the same `PortfolioRiskSummary` struct (risk.py:2098-2114):

```python
        portfolio_volatility_pct=round(_calculate_annualized_volatility(portfolio_samples) * 100, 2) if len(portfolio_samples) >= 2 else None,
        benchmark_volatility_pct=round(_calculate_annualized_volatility(benchmark_samples) * 100, 2) if len(benchmark_samples) >= 2 else None,
```

Do NOT change `_calculate_annualized_volatility`'s own internal `if len(values) < 2: return 0.0` (risk.py:2117-2120) — every other call site that reaches it already pre-guards with its own `len >= 2` check, so that internal branch is either already unreachable at those sites or (per methodology.md:1040-1052, the N≥60 constant-series ruling for `risk_tab_volatility`) serves a documented, cited, deliberate purpose elsewhere in this file. Changing the shared helper's internal default would be a second, undeclared fix touching code outside this finding's scope — the audit's FINDING 4 is specifically about the `build_portfolio_risk_summary` call site's guard, not the helper.

**Doc correction (docs lane):** `financial-methodology.md:1054-1058` currently states "The Dashboard surface is unchanged... it publishes from N ≥ 2 and returns 0.00% at N = 1." This sentence documents the bug being fixed here and must change to state the Dashboard's `portfolio_volatility_pct` now returns `null` (not `0.00%`) at N=1, consistent with `portfolio_beta`/`portfolio_correlation`/`r_squared` in the same struct — remove the "returns 0.00% at N=1" clause entirely rather than leaving it as stale grounding. This is the same paragraph that documents the Risk-tab's 60-observation floor (`risk_tab_volatility`) — that floor and its chi-square-distribution citation are UNCHANGED by this fix (Fix 4 only touches the N=1 case of the Dashboard's own field, `portfolio_volatility_pct`, not `risk_tab_volatility`); docs lane must edit only the N=1 sentence, not the surrounding N≥60 ruling.
- `docs/contracts/dashboard-fields.md:238` — "Portfolio Volatility here has no minimum-observation floor: it publishes from N ≥ 2 (0.00% at N = 1)" — same correction, change "(0.00% at N = 1)" to reflect `null` at N=1 (N≥2 threshold itself is unaffected — N=2 still publishes a real value).

**Test coverage (test lane):** 01-quant-audit.md's § Independent recomputation log item 3 already hand-verified the N=1 case reproduces `0.0` today (pre-fix) — add a regression test asserting `portfolio_volatility_pct is None` and `benchmark_volatility_pct is None` at exactly 2 daily states (1 paired observation), alongside the existing N=0 (`None`, already correct) and N≥2 (real value) cases, in `test_analytics.py` near the existing `build_portfolio_risk_summary` coverage.

## Reuse

- Fix 1 and Fix 2 both reuse the `historical_sections_available` parameter shape already established by `build_diagnostics_section_trust` (trust_gate.py:217-228) — named specifically so both gates take the same input the trust-rollup function already takes, rather than inventing a new signal.
- Fix 4 reuses the exact `len(...) >= 2` guard pattern already present at risk.py:750, :1177, :1669, :1890 in the same file, and the `None`-at-N<2 convention already used by `_calculate_beta`/`_calculate_correlation` in the same struct — no new pattern introduced.
- Fix 3 reuses the existing `sectionTrustLabel` three-state vocabulary; only the copy changes, not the mechanism.

## Decisions

- Fix 1/Fix 2 call sites pass `historical_sections_available=True` as a literal, not by threading a live variable further, because `build_historical_diagnostics_result` (where both call sites live) is structurally only ever invoked on the available path — the unavailable path (diagnostics_engine.py:497-539) constructs its own all-null summaries directly and never reaches either gate. Do not refactor the unavailable path to also call through the gate; that would be a scope-creep restructuring this fix does not need.
- Fix 3: relabel the surrounding sentence (RiskSummaryCard.tsx:95), not `sectionTrustLabel`'s return strings, to keep the shared helper's vocabulary reusable — see § Fix 3 for the frontend lane's latitude to choose otherwise with declared reasoning.
- Fix 4 touches only the `build_portfolio_risk_summary` call site, not `_calculate_annualized_volatility`'s internal default — the internal `0.0`-at-N<2 branch is pre-guarded-around everywhere else in this file and is out of this finding's scope.
- No fix touches `_herfindahl_index` duplication (audit FINDING 5, MINOR, explicitly "not blocking" — excluded from this work order's `definition_of_done` and out of scope here).

## Risks (design-level)

- Fix 1 and Fix 2's doc corrections both hinge on 03-quant-research.md's read that the current contract-doc wording becomes ACCURATE once the gates are unwithheld, requiring confirmation rather than rewriting. If the docs lane's close-out read finds residual inaccuracy (e.g., wording that still implies conditional-on-math-only nullability differs subtly from what shipped), that is a normal docs-lane finding, not evidence the code fix is wrong.
- No test today exercises a `verified_adjusted_close` diagnostics run end-to-end (03-quant-research.md risks, confirmed again during this design pass via `grep "verified_adjusted_close" test_routes.py` returning no hits per the research's grounding log item 13) — the test lane is building new fixture infrastructure, not just relaxing assertions; likely the largest-effort single task in this slice.
- Fix 1's new parameter on `allow_diagnostics_drawdown_outputs` is always called with the literal `True` today — a future reviewer could read this as dead flexibility. The required rationale comment (§ Fix 1) is load-bearing, not decorative; do not skip it.
