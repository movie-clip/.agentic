REPORT 2026-09-07-new-epic-perf-benchmark-trust/02
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order verification field was NONE; no command to run. Grounding assembled from financial-methodology.md and the four cited engine modules.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - P1 rule: monthly compounding must apply the shared `DailyPortfolioState.return_is_publishable` gate and `market_derived_terminal_value` exactly as `performance.py::_time_weighted_daily_return` does — see § P1.
  - P1 defect confirmed: `_compute_contribution_adjusted_monthly_returns` (dashboard_history_engine.py:837-863) is a third, ungated re-implementation of the daily-return formula — see § P1 and § Duplication.
  - P2 boolean: UI switches on the sign of `run_metadata.withheld_return_impact_pct` — `> 0` understates, `< 0` overstates, `0.00`/absent no directional claim — see § P2.
  - P3 decomposition: portfolio TWR, MWR, contributions, monthly returns, dashboard max-drawdown need no benchmark history; only relative return, tracking error, beta and the benchmark line do — see § P3.
  - P3 engineering dependency: `valuation_dates` is currently derived from `benchmark_rows` (dashboard_history_engine.py:313); a benchmark-independent trading calendar is required before the line-304 collapse can be removed — see § P3.
  - Benchmark-absent trust levels: benchmark-derived fields take `unavailable` (honest: input absent); portfolio-economics fields keep their own `verified`/`replay_derived` level — see § P3.

risks:
  - financial-methodology.md § "Monthly Returns (Dashboard)" is silent on withheld-day handling and on the terminal-reconciliation input; it only says "compound the same cash-flow-neutral daily returns as the time-weighted return chain". Intent is groundable but the doc should be made explicit at close-out — human/docs decision, see § Methodology gaps (a).
  - No per-month disclosure exists for a month that excludes a withheld day (the TWR chain has `withheld_return_impact_pct`; the monthly grid has nothing). Whether a gap-containing month needs its own marker is an open trust-design question — human decision, see § Methodology gaps (b).
  - financial-methodology.md § "Publication rungs" (US-34.2) documents `withheld_return_impact_pct` only through an understatement example; the general signed interpretation is undocumented — human/docs, see § Methodology gaps (c).
  - No methodology section states that a total benchmark-history outage must still publish portfolio-economics on the imported dashboard path; guardrails 3 and 4 imply it but the rule is unwritten — human decision, see § Methodology gaps (d).
  - Point 4 (benchmark selector) is out of quant scope per the order; its only quant interaction is that a user-chosen non-default benchmark makes a benchmark-history outage (P3) more likely, which raises the stakes on the P3 fix. Noted, not designed.

---

## Orchestrator brief

Grounding brief for three trust/analytics defects in the imported-dashboard performance chain. Read-only; no story exists yet. Verdict NONE (RESEARCH mode).

Decisions taken:
- P1: monthly returns MUST exclude any day where `return_is_publishable` is False and MUST use `market_derived_terminal_value` for the terminal day — identical to the sanctioned TWR chain. Current monthly path does neither: it violates the methodology's stated "same daily returns as the TWR chain" rule. Correct behaviour is exclude-the-day (preserves the chaining identity), not withhold-the-month, not fabricate. A month with an excluded day keeps the range's own TWR trust level; the whole-grid `monthly_returns_reliable` guard is not the right instrument.
- P2: the "understates/overstates" copy switches on `sign(withheld_return_impact_pct)`; that scalar is already on the wire (`run_metadata`), so P2 is a UI-logic fix and the rule is the only quant deliverable.
- P3: five portfolio-economics outputs are benchmark-independent and must publish when benchmark history is absent; collapsing them to `unavailable` violates guardrails 3 and 4. Benchmark-derived fields take honest `unavailable`. One engineering dependency named (`valuation_dates` sourced from `benchmark_rows`).

Sections below, by exact name: "P1 — Monthly returns can publish a fabricated return on a withheld day", "P2 — Direction of the withheld-return warning", "P3 — A benchmark outage must not suppress portfolio-performance output" (each: documented rule, citation, violation check, correct behaviour, trust-class analysis); "Duplication — the third daily-return implementation" (the ungated monthly copy); "Methodology gaps — flagged for the human (financial-methodology.md is silent or incomplete)" (items a-d, human decisions); "Field / contract inventory — nullability and trust per output field" (per-field table).

