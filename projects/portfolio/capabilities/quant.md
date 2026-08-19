# Capability pack: quant — project `portfolio`

For the `quant-analyst` lane, both modes. This is the pack behind guardrail one.

Companion source: `portfolio/.claude/skills/quant-research/SKILL.md` — read it in
research mode for the full brief template.

---

## Sources of truth

| Doc | Role |
|---|---|
| `docs/finance/financial-methodology.md` | **the specification.** Every implemented formula, with citations. Code is measured against this, not the reverse. |
| `docs/product/current-product-state.md` | what already ships — do not re-derive it |
| `docs/contracts/<area>-fields.md` | field ↔ formula traceability |
| `docs/tech-debt-register.md` | recorded hardcodes, magic numbers, fragile couplings |

## The analytics modules

Read the relevant module before proposing or auditing anything nearby.
Duplication is a much worse smell than coupling here.

| Module | What lives there |
|---|---|
| `performance.py` | TWR (`build_true_performance_series`), money-weighted return (Modified Dietz), enriched positions |
| `risk.py` | **far more than its name suggests.** Volatility, drawdown, rolling factor model, rolling correlation/beta vs primary benchmark, risk contribution + concentration (risk-share, top-N, HHI), tracking error, Information Ratio, **and** sector/look-through exposure. Grep it before assuming a metric does not exist. |
| `correlation.py` | Pearson ρ, beta, R², pairwise matrix, diversification ratio, effective number of bets |
| `attribution.py` | factor-return decomposition + residual |
| `drawdown.py` | underwater curve, episodes, per-position contributors |
| `distribution.py` | return histogram, percentiles, VaR/CVaR, distribution shape |
| `activity.py` | monthly ledger activity, holdings timeline |
| `reconciliation.py` | statement reconciliation (cash, NAV, withholding) |
| `overview.py` | `build_portfolio_overview` snapshot summary |
| `currency.py` | base-currency conversion for weight denominators |
| `currency_exposure.py` | currency mix by weight |
| `currency_risk.py` | share of return volatility from FX moves |
| `portfolio_imports.py` | composition layer, not a metric target |
| `services/drift_engine.py` | drift windows — **no `analytics/drift.py` exists** |

**This table is a claim, and prior versions of it were wrong.** Two earlier
versions named modules that do not exist (`analytics/portfolio.py`,
`analytics/drift.py`, `analytics/exposure.py`). Both were caught only by
listing the directory mid-task. Since US-32.1 the equivalent table in the
repo's own skill is checked mechanically, but the habit stands:

```bash
ls services/quant-engine/app/analytics/
```

Run it before trusting any row here for a nontrivial change. The fastest way
this table goes stale is a module name that *sounds* right.

## Project-standard constants — never re-derive

Import from `app/core/constants.py` (US-24.3):

- `_lookback_calendar_days(window) = ceil(window * 1.6) + 30` — trading-day
  window to calendar-day fetch. window=252 → ~434 calendar days.
- `MIN_DAILY_OBSERVATIONS`
- `DEFAULT_BENCHMARK_SYMBOL`

A second copy of any of these is a `MATERIAL` finding. US-34.8 found `risk.py`
holding its own copy of the daily-return formula; that is the pattern to hunt.

## The truth classes

Four, never mixed in one number:

| Class | Meaning |
|---|---|
| **broker truth** | direct from the statement |
| **snapshot analytics** | computed from current holdings, no history |
| **synthetic history** | current holdings applied to historical prices — **at most `synthetic`, never `verified`** |
| **persisted import** | stored prior import |

The trust ladder: `verified > degraded > withheld > unavailable`.

`withheld` means "we have it and do not trust it". `unavailable` means "we do
not have it". Collapsing them is a `CRITICAL` finding — the distinction is the
product's central promise.

## Known deliberate withholdings

Do not "fix" these without the owner's decision. Each was a considered call:

- **Dashboard-history `max_drawdown_pct`** — withheld pending price-basis
  verification (US-34.7).
