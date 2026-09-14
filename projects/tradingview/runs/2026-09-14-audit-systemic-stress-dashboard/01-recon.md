REPORT 2026-09-14-audit-systemic-stress-dashboard/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only recon order, no verification command named

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - see § Script inventory — full formula/input/plot/ticker catalogue for the quant-audit lane's independent re-derivation
  - see § Header contract claims — the exact admissions the header makes, quoted, for the audit report to cross-check against
  - see § Local verification tooling — what pine_check.py and test_pine_check.py actually check, confirmed by reading both files
  - Answer to the order's explicit question: there is no way to get a deterministic pass/fail on a .pine script's actual computed output without TradingView's editor — see § Deterministic local testing question

risks:
  - tradingview/fixtures/ and tradingview/docs/ do not exist as directories at all (not just empty) — CLAUDE.md's documented layout names both, but the repo currently has neither; the one Strategy Tester CSV export present lives at the repo root (tradingview/Trend_+_Carry,_Risk-Regime_Sized_(Strategy_13)_AMEX_VTI_2026-08-24_55c9e.csv), not under fixtures/, and belongs to strategy13_trend_carry.pine, not to systemic_stress_dashboard.pine — so no fixture evidence exists for the script this audit concerns
  - the header's claim that COR1M "may not be available on your TradingView plan/exchange feed" and the CBOE:COR1M ticker itself are unverified per the header's own text; I did not attempt independent verification of ticker validity, symbol resolution, or the CFTC/Cboe data source, since that is explicitly the next lane's job (quant-audit) and this order's non_goals exclude judging formula correctness
  - pine_check.py's P008 rule (request.security without explicit lookahead) would fire SHOULD_FIX on all four request.security() calls in this script (lines 57-60) since none pass a `lookahead` argument — I did not run the tool (no Bash access), so this is read from source inspection of both files, not a verified command result; the audit/integration lane should actually run `pine_check.py --strict` to confirm

## Orchestrator brief

