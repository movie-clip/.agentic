REPORT 2026-10-07-ecs-animation-approach/04
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only producer brief, order verification was NONE

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - 9 slices proposed for the animation epic (S1 to S9), run-local only, no repo file - see § Stories
  - Recommended build scope for THIS run: S1 (bridge link lifecycle fix plus the animation test harness); design fires for it, specification does not - see § Sequence
  - S2 (backend-swappable bridge contract, sized 30 to 150) is the next run and does fire specification and design - see § Stories
  - open decision: confirm S1 as this run's scope, and that the design pass does not also design S2 - see § Open decisions
  - open decision: Timeline cannot be removed under D-5's own condition (66 Synty .playable assets plus 2 Gallery scenes use it) - see § Open decisions
  - open decision: combat clips do not exist in the project and no combat gameplay code exists, so S5 needs a clip-source call - see § Open decisions
  - open decision: lock-on activation model, root-motion scope, 150-character frame budget, Samurai route, vendor-pack edit policy, unused Sidekick set - see § Open decisions
  - already covered: Humanoid retargeting and every Animator parameter name already match across code and controller; no slice needed for either - see § Already covered
  - precondition: 34 uncommitted files, including the skin and hybrid flow S1 edits; the human commits or confirms them before build dispatch - see § Open decisions

skill_calls:
  - none

risks:
  - Took on trust from 01-recon: the ghost-entity leak. Marker removal is verified by my own read, but nobody has run it in Play mode, so S1 starts by reproducing it with a failing test.
  - Took on trust from 01-recon: jump/landing, gait and dead-strafe details (isStrafing hard-coded false, JumpTriggered as a landing edge). They colour S2 and S3 but change no verdict here.
  - Took on trust from 02-recon: stale rig errors in 34 Masc FBX metas and the dangling Samurai controller GUID effect. S7 begins with an audit, not a fix, for this reason.
  - Took on trust from 03-recon: Rukhanka and Latios facts. Not used for any verdict, since D-2 is ruled and the options are not re-evaluated.
  - Recon 02 listed 3 SkinnedMeshRenderers per Viking skin prefab and recon 03 listed 6. I counted 6 in both Visuals prefabs (3 inactive). Recon 03 is right; this affects only S2 sizing.
  - Cinemachine and Rigging show no asset or scene reference by name, but I did not search by script GUID. S8 owns the GUID-level confirmation D-5 requires.
  - Review gate: no slice here carries a story, so review does not fire unless specification does (S2, S4, S5). The orchestrator should expect that.
  - Package sequencing: Animation Rigging is the usual tool for aim and head-look IK. D-5 ruled removal and I did not reopen it. Removal sits late in the order so a later feature can still say it needs Rigging.

