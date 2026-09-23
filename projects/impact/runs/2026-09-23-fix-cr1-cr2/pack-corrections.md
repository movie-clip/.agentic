# Pack corrections — 2026-09-23-fix-cr1-cr2

## PC-1 · capabilities/testing.md
found by:   02-test.md § pack_corrections
what:       `testing.md:36-40` still describes `-CoreOnly` as mapping to
            `-testFilter "Core"` (the CR-1 finding this run fixed). Now stale
            — 02-test.md's fix changed `Run-UnityTests.ps1` so `-CoreOnly`
            passes `-testCategory "Core"`, a true NUnit category match,
            selecting the full 35-test Core suite.
replacement: "`-CoreOnly` now passes `-testCategory \"Core\"`, a true NUnit
            category match, and selects the full 35-test Core suite;
            `-Filter` is unaffected."
