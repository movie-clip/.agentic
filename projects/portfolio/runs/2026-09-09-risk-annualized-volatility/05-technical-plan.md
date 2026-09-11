REPORT 2026-09-09-risk-annualized-volatility/05
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   none
  result:    NOT_RUN
  detail:    Read-only DESIGN pass; order verification field is NONE. No repo file edited; only this artifact written.

contract_notes:
  - docs/finance/financial-methodology.md section "Annualized realized volatility" (~line 1012) needs an AMENDMENT (not a new section) recording the Risk-tab 60-paired-observation publication floor and the N=0 unavailable / 1-59 withheld / >=60 published(synthetic) rungs, Dashboard surface unchanged and unfloored. Docs lane writes the text at close-out. see section 7.
  - docs/contracts/risk-fields.md needs a NEW section for the risk_tab_volatility object (4 fields) plus a note that its synthetic|withheld|unavailable trust vocabulary extends the Risk-tab preamble's "no withheld rung" for this one figure. see section 7.
  - docs/contracts/diagnostics-fields.md volatility_summary block (~line 216) needs a cross-reference: risk_tab_volatility.annualized_volatility_pct is the publication-gated Risk-tab view of volatility_summary.portfolio_volatility_pct, same source scalar and code path. see section 7.
  - docs/product/current-product-state.md needs the Risk-tab annualized volatility figure added to shipped Risk-tab scope at close-out. see section 7.
  - services/quant-engine/app/schemas/diagnostics.py adds a RiskTabAnnualizedVolatility model + RiskTabVolatilityTrust literal and a required risk_tab_volatility field on DiagnosticsResult; the schema hook will fire and TS types + both contract docs must move in the same slice. see section 1.

pack_corrections:
  - none

handoff:
  - TECHNICAL PLAN follows in sections 1-9; orchestrator brief is the index. Lane split and ordered work orders in section 6.
  - Chosen shape: a backend-gated dedicated view (scout Option B, minimal form) consumed by frontend via scout Option A wiring (thread the already-in-App-state diagnosticsAnalysis, no new fetch). Rationale in section 4.
  - Backend work order (T-44.1.1): core/constants.py new floor constant; schemas/diagnostics.py new model + literal + field; services/diagnostics_engine.py gate helper wired into both the populated and the unavailable builder. Reuse only, no analytics/risk.py edit. Contract section: section 1.
  - Frontend work order (T-44.1.2): types.ts mirror; App.tsx:912 prop; RiskPanel.tsx prop + new AnnualizedVolatilityCard.tsx (prop-driven, no self-fetch, no WindowSelector); optional minimal TrustBadge union extension. Contract section: section 1. Reuse: section 2.
  - Test work order (T-44.1.3): backend + frontend + cross-surface cases from the story test plan; encodes the Open-decision-2 resolution once the human rules. Depends on T-44.1.1 + T-44.1.2.
  - Docs close-out (T-44.1.4): the four doc targets in section 7, driven by the contract_notes above. After the gates pass.
  - Human ruling needed BEFORE T-44.1.1 backend implements the gate: Open decision 2 (zero-variance series at N>=60 -> publish 0.00% or withhold). Recommendation and trade-off in section 5; recommendation is PUBLISH 0.00%.
  - Guardrail 1: this is net-new trust-state logic. quant-audit (AUDIT) runs after implementation; the RESEARCH brief 02 already precedes it.
  - Frozen diagnostics fixtures/goldens will need regeneration once the required field lands (test lane); the field is deliberately required, not defaulted, so every construction path classifies.

