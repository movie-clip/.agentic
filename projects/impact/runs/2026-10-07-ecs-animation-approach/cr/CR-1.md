CHANGE REQUEST CR-1 — 2026-10-07-ecs-animation-approach
lane:        backend
severity:    SHOULD_FIX
round:       1 of 2
raised by:   C:\projects\investments\.agentic\projects\impact\runs\2026-10-07-ecs-animation-approach\08-integration.md § Ruling on 07 risks item 1
scope fence: Impact/Packages/athena.shared/Runtime/Systems/CharacterAnimationBridgeSystem.cs only. No tests, no other system, no component, no .asmdef.

Finding. In CharacterAnimationBridgeSystem.TryLink (the Debug.LogWarning branch, about line 75), an instance with no Animator and no CharacterAnimatorSync logs a warning and returns false. Neither pass records that outcome. Pass 1 re-enters the same character every frame, because no marker is added. Pass 2 does the same for a swapped-in instance without an Animator, because the marker still points at the destroyed old instance. So the warning fires once per frame per affected character, and each call also builds an interpolated string and runs two GetComponentInChildren lookups.

Consequence. Before this change that case was silent. A skin prefab that lost its Animator, or an NPC visual without one (S4), would now write 60 warnings per second per character into the console and Editor.log. That buries the real diagnostics and conflicts with 05 § S2 seam constraint (no per-frame allocation). Nothing in the current suite hits it (0 occurrences in the EditMode and PlayMode logs), so this is a misconfiguration path, not a live failure. Hence SHOULD_FIX, not BLOCKING.

What satisfies it. The warning is emitted once per spawned instance, not once per frame. Keep link ownership in this system: remember the last instance already warned about in a private field of the system (for example one GameObject reference per entity, or a small Dictionary<Entity, GameObject> trimmed when the entity is no longer a character). Do not add a component, do not touch CharacterSkinChangeSystem, and do not change the marker's shape. Pass 1 and pass 2 link behaviour stays exactly as it is. Existing EditMode and PlayMode Core tests must stay green; no new test is required.
