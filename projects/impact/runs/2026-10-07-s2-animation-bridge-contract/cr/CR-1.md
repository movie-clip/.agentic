CHANGE REQUEST CR-1 — 2026-10-07-s2-animation-bridge-contract
lane:        test
severity:    BLOCKING
round:       1 of 2
raised by:   C:\projects\investments\.agentic\projects\impact\runs\2026-10-07-s2-animation-bridge-contract\06-integration.md § Skill-call fidelity
scope fence: C:\projects\investments\.agentic\projects\impact\runs\2026-10-07-s2-animation-bridge-contract\05-test.md (skill_calls and risks only); Impact/Assets/Tests/PlayMode/Animation/** and Impact/Assets/Tests/EditMode/Animation/** only if the skill call changes a test. No production file, no asmdef.

Finding. 05-test.md `risks` carries the bullet "Shipped deviation tested as-is: CharacterAnimatorSync keeps a settle-only Update (order 04). Mapping_* tests and AC-5 MoveSpeed rely on it." and the bullet "Mapping and AC-5 tests wait up to 10 s of real time for the smoothed MoveSpeed to converge." Together they say the test lane accepted test-to-production coupling: those tests only pass because production keeps a private Update that finishes the MoveSpeed smoothing, and they poll real time to observe it. The same report's `skill_calls` says `mattpocock-skills:tdd` was "not called", with the reason "no fake-versus-real choice was open". The pack (capabilities/testing.md § Definition of done) names two triggers, and the second is "accepted test/production coupling". The report contradicts itself: the coupling is named, the call that the coupling requires is denied.

Why it matters. The coupling is exactly where a later change to the adapter (for example the CR-2 fix, or S5/S6 moving smoothing) will turn these tests red or flaky for a reason that is not a behaviour change. The tdd call is where that choice (assert the converged Animator value through real frames, versus assert the target the adapter was given) is supposed to be made on purpose, and recorded.

What would satisfy it. Call `mattpocock-skills:tdd` for the coupled tests (Mapping_* MoveSpeed cases, EveryMappedField_ReachesItsAnimatorParameter MoveSpeed branch), apply its guidance, and record the call in 05-test.md `skill_calls` with what it changed or confirmed. If it confirms the current tests, say so in the one line; if it changes a test, change only that test, keep the full -CoreOnly runs green and update the counts in `verification.detail`. Do not add new tests beyond that, and do not edit production code.
