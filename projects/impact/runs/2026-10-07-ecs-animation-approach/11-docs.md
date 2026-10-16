REPORT 2026-10-07-ecs-animation-approach/11
status:      DONE
verdict:     NONE

changed:
  - Impact/Packages/athena.shared/PACKAGE_DOCUMENTATION.md — known-issue line (was :97) replaced with current bridge behaviour: link follows instance, managed cleanup marker, Prefab never written, generic spawner skips ManualCreation, warn once per instance
  - Impact/CHARACTER_ANIMATION_SETUP.md — corrected "runs once" bridge description, marker semantics, skin-swap relink, system-order tree, Files Created list; added partial-staleness note with authoritative code paths at top
  - Impact/ARCHITECTURE_REVIEW.md — Testability "what is good" lists the new Animation EditMode/PlayMode fixtures; hybrid pipeline Strengths notes relink on skin swap and no shell entities
  - C:/projects/investments/.agentic/projects/impact/capabilities/testing.md — § Which packages a test can see: Unity.Transforms added to both assembly rows
  - C:/projects/investments/.agentic/projects/impact/runs/2026-10-07-ecs-animation-approach/pack-corrections.md — entry state set to APPLIED

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Claims checked by reading code: CharacterAnimationBridgeSystem.cs, CharacterAnimationBridgeCleanupSystem.cs, CharacterAnimationState.cs, SpawnHybridCharacterSkinSystem.cs, both test asmdefs, test file list.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - CHARACTER_ANIMATION_SETUP.md still carries parameter-name and system-order drift (Speed/MoveX vs MoveSpeed/CurrentGait etc.), flagged stale at its top, left for the later rewrite
  - Test lane may cover: warn-once path, warned-entry trimming, bridge pass 2 skip when Instance is null for a frame, not-ready skin fallback spawning the baked default (from 07, 09 handoffs)

skill_calls:
  - none

risks:
  - The order said mark the ghost-entity weak spot resolved "if listed"; ARCHITECTURE_REVIEW.md did not list it, so I added a Strengths line to § 6 instead of a resolution mark
  - PACKAGE_DOCUMENTATION.md line 96 (skin ref-count flow incomplete and duplicated) was not touched; not verified against code and outside the S1 statements
  - The "partially stale" note in CHARACTER_ANIMATION_SETUP.md names the bridge/skin-swap sections as updated; the Troubleshooting step "Check console for Auto-added message" is still accurate (message still logged)
  - The old known-issue line was converted to a behaviour description inside the Known Issues list, as the order located the statement there; the human may prefer to move it to the flow section

## Orchestrator brief
- Four docs and one pack file edited; no roadmap or slice content added.
- Pack correction applied verbatim from 06 and verified against the asmdefs.
- No contract notes or new pack corrections.