Blocks dispatch: none. Methodology gaps a-d are flagged for the human but do not block story authoring — the groundable rule is stated for each.

---

## P1 — Monthly returns can publish a fabricated return on a withheld day

### The documented rule for when a daily return is not publishable

`DailyPortfolioState.return_is_publishable` (schemas/reconciliation.py:589-635) is the
single shared predicate. It is **False only** when the state carries a *material*
`unbacked_cash_flow` — base-currency cash moved by a trade in a symbol whose
reconstructed quantity was withheld (US-33.2 share-unit discontinuity), so
`total_portfolio_value` steps with no position behind it and no corrected value
exists. Materiality is `abs(unbacked_cash_flow) / abs(total_portfolio_value) >=
REPLAY_UNBACKED_CASH_MATERIAL_SHARE` (0.1%, US-34.4).

A reconciled **terminal** day is *publishable* (US-34.8): its return is computed
from `market_derived_terminal_value(states)` = terminal `total_portfolio_value`
less its recorded `reconciliation_adjustment`, so the accounting correction
cannot enter the return by construction. It is no longer withheld.

Citations: financial-methodology.md § "Terminal-value input rule (US-34.6)"
lines 565-638 (esp. "The daily return uses it too (US-34.8)", lines 607-638);
§ "Opening cash anchor + reconciliation adjustments" lines 2440-2462;
§ "Rolling Pearson Correlation" → "Withholding still wins" lines 2570-2575.

The two sanctioned daily-return builders both enforce this:
- `performance.py::_time_weighted_daily_return` (lines 362-374): returns `None`
  when `not current_state.return_is_publishable`; uses
  `total_portfolio_value - (reconciliation_adjustment or 0.0)`.
- `risk.py::_portfolio_time_weighted_return_series` (lines 1489-1558): `continue`
  when `not state.return_is_publishable`; same market-derived current value.

financial-methodology.md lines 633-638 names these as "two independent
implementations of the same formula — `return_is_publishable` is shared between
them, the arithmetic is not — so the correction is applied in both."

### What monthly aggregation MUST do with a withheld day

**Exclude that day's daily return from the month's product.** Not withhold the
whole month; not degrade the month; never fabricate a 0.0%.

Rationale — the chaining identity. financial-methodology.md § "Monthly Returns
(Dashboard)" lines 646-658 requires
`Π_m (1 + monthly_return_m) = Π_t (1 + daily_return_t)` (the period TWR chain).
The published TWR chain already *skips* withheld days
(`performance.py::withheld_return_impact_pct._chain`, lines 281-293:
`if honour_withholding and not current.return_is_publishable: continue`), and
financial-methodology.md line 493 states "the published chain has gaps by
design." For the identity to hold, monthly compounding must skip the identical
set of days. Withholding the whole month or degrading it would break the
identity and would over-suppress: a single un-interpretable interior day does
not make the surrounding ~21 trading days un-interpretable.

The terminal-day treatment is the same as the TWR chain: use
`market_derived_terminal_value`, i.e. compound
`(V_t − reconciliation_adjustment_t − CF_t) / V_{t−1} − 1` for the reconciled
terminal day, not the raw reconciled value.

### Does the current monthly path violate it — yes

`dashboard_history_engine.py::_compute_contribution_adjusted_monthly_returns`
(lines 837-863) computes, for every state after the anchor:

```text
daily_return = ((state.total_portfolio_value - state.external_cash_flow)
                / previous_state.total_portfolio_value) - 1
growth_by_month[month] *= (1 + daily_return)
```

It reads `return_is_publishable` **nowhere** and subtracts
`reconciliation_adjustment` **nowhere**. Consequences:

1. A material-unbacked-cash day (US-33.2) contributes its raw, un-interpretable
   move to the month's product. P1's reported "+100% monthly return" is this:
   the phantom position's cash step is compounded as performance. This is the
   guardrail-3 fabrication class that `return_is_publishable` exists to close,
   re-opened on this one surface.