- Full read of systemic_stress_dashboard.pine done: formulas, inputs, plots, tickers all catalogued in § Script inventory below.
- Header contract quoted precisely in § Header contract claims — script is self-declared "ORIGINAL approximation, not a reproduction," with explicit named-source claims only for VIX and COR1M identity (not formula), and explicit caveats about COR1M availability and untuned weights/thresholds.
- pine_check.py confirmed (by reading it, not CLAUDE.md's word) to check: version annotation/mismatch, single declaration, v4 leftovers (study/security/iff), bare v5 namespace calls, repaint via lookahead_on or missing lookahead, strategy cost declarations, paren/bracket balance, plot ceiling. Detail in § Local verification tooling.
- test_pine_check.py tests pine_check.py itself (a regression suite for the checker), not any .pine script's output — confirmed by reading it.
- No deterministic local test of a .pine script's actual computed output exists in this repo — see § Deterministic local testing question for the direct answer the order asked for.
- fixtures/ and docs/ directories do not exist; one loose CSV at repo root belongs to a different script (strategy13_trend_carry.pine), not this one — flagged in risks, not glossed over.
- Sections below: § Script inventory, § Header contract claims, § Local verification tooling, § Deterministic local testing question, § Repo listing notes.

## Script inventory

**File:** `C:\projects\investments\tradingview\systemic_stress_dashboard.pine` (141 lines), `//@version=6`, `indicator("Systemic Stress Dashboard (approximation)", overlay=false)`.

**Data sources / symbols (`request.security`, all with `ignore_invalid_symbol = true`, no explicit `lookahead` argument):**
- `vixSymbol` default `TVC:VIX` (line 33) → `vixClose` (line 57)
- `corSymbol` default `CBOE:COR1M` (line 34) → `corClose` (line 58)
- `creditLongSymbol` default `AMEX:LQD` (line 35) → `lqdClose` (line 59)
- `creditShortSymbol` default `AMEX:HYG` (line 36) → `hygClose` (line 60)
- All four are `input.symbol()`, i.e. user-correctable, satisfying guardrail 3's "must be an input.symbol()" clause.

**Computed sub-indicators:**
- `vixPct` (line 63): `ta.percentrank(vixClose, percentileLookback)`, `na` if `vixClose` is `na`. Percentile rank of VIX within `percentileLookback` (default 252) bars.
- `corPct` (line 64): same pattern on `corClose` (COR1M).
- `creditRatio` (line 68): `hygClose / lqdClose`, `na` if either input is `na`.
- `creditRawStress` (line 69): `-ta.roc(creditRatio, creditRocLen)` (default `creditRocLen=20`) — negated rate-of-change of the HYG/LQD ratio, so falling ratio (junk underperforming) reads as rising stress.
- `creditPct` (line 70): `ta.percentrank(creditRawStress, percentileLookback)`.
- `systemicStress` (lines 73-80): weighted average of `vixPct`, `corPct`, `creditPct` using inputs `wVix=1.0`, `wCor=1.0`, `wCredit=0.5`; weights of any `na` component are zeroed and the denominator (`sumWeights`) is the sum of *effective* (non-na) weights only — i.e. auto-renormalization on missing components. `na` if `sumWeights <= 0`.
- `stressImpulse` (line 83): `systemicStress - systemicStress[impulseLen]` (default `impulseLen=5`), `na` if either term is `na`.
- `regimeLabel` / `regimeColor` (lines 86-94): thresholded on `systemicStress` against inputs `calmMax=25`, `normalMax=50`, `elevatedMax=75` → labels `"Calm" | "Normal" | "Elevated" | "Stressed"` (or `"N/A"`/gray if `systemicStress` is `na`).

**All inputs (grouped as declared):**
- Data Sources: `vixSymbol`, `corSymbol`, `creditLongSymbol`, `creditShortSymbol` (all `input.symbol`, described above).
- Calculation: `percentileLookback` (int, default 252), `creditRocLen` (int, default 20), `impulseLen` (int, default 5).
- Weights: `wVix` (float, 1.0), `wCor` (float, 1.0), `wCredit` (float, 0.5).
- Regime Thresholds: `calmMax` (float, 25), `normalMax` (float, 50), `elevatedMax` (float, 75).
- Display: `showComponents` (bool, false — gates the Credit Percentile plot's default visibility and the table row), `tablePos` (string, default `"top_right"`, options top_right/top_left/bottom_right/bottom_left).

**Plots / visuals (lines 99-140):**
- `plot(systemicStress, "Systemic Stress", red, linewidth=2)`
- `plot(vixPct, "VIX Percentile", blue)`
- `plot(corPct, "COR1M Percentile", purple)`
- `plot(creditPct, "Credit Percentile", teal)` — `display = showComponents ? display.all : display.data_window` (hidden from the chart by default, still in the data window).
- `plot(stressImpulse, "Stress Impulse", orange)`
- Three `hline()` calls at `calmMax`, `normalMax`, `elevatedMax` (dotted, gray) plus one at 0 (dashed, gray) as the impulse zero-reference.
- `bgcolor()`: red shading (90% transparent) when `systemicStress >= elevatedMax`.
- A 2-column, up-to-6-row `table.new()` (position from `tablePos`), populated only `if barstate.islast`, showing Systemic Stress, VIX Percentile, COR1M Percentile, (optionally) Credit Percentile, Stress Impulse, and Market Regime (regime cell colored by `regimeColor`). `fmt()` helper (line 117) renders `na` as the literal string `"n/a"`.
- **No `alert()` / `alertcondition()` calls anywhere in the script** — it emits no alerts, only plots/table/bgcolor.
- **No `strategy()` declaration** — this is an `indicator()`, so guardrail 4 (cost declaration) does not apply to it.

## Header contract claims

Quoted from the script's opening comment block (lines 1-27), for the audit lane to check against, not paraphrased where precision matters:

- Self-description: `"Systemic Stress" dashboard — an ORIGINAL approximation, not a reproduction of any specific published indicator.` The header explains this directly: `You didn't have the source script/name for the panel in your screenshot, so this builds a transparent, checkable version from standard building blocks instead of guessing at someone else's exact formula.`
- Per-component descriptions in the header (lines 9-19) name each sub-indicator's construction in prose matching the code (VIX Percentile, COR1M Percentile, Credit Percentile "off-screen by default," Systemic Stress as weighted average, Stress Impulse, Market Regime) — no external source (book/paper/spec) is cited for any of the five; the only "sourcing" claim is identifying COR1M itself as `Cboe's 1-Month S&P 500 Implied Correlation Index (ticker COR1M)` — i.e. the header asserts the *identity* of that named index, not a formula source for how it's combined here.
- Explicit unverified/caveat admissions (lines 20-27), verbatim intent:
  - `COR1M may not be available on your TradingView plan/exchange feed. If it fails to resolve, this script excludes it and re-normalizes the remaining weights rather than erroring out — check the COR1M Percentile cell; if it stays blank, the symbol didn't resolve and you may need a different ticker/exchange prefix.`
  - `The specific weights, lookback, and regime thresholds are reasonable defaults, not a match to any specific published index — tune them to your taste, or swap this against the real source panel's numbers once you find it to calibrate.`
- No claim anywhere in the header that the COR1M ticker (`CBOE:COR1M`) has been confirmed via TradingView's symbol search — the header only says it may not resolve, which is the degrade-visibly behaviour, not a verification claim. This is consistent with `mm_cot_long_short_index.pine`'s convention referenced in `project.md` but is a narrower admission than that script's ("reconstructed from search results and not confirmed") — this script does not explicitly say whether `CBOE:COR1M`, `TVC:VIX`, `AMEX:LQD`, `AMEX:HYG` were confirmed against TradingView's own symbol search or assumed. That silence is itself worth flagging to the audit lane as a header-contract gap, not a formula question.

## Local verification tooling

**`pine_check.py`** (`C:\projects\investments\.agentic\scripts\pine_check.py`), confirmed by reading the full source, checks (rule codes in parens):
- `//@version` presence (P001), duplicate declarations (P002), version mismatch against `--version` (default 6) (P003).
- Exactly one `indicator()`/`strategy()`/`library()` declaration present (P004) and not duplicated (P005); v4 `study()` blocks (P006).
- Repaint: `request.security(..., lookahead=barmerge.lookahead_on)` blocks (P007, BLOCKING); `request.security()`/`request.security_lower_tf()` with no explicit `lookahead` argument at all advises (P008, SHOULD_FIX — not blocking, since the runtime default is already `lookahead_off`).
- v4 leftovers: bare `security()` (P009), `iff()` (P010).
- v6 namespace violations: bare calls to a fixed list of `ta.*`/`math.*`/`str.*` builtin names without their namespace prefix (P011), with a lookbehind so a user function like `my_sma()` is not falsely flagged.
- Strategy costs (only checked when the declaration is `strategy(...)`): missing `commission_value` blocks (P012, BLOCKING); missing `slippage` advises (P013, SHOULD_FIX); `calc_on_every_tick=true` advises (P014).
- Paren/bracket balance (P015/P016) via depth-walking with string/comment stripping.
- Plot-call ceiling of 64 (P017).
It is explicitly a **pattern checker over stripped source text, not a parser and not a compiler** — the docstring and inline comments say so directly (lines 2-15): "It is deliberately not a parser," "The compile check is the authority. This is the fast filter in front of it."

**`test_pine_check.py`** (`C:\projects\investments\.agentic\scripts\test_pine_check.py`) tests **`pine_check.py` itself**, not any `.pine` script's computed output. It is a dependency-free assertion suite (no pytest import despite CLAUDE.md's command table calling it via `python -m pytest`; the file runs standalone via `sys.exit`) covering: the happy path, every rule code above (each triggered and asserted BLOCKING/SHOULD_FIX as appropriate), line-number correctness (including the specific historical bug the suite was written to pin, an anchored `\s*` regex dragging line numbers toward 1), string/comment-stripping correctness, exit-code behaviour, BOM tolerance, and a final corpus check that asserts **no `.pine` file actually present in the bound `tradingview/` repo produces a BLOCKING finding** (line 230-237) — this last case is the only place this test file touches real repo scripts, and even there it only re-runs the static pattern checker against them, not their output.

## Deterministic local testing question

**No.** There is no mechanism in this repo, or in the `.agentic` scripts bound to it, that produces a deterministic pass/fail result on what a `.pine` script actually *computes* (its numeric output, its plotted series, its backtest equity curve) without opening TradingView's editor/Strategy Tester. Confirmed by inspection of both tools in scope:
- `pine_check.py` operates purely on source text (regex/paren-depth over a comment-and-string-stripped copy of the file) — it has no Pine interpreter and evaluates nothing. It can tell you the script is syntactically suspicious in specific known ways; it cannot tell you `systemicStress` computes the number the formula implies.
- `test_pine_check.py` tests the checker's own pattern-matching correctness, not any script's runtime behaviour.
- No fixture directory or CSV in the repo is wired to any script as an expected-output comparison; the one CSV present (see § Repo listing notes) is a raw Strategy Tester export kept as human-readable evidence, not consumed by any test or check script found in this repo or in `.agentic/scripts/`.
`project.md`'s own "Why this project is unusual" section (already in context) states this as the project's structural premise: static check proves the text is clean, and only the TradingView compile/backtest — run by a human in the browser — proves the script actually computes anything, let alone the right thing.

## Repo listing notes

- `tradingview/fixtures/` — directory does not exist (glob for `tradingview/fixtures/**` returned nothing, and `tradingview/*` does not list a `fixtures` entry).
- `tradingview/docs/` — directory does not exist, same evidence.
- `tradingview/*` (actual root listing): `Trend_+_Carry,_Risk-Regime_Sized_(Strategy_13)_AMEX_VTI_2026-08-24_55c9e.csv`, `strategy13_trend_carry.pine`, `systemic_stress_dashboard.pine`, `mm_cot_long_short_index.pine`, `user-project-description.txt`, `.agentic.json`, `CLAUDE.md`.
- The lone CSV (`Trend_+_Carry,...VTI_2026-08-24_55c9e.csv`) is a Strategy Tester trade-list export (columns: Trade number, Type, Date and time, Signal, Price, Size, Net PnL, Return %, Commission, MFE/MAE, Cumulative PnL, Duration) for `strategy13_trend_carry.pine` on `AMEX:VTI` — it is not associated with `systemic_stress_dashboard.pine`, which is an `indicator()` (no strategy, no trades) and has no fixture evidence in the repo at all.
