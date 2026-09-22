CHANGE REQUEST CR-2 — 2026-09-18-vertical-volume-indicator
lane:        backend
severity:    BLOCKING
round:       1 of 2
raised by:   C:\projects\investments\.agentic\projects\tradingview\runs\2026-09-18-vertical-volume-indicator\compile.md § Attempt 1 — 2026-09-18, FAIL
scope fence: C:\projects\investments\tradingview\volume_profile.pine — only
             the rolling-window storage (currently `closesQueue`/`volsQueue`
             as `var array<array<float>>` at lines 210-211, and every read/
             write/shift site that touches them: the push/shift block at
             214-220, and the binning loop's `array.get(closesQueue, idx)` /
             `array.get(volsQueue, idx)` reads at ~281-282). No formula
             change, no change to the window/repaint semantics, no change to
             CR-1's na-skip logic beyond whatever the new storage
             representation mechanically requires it to read from.

The finding (compile.md § Attempt 1): the live TradingView compile check
fails with `Error at 210:10 — Arrays of type array are not supported.
(CE10022)`. Pine v6 does not support nested typed arrays
(`array<array<float>>`). The script never reaches "start" — nothing past
this declaration has ever actually run in TradingView, including CR-1's fix
and both quant-audit passes, which verified the *logic* against Python
re-derivations, not against a compiled script (neither audit lane can
compile Pine; that is this project's structural reason the live check
exists at all).

What would satisfy it: replace `closesQueue` and `volsQueue`'s nested-array
representation with something Pine v6 actually supports, while preserving
exactly what the window currently does — the last `lookbackBars + 1` bars'
worth of per-bar intrabar close/volume arrays, available for the binning
loop to iterate over `startIdx..endIdx` the same way it does today. A flat
`array<float>` per quantity plus an `array<int>` of per-bar intrabar counts
(prefix-summed or walked to find each bar's slice) is one way; pick whatever
representation is cleanest in Pine — the requirement is that it compiles and
preserves the queue's current push/shift-when-over-length/read semantics
exactly, not a specific data structure.

Also required: since this is exactly the class of failure `03-backend.md`
already flagged as unverified but shipped anyway (§ risks: "nested typed
arrays array<array<float>>... standard v6 pattern per training but none
compiled live"), check the same report's other named-unverified constructs
(the `[a, b] = request.security_lower_tf(...)` tuple-destructuring form, and
`ignore_invalid_timeframe` as a named argument) against this same compile
attempt's result — the error panel showed exactly one problem, so if those
constructs are still present in the file after your fix and the next compile
attempt shows no further errors, say so plainly in your report; do not
re-guess at their correctness from training data a second time.

The human has not separately ruled on this CR — it is a compile FAIL, which
this project's acceptance command makes blocking by definition
(project.md § "Why this project is unusual": "A run that closes without it
has shipped text nobody loaded").
