REPORT 2026-10-07-s2-animation-bridge-contract/01
status:      DONE
verdict:     NONE

changed:
  - C:\projects\investments\.agentic\projects\impact\runs\2026-10-07-s2-animation-bridge-contract\01-story.md — DRAFT story for S2 (this file); no repo file touched

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    draft story, order verification was NONE

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - DRAFT for human review, not an approved story. Story body below: Open decisions, Story, Acceptance criteria, Out of scope, Test plan, Tickets
  - Blocking ticketing, OD-1: S2 is six tickets; the brief's split (contract and mapping, versus cost at 150, measurement first) is proposed, not decided, see § Open decisions
  - Blocking ticketing, OD-2: may unifying the three speed constants change which gait a given speed produces, or must gait output stay identical, see § Open decisions
  - Blocking ticketing, OD-3: which conditions the 150-character figure is recorded under (machine, Editor or player build, scene), see § Open decisions
  - Order for the next lanes: characterization tests (T-1) and the baseline figure (T-2) come before any refactor ticket; the design lane picks the contract shape after the human approves
  - Fixtures to reuse, from 06-test: CharacterAnimationEditModeWorld and CharacterAnimationPlayModeHarness, whose write-state and read-presentation helpers are the intended swap point for a test-double backend
  - Review gate fires for this slice (specification fires, brief § Stories S2). The reviewer measures against the Acceptance criteria section

skill_calls:
  - none

