REPORT 2026-10-07-ecs-animation-approach/03
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only research

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Installed stack is Entities 6.4.0 + Entities Graphics 6.4.0 + CharacterController 1.4.1 + URP 17.4.0; Entities 6.4.0 changelog (2025-10-16) says only "Package is now a core package embedded in Unity" (the 1.4.x line renumbered). Impact/Packages/manifest.json; Library/PackageCache/com.unity.entities@d66668920c3f/CHANGELOG.md
  - Latios Framework 0.16.1 (2026-09-26) targets Entities 1.4.8 and editor 6000.3.8f1, and its README says "Entities 6.4.0 compatibility is not supported at this time." https://github.com/Dreaming381/Latios-Framework/blob/master/README.md
  - Latios author, 2026-06-15: "the reason 6.4+ is not supported ... Fixing this means breaking 6.3 LTS compatibility. I intend to resolve this when the framework eventually moves forward to Unity 6.7 LTS." https://github.com/Dreaming381/Latios-Framework/issues/74
  - Rukhanka Animation System 2 v2.9.1 (2026-07-02/03) fixes "Unity 6000.4+ warnings related to the new EntityID usage" and 6000.6 errors. Its Asset Store page lists URP as compatible and Unity 6000.3.18f1 as the original upload version. https://docs.rukhanka.com/changelog ; https://assetstore.unity.com/packages/tools/animation/rukhanka-animation-system-2-298480
  - Rukhanka bakes standard Animator Controllers, supports Humanoid and Generic rigs, all blend tree types, sub-state machines, override/additive layers, root motion and events. Unsupported: Write Defaults, Mirror, the clip-import Mask, and Mecanim IK pass (it has its own IK). https://docs.rukhanka.com/feature_support_tables
  - Rukhanka 2.6.0 (2025-12-08) dropped support for Entities Graphics deformation and uses its own compute deformation. Meshes need a shader that includes the "Rukhanka Deformation" subgraph plus the _DeformedMeshIndex and _DeformationParamsForMotionVectors per-instance params. https://docs.rukhanka.com/changelog ; https://docs.rukhanka.com/shaders_with_deformations
  - Only Rukhanka's CPU engine supports IK, root motion, blend shapes, bone writeback and physics bodies on bones. GPU-engine attachments need a GPU Attachment shader and authoring. https://docs.rukhanka.com/animation-engines ; https://docs.rukhanka.com/physics ; https://docs.rukhanka.com/bone_attachments
  - Entities Graphics 6.4.0 marks skinning/deformations "Experimental" and says to use the Compute Deformation Shader Graph node. Known limits: no frustum culling of deformation, bounds not resized, no sub-graphs, no blend-shape frames. Library/PackageCache/com.unity.entities.graphics@2ad17cac7401/Documentation~/mesh_deformations.md
  - Animator is not on the Entities Graphics companion-component list, so baking strips it. The official hybrid pattern is a UnityObjectRef/managed reference to a GameObject prefab that a system instantiates at runtime. Library/PackageCache/com.unity.entities@d66668920c3f/Documentation~/reference-unity-objects.md ; .../com.unity.entities.graphics@2ad17cac7401/Documentation~/companion-components.md
  - Unity's own CharacterControllerSamples Platformer (repo pushed 2026-08-24) animates through PlatformerCharacterHybridSystem, which instantiates a mesh prefab with an Animator and copies LocalToWorld into the GO each frame. https://github.com/Unity-Technologies/CharacterControllerSamples/blob/master/Platformer/Assets/Scripts/Character/PlatformerCharacterHybridSystem.cs
  - Unity's new animation system is still unreleased. The last official status (2025-07-29) says it ships in the Unity 6 lifecycle with no date, and "we plan to support ECS Skinned Mesh Renderer as soon as we can but cannot commit to a timeline." https://discussions.unity.com/t/animation-status-update-summer-2025/1672386
  - In this project, Synty Characters.fbx for FantasyRivals, Samurai and Vikings, and all Base Locomotion clips, import as Humanoid (animationType 3). Every FBX has optimizeGameObjects 0. Character materials use URP Lit.shader (guid 933532a4...), which is not a deformation-aware Shader Graph. Impact/Assets/PolygonVikings/Models/Characters.fbx.meta ; Impact/Assets/PolygonVikings/Materials/*.mat
  - Each project character visual prefab (Viking_BaseSkin_Visuals, Viking_WarriorSkin_Visuals) holds 6 SkinnedMeshRenderers and 1 Animator. The project already runs the hybrid approach (ECS state, then CharacterAnimatorSync MonoBehaviour, then Animator). Impact/Assets/Content/Characters/Viking/Gameplay/Skins/ ; Impact/CHARACTER_ANIMATION_SETUP.md

skill_calls:
  - none

risks:
  - Rukhanka on 6000.4 is inferred from its 2.9.1 changelog fixing 6000.4+ and 6000.6 issues. No page says "supports Unity 6.4 / Entities 6.4.0" in those words. The Getting Started page still lists Entities >=1.4.3 and Entities.Graphics >=1.4.16 as minimums, and 6.4.0 core packages satisfy that numerically, but nobody has test-imported it on 6000.4.0f1 (UNCONFIRMED).
  - Rukhanka's two docs pages disagree on avatar masks: the feature table marks the clip-import "Mask" unsupported, while the engines page lists avatar masks as supported on both engines. Layer masks are probably supported, but this is UNCONFIRMED.
  - Kinemation's humanoid/Mecanim support was not confirmed from primary docs. The Kinemation README describes clip baking, sampling, masking and IK, and Animator Controller runtimes exist only as community Add-Ons (Mecanim V1/V2), which their README says may be experimental or abandoned. This is moot for 6.4 anyway, because Latios refuses Entities 6.4.0.
  - GPU ECS Animation Baker was last updated as v1.3.6 (2024-04-15) with a 2022.3.24 minimum. Its compatibility with Unity 6.4 is UNCONFIRMED. The release date of GPU Animation Entities PRO v1.4.0 (about 2026-07-28) was derived from "71 days ago", and its supported Unity versions were not stated.
  - No primary source was found about using Synty POLYGON characters with Rukhanka or Kinemation specifically. The Synty-specific gotchas below come from project inspection and general docs (UNCONFIRMED against third-party reports).
  - The Unity Discussions animation category shows no official animation status update after 2025-07-29. Something posted after that may not have been indexed.
  - Asset Store prices are a snapshot from the fetch date (Rukhanka shown at a 50% sale price).

## Orchestrator brief
- `## Options compared`: Six options were compared. On this exact stack (Unity 6000.4 + Entities 6.4.0), only Hybrid Animator (official pattern, already in the project) and Rukhanka 2.9.1 (paid, Mecanim-baking, 6000.4 fixes shipped) are viable today. Latios/Kinemation is NO-FIT (refuses Entities 6.4.0 until a 6.7 LTS move). GPU vertex bakers fit crowds, not a player character (no IK or ragdoll, version compat unconfirmed). Entities Graphics raw deformation is experimental and has no animation layer. Unity's com.unity.animation is dead.
- `## Unity official status`: Unity ships no official ECS animation package. The new animation system is unreleased and undated, ECS SkinnedMeshRenderer support has no committed timeline, and the documented and sampled path is a hybrid GameObject Animator.
- `## Synty POLYGON notes`: Project assets are Humanoid, unoptimized hierarchies with 6 SMRs per character on URP Lit. Every ECS-skinning option needs a material/shader swap to a deformation-aware Shader Graph. Base Locomotion is Humanoid/Mecanim with root-motion clips.
- `## Entities Graphics constraints`: EG 6.4.0 deformation is Experimental: compute-only via Shader Graph node, no deformation culling, static bounds, no blend-shape frames. Rukhanka bypasses it with its own deformation, and Kinemation replaces it.
- `## Sources`: The list of primary URLs and local file paths, with dates.

## Options compared

| Option | Latest version + date | Entities 6.4.0 / Unity 6000.4 compat | Humanoid / Mecanim support | Perf model | License / cost | Maintenance | Source |
|---|---|---|---|---|---|---|---|
| Hybrid: ECS sim + Animator on runtime-instantiated GameObject | N/A (engine Mecanim, 6000.4.0f1). Official doc and samples are current (ECS samples repo pushed 2026-10-06, CC samples 2026-08-24) | FIT. Documented in the installed Entities 6.4.0 docs (UnityObjectRef + Animator example) | Full Mecanim: Humanoid, retargeting, avatar masks, IK pass, Animation Rigging | One Animator + SMR per character on the GameObject side (Mecanim is internally multithreaded). The ECS-to-GO sync is main-thread and non-Burst (companion/managed queries "cannot be Burst compiled and must run in the main thread"). Rendering goes through the regular SkinnedMeshRenderer, not Entities Graphics. Bones are GO transforms, so ECS physics or attachments need copying back. | Free (engine) | Supported engine feature. Unity's stated long-term replacement is the new animation system | Entities docs reference-unity-objects.md. EG companion-components.md. https://github.com/Unity-Technologies/CharacterControllerSamples (Platformer HybridSystem). https://github.com/Unity-Technologies/EntityComponentSystemSamples (Graphical/AnimateGameObject, Firefighters Step 4) |
| Rukhanka Animation System 2 | 2.9.1, 2026-07-02 (changelog) / 2026-07-03 (store) | LIKELY FIT. 2.9.1 fixes "Unity 6000.4+ warnings related to the new EntityID usage". 2.9.0 fixes 6.6 alpha and 2.8.0 fixes 6000.5 alpha. Minimums: Entities 1.4.3, EG 1.4.16 (2.7.0, 2026-01-01). An explicit "6.4.0 supported" statement is UNCONFIRMED | Bakes standard Animator Controllers. Humanoid ✅ (needs avatar), Generic ✅. All blend tree types, sub-SMs, interruptions, override/additive layers, root motion, events ✅. Write Defaults, Mirror and clip-import Mask ❌. Mecanim IK pass ❌ (own IK) | CPU engine (Burst jobs, reference) or GPU engine (compute), switchable at runtime. Own compute deformation (EG deformation dropped in 2.6.0). Animation culling limits deformation to visible LODs. CPU-only: IK, root motion, blend shapes, bone writeback, physics. Netcode for Entities: predicted and interpolated ghosts via the RUKHANKA_WITH_NETCODE define | Asset Store Standard EULA (Extension Asset, per seat). €110.41 list (€55.20 on sale at fetch) | Active: 8 releases from 2025-11 to 2026-07 | https://docs.rukhanka.com/changelog ; /feature_support_tables ; /animation-engines ; /netcode ; /getting_started ; https://assetstore.unity.com/packages/tools/animation/rukhanka-animation-system-2-298480 |
| Latios Framework Kinemation | 0.16.1, 2026-09-26 (0.16.0 on 2026-09-20). Add-Ons 0.9.0 | NO-FIT. README: "This version targets Entities 1.4.8 and a minimum editor version of 6000.3.8f1. Entities 6.4.0 compatibility is not supported at this time." The author (2026-06-15) says the fix waits for the move to Unity 6.7 LTS | Kinemation: clip baking and compression (ACL), sampling, masking, root motion, inertial blending, EWBIK, sockets, blend shapes, DQS. Animator Controller runtime only via community Add-Ons (Mecanim V1/V2, KAG50). Humanoid/retargeting is UNCONFIRMED from primary docs | Replaces key parts of Entities Graphics. Bones as entities or as an optimized skeleton. Skinning in compute (deform) or vertex shader. Shaders need Kinemation deform nodes. Requires the Latios custom bootstrap (modules off by default). Defaults to QVVS Transforms, with LATIOS_TRANSFORMS_UNITY needed to keep Unity Transforms (CharacterController / Unity Physics) and "some features ... disabled" | Unity Companion License, free | Active (frequent releases), but tied to the 6000.3 LTS line | https://github.com/Dreaming381/Latios-Framework/blob/master/README.md ; https://raw.githubusercontent.com/Dreaming381/Latios-Framework/master/package.json ; https://github.com/Dreaming381/Latios-Framework/issues/74 ; https://github.com/Dreaming381/Latios-Framework-Documentation/blob/main/Kinemation%20Animation%20and%20Rendering/README.md ; https://github.com/Dreaming381/Latios-Framework-Add-Ons |
| GPU ECS Animation Baker (The Orange Coder) | 1.3.6, 2024-04-15 | UNCONFIRMED (min 2022.3.24, no Unity 6.x statement found) | Converts Animator + SMR into baked GPU animation. Mecanim state machine support UNCONFIRMED | Baked GPU animation and instancing, "tens of thousands" of characters | Asset Store EULA, €45.08 | Stale (no update in about 2.5 years) | https://assetstore.unity.com/packages/tools/animation/gpu-ecs-animation-baker-250425 |
| GPU Animation Entities PRO (Sniveler Code) | 1.4.0, about 2026-07-28 (derived from "71 days ago") | UNCONFIRMED | Baked skeletal animation, DQS, root motion, attachments. "Runtime IK ... and physics-driven Ragdolls are not supported" | Vertex-shader GPU skinning, 10k+ units. Crowd-oriented, so player-character fit is weak (no IK or ragdoll) | $49.99+ (itch.io) | Active in 2026 | https://snivelercode.itch.io/gpu-animation-entities-pro |
| Raw Entities Graphics deformation (write SkinMatrix / BlendShapeWeight yourself) | Ships in EG 6.4.0 (2025-10-16) | Built in, but "Experimental" | None. EG bakes the SMR into deformation components and you must compute the bone matrices yourself (no clip sampling or state machine) | GPU compute skinning. No deformation culling, no bounds update | Free | Unity-owned, still experimental | EG Documentation~/mesh_deformations.md ; entities-graphics-versions.md |
| Unity com.unity.animation (DOTS Animation) | 0.9.0-preview.6 (depends on Entities 0.17) | NO-FIT (dead) | N/A | N/A | N/A | Discontinued. "should NOT be considered suitable for production" | https://discussions.unity.com/t/animation-status-update-q2-2022/877939 |
| Old community GPU repos (joeante/Unity.GPUAnimation, Unity-Technologies/Animation-Instancing) | Last pushed 2021-12-11 / 2024-03-06 | NO-FIT (unmaintained, pre-1.0 APIs) | N/A | Vertex animation | Open source | Unmaintained | GitHub API repo metadata (fetched 2026-10-07) |

## Unity official status
- Unity has no official Entities animation package. com.unity.animation stopped at 0.9.0-preview.6 on Entities 0.17, and development was halted until after Entities 1.0. https://discussions.unity.com/t/animation-status-update-q2-2022/877939
- The new animation system was announced 2025-03-19 (GDC). It "leverages ... ECS", works "both with Entities and GameObjects", and will "exist as a package" that co-exists with Mecanim. Quote: "Skin mesh renderers using entities and ECS unification will likely be delayed". https://discussions.unity.com/t/animation-status-update-q1-2025-gdc-roadmap/1614718
- On 2025-07-29 Unity said it is "still on track" for the Unity 6 lifecycle, with no version or date. Quote: "we plan to support ECS Skinned Mesh Renderer as soon as we can but cannot commit to a timeline." https://discussions.unity.com/t/animation-status-update-summer-2025/1672386
- The Unity 6.5 "What's new" (2026-06) lists only Animation window, animation-event and AnimationEventInfo changes. It has no new animation system and no ECS skinning. https://docs.unity3d.com/6000.6/Documentation/Manual/WhatsNewUnity65.html
- The ECS Development Status of 2025-12-11 says Entities, Collections, Mathematics and Entities Graphics became core packages in 6.4, and that EntityId will unify GameObjects and Entities across future 6.x releases. It says nothing about animation or skinning. https://discussions.unity.com/t/ecs-development-status-december-2025/1699284/1
- Official hybrid pattern, from the installed Entities 6.4.0 docs: store a `UnityObjectRef` to a GameObject prefab with an `Animator` in an `IComponentData`, instantiate it from a system, then drive the Animator from another system. Library/PackageCache/com.unity.entities@d66668920c3f/Documentation~/reference-unity-objects.md
- `Animator` is not on Entities Graphics' supported companion-component list, and unlisted MonoBehaviours "will be stripped from the GameObject". Companion queries can't be Bursted and run on the main thread. Library/PackageCache/com.unity.entities.graphics@2ad17cac7401/Documentation~/companion-components.md
- Unity samples using the hybrid pattern:
  - EntitiesSamples `Graphical/AnimateGameObject` adds the Transform and Animator as component objects on the entity.
  - Entities101 `Firefighters/Step 4/AnimationSystem.cs` removes `MaterialMeshInfo` from the entity and renders through the GO.
  - CharacterControllerSamples Platformer `PlatformerCharacterHybridSystem` copies the mesh-root `LocalToWorld` into the GO and sets Animator params. It runs `OrderLast` in SimulationSystemGroup, after EndSimulationECBSystem.
  - Sources: https://github.com/Unity-Technologies/EntityComponentSystemSamples and https://github.com/Unity-Technologies/CharacterControllerSamples

## Synty POLYGON notes
- Synty ANIMATION - Base Locomotion: 247 clips, Mecanim controllers (masculine and feminine), and root-motion variants. It is "designed to work with the Mecanim humanoid avatar" and with "POLYGON characters, and any characters that work with the Mecanim humanoid avatar". It requires Unity 2022.3+ and supports URP, Built-in and HDRP. Price is $69.99 (5 seats) or SyntyPass. https://syntystore.com/products/animation-base-locomotion (fetched 2026-10-07)
- Project inspection on 2026-10-07:
  - `Characters.fbx` in PolygonFantasyRivals, PolygonSamurai (including FixedScaleCharacters) and PolygonVikings imports as Humanoid (`animationType: 3`).
  - Base Locomotion animation FBXs are Humanoid.
  - 26 Generic (`animationType: 2`) FBXs sit in `Synty/AnimationBaseLocomotion/Samples/Meshes`, with a few more in Samurai/Vikings/Rivals model folders.
  - All 1,606 FBX metas have `optimizeGameObjects: 0`.
  - Path: Impact/Assets/**/*.fbx.meta
