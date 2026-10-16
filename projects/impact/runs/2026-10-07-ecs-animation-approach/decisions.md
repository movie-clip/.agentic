# Decisions — 2026-10-07-ecs-animation-approach

## D-1 · ground-truth · 2026-10-07
open decision:  no network lane has web access; how to cover external research on ECS animation approaches for Entities 6.4 and current package versions
raised by:      run.md § Phases (ground-truth) — orchestrator gap report at intake
ruling:         "General-purpose agent (Recommended)" — a general-purpose web-research agent, same report shape, recorded as an unbound lane
by:             the human, in session

## D-2 · framing · 2026-10-07
open decision:  target animation architecture
raised by:      03-recon.md § Options compared; 01-recon.md § ECS to presentation bridge
ruling:         "Hybrid, done properly (Recommended)" — keep Mecanim Animator on GameObject; make the bridge a clean, tested contract (fix skin-swap bug, proper ECS->Animator parameter mapping) with a seam that allows a later backend swap; Polygon materials unchanged
by:             the human, in session

## D-3 · framing · 2026-10-07
open decision:  expected animated characters on screen
raised by:      03-recon.md § Options compared (hybrid main-thread sync cost)
ruling:         "Dozens (30–150)"
by:             the human, in session

## D-4 · framing · 2026-10-07
open decision:  feature scope beyond fixing what exists
raised by:      01-recon.md § Problems (dead strafe paths); 02-recon.md § Import settings (unused *_RootMotion clips)
ruling:         all four selected — "Strafe / lock-on locomotion", "Root motion", "Combat / action layers", "AI / NPC animation"
by:             the human, in session

## D-5 · framing · 2026-10-07
open decision:  packages unused by code (animation.rigging, cinemachine, timeline); entities.graphics kept until confirmed unused for rendering
raised by:      01-recon.md § Packages
ruling:         "Remove unused ones (Recommended)" — remove each only after confirming no asset/scene dependency
by:             the human, in session

## D-6 · framing · 2026-10-07
open decision:  O1 — this run's build scope
raised by:      04-delivery-brief.md § Open decisions O1
ruling:         "S1 only (Recommended)" — design/build/test/verify S1 in this run; design notes a constraint for S2's seam but does not design S2; S2–S9 are follow-up runs
by:             the human, in session

## D-7 · framing · 2026-10-07
open decision:  O2 — the ~34 uncommitted files S1 overlaps
raised by:      04-delivery-brief.md § Open decisions O2
ruling:         "I'll commit first" — the human commits the WIP before build; build waits for their word
by:             the human, in session

## D-8 · framing · 2026-10-07
open decision:  O3 — Timeline package
raised by:      04-delivery-brief.md § Open decisions O3
ruling:         "Keep Timeline" — S8 removes only Animation Rigging and Cinemachine, each after dependency check
by:             the human, in session

## D-9 · framing · 2026-10-07
open decision:  O4 — combat clip source for S5
raised by:      04-delivery-brief.md § Open decisions O4
ruling:         "Placeholder action" — build S5 layers and event plumbing on an existing clip as a stand-in
by:             the human, in session

## D-10 · build · 2026-10-07
open decision:  go on S1 build, and dispatch order (05-technical-plan.md proposes test-first, departing from the order's backend-then-test)
raised by:      05-technical-plan.md § Test plan; orchestrator plan presentation
ruling:         "Go, test-first (Recommended)" — 06 test (red), 07 backend (green), 08 integration, 09 docs; human keeps Unity Editor closed during test runs. D-7 treated as satisfied: working tree clean at HEAD 9bb46bb.
by:             the human, in session

## D-11 · verify · 2026-10-07
open decision:  CR-1 (SHOULD_FIX, per-frame LogWarning) — fix in this run or carry to S2
raised by:      08-integration.md § Ruling on 07 risks item 1; cr/CR-1.md
ruling:         "Fix now (Recommended)" — backend fixes CharacterAnimationBridgeSystem.cs only, integration re-runs; budget re-planned
by:             the human, in session
