# Decisions — 2026-10-07-s2-animation-bridge-contract

## D-1 · specification · 2026-10-07
open decision:  O5 — frame budget for animation at 150 characters (main-thread ms, target machine) that makes S2's done pass or fail
raised by:      runs/2026-10-07-ecs-animation-approach/04-delivery-brief.md § Open decisions (O5)
ruling:         "Measure only, no pass/fail" — S2 records the 150-character main-thread animation cost; no budget threshold gates S2's done, and no scaling slice is auto-raised; the human decides afterwards from the recorded figure
by:             the human, in session

## D-2 · specification · 2026-10-11
open decision:  approve the S2 story draft as the specification
raised by:      01-story.md § Story, § Acceptance criteria, § Tickets
ruling:         "Approve as drafted (Recommended)"
by:             the human, in session

## D-3 · specification · 2026-10-11
open decision:  OD-1 — split S2 into contract/mapping and cost-at-150, or one story
raised by:      01-story.md § Open decisions (OD-1)
ruling:         "One story, unsplit (Recommended)"
by:             the human, in session

## D-4 · specification · 2026-10-11
open decision:  OD-2 — may gait output change when the three speed constants become one source
raised by:      01-story.md § Open decisions (OD-2)
ruling:         "No, keep today's gait (Recommended)" — option (a): default-Viking gait results identical to today at every speed; AC-5/AC-6 stand as written
by:             the human, in session

## D-5 · specification · 2026-10-11
open decision:  OD-3 — conditions for recording the 150-character figure
raised by:      01-story.md § Open decisions (OD-3)
ruling:         "Editor only, dev machine (Recommended)" — PlayMode scenario in the Editor, 150 continuously moving characters, timed over N frames; no player build
by:             the human, in session

## D-6 · build · 2026-10-12
open decision:  go on the S2 build plan (test T-1+T-2 → backend T-3+T-4 → test T-5+T-6), including the design's reading of AC-6 (speed reference 7, not GroundMaxSpeed)
raised by:      02-technical-plan.md § Dispatch plan, § Single speed source
ruling:         "Go (Recommended)"
by:             the human, in session

## D-7 · verify · 2026-10-12
open decision:  CR-2 (SHOULD_FIX) — fix in this run or carry
raised by:      06-integration.md § Ruling: settle-only Update; cr/CR-2.md
ruling:         "Fix now (Recommended)"
by:             the human, in session
