CHANGE REQUEST CR-2 — 2026-10-07-s2-animation-bridge-contract
lane:        backend
severity:    SHOULD_FIX
round:       1 of 2
raised by:   C:\projects\investments\.agentic\projects\impact\runs\2026-10-07-s2-animation-bridge-contract\06-integration.md § Ruling: settle-only Update
scope fence: Impact/Packages/athena.shared/Runtime/Components/Character/CharacterAnimatorSync.cs only. No other production file, no test, no asmdef.

Finding. In CharacterAnimatorSync.cs, `Apply` sets `targetMoveSpeed` (line 129) and then calls `StepSmoothing()` (line 130). `StepSmoothing` returns early at the one-step-per-frame guard (lines 201-205) and `settling` is recomputed only after that guard (line 216). So when `Apply` arrives in a frame where the settle `Update` already stepped, the new target is stored but `settling` keeps the value computed against the old target.

Failure sequence. Frame N: the MonoBehaviour `Update` runs first (plan section Ordering: the Update phase runs before the ECS group), the last settling step snaps the value to the old target and sets `settling = false`. Same frame N: `Apply` receives a state with a different `MoveSpeedNormalized`, stores the new target, skips the step (guard), and leaves `settling` false. Frame N+1 on: `Update` returns at `!settling` and `Apply` is no longer called while the state is steady. The Animator `MoveSpeed` parameter stays at the old target for as long as the character keeps a steady state, where the character should have approached the new one.

Why it matters. It needs a single final change of target landing on the frame a settle finishes, so it is rare, but the result is a frozen locomotion blend with no log line, and the code path exists only because of the declared deviation. The fix is one line and nothing in the current tests covers it.

What would satisfy it. After `targetMoveSpeed = state.MoveSpeedNormalized;` in `Apply`, recompute `settling = currentMoveSpeed != targetMoveSpeed;` (or move that assignment out of the guarded part of `StepSmoothing`), so the settle `Update` always knows the current target. Keep the one-step-per-frame guard. `dotnet build Impact.sln` clean, and EditMode and PlayMode `-CoreOnly` runs stay green. A regression test for the sequence is a separate order to the test lane; this request does not ask for one.
