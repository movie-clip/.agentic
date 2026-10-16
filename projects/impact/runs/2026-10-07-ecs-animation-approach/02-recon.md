REPORT 2026-10-07-ecs-animation-approach/02
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only recon, order verification NONE

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Every humanoid asset (3 Synty character packs, Synty animation FBXs) is animationType Humanoid, so Humanoid retargeting is already the working mechanism; see § Avatar and retargeting
  - Game animation is Mecanim on a GameObject Animator driven by AC_Polygon_Masculine; only Viking uses the skin-crate path, Samurai embeds the pack prefab; see § Prefabs and crate pipeline
  - Samurai pack prefabs reference a controller GUID with no asset (d62af11c...); see § Configuration problems
  - CHARACTER_ANIMATION_SETUP.md parameter names (Speed, MoveX, MoveZ, Jump, VerticalVelocity) differ from the code and controller (MoveSpeed, CurrentGait, StrafeDirectionX/Z...); see § Configuration problems
  - Recon 01 owns the C# systems; this artifact only names the authoring/component types the prefabs carry

skill_calls:
  - none

risks:
  - Hierarchy and avatar facts come from .meta and prefab YAML text only; nothing was opened in Unity, so the effective avatar validity and runtime behaviour are unverified
  - rigImportErrors "Transform 'pelvis' for human bone 'Hips' not found" is stored in 34 Masc animation FBX .meta files, but the skeleton listed in the same .meta has Hips, so the error may be stale; not confirmed
  - Script GUID c16549610bfe4458aa9389201d072bb6 (first MonoBehaviour on BaseCharacter.prefab) and PackageCache avatar be73df03... (Fantasy Rivals Character_Mystic_01) were not resolved to a script or asset name
  - Animator controller state counts come from m_Name greps on the 3.7k-line controller; the state list is a sample of names, not an exhaustive state-machine dump
  - Glob returned truncated or empty results for some patterns, so file counts use ripgrep match counts on *.fbx.meta; Samurai and Fantasy Rivals prefab counts are approximate (from directory listings)
  - Entity baking behaviour of Animator/SkinnedMeshRenderer on skin prefabs was not traced (out of scope, recon 01)

## Orchestrator brief
- Four Synty pack folders under Assets: PolygonVikings, PolygonSamurai, PolygonFantasyRivals, Synty/AnimationBaseLocomotion (Polygon + Sidekick animsets). Counts in § Pack inventory.
- All three character packs import Characters.fbx as Humanoid, importAnimation 0, copyAvatar 0, globalScale 1, useFileScale 1, optimizeGameObjects off.
- All 346 Polygon animation FBX are Humanoid, avatarSetup 2 (copy from PolygonSyntyCharacter.fbx), clips baked in place (keepOriginal=1); separate *_RootMotion variants exist but the controller does not use them. See § Import settings.
- Character skeletons share Synty bone naming (Root/Hips/Spine_01...), so one controller plays on Viking, Samurai and Rivals via the Humanoid avatar. See § Avatar and retargeting.
- Only 4 real controllers (AC_Polygon_Masculine/Feminine, AC_Sidekick_Masculine/Feminine) plus 172 one-clip sample controllers; no override controllers, no avatar masks. Only AC_Polygon_Masculine is used by the game. See § Animator controllers.
- Viking: VikingCrate -> default CharacterSkinCrate -> Viking_*Skin_Visuals prefab (full skeleton copy, Animator + CharacterSkinAuthoring); Samurai: pack prefab nested in SamuraiCharacter with controller overridden. See § Prefabs and crate pipeline.
- No Mixamo, no Unity starter-asset animations, no .anim clips in use. See § Non-Synty animation sources.
- Problems found (dangling controller GUID, doc/code parameter drift, duplicated skin skeletons, root motion on, rig errors): § Configuration problems. Doc governance: § Sources of truth.

