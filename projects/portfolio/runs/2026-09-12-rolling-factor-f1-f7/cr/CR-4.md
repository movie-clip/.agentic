CHANGE REQUEST CR-4 — 2026-09-12-rolling-factor-f1-f7
raised by:  08-quant-audit.md § FINDING 4 (MATERIAL); fix landed in 09-frontend.md
round:      1 of 2
scope fence: apps/desktop/src/features/portfolio/RollingFactorLoadingsCard.test.tsx only

Read `C:\projects\investments\.agentic\projects\portfolio\runs\2026-09-12-rolling-factor-f1-f7\08-quant-audit.md` § FINDING 4 and `C:\projects\investments\.agentic\projects\portfolio\runs\2026-09-12-rolling-factor-f1-f7\09-frontend.md` § handoff before editing. The test at line 106 currently asserts a "Degraded" badge for a short-history-only, all-16-proxies-present fixture — the exact false-positive case FINDING 4 named. CR-3 fixed the component; this test's assertion now needs to invert.