- Synty character materials in this project (Vikings, FantasyRivals) use URP `Lit.shader` (guid 933532a4fcc9baf4fa0491de14d08ed7, resolved in com.unity.render-pipelines.universal). That is not a Shader Graph with a deformation node, which has these consequences:
  - EG deformation requires the Compute Deformation node.
  - Rukhanka requires its "Rukhanka Deformation" subgraph and per-instance params.
  - Kinemation requires its deform nodes. Its docs say "All shaders require usage of special ECS skinning functionality".
  - Under all three ECS options, materials must be replaced. The hybrid option needs no change.
  - Sources: Impact/Assets/PolygonVikings/Materials/*.mat and the EG/Rukhanka/Kinemation sources above.
- Multiple SMRs: each project character visual prefab (`Viking_BaseSkin_Visuals`, `Viking_WarriorSkin_Visuals`) has 6 `SkinnedMeshRenderer` and 1 `Animator`. Each SMR becomes a separately deformed entity under any ECS option. Impact/Assets/Content/Characters/Viking/Gameplay/Skins/
- Synty `Characters.fbx` packs many characters into one FBX on a shared skeleton (project folder layout). Whether disabled or inactive SMRs bake into Entities Graphics entities is UNCONFIRMED.
- Rukhanka requires an avatar or humanoid rig definition to exist ("You will get an error during the baking process if avatar rig information is not available") and Optimize Game Objects off. Both are already true for the project's Synty FBXs. It also needs Animator culling mode "Always Animate". https://docs.rukhanka.com/getting_started
- Bone/SMR naming: Rukhanka 2.5.2 (2025-11-26) added "Support for skinned meshes with duplicated bone names". Kinemation lists a known issue when an optimized hierarchy has a Bone and an SMR with identical names. https://docs.rukhanka.com/changelog ; Kinemation README (link above)
- Synty + Rukhanka and Synty + Kinemation compatibility: no primary source found (UNCONFIRMED).
- Attachment bones (weapons):
  - Hybrid: parent to the GO bone transform.
  - Rukhanka CPU: parent the entity to the bone entity.
  - Rukhanka GPU: needs a GPU attachment shader and authoring.
  - Sources: https://docs.rukhanka.com/bone_attachments
- The project already documents the hybrid design (CharacterAnimatorSync MonoBehaviour reads ECS state and drives the Animator), and its rationale says clip playback stays in Mecanim "for Synty/Polygon compatibility". Impact/CHARACTER_ANIMATION_SETUP.md (created 2025-11-01)

## Entities Graphics constraints
- In EG 6.4.0, "Skinning & deformations" is "Experimental. Note: Must use Compute Deformation node in Shader Graph" on both URP and HDRP. EG also requires URP Forward+. Documentation~/entities-graphics-versions.md ; requirements-and-compatibility.md
- When baking a SkinnedMeshRenderer, EG adds the deformation components (`SkinMatrix`, `BlendShapeWeight`). Motion only happens when something writes to them. EG has no clip sampling or state machine. Documentation~/mesh_deformations.md
- EG does not support:
  - blend shape frames
  - optional normals/tangents
  - resizable render bounds from the animated pose
  - BakeMesh
  - cloth
  - the quality setting that limits skin influences
  - CPU deformation
- Per-vertex motion vectors work only on HDRP with a define. mesh_deformations.md § Feature comparison
- EG deformation limitations:
  - "No frustum or occlusion culling" of deformation
  - "Render bounds are not resized"
  - Shader Graph sub-graphs are not supported
  - deformed meshes "can disappear or show in their bind pose when Unity renders them as GameObjects"
  - no VFX Graph
  - Source: mesh_deformations.md § Known limitations
- Vertex-shader (Linear Blend Skinning node) skinning is "not encouraged and will not be supported in the future". It is dense 4-bone only, with no blend shapes or motion vectors. Source: mesh_deformations.md
- EG supports only one rendering World, which matters for netcode client/server worlds in one process. requirements-and-compatibility.md § ECS feature compatibility
- What each option needs from EG:
  - Hybrid: nothing. It renders through the classic SkinnedMeshRenderer on the GO, and the samples remove `MaterialMeshInfo` from the entity.
  - Rukhanka (≥2.6.0): replaces EG deformation with its own compute pass, but still depends on the Entities Graphics package (≥1.4.16).
  - Kinemation: replaces key parts of EG with its own culling and skinning.
  - GPU bakers: bypass deformation entirely, using vertex textures or buffers.
  - Sources: Rukhanka changelog/getting_started; Kinemation README.

## Sources
- Local, installed versions: Impact/Packages/manifest.json (entities 6.4.0, entities.graphics 6.4.0, charactercontroller 1.4.1, URP 17.4.0). Library/PackageCache/com.unity.entities@d66668920c3f/CHANGELOG.md (6.4.0, 2025-10-16). Library/PackageCache/com.unity.entities.graphics@2ad17cac7401/CHANGELOG.md (6.4.0, 2025-10-16)
- Local docs: com.unity.entities@d66668920c3f/Documentation~/reference-unity-objects.md. com.unity.entities.graphics@2ad17cac7401/Documentation~/{mesh_deformations, companion-components, entities-graphics-versions, requirements-and-compatibility, known-issues, whats-new}.md
- Local project: Impact/CHARACTER_ANIMATION_SETUP.md (2025-11-01). Impact/Assets/Polygon*/Models/Characters.fbx.meta. Impact/Assets/Synty/AnimationBaseLocomotion/. Impact/Assets/Content/Characters/Viking/Gameplay/Skins/*.prefab
- Rukhanka docs (fetched 2026-10-07): https://docs.rukhanka.com/ , /changelog , /feature_support_tables , /getting_started , /animation-engines , /deformation_system , /shaders_with_deformations , /netcode , /physics , /bone_attachments
- Rukhanka Asset Store: https://assetstore.unity.com/packages/tools/animation/rukhanka-animation-system-2-298480 (2.9.1, 2026-07-03). The deprecated v1 page is https://assetstore.unity.com/packages/tools/animation/rukhanka-ecs-animation-system-241472
- Latios: https://github.com/Dreaming381/Latios-Framework/blob/master/README.md ; CHANGELOG.md (0.16.1, 2026-09-26) ; package.json ; https://github.com/Dreaming381/Latios-Framework/issues/74 (author comment 2026-06-15) ; https://github.com/Dreaming381/Latios-Framework-Documentation/blob/main/Kinemation%20Animation%20and%20Rendering/README.md ; https://github.com/Dreaming381/Latios-Framework-Add-Ons (0.9.0)
- Unity official: https://discussions.unity.com/t/animation-status-update-q1-2025-gdc-roadmap/1614718 (2025-03-19) ; https://discussions.unity.com/t/animation-status-update-summer-2025/1672386 (2025-07-29) ; https://discussions.unity.com/t/ecs-development-status-december-2025/1699284/1 (2025-12-11) ; https://docs.unity3d.com/6000.6/Documentation/Manual/WhatsNewUnity65.html (2026-06) ; https://discussions.unity.com/t/animation-status-update-q2-2022/877939 (com.unity.animation halt)
- Unity samples: https://github.com/Unity-Technologies/EntityComponentSystemSamples (EntitiesSamples/Assets/Graphical/AnimateGameObject ; Dots101/Entities101/Assets/Firefighters/Step 4/AnimationSystem.cs ; pushed 2026-10-06) ; https://github.com/Unity-Technologies/CharacterControllerSamples/blob/master/Platformer/Assets/Scripts/Character/PlatformerCharacterHybridSystem.cs (pushed 2026-08-24)
- GPU bakers: https://assetstore.unity.com/packages/tools/animation/gpu-ecs-animation-baker-250425 (1.3.6, 2024-04-15) ; https://snivelercode.itch.io/gpu-animation-entities-pro (1.4.0, about 2026-07-28) ; https://github.com/joeante/Unity.GPUAnimation (pushed 2021-12-11) ; https://github.com/Unity-Technologies/Animation-Instancing (pushed 2024-03-06)
- Synty: https://syntystore.com/products/animation-base-locomotion (fetched 2026-10-07)