## Pack inventory
- Assets/PolygonVikings (POLYGON Vikings v1.4.0): 372 FBX total; character models: Models/Characters.fbx (1 skinned multi-character FBX); 18 character prefabs in Prefabs/Characters (Chief/Grunt/Shieldmadien/Warrior x colour variants); animation FBX: 0.
- Assets/PolygonSamurai (POLYGON Samurai v1.6.0): 468 FBX total; character models: Models/Characters.fbx and Models/FixedScaleCharacters/Characters.fbx (2); character prefabs in Prefabs/Characters about 20 plus Prefabs/Characters/FixedScaleCharacters about 20; animation FBX: 0.
- Assets/PolygonFantasyRivals (POLYGON Fantasy Rivals v1.3.1): 45 FBX total; character models: Models/Characters.fbx and Models/Characters_BR.fbx (2); 20 character prefabs in Prefabs/Characters; animation FBX: 0; only clips are Models/Runes_Inner.anim and Runes_Outer.anim (FX).
- Assets/Synty/AnimationBaseLocomotion (Synty ANIMATION Base Locomotion v1.1.0): character meshes Meshes/PolygonSyntyCharacter.fbx and Meshes/SidekickSyntyCharacter.fbx (2); animation FBX: Animations/Polygon/Masculine 171, Polygon/Feminine 171, Polygon/Neutral 4 (TPose, Lean, HeadLook, BodyLook additive) = 346; Animations/Sidekick 346.
- Same pack: Samples/ holds 172 single-clip sample controllers, 66 Timeline .playable files (Polygon/Sidekick x Masc/Femn), Demo_01.unity, Demo_01_Sidekick.unity, Gallery_01.unity, PF_Player.prefab, SamplePlayerAnimationController.cs; only Samples/Meshes SM_* props are non-character.
- Other non-pack asset folders touching characters: Assets/Content/Characters (Viking, Samurai, Gameplay), Assets/Samples/Character Controller/1.3.11/Standard Characters (Unity sample, no animation), Assets/Content/Levels/Tests/{Viking,Samurai}.

## Import settings
- PolygonVikings/Models/Characters.fbx.meta: animationType 3 (Humanoid) line 919; importAnimation 0 line 248; copyAvatar 0 line 249 (avatar created from this model); globalScale 1, useFileScale 1; no optimizeGameObjects key set; humanDescription maps Hips, UpperLeg_L/R ...
- PolygonSamurai/Models/Characters.fbx.meta and FixedScaleCharacters/Characters.fbx.meta: animationType 3, importAnimation 0, copyAvatar 0, globalScale 1, useFileScale 1.
- PolygonFantasyRivals/Models/Characters.fbx.meta and Characters_BR.fbx.meta: animationType 3, importAnimation 0, copyAvatar 0, globalScale 1; Characters.fbx bones Root/Hips/Spine_01 (lines 576-586).
- Synty/AnimationBaseLocomotion/Meshes/PolygonSyntyCharacter.fbx.meta: animationType 3, avatarSetup 1 (create from this model), importAnimation 1, optimizeGameObjects 0 (line 21), hasExtraRoot 1, humanoidOversampling 1, bones Root, Hips at 429-434.
- Animation FBX sample Animations/Polygon/Masculine/Locomotion/Run/A_Run_F_Masc.fbx.meta: animationType 3, avatarSetup 2, lastHumanDescriptionAvatarSource = PolygonSyntyCharacter.fbx avatar (guid bfa42ba6...) lines 716-721, optimizeGameObjects 0, hasExtraRoot 1, animationCompression 0, rotation/position/scale error 0.5, resampleCurves 1, bakeSimulation 0.
- Same clip: one clip A_Run_F_Masc, frames 1-22, loopTime 1, loopBlend 1, loopBlendOrientation/PositionY/PositionXZ 1, keepOriginalOrientation/PositionY/PositionXZ 1 (root baked into pose), no lockRoot keys, maskType 3, no events or curves.
- Sibling RootMotion variant A_Run_F_RootMotion_Masc.fbx.meta (guid 8b45cba6...): loopTime 1, loopBlend 0, keepOriginalOrientation 0, keepOriginalPositionXZ 0, keepOriginalPositionY 1 (root motion not baked into XZ/orientation).
- Counts over Animations/Polygon *.fbx.meta (346 files): all 346 have avatarSetup 2; 218 files have a clip with loopTime 1 and 117 files have a loopTime 0 clip (184 clips); no .fbx.meta in Assets has optimizeGameObjects 1; 757 FBX across Assets have importAnimation 1.
- Controller uses 108 m_Motion refs to clip GUIDs; none is the RootMotion variant tested (8b45cba6...), the non-RootMotion A_Run_F_Masc (6c670ea8...) is referenced once.

