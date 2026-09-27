# Capability pack: `backend` (Impact)

Owns `Impact/Packages/**` and `Impact/Assets/**` (non-test) — every
gameplay/systems C# change in this repo. There is no separate frontend lane
here (`project.md` § "Why `frontend` and `quant` are not bound"), so this
pack is the one implementation pack for the whole codebase.

## Index

**Always read:** **Guardrails, in code terms** · **Package map and where
responsibility actually sits** · **Known weak spots — read before touching
these** · **Definition of done for this lane**

| Section | Read it when |
|---|---|
| Crate/content-loading pipeline | your order touches crate registration, loading, or content-management ownership |
| Player/character/skin flow | your order touches player, character spawn, or skin systems |
| Diagnosing a stuck bug | your first fix attempt didn't hold |

## Guardrails, in code terms

Guardrail 1 (third-party read-only): `Packages/com.projectdawn.navigation/**`
and `Library/PackageCache/**`. Guardrail 2 (asmdef boundaries): open the
target package's `.asmdef` before adding a reference; the real graph is the
table under `project.md` § Hard guardrails. The trap is
`athena.charactercontroller`: `athena.shared` references it, so it can never
reference `athena.shared` back. Guardrail 3 (compile before done):
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
- `athena.charactercontroller` — movement/camera. A dependency of
  `athena.shared`; references no Athena package.
- At runtime, charactercontroller relies on `athena.shared` spawning
  characters correctly. It breaks visibly when session/crate code is wrong,
  without being the source.
- `athena.gameplay` — thin glue package, still small, not yet the real home
  of most game rules.
- `athena.sceneslice` — scene composition tool; no Athena references.
- `athena.ai`, `com.ai.shared`, `com.ai.utility` — AI decision code on its
  own branch of the graph. `athena.ai` is immature; read around it before
  extending.
- `athena.templatepackage` — a template for new packages; not game code.

"Where do I find X" tables: `PACKAGE_ARCHITECTURE.md`. Its hierarchy diagram
is wrong about `athena.charactercontroller`, so use the `.asmdef` graph for
direction.

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

## Diagnosing a stuck bug

Your first fix attempt didn't hold: call the Skill tool with
`mattpocock-skills:diagnosing-bugs` rather than guessing again. Impact's
`.claude/settings.json` enables this plugin.

Adapted to this lane and to Unity:

- The skill's feedback loop here is a single test run:
  `Run-UnityTests.ps1 -Platform EditMode -Filter "<fully qualified name>"`.
- Run `dotnet build Impact.sln` before each run. A compile error there wastes
  the whole boot.
- If no existing test reaches the bug, there is no fast loop. Test assemblies
  are not yours to edit, so name the repro test the test lane should write in
  `handoff`. Record the missing loop in `risks`.
- Each batchmode run is a cold Unity boot, not seconds. Batch hypotheses per
  run rather than one probe per boot.
- Batchmode needs the Editor closed (`testing.md` § Gotchas). If it is open,
  say so in `risks` instead of working around it.
- For a runtime error the human saw, read
  `C:\Users\MovieClip\AppData\Local\Unity\Editor\Editor.log` first
  (`AGENTS.md` § Working Directories).
- Tag every probe `Debug.Log("[DEBUG-xxxx] ...")`, and grep the tag to remove
  them all before you report.
- For "is this API used right", read the package's
  `Library/PackageCache/<pkg>@*/Documentation~/`, e.g. Entities'
  `common-errors.md`.
- Diagnose the root cause and apply the fix — that part is yours.
- Do not write the regression test: name it in `handoff` for the test lane
  instead (you touch no test files).
- Name any scratch file you create in `handoff` with its `git rm <path>`
  command — you have no delete tool.
- The skill's "ask the user" moments become a `risks` entry instead.
- No commit. Your report is the protocol's report block, not a commit message.
- Record the call in `skill_calls:` (`PROTOCOL.md` § 7).

## Definition of done for this lane

- `dotnet build Impact.sln` is clean (or the equivalent Unity batchmode
  compile check, when the change needs it).
- No edit under `Packages/com.projectdawn.navigation/` or
  `Library/PackageCache/`, unless the order specifically targets it.
- No new `IAspect` type (`AGENTS.md` § Type Usage Conventions).
- Every new cross-package reference matches an already-declared `.asmdef`
  dependency, or the order added one deliberately and said so.
- `contract_notes` names any changed component/singleton shape another
  package reads, so `design`/`integration` can catch drift instead of a
  runtime NRE catching it later.