risks:
  - The floor gates on risk_summary.observations (paired portfolio+benchmark daily returns), not the distribution engine's unpaired return_count; the two N's count slightly different series. quant-audit should confirm gating on paired N is right here (brief 02 section 1.2 anchors on it).
  - Consequence of the paired-N gate: a researcher can see the VaR card populate (unpaired N>=20) while this figure withholds (paired N<60). That is the intended stricter-floor asymmetry, not a defect (brief 02 section 3.2).
  - diagnosticsAnalysis can be null in App state when the Risk tab renders if exposure analysis threw (scout risk). The card then renders loading/unavailable; the Risk-tab figure silently depends on the Dashboard's diagnostics fetch succeeding.
  - Extending the shared TrustBadge primitive with a "withheld" member touches every card that imports it plus designSystem.audit.test.ts. Contained and invited by the primitive's own docstring, but not zero-blast; the fallback (distinct EmptyState copy only) also satisfies the ACs.
  - If the human rules "withhold" on zero-variance, the backend helper gains a branch (n>=floor and vol==0.0 -> withheld) and the T-44.1.3 tests change; cross-surface byte-equality at N>=60 then no longer holds for that portfolio.
  - The TS diagnostics response has multiple shapes (ImportedDiagnosticsSource, the snapshot-request variant, DiagnosticsEngineResponse); the mirror must reach every shape that mirrors DiagnosticsResult or tsc diverges.
  - analytics/risk.py already carries WINDOW_MIN_OBSERVATIONS = {20:25, 60:75, 252:275} containing a "60"; the new constant's comment must disambiguate it from that OLS buffer and from MIN_DAILY_OBSERVATIONS (20).

## Orchestrator brief

