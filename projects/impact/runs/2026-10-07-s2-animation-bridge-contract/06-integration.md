REPORT 2026-10-07-s2-animation-bridge-contract/06
status:      DONE
verdict:     CHANGES_REQUESTED

changed:
  - none

verification:
  command:   cd Impact; dotnet build Impact.sln; Run-UnityTests.ps1 -Platform EditMode -CoreOnly; Run-UnityTests.ps1 -Platform PlayMode -CoreOnly (Git Bash, forward slashes, run sequentially)
  result:    PASS
  detail:    dotnet build 0 errors, 17 warnings (MSB3277 only). EditMode -CoreOnly total=164 passed=164 failed=0. PlayMode -CoreOnly total=26 passed=26 failed=0. Counts read from the results XML test-run element. Anchor: results XML, not the engineers' reports.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - CR-1 BLOCKING, test lane: C:\projects\investments\.agentic\projects\impact\runs\2026-10-07-s2-animation-bridge-contract\cr\CR-1.md (05-test.md skill_calls denies tdd while risks name accepted test/production coupling). See § Skill-call fidelity
  - CR-2 SHOULD_FIX, backend lane: C:\projects\investments\.agentic\projects\impact\runs\2026-10-07-s2-animation-bridge-contract\cr\CR-2.md (settle Update can leave Animator MoveSpeed stuck after a final target change). Goes to the ledger Open table. See § Ruling: settle-only Update
  - Ruling for the ledger: the settle-only Update deviation is ACCEPTED, subject to CR-2 being recorded. See § Ruling: settle-only Update
  - Ruling for the ledger: HasApplied set true on a controller-less Animator is ACCEPTED as a documented limitation, not a CR. See § Ruling: HasApplied on a controller-less Animator
  - Reviewer: AC-6 is built to D-6 (reference 7, not GroundMaxSpeed 10), AC-7 is by construction only, AC-10 is thin by design. All three are declared in 02, 05 and the ledger and are not engineering defects
  - After CR-1 only the test lane re-runs; the engineering verdict re-runs on this gate alone (gates.md § 4). No production file changes in CR-1, so the build and test counts above stand unless CR-2 is also dispatched

skill_calls:
  - mattpocock-skills:codebase-design — called, before writing the reuse and consistency judgments below. Applied: the ICharacterAnimationBackend seam has two adapters (Animator, double), so it is real; the settle Update gives the adapter a second driver the interface does not mention, which is where CR-2 lives