2. A reconciled terminal day compounds the accounting adjustment into its month
   — the exact figure US-34.6/US-34.8 removed from TWR, MWR and investment gain,
   still present here.
3. The only backstop is `_monthly_returns_are_reliable` (lines 866-875): if any
   `abs(month) > 100` it hides the **entire grid** (all months, every range).
   So the observable failure is bimodal — either one month cell is silently
   wrong (distortion < 100%), or the whole grid vanishes (distortion > 100%).
   Both are wrong; the correct output is the grid intact with the affected
   month showing its real partial-month return.

Note: `_compute_max_drawdown` (lines 878-899) does *not* have this bug — it
delegates to `risk.py::_portfolio_time_weighted_return_series`, which gates
correctly. Of the investor-performance family, the monthly grid is the sole
member that bypasses the shared predicate.

### Correct behaviour (statement the story can cite)

Monthly returns are `Π (1 + daily_return_t) − 1` over the daily returns that
*the published TWR chain contains* for that calendar month — i.e. computed by
the same builder / helper the TWR chain uses, honouring
`return_is_publishable` and `market_derived_terminal_value`. A month whose only
daily returns are all withheld emits **no entry** (same rule as the existing
"anchor month" edge case, lines 660-673). A month that loses *some* but not all
of its days to withholding emits its entry computed from the surviving days.

### Trust-class analysis — the level a month containing a withheld day carries

- Truth class: **broker-truth historical diagnostics** on reconstructed inputs
  (imported ledger replay). Unchanged by the presence of a withheld day.
- Trust level: the **same level the range's TWR carries** —
  `DashboardRangeMetrics.portfolio_return_trust` = `verified` when the slice
  matches an admitted exact portfolio-proof scope, else `degraded`
  (`replay_derived`), else `unavailable` (dashboard_history_engine.py:631-637).
  A month that merely *excludes* an interior withheld day is **not**
  independently downgraded to `withheld` or `degraded` — the TWR chain that
  shares its gaps stays at its own rung and only *discloses* the omission via
  `withheld_return_dates` / `withheld_return_reason` /
  `withheld_return_impact_pct` (lines 463-465). Monthly returns should inherit
  that same run-level disclosure, not carry a per-cell trust flag.
- `withheld` vs `unavailable` for the grid as a whole: `withheld` is not
  reachable for monthly returns by this mechanism — an excluded day is a
  disclosed gap in an otherwise-publishable chain, not a suppression of the
  family. `unavailable` remains correct only when the replay produced no
  publishable daily returns at all.
- Open sub-question for the human (see § Methodology gaps b): whether a month
  that dropped a day needs its own visible marker, since a single cell gives
  the researcher no equivalent of `withheld_return_impact_pct`.

---

## P2 — Direction of the withheld-return warning

### The quantity the copy must read

`run_metadata.withheld_return_impact_pct`, produced by
`performance.py::withheld_return_impact_pct(states)` (lines 265-295):

```text
withheld_return_impact_pct = round(chain_all_days − chain_published, 2)
  chain_all_days   = Π over every day (honour_withholding = False)
  chain_published  = Π skipping days where return_is_publishable is False
  → None when no day was withheld
```

It is **signed**: it is (return if the withheld days were included) minus (return
actually shown). financial-methodology.md line 501: "the published 2.43%
understates the all-days chain of 4.23% by 1.80pp" — i.e. impact = 4.23 − 2.43 =
**+1.80**, and the direction word for a positive impact is "understates".

### Exact condition for understatement vs overstatement

Let `I = withheld_return_impact_pct`.

- `I > 0` — including the withheld days would **raise** the return. The shown
  value **understates** performance. (The excluded days had net positive impact
  on the growth factor.)
- `I < 0` — including the withheld days would **lower** the return. The shown
  value **overstates** performance. (The excluded days had net negative impact.)
- `I == 0.00` (after rounding) or `I is None` — no directional claim. `None`
  means nothing was withheld: suppress the warning entirely. `0.00` means the
  omission is immaterial to two decimal places: say "does not materially change
  the shown return" or suppress.

### The boolean the UI copy should switch on