- Shape decision: backend-gated dedicated view + frontend Option-A wiring (no new fetch, no new engine, no new route). The N=0 vs 1-59 split is decided server-side in the diagnostics engine; the frontend only renders the arriving trust state.
- Contract decision: new `RiskTabAnnualizedVolatility` model on `DiagnosticsResult`, field `risk_tab_volatility`, with its own `trust: "synthetic" | "withheld" | "unavailable"` literal (a superset used only here, not an edit to the sibling engines' literals).
- Contract decision: `annualized_volatility_pct: float | None` non-null iff `trust == "synthetic"`; byte-identical to `volatility_summary.portfolio_volatility_pct` when published; `observations` and `minimum_observations` (=60) also on the wire for the UI copy.
- Constant decision: `RISK_TAB_ANNUALIZED_VOL_MIN_OBSERVATIONS = 60` in `core/constants.py`; frontend reads `minimum_observations` from the payload rather than mirroring a literal.
- Reuse decision: scout Option A wiring wins for the frontend (diagnosticsAnalysis already in App state); scout Option B (distribution-engine field) rejected - it forces a recompute on a different N. See section 4.
- Card decision: a new prop-driven `AnnualizedVolatilityCard.tsx` in `.risk-shell-stack`, no WindowSelector (figure uses full paired history), CardShell + TrustBadge + StatRow/EmptyState.
- Recommendation on Open decision 2 (zero-variance at N>=60): PUBLISH 0.00%. Human rules before T-44.1.1 backend. See section 5.
- Lane split (section 6): T-44.1.1 backend contract+gate -> T-44.1.2 frontend types+card -> T-44.1.3 tests -> gates -> T-44.1.4 docs close-out. Re-cut from the story's 5 tickets: methodology/contract text moves to the docs close-out lane.
- Blocks dispatch: human ruling on Open decision 2 before T-44.1.1. Nothing else.
- Sections below: "1. The contract" field by field; "2. Reuse map" named per lane; "3. The floor constant" name/location/call sites; "4. Where the 60-observation gate executes" placement and why not Option A/B; "5. Recommendation - Open decision 2 (zero-variance series at N >= 60)"; "6. Lane split and ordered work orders" re-cut from the story; "7. Contract-doc impact (contract_notes for the docs close-out)"; "8. Decisions taken (engineers must not remake these independently)"; "9. Risks".

---

## 1. The contract

The single most load-bearing output of this pass. Both the backend and frontend
work orders are pointed here.

### 1.1 Truth class

**Synthetic history** throughout - current holdings valued over historical
prices, no trade replay. This is the *same* truth class and the *same* scalar as
the Dashboard's `volatility_summary.portfolio_volatility_pct`; the only
difference is a presentation-layer publication threshold. No truth-class mix
(guardrail 3): there is one documented formula and one executable code path
(`_calculate_annualized_volatility`, `analytics/risk.py:2117-2120`), reused, not
re-implemented.

### 1.2 The wire representation

A new Pydantic model, added to `services/quant-engine/app/schemas/diagnostics.py`
next to `DiagnosticsVolatilitySummary`:

```python
RiskTabVolatilityTrust = Literal["synthetic", "withheld", "unavailable"]

class RiskTabAnnualizedVolatility(BaseModel):
    """Risk-tab publication-gated view of the SAME scalar as
    volatility_summary.portfolio_volatility_pct. Not a recomputation:
    annualized_volatility_pct is copied from risk_summary.portfolio_volatility_pct
    when the paired-observation floor is met. US-44.1."""
    annualized_volatility_pct: float | None = None
    trust: RiskTabVolatilityTrust = "unavailable"
    observations: int = 0
    minimum_observations: int
```

Added to `DiagnosticsResult` (`schemas/diagnostics.py`), **required, no default**:

```python
    risk_tab_volatility: RiskTabAnnualizedVolatility
```

### 1.3 Field by field

| Field | Python type | TS type | Nullable | Rule / meaning |
|---|---|---|---|---|
| `annualized_volatility_pct` | `float \| None = None` | `number \| null` | yes | Non-null **iff** `trust == "synthetic"`. Percent units, already x100, 2 dp (inherits `round(..., 2)` from `risk.py:507`). When non-null it is the exact value of `volatility_summary.portfolio_volatility_pct` for the same response - byte-identical, not recomputed (AC 4, AC 5). |
| `trust` | `Literal["synthetic","withheld","unavailable"]` | `'synthetic' \| 'withheld' \| 'unavailable'` | no (default `"unavailable"`) | `synthetic` = published, paired observations >= floor. `withheld` = 1..59 paired observations: the series exists, the annualized projection over a sub-quarter sample is not trustworthy (brief 02 section 2). `unavailable` = 0 paired observations, or no history context. Never serialized as `unavailable` when the state is withheld (AC 10, guardrail 4). |
| `observations` | `int` (default 0) | `number` | no | Paired daily-return count; mirror of `risk_summary.observations`. Drives the "N of 60" UI copy in the withheld state (AC 8). |
| `minimum_observations` | `int` | `number` | no | The floor constant, `60`. Echoed on the wire so the card copy and the methodology link do not hardcode it and so the frontend needs no mirrored constant. |

### 1.4 Where the withheld rung lives - decision and justification

**Decision: a dedicated model with its own three-value `trust` literal, NOT an
extension of the sibling engines' literals.**

The distribution and stress engines expose `Literal["synthetic","unavailable"]`
(`schemas/distribution.py:18`, `DistributionTrustLevel`). This figure needs a
`withheld` rung they do not have. The options were (a) widen
`DistributionTrustLevel` / `StressTrustLevel`, or (b) a separate shape.

Chosen (b), because:

- Widening a per-engine literal forces the distribution and stress engines - and
  their cards, tests and contract rows - to reason about a `withheld` value they
  never emit. That is scope the story's non-goals explicitly exclude ("the
  sibling Risk-tab engines' trust vocabulary beyond what this figure needs").
- A dedicated model keeps the publication-gate semantics - the floor, the three
  rungs, the `null` rule - self-contained and documented in one place
  (`risk-fields.md` new section, methodology amendment).
- `RiskTabVolatilityTrust` is a strict superset used **only** by this field, so
  no sibling surface changes.

The Risk-tab contract preamble (`risk-fields.md:16`, "No Risk-tab field is ever
`verified`") stays true - this figure is `synthetic` or below, never `verified`
or `degraded` (AC 3). The preamble's implicit "synthetic|unavailable only" needs
a one-line note that this figure adds `withheld`.

### 1.5 Absence behaviour, per state (for the card)

| State | `annualized_volatility_pct` | Card renders |
|---|---|---|
| `synthetic` | the number | CardShell + `TrustBadge type="synthetic"` + one `StatRow` `X.XX%` |
| `withheld` | `null` | `EmptyState` titled as held-back, detail names the 60-trading-day requirement and "N of 60", and that the Dashboard shows an unfloored estimate for the same portfolio (AC 7, AC 8). No number, no `0`, no `-`. |
| `unavailable` | `null` | `EmptyState` titled unavailable, detail "no return history" - visibly distinct copy from the withheld state (AC 9, AC 10). |

Loading / pre-import: `diagnosticsAnalysis` null while a snapshot exists ->
`LoadingState`; no snapshot -> RiskPanel already renders its thin header only.

---

## 2. Reuse map

Named, per lane. A named function is an instruction.

### Backend (`services/quant-engine/`)

- **Reuse the value, do not recompute.** `risk_summary.portfolio_volatility_pct`
  is already on `DiagnosticsResult` (`diagnostics_engine.py:409`, `:422`) and
  already carries the paired count as `risk_summary.observations`
  (`analytics/risk.py:503`). The gate helper reads both off `risk_summary`; it
  does **not** call `_calculate_annualized_volatility`,
  `_paired_portfolio_and_benchmark_returns`, or anything in `analytics/`.
- `build_portfolio_risk_summary` (`analytics/risk.py:491`) - unchanged. It still
  computes the unfloored figure the Dashboard consumes.
- `build_unavailable_diagnostics_result` (`diagnostics_engine.py:437`) - the
  helper is called here too; its `risk_summary.observations` is already `0`, so
  it yields `trust="unavailable"`.
- New constant lives in `app/core/constants.py` beside `MIN_DAILY_OBSERVATIONS`
  (the US-24.3 single-home rule).

### Frontend (`apps/desktop/src/`)

- **scout Option A wiring.** `diagnosticsAnalysis` is already in App state
  (`App.tsx:287`) whenever a portfolio is loaded. Add
  `diagnosticsAnalysis={diagnosticsAnalysis}` to `<RiskPanel>` (`App.tsx:912`) -
  no new network call, no new adapter function.
- `RiskPanel.tsx` - add the prop to `RiskPanelProps`; mount the new card in the
  existing `.risk-shell-stack` after `VarDistributionCard`.
- New `AnnualizedVolatilityCard.tsx` - **prop-driven** like `StressScenariosCard`
  (RiskPanel passes it `risk_tab_volatility`), NOT self-fetching. No
  `WindowSelector` (the figure uses the full available paired history, not a
  window - brief 02 section 3.3).
- ui-polish primitives (`apps/desktop/src/app/primitives/`, import each - no
  barrel): `CardShell` (`{title, badge, children}`), `TrustBadge`
  (`type="synthetic"`), `EmptyState` (`{title, detail}`), `LoadingState`. The
  scalar row follows `VarDistributionCard`'s `StatRow` pattern
  (`VarDistributionCard.tsx:197-226`: flex row, `var(--font-body-sm)`,
  `fontVariantNumeric: 'tabular-nums'`), tokens only.
- Methodology reachability (AC 12): `TrustBadge` `tooltip` prop + a `helper`
  line, pointing at the "Annualized realized volatility" methodology section and
  naming the 60-observation floor - mirrors how `VarDistributionCard` surfaces
  its methodology note.
- **Optional, recommended:** extend `TrustBadge` (`primitives/TrustBadge.tsx`)
  with a `withheld -> "Withheld"` label so the card header badge is honest in the
  withheld state too. The primitive's docstring already anticipates this. If not
  taken, the distinct `EmptyState` copy carries the withheld/unavailable
  distinction on its own (AC 10 still satisfied).

### Test (`apps/desktop/src/test/`, `services/quant-engine/app/tests/`)

- `designSystem.audit.test.ts` - add `AnnualizedVolatilityCard.tsx` to
  `ALL_CARD_FILES` and `CARDS_WITH_BADGE` (scout section ui-polish pattern).
- Frozen diagnostics fixtures/goldens regenerate once the required field lands.

---

## 3. The floor constant

- **Name:** `RISK_TAB_ANNUALIZED_VOL_MIN_OBSERVATIONS`
- **Value:** `60`
- **Location:** `services/quant-engine/app/core/constants.py`, beside
  `MIN_DAILY_OBSERVATIONS`. Comment must state: it is a **publication floor for
  the Risk-tab surface of the annualized volatility figure only**; it is NOT
  `MIN_DAILY_OBSERVATIONS` (20, the product-wide per-metric minimum) and NOT
  `analytics/risk.py`'s `WINDOW_MIN_OBSERVATIONS` `{20:25, 60:75, 252:275}` OLS
  buffer; grounding is `02-quant-research.md` section 2.4.

**Call sites that must read the constant, never a literal `60`:**

1. `services/quant-engine/app/services/diagnostics_engine.py` - the gate helper
   `_build_risk_tab_annualized_volatility`, used on both the populated path
   (after `risk_summary` is built, ~line 422) and inside
   `build_unavailable_diagnostics_result` (~line 486). The helper writes the
   constant into `minimum_observations`.
2. `services/quant-engine/app/tests/**` - any test asserting the boundary reads
   the constant (or imports it) rather than pinning `60`.
3. Methodology amendment references it **by name** (docs lane).

**Not a call site - deliberately:** the frontend. It renders
`risk_tab_volatility.minimum_observations` from the payload. Do not add a
mirrored `60` constant on the frontend (the existing `MIN_OBSERVATIONS = 20`
literals in `DrawdownAnalyticsCard.tsx:63` / `VarDistributionCard.tsx:42` are a
known small duplication we are not repeating here).

---

## 4. Where the 60-observation gate executes

**Server-side, in the diagnostics engine.** A pure helper classifies the state
and selects the value; the view only renders what arrives.

```python
# services/quant-engine/app/services/diagnostics_engine.py
def _build_risk_tab_annualized_volatility(
    risk_summary: PortfolioRiskSummary,
) -> RiskTabAnnualizedVolatility:
    floor = RISK_TAB_ANNUALIZED_VOL_MIN_OBSERVATIONS
    n = risk_summary.observations
    if n <= 0:
        return RiskTabAnnualizedVolatility(
            trust="unavailable", observations=0, minimum_observations=floor)
    if n < floor:
        return RiskTabAnnualizedVolatility(
            trust="withheld", observations=n, minimum_observations=floor)
    return RiskTabAnnualizedVolatility(
        annualized_volatility_pct=risk_summary.portfolio_volatility_pct,
        trust="synthetic", observations=n, minimum_observations=floor)
```

Why this placement:

- **The split is server-side** (DoD): `N = 0` vs `1..59` is decided by
  `risk_summary.observations`, not by the card inspecting a value.
- **The `len < 2 -> 0.0` branch never reaches this field.** The classification
  keys on the observation count, not on whether `portfolio_volatility_pct` looks
  like a zero. At `N = 1` the reused path yields `0.0`
  (`risk.py:2118`); here `N = 1 < 60` so `trust = "withheld"` and
  `annualized_volatility_pct` stays `null`. AC 11 (never a fabricated zero) is
  satisfied structurally, not by a formatter check.
- **No recomputation, byte-identical when published.** At `N >= 60` the field is
  a straight copy of `risk_summary.portfolio_volatility_pct` from the same
  response object (AC 4, AC 5, guardrail 2).
- **Dashboard untouched.** `volatility_summary.portfolio_volatility_pct` and
  `build_portfolio_risk_summary` are not modified; the Dashboard keeps its
  unfloored estimate (story non-goal).

### Why not the other shapes

- **scout Option A, pure frontend gate** (render the withheld/EmptyState when
  `risk_summary.observations < 60` in the card): rejected. The DoD requires the
  `N = 0` vs `1..59` split server-side. A view-layer gate also means the
  withheld/unavailable semantics are not on the wire, not in the contract doc,
  and not checkable by the backend tests or quant-audit.
- **scout Option B, new field on `DistributionEngineResponse`**: rejected. The
  distribution engine builds an *unpaired* `returns` list and uses
  population-`N` std (`analytics/distribution.py`); reusing
  `portfolio_volatility_pct` there is not possible without recomputation on a
  different series and a different `N` - breaks AC 5 and guardrail 2. Its
  `return_count` is also a different count from `risk_summary.observations`.
- **A brand-new Risk-tab engine/route** just for one scalar already present in a
  response already in App state: unjustified weight (new route registration, new
  adapter fn, new self-fetching card) for no gain.

The chosen shape is scout Option B's *intent* (a gated field with real wire
semantics) at scout Option A's *cost* (no new fetch, no new engine): the gate
lands in the diagnostics engine, which already owns the source scalar, and the
frontend consumes the already-fetched response.

---

## 5. Recommendation - Open decision 2 (zero-variance series at N >= 60)

**Question:** with `N >= 60` and a constant daily-return series (sample stdev
`0`), does the Risk tab publish `0.00%` or withhold?

**Recommendation: PUBLISH `0.00%`.**

Engineering and methodology trade-off:

| | Publish 0.00% | Withhold |
|---|---|---|
| Methodology | Realized volatility is a **dispersion** statistic; over a genuinely constant series its value is well-defined and exactly zero - unlike a ratio (beta, correlation) which is `0/0` undefined. The quant pack's blanket "variance 0 -> null" rule is written for ratios; brief 02 (risks, section 3.3) explicitly flags it as not obviously right here. | Follows the pack's blanket edge-case rule literally. A real portfolio with 60+ identical daily returns is near-certainly a data defect (stale/flat price series), so "we do not believe this input" is defensible. |
| Code path | Zero added branches. The `trust="synthetic"` path carries the value straight through; cross-surface byte-equality with the Dashboard (AC 4) holds automatically. One documented formula, one path (guardrail 2). | A dedicated branch in `_build_risk_tab_annualized_volatility` (`n >= floor and vol == 0.0 -> trust="withheld"`). Breaks cross-surface equality at `N >= 60` for that portfolio (AC 4 survives only because it is conditioned on "when both display the figure"). |
| AC fit | AC 11 already carves out "a zero appears only as a genuinely computed value at or above the floor" - the ACs anticipate a legitimate computed `0.00%`. | Requires the withheld copy to also cover "computed zero we chose not to trust", a second meaning for the withheld state. |
| Defect detection | Not this figure's job. A stale/flat price series is surfaced by the synthetic-history coverage disclosures and per-holding price-coverage surfaces. | Bolts a variance-floor onto a presentation gate - an out-of-place half-measure. |

**This is flagged for the human to rule on before `T-44.1.1` (backend) implements
the gate.** If the ruling is "withhold", the change is the one-line branch above
plus the matching `T-44.1.3` test, and quant-audit must bless it. The story's
acceptance criteria deliberately do not assert this case either way; the test
lane encodes the resolved choice, not a guess.

---

## 6. Lane split and ordered work orders

Re-cut from the story's provisional `T-44.1.1..5`. The change: the story folded
contract representation and methodology/contract **text** into one ticket;
methodology and contract-doc prose is the docs close-out lane's under this
network (story non-goal: "name the target and hand it to docs"). So the backend
ticket carries the schema + gate and *emits contract notes*; the docs lane
writes the words at close-out.

Ordered:

**0. Human ruling** on Open decision 2 (section 5). Blocks T-44.1.1.

**T-44.1.1 - Backend: floor constant, contract, gate.** Lane: `backend`.
- Scope: `services/quant-engine/app/core/constants.py`,
  `services/quant-engine/app/schemas/diagnostics.py`,
  `services/quant-engine/app/services/diagnostics_engine.py`.
- Do: add `RISK_TAB_ANNUALIZED_VOL_MIN_OBSERVATIONS = 60` (section 3); add
  `RiskTabVolatilityTrust` + `RiskTabAnnualizedVolatility` + required
  `risk_tab_volatility` on `DiagnosticsResult` (section 1); add
  `_build_risk_tab_annualized_volatility` and call it on both the populated and
  the unavailable path (section 4). Reuse only - no `analytics/` edit.
- Resolve the zero-variance behaviour per the human ruling from step 0.
- Emit contract notes: the TS mirror, `risk-fields.md`,
  `diagnostics-fields.md`, `financial-methodology.md` (section 7).
- Not express-lane eligible (schema + trust-state logic).
- Contract reference: section 1. Reuse: section 2 (Backend).

**T-44.1.2 - Frontend: types mirror and the card.** Lane: `frontend`. Depends on
T-44.1.1's contract note.
- Scope: `apps/desktop/src/features/portfolio/types.ts`,
  `apps/desktop/src/app/App.tsx`,
  `apps/desktop/src/features/portfolio/RiskPanel.tsx`, new
  `apps/desktop/src/features/portfolio/AnnualizedVolatilityCard.tsx`, and
  (optional) `apps/desktop/src/app/primitives/TrustBadge.tsx`.
- Do: mirror `RiskTabAnnualizedVolatility` + the trust union onto every
  diagnostics-response shape in `types.ts`; thread `diagnosticsAnalysis` into
  `RiskPanel` (`App.tsx:912`); render the three states per section 1.5 with the
  ui-polish scaffold (section 2, Frontend). ui-polish skill is mandatory for the
  new card.
- Contract reference: section 1. Reuse: section 2 (Frontend).

**T-44.1.3 - Tests.** Lane: `test`. Depends on T-44.1.1 + T-44.1.2.
- Backend (`services/quant-engine/app/tests/`): `trust="unavailable"` at N=0;
  `trust="withheld"` value `null` at N in [1,59]; `trust="synthetic"` number at
  N>=60; the gate keys on observation count so N=1 never yields `0.00%` on this
  field; the withheld state serializes distinct from unavailable (guardrail 4);
  zero-variance at N>=60 asserted to the human's ruling; regression: Dashboard
  `volatility_summary.portfolio_volatility_pct` still unfloored from N>=2 and
  dashboard goldens regenerate clean; regenerate frozen diagnostics fixtures.
- Frontend (`apps/desktop/src/features/portfolio/`): `RiskPanel.test.tsx` +
  `AnnualizedVolatilityCard.test.tsx` - published number + Synthetic badge at
  N>=60; withheld presentation with the 60-day reason at N in [1,59];
  unavailable at N=0; withheld vs unavailable visually distinct; never
  `0`/`0.00%`/`-` when not published; methodology reference reachable. Update
  `designSystem.audit.test.ts` card lists.
- Cross-surface: one fixture drives both surfaces - equal to displayed precision
  at N>=60, diverge (number vs withheld) somewhere in 2 <= N < 60.

**Gates** (orchestrator-dispatched): `quant-audit` (AUDIT - guardrail 1, net-new
trust-state logic), then `integration` (tech-lead), then `review`.

**T-44.1.4 - Docs close-out.** Lane: `docs`. After the gates pass. Section 7.

**Then:** human runs `python scripts/run_all_tests.py` and commits. No lane
commits.

---

## 7. Contract-doc impact (contract_notes for the docs close-out)

| Target | Change | Detail |
|---|---|---|
| `docs/finance/financial-methodology.md` section "Annualized realized volatility" (~line 1012) | **Amendment**, not a new section | Risk-tab surface of this figure requires `N >= 60` paired daily-return observations; below it: `N = 0 -> unavailable`, `1 <= N < 60 -> withheld` (never collapsed to unavailable); `N >= 60 -> published`, trust `synthetic`. Dashboard surface unchanged and retains no explicit floor. Constant `RISK_TAB_ANNUALIZED_VOL_MIN_OBSERVATIONS = 60`, distinct from `MIN_DAILY_OBSERVATIONS` (20) and `WINDOW_MIN_OBSERVATIONS`. Record the zero-variance resolution from step 0. Cite `02-quant-research.md` section 2.4. Per the quant-pack convention this is an amendment to an existing section whose content the order specifies, so the docs lane writes it. |
| `docs/contracts/risk-fields.md` | **New section** | "Portfolio Annualized Volatility (US-44.1)" - the `risk_tab_volatility` object: `annualized_volatility_pct` (`float\|None` / `number\|null`, non-null iff published), `trust` (`synthetic\|withheld\|unavailable`), `observations` (`int`), `minimum_observations` (`int`). Backend type <-> TS type <-> UI surface (`AnnualizedVolatilityCard`). Note the trust vocabulary **extends** the preamble's synthetic/unavailable set with `withheld` for this figure only; sourced from the diagnostics engine, not a Risk-tab engine. |
| `docs/contracts/diagnostics-fields.md` `volatility_summary` block (~line 216) | **Cross-reference** | `risk_tab_volatility.annualized_volatility_pct` is the publication-gated Risk-tab view of `volatility_summary.portfolio_volatility_pct` - same source scalar, same code path, adds a 60-paired-observation floor. |
| `docs/contracts/dashboard-fields.md` | One-line note (optional) | The Dashboard figure is explicitly unfloored and unchanged by US-44.1; helps a future reader reconcile the ~2 <= N < 60 cross-surface divergence. |
| `docs/product/current-product-state.md` | Inventory add | List the Risk-tab annualized volatility figure in shipped Risk-tab scope, reconciled from the diff. |

No `docs/tech-debt-register.md` entry (brief 02 section 5.3 confirmed nothing
open touches this path). `CONTEXT.md` only if the team wants "publication floor"
recorded as vocabulary.

---

## 8. Decisions taken (engineers must not remake these independently)

1. **Shape:** gate in the diagnostics engine; frontend consumes the
   already-in-App-state `diagnosticsAnalysis`. No new engine, route, adapter
   function, or network call.
2. **Field name / model:** `risk_tab_volatility: RiskTabAnnualizedVolatility` on
   `DiagnosticsResult`; scalar field `annualized_volatility_pct`.
3. **Trust representation:** a dedicated `RiskTabVolatilityTrust =
   Literal["synthetic","withheld","unavailable"]`, not an edit to
   `DistributionTrustLevel` / `StressTrustLevel`.
4. **`annualized_volatility_pct` is non-null iff `trust == "synthetic"`.** Below
   the floor it is `null` - never `0`, never the daily stdev, never the
   Dashboard's unfloored number passed through.
5. **Gate keys on `risk_summary.observations`** (paired count), classified
   server-side, before any value is selected - not on inspecting the computed
   value.
6. **Value is copied, never recomputed** from `risk_summary.portfolio_volatility_pct`.
7. **Floor constant** `RISK_TAB_ANNUALIZED_VOL_MIN_OBSERVATIONS = 60` in
   `core/constants.py`; frontend reads `minimum_observations` off the payload,
   adds no mirrored constant.
8. **New dedicated card** `AnnualizedVolatilityCard.tsx`, prop-driven, no
   `WindowSelector`. Not a row welded onto a self-fetching card.
9. **`risk_tab_volatility` is a required field** (no default) so every
   construction path classifies; fixtures regenerate.
10. **Dashboard surface and `build_portfolio_risk_summary` are not touched.**
11. **Zero-variance at N >= 60:** recommendation is publish `0.00%`; the human
    rules before T-44.1.1 (section 5).

---

## 9. Risks

Carried in the report block above. In brief: the paired-`observations` vs
unpaired-`return_count` asymmetry (quant-audit to confirm); `diagnosticsAnalysis`
possibly null in App state if exposure analysis threw; the shared-`TrustBadge`
blast radius if the `withheld` label is added; the zero-variance ruling changing
the backend helper and tests if it comes back "withhold"; the multi-shape TS
diagnostics response mirror; and the pre-existing `WINDOW_MIN_OBSERVATIONS` "60"
that the new constant's comment must disambiguate.