- **Epic 34's open findings** — F-1a, part of F-10, F-12 were closed as
  will-not-fix: structurally unreachable, or bounded and immaterial. The reasons
  are in the epic's PRD.

Note the counter-example, so the rule is not read as "never publish": US-34.2
*did* publish a replay-derived TWR — under a new, explicitly labelled trust rung,
not by relaxing an existing one. Publishing under a new honest label is
legitimate; relabelling a number to make it publishable is not.

## Audit mode: recomputing independently

Your strongest move. Sketch:

```bash
cd services/quant-engine
python - <<'PY'
# 1. read the formula from financial-methodology.md, implement it from scratch
# 2. feed it the same inputs the engine used
# 3. compare, and report the numbers — not an impression
PY
```

Use `app/tests/fixtures.py` (`imported_snapshot`, `price_rows`,
`price_rows_from_returns`) to build deterministic inputs rather than inventing
your own — then your recomputation and the engine see identical data, and any
divergence is real.

Note `pytest.ini` disables sockets. Recompute against fixture data or the local
cache, not live FMP.

## The edge cases that matter here

For every audited metric, check numerically:

| Case | Correct behaviour |
|---|---|
| N < window | null for that date, not a partial-window value |
| variance = 0 (constant series) | null, **not** 0 and not 1 |
| holding with no price history (UCITS/FMP gaps) | degrade explicitly, never fabricate |
| empty portfolio / zero holdings | unavailable |
| single holding | defined, but check concentration and correlation metrics do not divide by zero |
| window longer than available history | unavailable, not silently truncated |

A degenerate case that returns a plausible number instead of null is the worst
outcome in this system — it never gets questioned.

## Units, signs, annualisation

The errors that survive review because everything looks reasonable:

- `_pct` vs `_pp` vs fraction. The suffix in the field name is the contract.
- Drawdown sign convention — check it matches the doc and the UI's expectation.
- Contribution decompositions should sum to the total; verify numerically.
- Trading days = 252. Annualisation factor √252 for volatility.
- FX: check the weight denominator is base-currency converted (`currency.py`),
  not raw. Note the tech-debt register records an FX-rate hardcode in
  `reconciliation.py` — build on it knowingly or not at all.

## Research mode: brief sections

Seven, in order — full templates in the `quant-research` skill:

1. Problem framing — what question, why not answerable now, what decision it enables
2. Concept & academic grounding — precise name, signed meaning, 1–3 citations, known pitfalls
3. Formulas — symbols, assumptions, edge cases, lookback mapping
4. Data requirements — source, field, frequency, lookback, trust; minimum viable dataset; benchmark universe; instrument gaps
5. Trust-class analysis, per field
6. Visualization design — chart type, axes, series, states, badge placement
7. Computed-metrics inventory — one row per schema field

Also check `docs/tech-debt-register.md` for open findings in the area. If the
brief builds near a recorded fragile spot, name it and state whether the work
depends on it, works around it, or should wait.

Do not draft tickets. That is story authoring.

## Definition of done for this lane

**Research mode**
- [ ] Checked the concept is not already implemented under another name
- [ ] `ls app/analytics/` run before trusting the module table
- [ ] Every formula has symbols, assumptions and edge cases; no edge case resolved with a fallback value
- [ ] Trust class and level stated per output field; synthetic-history outputs never claim `verified`
- [ ] Citations real and specific
- [ ] Metrics inventory complete, nullability correct
- [ ] Relevant tech-debt findings named
- [ ] No tickets drafted

**Audit mode**
- [ ] Values independently recomputed, not just read — numbers reported
- [ ] Code checked against the methodology doc, in that direction
- [ ] Grepped for duplicate implementations of the formula
- [ ] Trust classification checked against the basis it actually rests on
- [ ] Every edge case in the table above exercised numerically
- [ ] Units, signs, annualisation verified
- [ ] Anything unreproducible stated as unreproducible, not passed