```text
understates  ⇔  withheld_return_impact_pct  >  0
overstates   ⇔  withheld_return_impact_pct  <  0
magnitude shown = abs(withheld_return_impact_pct)   ("by X pp")
```

`PerformanceBenchmarkCard.tsx:249` currently hard-codes the "understates" branch
and only varies the magnitude. It already receives the signed value, so this is
a client-side copy-selection fix, not a contract change. The quant deliverable
is the rule above; the frontend lane owns the wording and the null/zero states.

### Trust-class analysis

`withheld_return_impact_pct` is an **impact estimate, never a return** (its days'
moves are explicitly not performance — that is why they are withheld). It rides
the same trust class as the dashboard-history run (broker-truth replay on
reconstructed inputs). It is a disclosure artifact: it has no trust level of its
own beyond "present / absent". The UI must never render it or its
sign-derived direction as itself a performance figure.

---

## P3 — A benchmark outage must not suppress portfolio-performance output

### The collapse

`dashboard_history_engine.py::run_imported_dashboard_history` line 304:

```text
if not benchmark_rows or not has_any_symbol_price_history(symbol_price_histories):
    return _build_unavailable_dashboard_history_result(...)   # everything unavailable
```

`_build_unavailable_dashboard_history_result` (lines 496-527) sets
`performance_history`, `monthly_returns`, portfolio path and benchmark path all
to `unavailable`, and returns empty `daily_states` / `performance_series`. So a
benchmark-history absence zeroes the entire dashboard even when holdings history
and replay states are fully usable.

### Independent-availability decomposition

Computable with **no benchmark history at all** (inputs are portfolio daily
states only — `total_portfolio_value`, `external_cash_flow`,
`reconciliation_adjustment`):

| Output | Builder | Benchmark input? |
|---|---|---|
| Portfolio TWR (`time_weighted_return_pct`) | `_range_time_weighted_return_pct` over `_time_weighted_daily_return` | none (methodology § Portfolio Return Methodology, lines 456-508) |
| Money-weighted return (`money_weighted_return_pct`) | `_compute_money_weighted_return` (lines 680-699) | none (Modified Dietz: portfolio values + cash flows only) |
| Net contributions / investment gain | `_compute_visible_summary` (lines 781-787) | none (`external_cash_flow` + `market_derived_terminal_value`) |
| Monthly returns (`monthly_returns`) | `_compute_contribution_adjusted_monthly_returns` (lines 837-863) | none (portfolio states only) |
| Dashboard max drawdown (`max_drawdown_pct`) | `_compute_max_drawdown` (lines 878-899) | none (compounded return index from portfolio TWR daily returns) — but separately gated by the investor-economics drawdown withholding policy, unchanged here |

Require benchmark history (genuinely un-computable without it):

| Output | Why |
|---|---|
| Relative / excess return (`excess_return_pct`) | defined as `time_weighted_return_pct − benchmark_return_pct` (methodology § Mixed-basis comparison, US-34.5, lines 719-751); one null leg ⇒ null excess, never zero |
| Benchmark return (`benchmark_return_pct`) | needs the benchmark price series |
| Benchmark line on the chart (`performance_series[*].benchmark_price` / `benchmark_return_pct`) | needs the benchmark price series |
| Tracking error, beta, rolling correlation (Risk-tab / relative-risk) | need paired portfolio/benchmark daily returns (methodology § Tracking error, § Information Ratio, § Rolling Pearson Correlation) |

### Trust level the benchmark-derived fields take when benchmark history is absent

