REPORT 2026-10-07-s2-animation-bridge-contract/03
status:      DONE
verdict:     NONE

changed:
  - Impact/Assets/Tests/EditMode/Impact.EditModeTests.asmdef — added references Athena.CharacterController.Runtime, Unity.CharacterController, Unity.Physics (CS0012 on ColliderKey)
  - Impact/Assets/Tests/PlayMode/Impact.PlayModeTests.asmdef — same three references added
  - Impact/Assets/Tests/EditMode/Animation/CharacterAnimationStateEditModeWorld.cs — new fixture, real CharacterAnimationStateUpdateSystem driven by hand at fixed 1/60 s
  - Impact/Assets/Tests/EditMode/Animation/CharacterAnimationStateUpdateEditModeTests.cs — new, 34 EditMode cases pinning today's state output (T-1a, T-1b)
  - Impact/Assets/Tests/PlayMode/Animation/CharacterAnimationPlayModeHarness.cs — additive helpers only, see handoff (whole-state write, ReadAnimatorFloat, CreateMovingCharacter, state system, bridge-off switch)
  - Impact/Assets/Tests/PlayMode/Animation/CharacterAnimationMappingPlayModeTests.cs — new, 12 PlayMode tests, state to Animator parameters on the real Viking prefab and AC_Polygon_Masculine (T-1d)
  - Impact/Assets/Tests/PlayMode/Animation/CharacterAnimationCostMeasurement.cs — new, 2 PlayMode tests, the T-2 scenario (A, B, C-on, C-off, three repeats each)

verification:
  command:   dotnet build Impact.sln; Run-UnityTests.ps1 EditMode -Filter Impact.EditModeTests.Animation; PlayMode -Filter Impact.PlayModeTests.Animation; EditMode -CoreOnly; PlayMode -CoreOnly
  result:    PASS
  detail:    build 0 errors. EditMode Animation 36/36. PlayMode Animation 19/19. EditMode -CoreOnly total=82 passed=82 failed=0. PlayMode -CoreOnly total=22 passed=22 failed=0 on the last two runs; the first run was 21/22 (StartupReproPlayModeTests timeout, passed alone and on both reruns, see risks)

contract_notes:
  - Test asmdefs now reference Athena.CharacterController.Runtime, Unity.CharacterController and Unity.Physics; the plan named the first two only, Unity.Physics came from CS0012
  - Order 05 must extend CharacterAnimationPlayModeHarness.SetBridgeEnabled to also disable the new presentation system (plan § Measurement harness, T-6)
  - Mapping tests write both MoveSpeed and MoveSpeedNormalized from a local constant 7 and read no CharacterAnimatorSync field, so they compile and hold on both sides of the refactor

pack_corrections:
  - capabilities/testing.md § Which packages a test can see — the table lists no Unity.Core/TimeData source; add: "TimeData is in namespace Unity.Core inside the Unity.Entities assembly, no extra reference; use World.SetTime(new TimeData(elapsed, dt)) before SystemHandle.Update"
  - capabilities/testing.md § Gotchas — add: "Run-UnityTests.ps1 run in the foreground did exit after Unity.exe ended on every run here (exit code = Unity's); the prior-run gap did not reproduce when output is piped. TestResults-*.xml are tracked in git and show as modified after every run"

handoff:
  - New EditMode fixture CharacterAnimationStateEditModeWorld (Impact.EditModeTests.Animation): CreateCharacter(), Step(entity, relativeVelocity, isGrounded, moveVector), Step(entity, frames, ...), FixedDeltaTime. Characters carry a null OwnedByPlayerEntity because the query needs it today
  - New EditMode tests CharacterAnimationStateUpdateEditModeTests; order 05 replaces MoveSpeedNormalized_Characterization_AssumedRunSpeedSix with MoveSpeedNormalized_FollowsSpeedReference
  - Test order 02 is expected to turn red: Impact.EditModeTests.Animation.CharacterAnimationStateUpdateEditModeTests.MoveSpeedNormalized_Characterization_AssumedRunSpeedSix, cases (3f,0.5f) and (6f,1f) only; cases (0f,0f) and (9f,1f) stay green because saturate gives the same value for 6 and 7
  - Every other new test should stay green after order 02; any other red is a regression (the gait boundaries and walk flag included, per D-4)
  - PlayMode harness additions: SetAnimationState(entity, CharacterAnimationState), static ReadAnimatorFloat, CreateMovingCharacter(prefab), AddStateUpdateSystem(), StepStateSystem(dt), SetBridgeEnabled(bool)
  - New PlayMode tests CharacterAnimationMappingPlayModeTests (Mapping_*) and CharacterAnimationCostMeasurement (Measure_MovingCharacters_BridgeOnThenOff, Measure_IdleCharacters_BridgeOnThenOff); order 05 re-runs the latter unchanged apart from the SetBridgeEnabled extension
  - Gait constants observed and pinned: 0.1 idle; 0.11 and 1.74 gait 1 walking; 1.75, 4.99, 5.0, 7.99 gait 2; 8.0 and 12 gait 3. Speed 5.0 is gait 2, as the plan predicted. No computed value differed from the prediction
  - Not pinned on purpose: no-owner and no-camera behaviour (T-1c); MoveSpeedNormalized outside the T-1b test; JumpTriggered is not mapped to the Animator so the mapping tests do not cover it
  - The tdd skill was not called: the order fixed the seams (real system, real prefab, no fake chosen)
  - Reading the figures: log lines are in Unity's console output, grep "[S2-MEASURE]"; copied below under § Before-side measurement
  - Generated meta files and TestResults-EditMode.xml / TestResults-PlayMode.xml / Packages/packages-lock.json show as modified; the first two are run output, the lock file was touched by Unity, none by hand

