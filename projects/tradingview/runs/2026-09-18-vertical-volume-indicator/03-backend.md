REPORT 2026-09-18-vertical-volume-indicator/03
status:      PARTIAL
verdict:     NONE

changed:
  - C:\projects\investments\tradingview\volume_profile.pine — new file: Pine v6 volume-by-price profile indicator per 02-quant.md's formula (bar-count window, bin-count-over-range, close-binning, V_max normalisation, explicit-tie-to-lower-j POC).
  - C:\projects\investments\tradingview\volume_profile.pine — rendered as price-anchored boxes at the right edge with a POC label; see § Formula/§ Out of scope "Rendering mechanics".
  - C:\projects\investments\tradingview\volume_profile.pine — 02-quant.md contract_note #1 addressed: header carries the three required admissions (ORIGINAL/no external authority; candle-close estimate via request.security_lower_tf, never tick-exact; not TradingView's native tool).
  - C:\projects\investments\tradingview\volume_profile.pine — header also states the close-binning-vs-range-spreading choice and the rolling-window/bin-instability caveat, per this order's definition_of_done.
  - C:\projects\investments\tradingview\volume_profile.pine — 02-quant.md contract_note #2 addressed: an always-visible on-chart table (never a tooltip) shows "M of N" window fill and "C of M" intrabar coverage.
  - C:\projects\investments\tradingview\volume_profile.pine — the same table shows realised average intrabars/bar flagged DEGRADED below the 50-100 target band (platform-research.md § 4 refinement), and the Σ-bins/Σ-volume reconciliation ratio.
  - C:\projects\investments\tradingview\volume_profile.pine — 02-quant.md contract_note #3 addressed: no input.symbol() anywhere; the script reads syminfo.tickerid only, at a lower timeframe.

verification:
  command:   python C:\projects\investments\.agentic\scripts\pine_check.py volume_profile.pine --strict
  result:    FAIL
  detail:    1 SHOULD_FIX finding: volume_profile.pine:182: P008 "request.security() without an explicit lookahead" — fires on the request.security_lower_tf() call, which has no `lookahead` parameter to pass (see risks). Without --strict this is 0 BLOCKING findings and the command exits 0.

contract_notes:
  - volume_profile.pine is a new script with no docs/volume-profile.md yet. The docs lane owns authoring it at close-out (this order's non_goals explicitly excludes it from this lane); the script's header block (lines 1-146) and 02-quant.md are the sourced content it should draw from.

pack_corrections:
  - none

handoff:
  - test-engineer: no fixtures/ exists for this indicator; the reconciliation ratio should read ~1.00 during/after the compile check.
  - test-engineer: also check the four distinct n/a branches (fewer than minBars, C=0 "no intrabar data", degenerate range, zero-volume "no volume reported for this symbol") each render their own exact label, not a shared generic n/a.
  - integration/reviewer: the sole pine_check.py --strict finding (P008, volume_profile.pine:182) is a deliberate, documented deviation — not an oversight to silence by adding an unverified `lookahead` argument to request.security_lower_tf(). See risks for the reasoning.
  - Rendering constants (right-edge offset = bar_index+2, max box width = 40 bars, diagnostics table at bottom_right) are my own implementation choices under 02-quant's "Rendering mechanics" non-goal — free for a later order to change without touching the formula.
  - The binning/POC/rendering computation is deferred to barstate.islast only (intrabar data is still fetched every bar into a rolling queue) — a performance choice, not a formula change; flagged so a reviewer does not read it as a construction deviation from 02-quant § Formula.

risks:
  - pine_check.py's P008 rule pattern-matches request.security_lower_tf() identically to request.security() (confirmed via the checker's own test suite, test_security_lower_tf_is_checked_too).
  - request.security_lower_tf() has no `lookahead` parameter in the Pine v6 API to my knowledge — its lower-timeframe intrabars are already-closed data within the current chart bar, nothing to look ahead into; a fabricated named argument risks an actual compile error, worse than an advisory finding, so I left it out.
  - Per backend.md's own guidance for exactly this situation ("if --strict flags something you genuinely should not fix... fix it or report it in risks and set PARTIAL"), status is PARTIAL and verification result FAIL rather than fabricating the parameter to force --strict to exit 0.
  - Constructs I used but could not verify compile, holding no browser/compiler tool: request.security_lower_tf()'s tuple-expression return `[a, b] = request.security_lower_tf(sym, tf, [close, volume])`, and the `ignore_invalid_timeframe` named parameter.
  - Also unverified: nested typed arrays `array<array<float>>`; `str.tostring(x, format.mintick)`; `input.timeframe("")` used as an auto-derivation sentinel compared later with `==`. All are standard v6 patterns per training but none compiled live.
  - lookbackBars/minBars/binCount maxval bounds (1000/500/100) are my own choices — 02-quant.md specified only minval floors and feel-chosen defaults, no numeric ceilings.