## Avatar and retargeting
- Viking, Samurai and Fantasy Rivals Characters.fbx each generate their own Humanoid avatar (copyAvatar 0); all list Root > Hips > Spine_01 with the same Synty bone names (UpperLeg_L, Ankle_L, Ball_L, Toes_L, Hand_R, Finger_03 ...), see Viking .meta lines 600-650, Samurai 614-664, Rivals 576-586.
- All 346 Polygon animation FBX copy the avatar of PolygonSyntyCharacter.fbx (avatarSetup 2), and the Polygon skeleton also uses Root/Hips/Spine_01 (A_Run_F_Masc.fbx.meta lines 454-464), so the clips are Humanoid and retarget to any of the three character avatars through Mecanim.
- Evidence the pairing already runs: Viking_BaseSkin_Visuals.prefab line 701 has m_Avatar = PolygonVikings Characters.fbx avatar (guid a177b0e6...) with m_Controller = AC_Polygon_Masculine (guid a3a348fc...), line 702; Samurai pack prefabs keep their own Samurai avatar (2ba66718...) while SamuraiCharacter.prefab overrides m_Controller to AC_Polygon_Masculine.
- Not one shared avatar or skeleton asset: three character avatars plus the Synty animation source avatar; retargeting happens per Humanoid mapping, not by a shared Avatar asset.
- Skeleton is not optimised (optimizeGameObjects 0 everywhere); skin prefab Animator has m_HasTransformHierarchy 1 (Viking_BaseSkin_Visuals.prefab line 710).
- Sidekick animation set (346 FBX) targets SidekickSyntyCharacter.fbx skeleton; no Sidekick character model exists in the game content.

## Animator controllers
- AC_Polygon_Masculine.controller (Animations/Polygon/): guid a3a348fc...; layers: Base Layer, Additive_BodyLook, Additive_HeadLook, Additive_Lean (additive blend, weight 1, no avatar mask); parameters: MovementInputTapped/Pressed/Held (bool), MoveSpeed (float), CurrentGait (int), InclineAngle, LocomotionStartDirection, StrafeDirectionX/Z, ShuffleDirectionX/Z, ForwardStrafe, IsStrafing (float), IsStopped, IsTurningInPlace, IsStarting, IsWalking, IsCrouching, IsJumping, IsGrounded (bool), FallingDuration, LeanValue, HeadLookX/Y, BodyLookX/Y, CameraRotationOffset (float); 29 parameters.
- AC_Polygon_Masculine states by name include Idle_Standing, LocomotionBlendTree, Walk/Run/Sprint strafe and incline blend trees, Run_Start_F360, NonStrafing-Starts, Jump, Jump_Idle, Jump_Walking, Falling_BlendTree, LandingSoft/Hard/Walk/Default/Sprint, Stand_ToCrouch, Idle_Crouching, Crouch_FwdStrafe_BlendTree, ShuffleCrouchingBlendTree, TurnInPlace_Standing/Crouching, Sprint_ToCrouch, StandUp, HeadLook_State, Lean.
- Used by: Viking_BaseSkin_Visuals.prefab and Viking_WarriorSkin_Visuals.prefab (Animator line 702), and by SamuraiCharacter.prefab (m_Controller override on the nested Character_Samurai_Grunt_White instance, line 56-58).
- AC_Polygon_Feminine.controller, AC_Sidekick_Masculine.controller, AC_Sidekick_Feminine.controller: in Animations/Polygon and Animations/Sidekick; Sidekick Masculine is used by Samples/Scenes/Demo_01_Sidekick.unity only; none referenced by game content.
- 172 sample controllers AC_*.controller under Samples/Animations/Polygon/{Masculine,Feminine} (single-clip, e.g. AC_Run_F_Femn); used by sample scenes and Timelines only.
- AnimatorOverrideController: none in the project. Avatar masks (.mask): none. Layer masks inside the controller: none (m_Mask fileID 0).
- Unity-sample/third-party controllers exist only in Packages/com.projectdawn.navigation/Samples~ (Zerg.controller, Bot Animator.controller, Confirmation.controller), not imported into Assets.
- Pack prefabs for Vikings/Fantasy Rivals characters have m_Controller fileID 0 (Character_Chief_01_White.prefab line 2552, Character_Mystic_01.prefab line 1627), m_ApplyRootMotion 1.