skill_calls:
  - mattpocock-skills:tdd — not called, the order fixed real system and real prefab seams so no fake-versus-real choice was made
  - mattpocock-skills:diagnosing-bugs — not called, no test resisted diagnosis; the one PlayMode red passed alone and on two reruns

risks:
  - Flake: StartupReproPlayModeTests.MainBootstrap_CreatesLocalPlayerAndCharacter failed once in the first full PlayMode -CoreOnly run (10 s WaitForCondition) and passed alone and in two further full runs. The failing run followed a script recompile; I did not isolate the cause, so I cannot rule out interaction with the new measurement tests
  - Cost figures understate Animator work: every Animator reports cullingMode CullUpdateTransforms and batchmode PlayMode has no visible renderers, so animators are likely culled. The A minus B gap is therefore mostly the sync pull and the state system. I left culling untouched per the plan and D-1; the human should judge the figure with this in mind
  - Frame times are about 1 to 2 ms and the first A repeat is a visible outlier, so per-run spread is comparable to the A minus B gap of about 0.4 ms; read the three repeats, not one
  - GC allocated per frame reads about 529 bytes in every run including bridge-off, so the recorder shows a constant floor and not the animation path; treat it as non-informative
  - The wall-clock delta between coroutine resumptions includes the test's own per-frame driving (array copy of 150 bodies) in both A and B, so it cancels in A minus B but sits inside each absolute figure
  - Mapping tests wait for the smoothed MoveSpeed on real frame time (up to 10 s, converges in under 1 s here); a stalled editor could turn that into a timeout failure
  - Unity.Physics was added to both test asmdefs beyond the plan's two named references, as the plan allows on CS0012; an EditMode-only check would not have caught the PlayMode need

## Orchestrator brief
- Order 1 done: T-1a/b/d tests and the T-2 measurement exist and are green on unmodified production code.
- EditMode Animation 36/36, PlayMode Animation 19/19, EditMode -CoreOnly 82/82, PlayMode -CoreOnly 22/22 (first run 21/22, one flaky pre-existing test, see risks).
- Order 02 should turn red exactly: CharacterAnimationStateUpdateEditModeTests.MoveSpeedNormalized_Characterization_AssumedRunSpeedSix, cases 3f and 6f.
- Section "Before-side measurement" holds the figures, machine, Editor version, frame and character counts; caveat: animators likely culled in batchmode.
- No production file was touched; asmdefs gained Unity.Physics beyond the plan on CS0012.

## Before-side measurement

Machine: AMD Ryzen 7 7800X3D 8-Core, NVIDIA GeForce RTX 4080 SUPER. Unity 6000.4.0f1, Editor PlayMode via batchmode (-runTests), dev machine, Editor otherwise idle. 150 characters, real Viking_BaseSkin_Visuals.prefab and AC_Polygon_Masculine, cullingMode CullUpdateTransforms (unchanged), 60 warm-up frames, 300 sampled frames, 3 repeats per scenario, unmodified production code. Times are wall-clock ms per frame (mean / median / p95). No time is asserted anywhere.

| scenario | repeat | mean | median | p95 |
|---|---|---|---|---|
| A moving, bridge on | 1 | 1.763 | 1.730 | 2.339 |
| A moving, bridge on | 2 | 1.369 | 1.328 | 1.594 |
| A moving, bridge on | 3 | 1.414 | 1.328 | 1.813 |
| B moving, bridge off | 1 | 1.116 | 1.065 | 1.483 |
| B moving, bridge off | 2 | 0.969 | 0.934 | 1.212 |
| B moving, bridge off | 3 | 0.972 | 0.924 | 1.230 |
| C idle, bridge on | 1 | 1.302 | 1.264 | 1.529 |
| C idle, bridge on | 2 | 1.290 | 1.264 | 1.463 |
| C idle, bridge on | 3 | 1.439 | 1.404 | 1.774 |
| C idle, bridge off | 1 | 0.953 | 0.898 | 1.253 |
| C idle, bridge off | 2 | 0.979 | 0.887 | 1.484 |
| C idle, bridge off | 3 | 0.979 | 0.940 | 1.248 |

Reading: A minus B by repeat mean is 0.647, 0.400, 0.442 ms; idle on minus off is 0.349, 0.311, 0.460 ms. Log line format: `[S2-MEASURE] {"scenario":...,"meanMs":...}`, one per run, also carrying processor, gpu, unityVersion, controller, cullingMode, bridge state, characters and frame counts.