risks:
  - The settle Update fires in the MonoBehaviour Update phase, and the plan's ordering text says that phase runs before the ECS group. I did not run a frame-order probe; CR-2 rests on that stated order and on the code at CharacterAnimatorSync.cs:129-130 and 201-216
  - No test covers the CR-2 sequence (Update snap and Apply target change in one frame). The 118 EditMode Animation tests run Apply twice per Time.frameCount at most and cannot reach it
  - OnEnable sets cacheValid false without telling the presentation gate. A disabled and re-enabled sync gets no rewrite until the state changes. No code in Packages toggles a visual's active state or the sync, so it is latent; same class as the HasApplied ruling
  - Human WIP (athena.contentmanagement/**, GameAssetLoad.cs, packages-lock.json) built and tested clean with S2 in the tree, so it did not affect these counts. Not judged
  - TestResults-EditMode.xml and TestResults-PlayMode.xml are tracked and my runs rewrote them again (164 and 26). Expected run output, not S2 work
  - Cost figures (05-test.md § Cost measurement) are consistent in direction across all six moving and six idle repeats but their size is within the control-run drift. D-1 says measure only; I judged only that the figures are recorded with the noise and culling caveats
  - Skill-call check on 03-test and 04-backend found no contradiction. 03 risks only note real-time polling of a smoothing the order did not own, and 04 names no tradeoff that a skill gates
  - dotnet build here ran on csproj files Unity had regenerated, so it saw the new files. A fresh clone would hit CS0246 until Unity regenerates them, as 04-backend already noted

## Orchestrator brief
- Verdict: CHANGES_REQUESTED. Build 0 errors. EditMode -CoreOnly 164/164, PlayMode -CoreOnly 26/26, read from the results XML.
- Engineering is sound: contract, ordering, gating, speed source and authoring match 02-technical-plan.md. No asmdef edited in Packages; guardrails 1, 2, 5 hold.
- CR-1 (BLOCKING, test lane): 05-test.md skill_calls says tdd not called while its risks accept test/production coupling. Record the call, adjust only coupled tests if it says so.
- CR-2 (SHOULD_FIX, backend lane): settling flag is not recomputed in Apply, so Animator MoveSpeed can freeze after a final target change. One line. Goes to Open, does not hold the slice.
- Ruling: settle-only Update ACCEPTED (plan missed that gating strands the smoothing). Ruling: HasApplied on controller-less Animator ACCEPTED, limitation.
- All 11 consumers in plan § Consumers checked; none outside the table. No dispatch is blocked. Re-run this gate only after CR-1.
- Sections: Contract alignment · Ruling: settle-only Update · Ruling: HasApplied on a controller-less Animator · Design conformance and consumers · Guardrails and graph · Coverage adequacy · Skill-call fidelity.

## Contract alignment

Compared 02-technical-plan.md § Contract against the code, field by field.
- `ICharacterAnimationBackend.Apply(in CharacterAnimationState)`: one method, namespace `Athena.Shared.Components`, matches exactly.
- `CharacterAnimationBridgeInitialized`: `LinkedInstance`, `Backend`, `LastApplied`, `HasApplied` as specified, same class and file. G1 holds in both bridge passes (`HasApplied = false` set with `Backend`). G2 holds: only the bridge assigns `Backend` for GameObject links, only the presentation system writes `LastApplied` and sets `HasApplied = true`. G3 holds: pass 1 requires no marker and pass 2 requires `HybridGameObjectSpawned`, so an attached double is left alone.
- `CharacterAnimationState`: field names and order unchanged, 24 fields. `Equals` covers all 24 by hand (`MoveDirection` as x and y), no memcmp. `CreateDefault()` returns the specified neutral values.
- `CharacterAnimationContract.Fields`: 24 rows in field order, 14 Parameter, 5 OptionalParameter, 1 EcsOnly, 3 Retired, naming traps (`MoveSpeed` parameter carries `MoveSpeedNormalized`, `IsStrafing` Float, `IsMoving` inverted as `IsStopped`) as specified.
- `CharacterAnimationSpeedReference`: `DefaultMaxSpeed` 7, `MaxSpeed <= 0` means default. State system uses `maxSpeed / 7` as the scale of 1.75 and 8, `MoveSpeedNormalized = saturate(speed / maxSpeed)`, `AssumedRunSpeed` and `RunSpeedThreshold` deleted. `CharacterAuthoring.AnimationMaxSpeed` defaults to the constant and the baker adds the component.
- `CharacterAnimatorSync`: passive, no entity or world access, `Initialize()` with no arguments, inspector strings removed. The two deviations from the plan are the settle Update (ruled below) and `showDebug` staying (declared in 04 contract_notes, harmless).
- No backend/frontend mismatch is possible here: there is no client type. The mismatch that could occur is test helpers calling the old `Initialize(Entity, World)`; the build and both test runs show none do.

## Ruling: settle-only Update

Accepted.
- The plan said the adapter has no `Update`. It also said smoothing stays in the adapter and that Apply is never called for an unchanged state. Those two statements cannot both hold: once the state is steady, nothing calls Apply, and the smoothed `MoveSpeed` is still short of its target. 04-backend found this and kept a private `Update` that returns unless smoothing is unfinished. That is the smallest fix that keeps the plan's decisions (smoothing is presentation; nothing else smooths; the gate is backend-agnostic).
- It reads no entity data and does not weaken the seam: `Apply` is still the only way state enters. The deviation was declared in `risks` and the orchestrator brief, which is what the review asked of an engineer who found a better path.
- Alternatives I rejected: a second interface method for settling (the plan forbids a second method), or Animator `SetFloat` damping (changes the damping curve, breaks D-4 for AC-2).
- Cost: one managed Update call per enabled sync per frame. 05-test.md § Cost measurement shows the idle gap fell from about 0.37 ms to about 0.05 ms with this Update in place, so it is not a regression.
- Defect found inside it: CR-2. The one-step-per-frame guard stops `settling` being recomputed when `Apply` follows a settling `Update` in the same frame. SHOULD_FIX because it needs a final target change on the frame a settle completes, but the fix is one line.
- Declared effect "a target change in a settling frame steps one frame later": accepted, one frame is below visible threshold.

## Ruling: HasApplied on a controller-less Animator

Accepted as a limitation, no CR.
- Behaviour: the adapter returns early for a null `runtimeAnimatorController`, the presentation system still records `HasApplied = true`, so a controller assigned later to the same instance gets nothing until the state next changes.
- Reason to accept: a grep over Packages and Assets finds no production code that assigns `runtimeAnimatorController` after spawn (only the test harness, at creation). Every skin change spawns a new instance, and a new instance relinks with `HasApplied = false`. The pre-S2 pull would have recovered, so this is a real change, but it has no live trigger.
- Making the adapter report "not applied" would need a return value on `Apply`, which the plan fixes as `void`. That is a design change for a case nothing exercises. If a feature starts assigning controllers late, it should add the recovery with that feature.
- The warning text says "Animation state is not applied", which tells a developer what to expect. 05 left this untested on purpose, which I agree with: a test would pin a questionable behaviour.

## Design conformance and consumers

- Ordering: `CharacterAnimationStateUpdateSystem` has `[UpdateInGroup(SimulationSystemGroup)] [UpdateAfter(ThirdPersonCharacterVariableUpdateSystem)]`, and that system is in `SimulationSystemGroup` (ThirdPersonCharacterSystems.cs:75-79), so the attribute takes effect. Presentation is in `PostEntityLifecycleGroup` after the bridge, as specified. The cleanup system keeps `UpdateAfter(Bridge)`.
- Gating, both layers present: system-level compare of `LastApplied` in the presentation system, parameter write cache in the adapter with `cacheValid` reset in `Initialize` and `OnEnable`.
- Degraded cases: `TryLink` returns the backend or null with the S1 warn-once map and trim unchanged; the state system does not read the link.
- Authoring: `CharacterAnimationAuthoring` is an `[Obsolete]`, `[AddComponentMenu("")]` stub whose baker only logs an error. GUID grep: neither it nor `CharacterAnimatorSync` is serialised in any prefab, scene, asset or controller.
- Consumers in plan § Consumers: state system, bridge, cleanup, presentation, adapter, both bakers, `athena.charactercontroller`, `athena.gameplay`, `athena.ai` family, EditMode tests, PlayMode tests, four docs. A fresh grep over Packages and Assets finds no other reader of the four types. `athena.charactercontroller` is unedited (git diff empty). The four docs still describe the pull model and are already routed to the close-out docs lane in the ledger.
- Reuse: no `IAspect`; `ComponentLookup.TryGetComponent` replaces the `EntityManager` reads; the presentation query copies the bridge's managed-component query shape; test fixtures were extended additively. Looks like the neighbouring features, not a different codebase.

## Guardrails and graph

- Guardrail 1: no change under `Packages/com.projectdawn.navigation` or `Library/PackageCache`.
- Guardrail 2: no production `.asmdef` changed (git diff on `Packages` shows none). Production gains no reference. `Athena.Shared.Runtime` already referenced `Athena.CharacterController.Runtime` and `Unity.CharacterController`; `athena.charactercontroller` is not edited, so no cycle. The test asmdefs gained `Athena.CharacterController.Runtime`, `Unity.CharacterController` and `Unity.Physics` (the third beyond the plan, from CS0012). No runtime assembly references a test assembly.
- Guardrail 3: build and both Unity runs done above. Guardrail 4: no roadmap document. Guardrail 5: no `Library/`, `Temp/`, `obj/`, `Logs/` or csproj in `git status`.
- The only non-S2 paths in the tree are the human WIP files; not judged.

## Coverage adequacy

- The tests assert the contract, not the implementation. Examples checked: the field-map reflection test fails on a missing, stale or duplicate row; the `Equals` test changes each field in turn; the PlayMode AC-5 test reads every Parameter field back from the real Viking controller by the map's own name and type; the sentinel test would fail if the adapter rewrote an unchanged parameter; the G3 skin-swap test sets no state after the swap.
- The AC-8 sort test is red on the state-first insertion order without the attribute. 05 states this by reasoning, not by run; I agree with the reasoning (no constraint means insertion order is kept).
- Gaps, none blocking: no test for the CR-2 sequence; AC-10 can only show neutral camera values while `isStrafing` is hard-coded false (S4); AC-7 has no real bake (internal API).
- Order of work respected: the one expected-red test was red after order 2 for exactly the two cases named, and replaced in order 3.

## Skill-call fidelity

Set each report's `skill_calls` against the rest of the same report.
- 05-test.md: CONTRADICTION. `risks` says "Shipped deviation tested as-is ... Mapping_* tests and AC-5 MoveSpeed rely on it" and "Mapping and AC-5 tests wait up to 10 s of real time for the smoothed MoveSpeed to converge". That is accepted test/production coupling, which capabilities/testing.md § Definition of done makes a trigger for `mattpocock-skills:tdd`. `skill_calls` says tdd "not called, ... no fake-versus-real choice was open", which answers the first trigger and not the second. Raised as CR-1.
- 03-test.md: no contradiction. Its `risks` note real-time polling, but the production code it polled did not exist yet in changed form, and no coupling choice was made by that order.
- 04-backend.md: no contradiction. Its only skill is diagnosing-bugs, gated on a failed fix, and no fix attempt failed.
- 02-technical-plan.md (my own earlier pass) recorded codebase-design as called.