risks:
  - Brief done-criterion (3) and (6) are replaced by D-1: the figure is recorded, no threshold, no auto-raised scale slice. I carried that into AC-14 and AC-15 and wrote no budget anywhere
  - There is no capabilities/story.md pack for impact, so I had no project convention for the story's opening status value. The draft marks itself DRAFT and takes no other status field
  - Gait unification (AC-5) may change observable gait; the brief says "one source" without saying whether results must stay identical. I made it OD-2 rather than guess
  - The S1 follow-up C-1 (warn-once path and its trimming are untested, 09-backend § handoff) is pulled into AC-12 because S2 reshapes the bridge. If the human wants it left out, drop AC-12 only
  - Recon problems 3, 4, 7, 16 are code reads that nobody ran. Characterization tests (T-1) pin what the code actually does, which may differ from what recon read
  - The 06-test pack gap (no Assert.Multiple in this project's NUnit) and the dotnet-build-only-sees-new-tests-after-Unity-regenerates-csproj gap apply to every test ticket here. They are the test lane's pack, not mine

## Orchestrator brief
- DRAFT story, awaiting human approval; nothing is ticketed until the three blocking open decisions below are answered.
- Decision: D-1 applied. The 150-character figure is recorded with its conditions and reported; no threshold, no auto-raised scale slice. Brief done (3) and (6) are replaced.
- Decision: characterization tests (T-1) and the pre-refactor 150 baseline (T-2) are ordered before every refactor ticket (T-3 onward).
- Decision: ACs state observable outcomes only; no interface names, component layouts, asmdef placement or ordering attributes. Design lane settles those next.
- Lane split proposed: T-1, T-2 test; T-3, T-4 backend after design; T-5 test; T-6 test measurement. Review gate fires.
- Size: six tickets, so the brief's split is raised as OD-1 for the human.
- Blocks ticketing: OD-1 split, OD-2 whether gait output may change, OD-3 measurement conditions.
- Sections: Open decisions · Story · Acceptance criteria (AC-1..AC-15) · Out of scope · Test plan · Tickets (T-1..T-6).

## Open decisions

All three block ticketing. The draft assumes the stated default so the design lane could start, but the human decides.

- **OD-1 Split S2? (blocks ticketing.)** The story is six tickets, more than a handful. The brief § Stories S2 (invest) names the split point: "contract and mapping" versus "cost at 150", measurement first. Proposal for the human to take or leave: S2a = T-1, T-3, T-4, T-5 (contract and mapping); S2b = T-2, T-6 (cost at 150). Tension to weigh: the figure in AC-14 is meant to be recorded both before and after the refactor. If S2b ships first it carries the baseline, and its second figure has to wait for S2a. Assumption in this draft: one story, unsplit.
- **OD-2 May gait output change when the three speed constants become one? (blocks ticketing.)** Recon problem 4 shows three independent speed normalisations (state system thresholds and an assumed run speed of 6, the Animator-side maximum of 7, and the character's ground maximum speed). Making one the source can move a gait boundary for the default Viking. Options: (a) default-character gait results stay identical to today's at every speed, so the single source is chosen to reproduce them; (b) results may shift, and the characterization tests are updated deliberately. Assumption in this draft: (a). AC-5 is written for (a) and must be rewritten if the human picks (b).
- **OD-3 Under what conditions is the 150-character figure recorded? (blocks ticketing.)** D-1 removed the threshold but not the question of what a figure means. The draft assumes: the development machine, in the Editor and, if the human wants one, a standalone player build; a scene or test with 150 characters moving continuously. The human fixes whether a player build is required or whether Editor-only is acceptable.

Already ruled and not re-asked: D-2 hybrid, D-3 30 to 150 characters, D-4 the four features, D-1 of this run (measure only).

## Story

As the developer building strafe, combat, root motion and NPC animation on top of this bridge, I want the ECS-to-Animator path to be one defined contract with a replaceable backend, so that I can change how a character state is played, or later swap the Animator for something else, without editing the state system, the authoring and the MonoBehaviour three times; and I want the per-frame cost of 150 animated characters recorded rather than guessed.

Scope is the brief's S2 (04-delivery-brief § Stories S2), minus the done-criterion (3) budget comparison and (6) automatic scale slice, which D-1 replaces with a recorded figure. S1 (committed in 4825be0) is the foundation: link lifetime, cleanup, default-skin return and the two test fixtures already exist.

Why it is not a pure refactor: the player-visible result is that a character animates identically to today, and the developer-visible result is a known cost and a proven seam.

## Acceptance criteria

Each criterion is one checkable statement. "Test" means an automated EditMode or PlayMode test in `Assets/Tests`; "recorded" means a figure or note in the run artifact the reviewer can open.

**Behaviour preserved (characterization)**

- **AC-1.** For a scripted set of inputs (idle, walk, run, sprint, a jump ascent, a fall, a landing, start and stop of movement input), the existing state update produces a recorded set of animation-state values, and a test asserts those values. This test exists and passes before the state update system is changed.
- **AC-2.** The same scripted sequence, driven through a real Animator on the Viking prefab, produces the Animator parameter values recorded before the refactor, and a PlayMode test asserts them. This holds after the refactor with the same expected values (subject to OD-2).

**Contract and swappable backend**

- **AC-3.** A test double standing in for the animation backend receives every animation-state change for a character, with no Animator and no GameObject animation component present in the test world.
- **AC-4.** The Animator backend and the test double both receive the same state sequence in one test run, and the sequence the test double records equals the sequence of ECS-side state changes the test applied.
- **AC-5.** Every animation-state field is, in a test, either shown to reach the backend (the Animator parameter changes, or the test double sees the value) or listed in one place as retired and not written. A field in neither group fails the test. (Retired today by recon problem 5: four unread fields, and the field named JumpTriggered, which is a landing edge, not a trigger. Its final name or retirement is the design lane's call.)
- **AC-6.** Changing the character's maximum movement speed in one place changes the reported normalised speed and the gait result consistently. A test with two different maximum speeds shows the gait boundaries and the normalised speed follow that single value. For the default Viking, gait results at every tested speed equal AC-1's recorded values (assumption (a) in OD-2).
- **AC-7.** A character prefab authored with the single supported authoring component receives the complete animation state on bake. A prefab carrying both authoring components today either bakes identically to one or reports a visible error; it is not silently baked twice. A test or a recorded bake of the Viking prefab shows this. The existing Viking prefabs use only that one authoring path.

**Ordering and independence**

- **AC-8.** The animation state computed in a frame reflects the character's movement of that same frame, regardless of unrelated system-sort changes. A test that moves the body in frame N asserts the state in frame N, and the ordering is declared explicitly, not left to sort order (recon problem 16).
- **AC-9.** A character with no owning player and no camera in the world receives animation-state updates and reaches the backend. A test runs it with neither. (This makes the state usable by AI; population tests are S3's.)
- **AC-10.** A player character in a world with no orbit camera still receives animation-state updates, with the camera-dependent values at their neutral defaults. The test asserts both.

**Cost per frame (per D-3)**

- **AC-11.** When a character's animation state does not change between frames, the backend receives no write for that character in those frames. The test double counts writes over a run of unchanged frames and the count is zero after the first frame. The Animator backend does not write parameters whose values did not change; asserted for the discrete parameters (gait, jumping, grounded).

**Degraded and absent cases**

- **AC-12.** A linked instance with no usable backend (no Animator) logs a single warning for that instance and then stays silent for later frames, and the character's ECS animation state keeps updating. A swapped-in instance with no usable backend warns once more. When the character is destroyed, the per-instance bookkeeping is released and a later character on the same world is unaffected. (Closes 09-backend § handoff: the warn-once and trim paths are untested.)
- **AC-13.** Every S1 lifecycle outcome still holds: skin swap relinks the new instance, a return to the default skin spawns the default prefab, and destroying a character leaves no cleanup shell. The S1 EditMode and PlayMode animation tests pass unchanged except where their read-presentation helper is pointed at the new contract.

**Measurement (D-1)**

- **AC-14.** Main-thread animation cost for 150 simultaneously animated characters moving continuously is recorded before the refactor. The record states the figure, the machine, Editor or player build, the scene or test used, and the number of frames sampled.
- **AC-15.** The same measurement is recorded again after the refactor, under identical conditions, and the report states both figures and their difference. There is no pass or fail threshold and no scale slice is raised automatically; the human decides from the two figures. 

## Out of scope

Each with a reason.

- Any non-Animator backend implementation. D-2 asks for the seam, not a second backend; the test double is the proof.
- Strafe and lock-on behaviour. S4 owns it. S2 only keeps its state fields mapped, so S4 does not have to reshape the contract.
- NPC and population tests at 30 and 150. S3 owns them. AC-9 only removes the player and camera coupling that would block S3.
- Combat layers, clip events and root motion (S5, S6). They will extend the contract; S2 must not pre-build them.
- Asset, prefab, package and shader changes (S7, S8, D-2).
- Rewriting `CHARACTER_ANIMATION_SETUP.md` (S9). Docs lane reconciles at close-out.
- A budget threshold, a pass or fail on cost, and a conditional scale slice (animator culling, update-rate throttling, change-gating as a separate slice). Replaced by D-1. Change-gating inside AC-11 stays: it is the brief's per-frame cost item, not a scale slice.
- Input fragility around `Keyboard.current` (recon problem 15). Not animation; routed to debt by the producer.
- S3 merging into S2. The producer's call at S2 close, not this story's.

## Test plan

Reuse, do not rebuild: `CharacterAnimationEditModeWorld` (EditMode, real `PostEntityLifecycleGroup`) and `CharacterAnimationPlayModeHarness` (PlayMode, real Animator, in-memory controller, real Viking prefabs for the P4 pattern). The harness's write-state and read-presentation helpers are where the test double plugs in.

- **State update characterization** (new fixture, EditMode, `Assets/Tests/EditMode/Animation/`): AC-1. Idle, each gait band including the exact boundary speeds, jump ascent, fall duration, landing edge, input-phase edges (pressed, held, tapped), movement start. Pins today's behaviour including the odd duplicate band in recon problem 4. Written and run green on unmodified code first.
- **Animator parity** (PlayMode, `Assets/Tests/PlayMode/Animation/`): AC-2. Same scripted sequence through the real Viking Animator; record parameter values before the refactor and assert them after. Use discrete parameters; the smoothed move speed needs a stated tolerance, as the S1 design noted.
- **Contract and mapping** (EditMode and PlayMode): AC-3, AC-4, AC-5. Test double receives the sequence with no Animator present; both backends receive the same sequence; a field-by-field check that every state field is mapped or retired.
- **Single source of speed** (EditMode): AC-6. Two maximum speeds, gait and normalised speed, and equality with AC-1 recordings at the default.
- **Authoring** (EditMode bake test, or a recorded bake if a bake test is not practical in this project): AC-7. Say which, in the test lane's report.
- **Ordering and independence** (EditMode, real group): AC-8, AC-9, AC-10. Frame-N movement visible in frame N; no owner player, no camera; player without orbit camera.
- **Change-gating** (EditMode with the test double, PlayMode for the Animator): AC-11. Unchanged frames produce no writes.
- **Degraded bridge** (EditMode, extends the S1 bridge fixture): AC-12. Warn-once on an Animator-less instance, a second warning on a swap to another Animator-less instance, no leaked bookkeeping after destroy. Count log lines by captured log, not by reading private state.
- **S1 regression** (existing fixtures): AC-13. The ten S1 tests plus the green control must stay green.
- **Measurement** (not a pass or fail test): AC-14, AC-15. A scene or PlayMode scenario with 150 characters and a profiler marker or timer recorded to the run artifact. Assert only that the scenario ran and produced a figure (150 characters existed, N frames sampled), never a time.
- Invariants worth a dedicated regression test: gait boundary speeds (AC-1, AC-6); same-frame ordering (AC-8); zero writes on unchanged state (AC-11).
- Mechanical gates for every ticket: `dotnet build Impact.sln` clean, `Run-UnityTests.ps1 -Platform EditMode -CoreOnly`, and PlayMode `-CoreOnly` (the slice reaches runtime flow). Run by the human or the integration gate, not self-invoked by the lane.

## Tickets

Ordered, one lane's worth each. Nothing in this list tells anyone to commit or to run a gate on their own work and mark it done. The human commits; the gates are dispatched by the orchestrator. Design (tech lead DESIGN) runs after the human approves this story and before T-3; it is a dispatch, not a ticket here.

- **T-1 Characterization tests for the state update (test lane).** AC-1, AC-2 (the before side), recorded expected values. Must be run against unmodified production code and be green. No production code changes. Precedes every other ticket that touches production code.
- **T-2 Baseline measurement at 150 characters (test lane).** AC-14. Builds the 150-character scenario on the existing fixtures and records the figure under the OD-3 conditions. No production change. Can run in parallel with T-1; both finish before T-3.
- **T-3 Contract, mapping and single sources (backend lane, after design).** AC-3 through AC-7. The seam, the one speed source, the retired or mapped fields, one authoring path. Design fixes the shapes; this ticket meets them.
- **T-4 State system: ordering, independence, change-gating (backend lane, after design).** AC-8 through AC-12. Explicit update order, no player or camera requirement, cost reductions, and the warn-once behaviour carried onto the new contract. Depends on T-3.
- **T-5 Contract, ordering, gating and degraded-case tests (test lane).** AC-3 through AC-13 not already covered by T-1. Can start after design (the test double needs the contract) and finishes alongside T-3 and T-4. Includes the S1 regression run.
- **T-6 Post-refactor measurement and report (test lane).** AC-15. Repeats T-2 under identical conditions and writes both figures and the difference into the run artifact. Depends on T-3 and T-4. If OD-1 is taken, this and T-2 form the second half of the split.

Docs lane reconciles `athena.shared/PACKAGE_DOCUMENTATION.md` and the setup doc at close-out from the actual diff; it is not a ticket here, and nothing here writes any index or inventory.