## Prefabs and crate pipeline
- Content/Characters/Gameplay/Setup/BaseCharacter.prefab (guid 1d2ebc93...): root with ThirdPersonCharacterAuthoring, CharacterAuthoring, CameraTargetAuthoring, HybridGameObjectAuthoring, CapsuleCollider (r 0.5 h 2), an unresolved script c16549610..., child Capsule and Cylinder placeholders; no Animator on the base.
- Content/Characters/Viking/Gameplay/VikingCharacter.prefab: variant of BaseCharacter; adds ThirdPersonCharacterExternalInputAuthoring, ThirdPersonCharacterMoveToTargetAuthoring; sets HybridGameObjectAuthoring.Prefab to Viking_BaseSkin_Visuals; nests PF_Player (Synty sample, inactive) and a Viking_Chief_01_White instance of Viking_BaseSkin_Visuals (inactive); removes one child.
- Content/Characters/Viking/Gameplay/Skins/Viking_BaseSkin_Visuals.prefab (guid 141792be...): root Viking_BaseSkin_Visuals has Animator (Avatar a177b0e6..., Controller AC_Polygon_Masculine, ApplyRootMotion 0, CullingMode 1, UpdateMode 0) and CharacterSkinAuthoring; SkinnedMeshRenderers for Chief_01 (active), Warrior_01, Grunt_02 (inactive), meshes from PolygonVikings Characters.fbx; full 49-bone skeleton under Root; MeshRenderer items (Item_Dagger, Item_Horn, Item_WarriorSholderArmor) inactive, parented to bones.
- Content/Characters/Viking/Gameplay/Skins/Viking_WarriorSkin_Visuals.prefab: a separate full copy (not a variant) of the same hierarchy with Character_Viking_Warrior_01 active instead of Chief; same Animator, same avatar, same controller; same fileIDs.
- Crates: Viking_BaseSkin.asset and Viking_WarriorSkin.asset are CharacterSkinCrate with skinEntityPrefab (EntityPrefabReference, GenerationType 5) pointing at the respective Visuals prefab root (fileID 2122507923211388599); childCrates empty. CharacterSkinCrate is NonCritical; load request via CreateEntityPrefabLoad.
- VikingCrate.asset (CharacterCrate guid 8025de30...): characterName Viking, defaultSkinCrateComponent = Viking_BaseSkin, characterPrefab = VikingCharacter.prefab; Viking_GameplaySkinMap.asset (CharacterSkinCrateLookup): defaultSkinId 1, SkinId 2 -> Viking_WarriorSkin; GameplayeCharacterLookup.asset: HeroId 1 -> Viking_GameplaySkinMap; Viking_Registration.asset lists the three crates; CharactersRegistrationList.asset lists SamuraiCrate and child list Viking_Registration.
- Content/Characters/Samurai/Gameplay/SamuraiCharacter.prefab: variant of BaseCharacter with nested pack prefab Character_Samurai_Grunt_White (PolygonSamurai, own avatar 2ba66718...) as child with m_Controller overridden to AC_Polygon_Masculine; pack Animator has ApplyRootMotion 1; no skin crate, no CharacterSkinAuthoring; SamuraiCrate.asset (CharacterCrate) has no defaultSkinCrateComponent.
- Skeleton sharing between skins: each skin prefab owns its own full skeleton, Animator and controller reference (nothing shared); skins are swapped by whole-prefab replacement (SkinId lookup), and both skins use identical avatar and controller.
- ECS-side types the prefabs touch (names only, recon 01 owns tracing): CharacterSkinAuthoring (SkinReference), HybridGameObjectAuthoring, CharacterAuthoring, CharacterAnimatorSync (MonoBehaviour, RequireComponent Animator), CharacterAnimationState (IComponentData), CharacterAnimationStateUpdateSystem, CharacterAnimationBridgeSystem, CharacterAnimationAuthoring (all in athena.shared).
- CharacterAnimatorSync writes MoveSpeed, CurrentGait, IsGrounded, IsJumping, FallingDuration, IsWalking, LocomotionStartDirection, StrafeDirectionX/Z, ShuffleDirectionX/Z, ForwardStrafe, IsStrafing (float), CameraRotationOffset, IsTurningInPlace, plus optional IsStarting/IsStopped/MovementInput*; all names exist in AC_Polygon_Masculine with matching types; Initialize sets animator.applyRootMotion = false.
- Test content: Content/Levels/Tests/Viking/Viking_Sandbox.asset and Samurai/Samurai_Sandbox.asset reference the crates; Content/Gameplay/Core/Crates/Gameplay.asset (critical crate, empty lists); Content/Core/gameWorldStateRunner.prefab (modified in git).

