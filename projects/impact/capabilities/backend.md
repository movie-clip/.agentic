# Capability pack: `backend` (Impact)

Owns `Impact/Packages/**` and `Impact/Assets/**` (non-test) — every
gameplay/systems C# change in this repo. There is no separate frontend lane
here (`project.md` § "Why `frontend` and `quant` are not bound"), so this
pack is the one implementation pack for the whole codebase.

## Index

**Always read:** **Guardrails, in code terms** · **Package map and where
responsibility actually sits** · **Known weak spots — read before touching
these** · **Unity CLI for fast iteration** · **Definition of done for this
lane**

| Section | Read it when |
|---|---|
| Crate/content-loading pipeline | your order touches crate registration, loading, or content-management ownership |
| Player/character/skin flow | your order touches player, character spawn, or skin systems |

## Guardrails, in code terms

Guardrail 1 (vendored read-only): `Impact/Packages/com.unity.entities@*/**`.
Guardrail 2 (asmdef boundaries): open the target package's `.asmdef` before
adding a reference; the dependency chain is `athena.core` (no deps) →
`athena.contentmanagement` → `athena.shared` → `athena.gameplay` /
`athena.charactercontroller` / `athena.sceneslice` — never add a reference
that runs the chain backwards. Guardrail 3 (compile before done):
`dotnet build Impact.sln` is the floor; use Unity batchmode compile
(`AGENTS.md` § Build/Compile Commands) when the change touches codegen,
baking, or package-generated assemblies. `AGENTS.md` §§ Naming Conventions,
Type Usage Conventions, ECS/DOTS Style, Error Handling and Diagnostics, and
Null/Validity/Guard Patterns are the C# house style for every edit this lane
makes — read as part of your context load, not repeated here.

## Package map and where responsibility actually sits

- `athena.core` — low-level helper infrastructure. Some helpers still depend
  on Unity internals; treat as fragile, not as a place to add new coupling.
- `athena.contentmanagement` — low-level content loading:
  `ArchiveObjectSceneLoader`, reference-counted GameObject scene lifetime,
  weak-reference object-scene access. Small but load-bearing — `athena.shared`
  depends on it for all object-scene content.
- `athena.shared` — the gameplay/runtime orchestration core, and the center of
  gravity for most feature work: crate registration and load state, asset
  load orchestration, session setup and level switching, player allocation,
  character spawning and skin switching, hybrid ECS/GameObject visual
  lifecycle, world/bootstrap/service glue.
- `athena.charactercontroller` — movement/camera. Depends heavily on
  `athena.shared` ownership and correct character-spawn behaviour; not
  usually the source of session/crate bugs, but breaks visibly when those are
  wrong.
- `athena.gameplay` — thin glue package, still small, not yet the real home
  of most game rules.

Full dependency chain and "where do I find X" table: `PACKAGE_ARCHITECTURE.md`.

## Known weak spots — read before touching these

Condensed from `ARCHITECTURE_REVIEW.md`'s critical findings — read that file
in full before a change to any of these, it is richer than this summary:

- **Crate/content loading is the project's most critical subsystem.** Level
  loading, player/character loading and skin switching all depend on it.
  Registration/runtime state is singleton-heavy and sensitive to lifecycle
  ordering — an ordering change here has the widest blast radius in the repo.
- **Asset-load ownership is split between ECS-singleton and managed-service
  lifetime** (`GameAssetLoadSystem.cs`, `ServiceProvider.cs`). Teardown and
  update-flow changes here are easy to get subtly wrong; check both halves,
  not just the one your order names.
- **`CharacterPossessionSystem` is still effectively a stub.** Do not build
  new logic assuming it does more than it does without checking first.
- **The hybrid visual pipeline is stateful and order-sensitive** — depends on
  manual hybrid markers and cleanup components being present; a change that
  removes or reorders one silently breaks visual respawn.

## Crate/content-loading pipeline

Main files: `GameCrateRegistrationSystem.cs`, `GameCrateLoadByGuidSystem.cs`,
`GameCrateLoadSystem.cs`, `GameCrateSingleton.cs`,
`Components/Authoring/Crates/*` (all under `Packages/athena.shared/Runtime/`).
Higher-level gameplay code thinks in crate GUIDs and crate types — preserve
that abstraction rather than reaching past it. A change to
`GameCrateLoadByGuidRequested` ownership semantics or to `LevelCrate`
switching is exactly the shape that fires `design` (`phases.md` § "Why
`design` fires more often than it looks like it should") — do not make that
call unilaterally inside a `backend` dispatch.

## Player/character/skin flow

Main files under `Packages/athena.shared/Runtime/Systems/Player/*`,
`CharacterCrateLookupSingleton.cs`, `AuthoritativeCharacterSkinLoadSystem.cs`.
Skin switching does real on-demand crate loading and deferred visual
rebuild — it must wait for real skin-crate readiness before the visual
rebuild fires; do not short-circuit that wait to simplify a change.

## Unity CLI for fast iteration

Once the Editor is open on this project, use the `unity-cli` skill (from the
project-scoped `unity-agent-plugin`) for exact current syntax rather than a
remembered command — `unity command eval` takes the C# snippet positionally
plus required `--caller`/`--skill` flags, and the syntax has already drifted
once since this pack's authoring. `unity pipeline list` confirms the Editor
is connected. This is for iteration only — it does not substitute for the
`dotnet build` / `Run-UnityTests.ps1` commands `integration` actually runs.

## Definition of done for this lane

- `dotnet build Impact.sln` is clean (or the equivalent Unity batchmode
  compile check, when the change needs it).
- No edit under a vendored `@<hash>` package, unless the order specifically
  targets it.
- Every new cross-package reference matches an already-declared `.asmdef`
  dependency, or the order added one deliberately and said so.
- `contract_notes` names any changed component/singleton shape another
  package reads, so `design`/`integration` can catch drift instead of a
  runtime NRE catching it later.