## Orchestrator brief
- verdict: New epic (the human's animation epic). Framing fires. The epic is run-local only; guardrail 4 forbids a repo roadmap and none exists.
- epic: PROPOSED, no precedent epic in this repo. Nearest precedent is commit 7ba63ea "animations, input", which built the current hybrid bridge.
- 9 slices: S1 bridge lifecycle fix and test harness. S2 backend-swappable bridge contract sized for 30 to 150. S3 AI/NPC animation at population scale. S4 strafe and lock-on. S5 combat/action layers with clip events back into ECS. S6 root motion. S7 content config hygiene (Samurai GUID, Viking skin duplication). S8 package removal per D-5. S9 setup doc rewrite.
- Animation test coverage is not a separate slice. Every slice carries its own tests and S1 lands the harness; see the coverage matrix in § Stories.
- Recommended build scope for this run: S1. Phases: design fires (skin/hybrid flow is the named central risk), specification does not, review does not.
- blocks dispatch: human confirms S1 as scope and commits or accepts the 34 uncommitted files (skin and hybrid files among them). Everything else blocks only later slices.
- Two findings changed the plan: no combat clips or combat code exist (blocks S5 content), and Timeline has real asset dependencies (D-5 condition fails for it).
- sections below: Placement · Stories · Sequence · Open decisions · Already covered

## Placement
No epic tree exists in this repo and guardrail 4 forbids creating one, so the epic below is a run-local grouping. It lives in this artifact and in the human's head, not in a roadmap file. The pack says the producer's real decision here is "new feature surface (framing fires) versus ordinary change". Strafe, root motion, combat layers and AI animation are new feature surfaces, so framing fires. S1 and S7 to S9 are ordinary changes that ride in the same epic only for ordering.

Nearest precedent is git, not a roadmap. Commit 7ba63ea ("animations, input") created the current bridge, and commit 944581f ("fixes") touched the strafe state code. Neither was an epic. This epic is therefore not a sibling of anything; there is no precedent to inflate against. The epic is one problem: ECS owns animation intent, a swappable presentation backend plays it, and the contract between them is correct and tested.

Slices are not a technical-layer cut. S2 is the one slice that is partly a layer (a contract), and it is justified as the hinge: D-2 asks for a seam, and S3 to S6 all consume it. S2 still ships a visible result, a character count and cost figure at 150 characters, plus a proof that the Animator side can be replaced in tests.

## Stories
Each slice: intent, what it depends on, areas touched, design trigger (package or component/singleton shape that another package reads), specification trigger (crosses more than one lane's contract with no approved brief), and a checkable done statement. Every "done" also requires `dotnet build Impact.sln` clean and EditMode `-CoreOnly`, plus PlayMode `-CoreOnly` where the slice reaches runtime flow, per `phases.md`.

### S1 - A swapped or destroyed character leaves no broken animation link
  intent:     A character whose skin is swapped keeps animating, and a destroyed character leaves nothing behind in the world.
  value:      The skin cheat command stops producing a frozen character; characters can be spawned and destroyed repeatedly without ghost entities accumulating.
  depends_on: none. Precondition: the working tree's uncommitted skin and hybrid edits are committed or accepted (see § Open decisions).
  touches:    `athena.shared` Systems/Hybrid, Systems/Player, Components/Character (CharacterAnimationBridgeInitialized, HybridGameObject and the default-prefab path); `Assets/Tests` (EditMode and PlayMode). No Assets/prefab change expected.
  design:     YES. The skin/character flow is the project's named central risk, and the fix chooses who owns the link marker's lifetime (S2 formalises that choice). The default-skin return path may also need the default prefab remembered, which changes a component shape.
  specification: NO. One package; the brief is the specification.
  scope in:   marker never cleared on swap (verified: written at CharacterAnimationBridgeSystem.cs:37 and :46, removed nowhere); cleanup component keeps destroyed characters as shells; default skin return (verified: SpawnHybridCharacterSkinSystem overwrites HybridGameObject.Prefab at :68 and the default branch never restores it, so swapping back to default may respawn the override); possible second CharacterAnimatorSync when the Animator sits on a child (01-recon § Problems 8); the generic spawner not honouring HybridGameObjectManualCreation (§ Problems 9, only if reproduction confirms).
  scope out:  strafe dead code, parameter mapping, authoring duplication (those are S2 and S4), and the Keyboard.current null check (adjacent input fragility, route to debt).
  done:       (1) A failing test reproduces each in-scope defect before any fix, run in the current tree. (2) After a Viking Base to Warrior to Base swap, the new instance has a linked CharacterAnimatorSync pointing at the entity, and the Animator parameters change when the state changes; asserted in a test, not by eye. (3) After a character entity is destroyed, a query for leftover animation-link entities returns zero. (4) Returning to the default skin spawns the default prefab. (5) The tests form a reusable fixture, a minimal world with spawn, skin change and bridge, that S2 reuses. (6) Build and both test platforms are clean.
  invest:     Estimable only after step (1): recon never ran this in Play mode, so the first ticket is a reproduction. Acceptable; it is also what proves the finding is real.

### S2 - The ECS to Animator bridge is a clean contract with a swappable backend, sized for 30 to 150 characters
  intent:     One mapping from ECS animation state to Animator parameters, behind a seam that a different backend could replace, whose cost at 150 characters is measured.
  value:      The developer can change how a state is played, or later swap the Animator for another backend, without editing the state system, the authoring and the MonoBehaviour three times. The cost of 150 animated characters is known, not guessed.
  depends_on: S1 hard for its fixture and lifecycle ownership; S1 soft for the fix itself.
  touches:    `athena.shared` (CharacterAnimationState, state update system, bridge, CharacterAnimatorSync, both authoring bakers); possibly a new seam location (an asmdef decision is the design lane's). `Assets/Tests`.
  design:     YES. A component shape that AI, gameplay and charactercontroller consumers will read (CharacterAnimationState) changes, and the seam location may cross the guardrail-2 graph.
  specification: YES (recommended). The state shape is the shared contract S3 to S6 all extend, and nothing approved covers it. Review then fires too.
  scope in:   one source for speed normalisation (three constants today: 6, 7 and GroundMaxSpeed, 01-recon § Problems 4); every state field written to a parameter or explicitly retired (JumpTriggered is misnamed; four fields unread); one baker (CharacterAuthoring and CharacterAnimationAuthoring duplicate it); explicit update ordering instead of sort-order luck (§ Problems 16); no player/camera coupling in the state query (§ Problems 3 and 7, so AI can use it); per-frame cost reduced per D-3 (per-character EntityManager reads, unconditional parameter writes); characterization tests of the existing state system written before it is refactored.
  scope out:  any non-Animator backend implementation (D-2 asks for the seam only), strafe behaviour (S4), shader/material changes (D-2).
  done:       (1) A test double backend implements the contract and receives every state change with no Animator present. (2) A mapping test shows each state field has a parameter or is marked retired. (3) A 150-character scene or test records main-thread animation cost, compared with the budget in § Open decisions. (4) One baker only; setup doc contradictions on this point resolved in S9. (5) Characterization tests pass before and after the refactor. (6) If the 150-character figure misses the budget, a conditional scale slice (animator culling, update-rate throttling, parameter change-gating) is raised before S3.
  invest:     Largest slice; weak on Small. If design sizes it as more than a handful of tickets, split at "contract and mapping" versus "cost at 150", keeping measurement first in whichever half goes first.

### S3 - NPCs animate at crowd scale
  intent:     AI-driven characters animate as correctly as the player, at the 30 to 150 population D-3 names.
  value:      A scene with dozens of NPCs shows them walking, stopping and jumping, with measured cost, instead of a player-only animation path.
  depends_on: S2 hard.
  touches:    `athena.shared` state query; `athena.ai`, `com.ai.utility` (read only, as the driver); a sandbox scene under `Assets/Content/Levels/Tests`; `Assets/Tests`.
  design:     NO unless S2 left an open coupling. specification: NO.
  scope in:   an NPC path through ExternalInput and MoveToTarget that produces animation state; a population test at 30 and 150; Viking NPC as the sample.
  scope out:  AI choosing to strafe or attack (AI behaviour is not animation; it consumes S4 and S5 when those land).
  done:       (1) An NPC with no OwnedByPlayerEntity player and no camera animates in a test. (2) A sandbox with 30 and 150 NPCs runs, and the recorded cost matches S2's figure within noise. (3) NPC spawn and destroy at that count leaves zero ghost entities.
  invest:     May be thin if S2 already covers the NPC path; if so, S3 is a verification pass and may merge into S2's done, the producer's call at S2 close.

### S4 - Strafe and lock-on locomotion
  intent:     The character strafes, turns in place and faces a target instead of always facing its move direction.
  value:      The player can circle a target with the correct strafe animations; the already-authored strafe, turn-in-place and forward-strafe parameters and blend trees stop being dead.
  depends_on: S2 hard (state shape and mapping). The activation model is a human decision.
  touches:    `athena.shared` state update system; `athena.charactercontroller` (character rotation mode, input binding); `athena.gameplay` only if target selection lives there; the controller asset needs no change (parameters and trees exist).
  design:     YES. A rotation mode in the character controller is a contract shared by charactercontroller and shared (and charactercontroller cannot reference shared).
  specification: YES. Crosses charactercontroller and shared with no approved brief.
  done:       (1) With strafing active, movement input produces non-default StrafeDirection, ForwardStrafe and IsStrafing, asserted in a state-system test. (2) Turn-in-place triggers when the facing delta exceeds the threshold. (3) Toggling back returns to the non-strafing values. (4) The Animator reaches the strafe blend tree for the Viking, verified in PlayMode by state name. (5) Works for an AI-driven character without a player camera.
  invest:     Weak on Independent: the activation model (§ Open decisions) must be settled first.

### S5 - Combat/action layers with clip events back into ECS
  intent:     An ECS-requested action plays on an action layer and events authored in the clip reach ECS.
  value:      An action such as an attack plays without breaking locomotion, and ECS learns when a hit window opens and closes from the clip itself.
  depends_on: S2 hard. A clip source decision (§ Open decisions) for real combat content.
  touches:    `athena.shared` (action request component, the animation to ECS event channel); `athena.gameplay` (consumer, only if combat exists there; it does not today); the controller asset (action layer, avatar mask; none exist now); clip import events in FBX .meta; `Assets/Tests`.
  design:     YES. A new component/event contract that gameplay reads, with the direction reversed (presentation to ECS).
  specification: YES. Crosses shared, gameplay and the content/asset lane.
  done:       (1) An action request from ECS sets an action layer state, and the base layer keeps locomoting, asserted by layer weight and state. (2) A clip event arrives as an ECS component or event within one frame, in a test. (3) An avatar mask exists and is applied. (4) Works for both the Viking player and an NPC.
  invest:     Weak on Valuable until clips exist: nothing in the project is a combat clip (verified: Base Locomotion has Idle, InAir, Locomotion, Transitions only; the Polygon character packs have 0 animation FBX; there is no attack, damage or weapon logic in athena.gameplay or athena.ai). Acceptable only with a stand-in action built from existing clips, which proves layers and events but not combat feel. Ask the human, see § Open decisions.

### S6 - Root motion for actions
  intent:     Selected actions move the character by the animation's own root motion.
  value:      Lunges, dodges and attack steps travel the distance the clip authors, not a guessed ECS distance.
  depends_on: S2 hard (return channel); S5 soft (first real consumer, since root motion is mostly for actions).
  touches:    `athena.charactercontroller` (accepting an external delta on the kinematic body); `athena.shared` (bridge return channel); controller and clip assets (the `*_RootMotion` clips exist but no controller state uses them); `Assets/Tests`.
  design:     YES. ECS currently drives the GameObject; root motion inverts that for one channel, and the Animator evaluates after ECS, so a frame of latency is expected. This is the project's riskiest design.
  specification: YES. Crosses charactercontroller, shared and assets.
  done:       (1) A spike result is recorded: whether Animator-to-ECS root delta is viable at 150 Animators, and its latency. (2) One action moves the character by the clip's root delta; the kinematic body, not the GameObject transform, owns the final position. (3) Locomotion remains root-motion-off. (4) A test asserts the final position within a stated tolerance.
  invest:     Weak on Estimable; hence the spike comes first. Does not scope the human's "root motion" to all locomotion; that is a decision (§ Open decisions).

### S7 - Character content configuration is consistent
  intent:     Character prefabs and imports carry no dangling or duplicated animation configuration.
  value:      Fewer places a prefab edit has to be repeated or can silently go wrong; the console shows no missing-controller or rig-import warnings for game content.
  depends_on: none for the audit; S2 soft (so the prefab contract is settled before prefabs are reshaped).
  touches:    `Assets/Content/Characters/**`; `Assets/PolygonSamurai/**` only per the vendor-edit decision; `Assets/Synty/**` FBX metas for the rig-error audit. No code.
  design:     NO. specification: NO.
  scope in:   audit first: re-import to see whether the 34 stored rig errors ('pelvis' not found) are stale; the Samurai pack controller GUID d62af11c (20+ pack prefabs) that has no asset; two full-copy Viking skin prefabs (3.6k lines each) that differ only in the active renderer; VikingCharacter nesting an inactive Viking_Chief_01_White instance and an inactive PF_Player while also being the hybrid spawn target; pack prefabs with root motion on; Samurai using an embedded prefab with no skin crate.
  scope out:  deleting the Sidekick set or the Polygon Feminine controller (a decision), and any shader or material change (D-2).
  done:       (1) A written audit result states which of the above are real. (2) After fixes, no game-owned prefab references a missing controller or missing script. (3) The two Viking skin prefabs are variants of one base, or the decision to keep them is recorded. (4) The Samurai prefab follows the route the human picks. (5) Skin swap test from S1 still passes.
  invest:     Value is weak for the dangling GUID alone: SamuraiCharacter.prefab already overrides the controller (02-recon § Prefabs and crate pipeline, line 56-58), so the broken reference only bites pack prefabs used directly. It rides with the other config items instead of standing alone, and is the first candidate to drop.

### S8 - Unused packages are removed per D-5
  intent:     The manifest lists only packages the project uses.
  value:      Smaller import and compile surface; no packages with no consumer in AGENTS.md's package list.
  depends_on: none hard. Sequenced late so a feature slice can still ask for Animation Rigging.
  touches:    `Impact/Packages/manifest.json` (packages-lock.json regenerates); `Assets/Synty/**/Samples` if Timeline is removed; no first-party code.
  design:     NO. specification: NO.
  scope in:   confirm each package is unused by script GUID, asset and scene before removing it, per D-5. Cinemachine and Animation Rigging show no reference by name (01-recon § Packages; my grep). They come in through `com.unity.feature.characters-animation`, so removal means removing the feature-set line, not the packages individually. Timeline is a direct manifest dependency and fails the check (see § Already covered). Entities Graphics stays unless a rendering check proves it unused.
  scope out:  Entities, Physics, CharacterController, URP, Input System, Burst, Mathematics, Collections.
  done:       (1) Each removal has a recorded reference check. (2) `dotnet build Impact.sln` and a Unity batchmode compile are clean with the packages removed, since manifest changes touch package-generated assemblies. (3) EditMode and PlayMode `-CoreOnly` are green. (4) The Timeline outcome follows the human's call.
  invest:     None weak. Manifest and lock only; Library/ and generated .csproj are not touched (guardrail 5).

### S9 - CHARACTER_ANIMATION_SETUP.md describes the system that exists
  intent:     The setup doc matches the code and the controller.
  value:      The next person setting up a character is not told to use parameters that do not exist (Speed, MoveX, MoveZ, Jump trigger) or to add both authoring components.
  depends_on: S2 (rewrite once, against the final contract). Interim: this run's close-out docs pass adds a stale banner, corrects the system order and the "runs once" claim, and fixes the stale rename and the inverted "initialized repeatedly" claim in `athena.shared/PACKAGE_DOCUMENTATION.md:97`. It also adds the animation line `AGENTS.md` omits (01-recon § Problems 13).
  touches:    `Impact/CHARACTER_ANIMATION_SETUP.md`, `athena.shared` PACKAGE_DOCUMENTATION.md, `PACKAGE_ARCHITECTURE.md`. Docs lane only.
  design:     NO. specification: NO.
  done:       (1) Every claim marked Contradicted in 01-recon § Doc claims verified is corrected or removed. (2) The parameter list is the controller's, with no duplicate vocabulary. (3) One setup path for authoring. (4) Each of S3 to S6 appends its section as it ships.
  invest:     None weak.

### Test coverage matrix (not a slice; each slice owns its tests)
| Area uncovered today (01-recon § Problems 12) | Covered by |
|---|---|
| spawn, skin change, link lifecycle | S1 (and the harness) |
| CharacterAnimationStateUpdateSystem (gait, edges, input) | S2 characterization tests, before the refactor |
| Animator parameter mapping | S2 mapping test |
| strafe values and turn-in-place | S4 |
| action layers and clip events | S5 |
| root-motion position | S6 |
| NPC and population | S3 |

A trailing "write the tests" slice would leave S1 and S2 unprotected while they are the ones that change the most. That is why coverage is a done-criterion per slice.

## Sequence
1. S1 first. It is the risk-first slice: if the lifecycle is wrong, every later test and measurement runs on a leaking world. It is also the smallest independently shippable fix, and it lands the test harness S2 reuses. Edge: S2 hard on S1's fixture.
2. S2. The contract before features: S3 to S6 each add to CharacterAnimationState or the bridge, and building them before S2 would mean rewriting each. It also carries the first cost figure for D-3 and the gate for a conditional scale slice. Edge: S3 to S6 hard on S2.
3. S3. It proves the D-3 population with real NPCs right after the contract, while the cost figure is fresh. If it turns out thin, merge it into S2.
4. S4, then S5. S4 is the smaller of the two feature slices and consumes only the existing controller; S5 needs the clip-source decision, which gets time to be answered. Edge: S4 needs the activation model decision first.
5. S6 after S5. Soft dependency: its first consumer is an action. Spike first, since this slice could invalidate the "Animator output feeds ECS" assumption S5's event channel also relies on. Putting the spike earlier is allowed, and the human may want it if root motion is the priority.
6. S7 after S2 (soft), S8 late (soft, keeps Rigging available for S4 to S6), S9 after S2 with per-slice appendices. S7 and S8 are independent of S3 to S6 and may be pulled forward, or bundled into one run with S9's interim pass.

This run: carry S1 through design, build and verify. It is the smallest slice with a real design trigger, it proves the harness and the diagnosis in code, and it uses the reserved design and build dispatches without outsizing the 7 remaining budget. If the human prefers S2, specification fires, which adds the one hard stop and pushes build past this run's budget.

Follow-up runs, one slice each: S2, then S3 (or merged), S4, S5, S6, and a bundled S7, S8 and S9 hygiene run.

## Open decisions
Already-ruled items (D-2 hybrid, D-3 30 to 150, D-4 four features, D-5 removal) are not re-asked.

- O1. Is S1 this run's build scope, with the design pass scoped to S1 only (constraint note for S2's seam, no S2 design)? Raised by this brief § Sequence. Blocks dispatch.
- O2. Are the 34 uncommitted files, including `HybridGameObjectSystemBase.cs`, `CharacterSkinCrate.cs`, the `AuthoritativeCharacterSkinLoadSystem` rename and the Player systems, settled and committed before S1 build? Raised by `git status` in this brief § Sequence. Blocks dispatch: S1 edits the same flow.
- O3. Timeline: D-5 says remove only after confirming no asset or scene dependency. I opened the assets: 66 `.playable` files under `Assets/Synty/AnimationBaseLocomotion/Samples/Timelines` and `Gallery_01_Polygon.unity` and `Gallery_01_Sidekick.unity` use it. Keep Timeline, or approve deleting those Synty sample timelines and scenes? Raised by 01-recon § Packages and 02-recon § Pack inventory. Blocks S8 only.
- O4. Combat clip source: the project has no attack, dodge or hit clips and no combat code. Buy or import a combat animation pack, source clips elsewhere, or build S5 on a stand-in action? Raised by 02-recon § Pack inventory; verified in this brief § Stories S5. Blocks S5 content only.
- O5. Frame budget for animation at 150 characters: what main-thread millisecond figure and what target machine make S2's done pass or fail? Raised by 03-recon § Options compared (hybrid perf model). A proposal for the human to adjust: 1.0 ms on the development machine. Blocks S2's done statement.
- O6. Strafe and lock-on activation: lock onto a target entity, hold a key to strafe, or always face the camera? Raised by 01-recon § Problems 3 and § Input to animation flow (no lock-on input or target concept exists). Blocks S4.
- O7. Root-motion scope: actions only, or also locomotion? Raised by 02-recon § Import settings (`*_RootMotion` clips exist, no controller state uses them) and 02-recon § Configuration problems (pack prefabs ship with root motion on). Recommendation: actions only. Blocks S6 scope.
- O8. Samurai route: move it onto the skin-crate path like Viking, or keep the embedded pack prefab? Raised by 02-recon § Prefabs and crate pipeline. Blocks S7's Samurai item only.
- O9. May S7 edit vendor pack prefabs under `Assets/PolygonSamurai` (a pack update would overwrite them), or only game-owned prefabs? Raised by 02-recon § Configuration problems. Guardrail 1 covers only `Packages/` and `Library/PackageCache`, so this is a policy call. Blocks S7's GUID item only.
- O10. The Sidekick set (346 FBX, 4 controllers, timelines, demo scenes) and Polygon Feminine controller have no game consumer. Keep (purchased, may be wanted) or delete? Raised by 02-recon § Configuration problems. Not a D-5 item (D-5 is about packages). Blocks nothing; a deletion is outside every slice until answered.
- O11. The controller's crouch, incline, lean and head-look parameters exist but Impact never writes them. They are not in D-4, so I did not schedule them; say if any should join the epic. Raised by 02-recon § Animator controllers.

## Already covered
- Humanoid retargeting: all three character packs and all 346 Polygon clips are Humanoid, and the three skeletons share Synty bone names (02-recon § Avatar and retargeting). Viking_BaseSkin_Visuals pairs a Viking avatar with AC_Polygon_Masculine today (line 701-702 per recon). Nothing to schedule. I did not re-open those meta files; this colours the plan and changes no verdict.
- Parameter names: the 15 or so parameters CharacterAnimatorSync writes all exist in AC_Polygon_Masculine with matching types (02-recon § Prefabs and crate pipeline). No mapping-repair slice is needed; S2's mapping work is about the contract, not mismatch.
- Strafe parameters, blend trees and `*_RootMotion` clips already exist in the controller and assets. S4 and S6 are wiring and state work; no animation authoring is proposed.
- The bridge marker defect: verified by my own read. `CharacterAnimationBridgeInitialized` is added at `CharacterAnimationBridgeSystem.cs:37` and `:46` and appears nowhere else in `Packages/` or `Assets/` (grep, whole project), and the bridge query is `WithNone<CharacterAnimationBridgeInitialized>`. The finding stands. Git: the bridge file was last touched in 7ba63ea, so the doc claim at `PACKAGE_DOCUMENTATION.md:97` ("initialized repeatedly") is the stale one.
- Default-skin return: 01-recon § Problems 11 said it could not confirm. I read `SpawnHybridCharacterSkinSystem.cs` lines 62-82 and `CharacterSkinChangeSystem.cs` lines 136-145. The default branch only logs and never restores `hybridGameObject.Prefab`, so the suspicion is a real defect to reproduce, folded into S1.
- Dropped as out of epic: Keyboard.current and Mouse.current null dereference (01-recon § Problems 15). It is input fragility, not animation. Route to the debt register; I did not verify it.
- Already recorded as a rename in the working tree: `AuthoritativeCharacterSkinLoadSystem` to `CharacterSkinLoadSystem` (git status). The doc references to the old name are S9's interim pass.
- Dropped: the Entities-Graphics-skinning, Rukhanka, Kinemation and GPU baker alternatives (03-recon § Options compared). D-2 is ruled; not re-evaluated.
- Not covered by anything: package removal (S8), combat clips, lock-on, root-motion return channel, and animation tests generally. I listed `Assets/Tests/EditMode` and `Assets/Tests/PlayMode`: no animation fixture exists there, which agrees with 01-recon § Problems 12.
