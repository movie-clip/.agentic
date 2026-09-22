# Decisions — 2026-09-18-vertical-volume-indicator

## D-1 · framing · 2026-09-18
open decision:  is a custom Pine script the right vehicle, given TradingView's
                native Volume Profile tool already renders a price-anchored,
                right-edge histogram
raised by:      01-product.md § Open decisions (bullet 2); platform-research.md § 1
ruling:         "Build a custom Pine script anyway"
by:             the human, in session

## D-2 · framing · 2026-09-18
open decision:  what "better than VSA Wyckoff Volume" means — rendering,
                signal, or both
raised by:      01-product.md § Open decisions (bullet 1); platform-research.md § 3
ruling:         "It's about the rendering only" — the trader wants the
                price-anchored profile view; no VSA-style signal replacement
                is in scope for this run
by:             the human, in session

## D-3 · verify · 2026-09-18
open decision:  F1 (MATERIAL): partial-na intrabar data can silently produce
                a wrong POC while Status still reads OK — fix now, or ship and
                carry to a later pass?
raised by:      04-quant-audit.md § Findings, FINDING 1
ruling:         "Fix now" — a CR was written (cr/CR-1.md) and dispatched to
                backend before close
by:             the human, in session

## D-4 · close · 2026-09-18
open decision:  the run passed 2x its original derived budget (1, from
                intake's framing-only estimate; ceiling = 2) without an
                explicit stop naming that threshold — orchestrator.md § 3
                requires one. The threshold was actually crossed right after
                02-quant (spent=2), the same point where the orchestrator
                separately asked "want me to go ahead and dispatch backend?"
                and got a yes — a real human checkpoint, just not framed as
                or logged against the budget rule, and not repeated at each
                of the three subsequent CR rounds (CR-1/CR-2/CR-3).
raised by:      the orchestrator's own close-out sweep (check_report.py
                --require-heads), surfaced to the human rather than silently
                patched
ruling:         Ratified — ship what was built. All of the spend past the
                ceiling went to real, gate-found defects (F1's silent-wrong-
                POC risk, CE10022's compile failure, F8's crash-on-first-
                render), not scope creep, and the pre-build go-ahead already
                given served the checkpoint's actual purpose even though it
                was not labelled as one. Recorded as a near-miss: the
                specific mechanism (name the threshold, log the ruling) should
                fire explicitly next time, on its own, not be inferred after
                the fact from an adjacent approval.
by:             the human, in session