**`unavailable`** — and this is the *honest* `unavailable`: the required source
input does not exist (financial-methodology.md lines 48-50, "the required source
inputs or trustworthy path do not exist for the requested output"). This is not
a collapse; it is the correct label for a genuinely missing input. It must be
surfaced field-by-field (via `section_trust.benchmark_path = "unavailable"` and
`source_status.benchmark_history`), not as a run-level top-line.

The portfolio-economics fields in the first table keep **their own** level —
`verified` where the slice matches an admitted portfolio-proof scope, otherwise
`degraded` (`replay_derived`) — determined with no reference to the benchmark.

### Does collapsing every output to `unavailable` violate guardrail 4 — yes

It violates **guardrail 4 (trust semantics over fabrication)** and
**guardrail 3 (truth-class / mixed-trust separation)**:

- The portfolio-economics outputs are *available* (`verified` or
  `replay_derived`). Stamping them `unavailable` because a *different,
  independent* field's input is missing fabricates a trust verdict — the engine
  asserts "we do not have this" about numbers it does have. The pack (§ "The
  truth classes", lines 95-99) rates collapsing the `withheld`/`unavailable`
  distinction a CRITICAL finding: "the distinction is the product's central
  promise." The same principle governs collapsing `verified`→`unavailable`.
- financial-methodology.md line 170: dashboard-history "expose[s] grouped
  `section_trust` so mixed trust does not collapse into one top-line label."
  The line-304 branch is exactly that collapse — it discards `section_trust`'s
  reason for existing.
- CLAUDE.md guardrail 3 / project.md guardrail 4: "never collapse `withheld`
  into `unavailable`" — the general rule is: surface the level per section,
  never let one missing section decide the whole response.

Correct behaviour: a benchmark-history outage degrades **only** the benchmark
section. `daily_states`, `performance_series` (portfolio leg), the range
summaries' portfolio/MWR/contribution/monthly fields and (subject to its own
policy) max drawdown publish at their own trust level; benchmark leg,
`excess_return_pct`, `benchmark_return_pct` and the benchmark line report
`unavailable` with `section_trust.benchmark_path` / `source_status.benchmark_history`
as the authoritative explanation.

### Engineering dependency the story author must know (not a methodology point)

`valuation_dates = sorted({row["date"] for row in benchmark_rows})`
(dashboard_history_engine.py:313). The replay's trading calendar — the date set
every `DailyPortfolioState` is built on — is currently sourced *from the
benchmark rows*. Simply deleting `not benchmark_rows` from line 304 would leave
`valuation_dates` empty and produce zero daily states. A benchmark-independent
calendar is required: the natural candidates are the union of in-window dates
across `replay_price_histories` / `symbol_price_histories`, or an exchange
calendar. This is a tech-lead / backend design decision; the brief only flags
that the P3 fix is not a one-line guard removal.

`tech-debt-register.md` was checked: it records an FX-rate hardcode in
`reconciliation.py` (also noted in the quant pack) — not in the path P1/P2/P3
touch. No open tech-debt item covers the benchmark-calendar coupling or the
monthly-returns gate; both are new findings from this brief.

---

## Duplication — the third daily-return implementation

The cash-flow-neutral daily return
`(V_t − CF_t) / V_{t−1} − 1` (with the `return_is_publishable` gate and the
`market_derived_terminal_value` correction) now exists in **three** places:

1. `performance.py::_time_weighted_daily_return` (lines 362-374) — gated,
   corrected. Sanctioned (methodology lines 633-638).
2. `risk.py::_portfolio_time_weighted_return_series` (lines 1489-1558) — gated,
   corrected. Sanctioned (methodology lines 633-638).
3. `dashboard_history_engine.py::_compute_contribution_adjusted_monthly_returns`
   (lines 837-863) — **un-gated, un-corrected.** Undocumented as a separate
   implementation. This is P1's root cause.

The quant pack (§ "Project-standard constants", "US-34.8 found `risk.py`
holding its own copy of the daily-return formula; that is the pattern to hunt")
calls this exact class out. The methodology already accepts *two* sanctioned
copies with a shared predicate; a third that silently diverges is the failure
mode the shared-predicate design was meant to prevent. The story should route
the monthly path through the same helper the TWR chain uses (a shared
per-day function returning `float | None`), not add a fourth gated copy.

---

## Methodology gaps — flagged for the human (financial-methodology.md is silent or incomplete)

**(a) § "Monthly Returns (Dashboard)" (lines 640-685) does not state the
withheld-day rule.** It says monthly returns "compound the same cash-flow-neutral
daily returns as the time-weighted return chain" and lists edge cases for
*missing* days but never mentions `return_is_publishable` or the terminal
`reconciliation_adjustment`. The intent is groundable (via "the same daily
returns as the TWR chain" plus the shared-predicate rule at lines 633-638 and
2570-2575), but the section should be made explicit at story close-out. The
human should confirm the resolution is **exclude the withheld day** (this
brief's reading, required by the chaining identity) rather than withhold the
month.

**(b) No per-month disclosure for a month that excludes a withheld day.** The
TWR chain discloses its gaps through `withheld_return_impact_pct`; the monthly
grid has no equivalent, and `monthly_returns_reliable` is an all-or-nothing
grid switch. Whether a gap-containing month needs its own marker (a per-cell
flag, a footnote, or reuse of the run-level disclosure) is an unaddressed
trust-design question. Human decision; it does not block P1's arithmetic fix.

**(c) § "Publication rungs for the replayed return" (US-34.2, lines 472-508)
documents `withheld_return_impact_pct` only through the IB2026 understatement
example.** The general signed interpretation (positive ⇒ shown value
understates; negative ⇒ overstates) is not written down anywhere, yet P2's UI
copy depends on it. A one-sentence addition to this section is the fix. Minor;
docs lane at close-out, human confirms the wording.

**(d) No section states that a total benchmark-history outage must still
publish portfolio-economics on the imported dashboard path.** § "Mixed-basis
comparison" (US-34.5, lines 719-751) covers a null benchmark *leg* inside an
otherwise-live run, and line 170 says `section_trust` exists to prevent
collapse, but the line-304 whole-run collapse has no methodology backing in
either direction. Guardrails 3 and 4 strongly imply the decomposition in § P3,
but the operative rule for this surface is unwritten. Human decision on the
intended rule before or during story authoring.

---

## Field / contract inventory — nullability and trust per output field

One row per dashboard-history output field the three defects touch. "Benchmark
absent" = the P3 scenario (`benchmark_rows` empty, symbol histories present).

| Field (schema) | Normal trust | Nullable | On withheld interior day (P1) | On benchmark absent (P3) |
|---|---|---|---|---|
| `range_metrics[*].monthly_returns[*].return_pct` | inherits `portfolio_return_trust` of the range | yes — month emits no row if all its days withheld / none computable | month computed from surviving days; **never** a fabricated value; row omitted only if empty | published (no benchmark input) |
| `range_metrics[*].monthly_returns_reliable` | n/a (boolean guard) | no | should stay `true` when only interior days were excluded; today can flip `false` and hide the whole grid | published |
| `range_metrics[*].summary.time_weighted_return_pct` | `verified` \| `degraded`(`replay_derived`) \| `unavailable` | yes | unchanged (already gated) | published at own level |
| `range_metrics[*].summary.money_weighted_return_pct` | same as TWR | yes (`< 2` states, or `D = 0`) | unchanged | published at own level |
| `range_metrics[*].summary.investment_gain` / `net_contributions` | same as TWR | `investment_gain` yes; `net_contributions` no (0.0 default) | unchanged | published at own level |
| `range_metrics[*].summary.benchmark_return_pct` | benchmark path trust | yes | unchanged | **`unavailable`** (honest — input absent) |
| `range_metrics[*].summary.excess_return_pct` | min(portfolio, benchmark) trust | yes — null if either leg null | unchanged | **null**, `unavailable` (one leg missing; never 0) |
| `range_metrics[*].max_drawdown_pct` | investor-economics drawdown policy (may be withheld regardless) | yes | unchanged (already gated) | published subject to its own policy |
| `performance_series[*].portfolio_return_pct` | portfolio path trust | yes (null point on a withheld / zero-prior day; chain resumes) | unchanged | published |
| `performance_series[*].benchmark_price` / `benchmark_return_pct` | benchmark path trust | yes | unchanged | **null / `unavailable`** |
| `run_metadata.withheld_return_impact_pct` | disclosure artifact (no trust rung) | yes — `None` when nothing withheld | present; sign drives P2 copy | present if replay ran |
| `run_metadata.section_trust.benchmark_path` | — | no | unchanged | **`unavailable`** (must not force `portfolio_path` to match) |
| `run_metadata.source_status.benchmark_history` | — | no | unchanged | outage status; portfolio `performance_history` stays `live` |
