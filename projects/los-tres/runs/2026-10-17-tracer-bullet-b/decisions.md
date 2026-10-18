# Decisions — 2026-10-17-tracer-bullet-b

## D-1 · design · 2026-10-17
open decision:  O-4 styling system for the UI, before slice B
raised by:      ../2026-10-16-tracer-bullet/02-design.md § Owner questions (O-4); carried as ../2026-10-16-tracer-bullet/08-docs.md § handoff 2
ruling:         "CSS Modules (Recommended)"
by:             the human, in session
meaning:        components style with co-located *.module.css (built into Next.js, no new dependency); src/app/globals.css keeps the CSS custom properties from slice A. Close docs records it as a decision file. Unblocks design.

## D-2 · build · 2026-10-17
open decision:  go on the build plan (02 backend, 03 frontend, 04 test, 05 docs; then integration, close docs, protocol-lint; budget 8); drizzle-kit as a new devDependency; 01-design owner questions Q-1..Q-3
raised by:      01-design.md § Owner questions, § Lane split, § handoff 4; run.md § Phases (build human stop)
ruling:         "Go, as planned (Recommended)"
by:             the human, in session
meaning:        build fires on the plan as presented; Q-1 hand-written CSV reader, Q-2 seed does not run import, Q-3 /producto/<slug>; drizzle-kit accepted. The human runs `git mv vitest.config.ts vitest.config.mts` before 04 and adds SEED_DEMO_DATA=true to local .env. Orchestrator creates the issue, branch and draft PR.
