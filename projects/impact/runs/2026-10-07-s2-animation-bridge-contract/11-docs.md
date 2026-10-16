REPORT 2026-10-07-s2-animation-bridge-contract/11
status:      DONE
verdict:     NONE

changed:
  - C:\projects\impact\Impact\CHARACTER_ANIMATION_SETUP.md — staleness note refreshed; diagram, authoring, CharacterAnimatorSync settings, How It Works, state table, update order, files list, example prefab, next steps, FAQ, three troubleshooting lines and two code samples corrected to the push model
  - C:\projects\impact\Impact\CHARACTER_ANIMATION_SETUP.md — new "Animation Speed Reference" subsection: MaxSpeed default 7, saturate normalisation, gait boundaries 1.75 and 8 scaled by MaxSpeed/7, not GroundMaxSpeed
  - C:\projects\impact\Impact\Packages\athena.shared\PACKAGE_DOCUMENTATION.md — flow step 6 corrected; new "Character animation" flow section (push model, ordering, contract, speed reference, authoring, gating); known-issues bridge bullets updated for Backend, HasApplied, no-controller case
  - C:\projects\impact\Impact\ARCHITECTURE_REVIEW.md — hybrid visual section: push-model strengths, three weaknesses (single backend, isStrafing hard-coded, speed reference vs GroundMaxSpeed), animation test coverage line
  - C:\projects\impact\Impact\Tools\TESTING.md — Core fixture list gains the Animation EditMode and PlayMode fixtures and the namespace filters
  - C:\projects\investments\.agentic\projects\impact\capabilities\testing.md — applied corrections 1, 2, 4, 5: TimeData note, script exit-code note reconciled to the code, Is.AnyOf, dotnet build vs new test files
  - C:\projects\investments\.agentic\projects\impact\capabilities\backend.md — applied correction 3: Git Bash forward-slash bullet in Definition of done
  - C:\projects\investments\.agentic\projects\impact\runs\2026-10-07-s2-animation-bridge-contract\pack-corrections.md — state APPLIED, per-item outcome recorded

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Docs lane has no Bash and the order's verification was NONE. Claims were read against CharacterAnimatorSync.cs, CharacterAnimationPresentationSystem.cs, CharacterAnimationStateUpdateSystem.cs and Run-UnityTests.ps1.

contract_notes:
  - CHARACTER_ANIMATION_SETUP.md is still partly stale (S9 rewrite): example Animator controllers, blend-tree walkthroughs, parameter names Speed/MoveX/MoveZ/Jump/VerticalVelocity and the troubleshooting hints naming them
  - PLAYER_SESSION_CHARACTER_FLOW.md was named in the plan's consumer table as describing the pull model; it was outside this order's scope and was not checked or edited
  - CharacterAnimationAuthoring.cs and its .meta are not removed (no delete tool). Docs describe it as an obsolete stub; when the human git rm's it, the "obsolete stub" lines in the three repo docs and two authoring tests need to follow
  - PACKAGE_ARCHITECTURE.md was not in scope and was not checked for animation statements

pack_corrections:
  - none

handoff:
  - Human close-out: git rm Impact/Packages/athena.shared/Runtime/Components/Authoring/CharacterAnimationAuthoring.cs Impact/Packages/athena.shared/Runtime/Components/Authoring/CharacterAnimationAuthoring.cs.meta once the stub has shipped
  - Human close-out: TestResults-EditMode.xml and TestResults-PlayMode.xml are tracked and modified by runs; revert or commit deliberately
  - Human close-out: the 150-character cost figure (0.496 ms before, 0.218 and 0.122 ms after, noise near 0.1 ms) is for the human to judge; it is deliberately not recorded in any repo doc (guardrail 4)
  - Next docs order: S9 rewrite of CHARACTER_ANIMATION_SETUP.md, and a check of PLAYER_SESSION_CHARACTER_FLOW.md and PACKAGE_ARCHITECTURE.md for the pull model

skill_calls:
  - none

risks:
  - Pack correction 2 was reworded, not applied verbatim: the script pipes Unity.exe through Out-Default (Run-UnityTests.ps1:71-79), so the "prior-run gap" no longer exists in the code. The pack held no gap bullet, so nothing contradicts it
  - Pack correction 4 (Is.AnyOf) could not be checked against NUnit in PackageCache. It rests on the test lane's compile error; the tests no longer use it
  - Pack correction 3 sits in backend.md's Definition of done as the entry named, though it is a shell fact rather than a done criterion. testing.md Running the suite shows .\Tools\ commands from PowerShell and was left alone
  - Doc statements about the HasApplied-on-controller-less behaviour and the settle-only Update reflect the shipped code the integration gate accepted; a reviewer may still want a different fix (04 risks)
  - The human's uncommitted athena.contentmanagement WIP and GameAssetLoad.cs changes were not documented, per the non-goal