## Non-Synty animation sources
- none found: no Mixamo references in any .meta, no non-Synty humanoid animation FBX, no Unity Starter Assets animations in Assets.
- Only non-Synty clips: PolygonFantasyRivals/Models/Runes_Inner.anim and Runes_Outer.anim (FX rotation clips from a Synty pack, not character animation).
- Assets/Samples/Character Controller/1.3.11/Standard Characters (Unity sample prefabs) carries no Animator or animation references.
- Packages/com.projectdawn.navigation/Samples~ controllers (Zerg.controller, Bot Animator.controller, Confirmation.controller) are in a tilde sample folder, not imported.

## Configuration problems
- Dangling controller: 20+ PolygonSamurai character prefabs (e.g. Character_Samurai_Grunt_White.prefab line 2652) reference controller guid d62af11c372059a4d9c2feacf46a754a; no .meta in the project carries that guid, so the controller reference is missing in the pack; SamuraiCharacter.prefab works around it by overriding to AC_Polygon_Masculine.
- Stale/contradicting rig errors: 34 Masc animation FBX .meta files (Run, Walk, Crouch, Turn_Crouching_90L; e.g. A_Run_F_Masc.fbx.meta line 19-20) store rigImportErrors "Copied Avatar Rig Configuration mis-match... Transform 'pelvis' for human bone 'Hips' not found", while the skeleton in the same .meta names Hips.
- Doc/code drift: CHARACTER_ANIMATION_SETUP.md documents parameters Speed, MoveX, MoveZ, Jump trigger, VerticalVelocity and states Idle/Walk/Run/Jump/Fall/Land, whereas CharacterAnimatorSync and AC_Polygon_Masculine use MoveSpeed, CurrentGait, StrafeDirectionX/Z, IsJumping, FallingDuration and crouch/shuffle/turn states; the doc also lists a jump trigger and 2D blend tree guidance that the shipped controller does not use.
- Doc claims CharacterAnimationAuthoring is unnecessary for CharacterAuthoring prefabs and CharacterAnimatorSync is auto-added; not verified here (recon 01).
- Root motion is on in the pack prefabs: Samurai Character_Samurai_Grunt_White.prefab and Viking Character_Chief_01_White.prefab have m_ApplyRootMotion 1, and the Samurai child nests under SamuraiCharacter with no override; only the sync code sets applyRootMotion false at Initialize; the Viking skin prefab Animator already has 0. CHARACTER_ANIMATION_SETUP.md FAQ states root motion must stay off.
- Viking skin variants are two full copies of one ~3.6k-line prefab (Base and Warrior Visuals) with duplicated skeleton, Animator, avatar and controller refs; they differ only in which SkinnedMeshRenderer is active.
- VikingCharacter.prefab nests an inactive Viking_Chief_01_White instance of Viking_BaseSkin_Visuals and an inactive PF_Player (Synty sample prefab with its own components) as children while also setting HybridGameObjectAuthoring.Prefab to the same Visuals prefab; the skin visual therefore appears both as nested child and as hybrid-spawn target.
- Samurai uses a different route (embedded pack prefab, no CharacterSkinCrate) than Viking (CharacterSkinCrate); no Samurai skin variants are wired through the skin lookup.
- Sidekick animation set (346 FBX, 4 controllers, Timelines, demo scene) is imported with no Sidekick character in the game; Polygon Feminine controller and clips also unused by game prefabs.
- Animation compression is 0 (off) with 0.5 error thresholds recorded and resampleCurves 1 on all sampled Synty animation FBX; optimizeGameObjects is 0 on all models (no transform hierarchy stripping) while skins use up to 49 bones x 3 skinned renderers each.

## Sources of truth
- CHARACTER_ANIMATION_SETUP.md (dated 2025-11-01, "Production Ready"): architecture diagram (ECS state -> CharacterAnimatorSync -> Animator) matches code names; parameter lists and state examples are out of date against the controller and sync script.
- AC_Polygon_Masculine.controller and CharacterAnimatorSync.cs are the current authority for parameter names and types.
- Synty ANIMATION Base Locomotion Documentation/Base Locomotion UserGuide.pdf and CHANGELOG.md ship in Assets/Synty/AnimationBaseLocomotion (not read).
- Impact/ARCHITECTURE_REVIEW.md and PACKAGE_ARCHITECTURE.md govern package layout (not read for this order); the .asmdef files are the authority on dependency direction per project.md guardrail 2.
- Per-pack provenance in each .fbx.meta AssetOrigin: POLYGON Vikings 1.4.0, POLYGON Samurai 1.6.0, POLYGON Fantasy Rivals 1.3.1, Synty ANIMATION Base Locomotion 1.1.0.
