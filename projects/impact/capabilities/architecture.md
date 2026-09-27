# Capability pack: `architecture` (Impact)

Read by `tech-lead` in both modes: `DESIGN` (before the build lane, when
`phases.md`'s `design` row fires) and `INTEGRATION` (after it, as the
engineering gate).

## Index

**Always read:** **Package dependency graph** · **What `integration` must
run** · **Design decisions this lane owns, not the engineer** · **Technique
skills (mattpocock-skills)**

| Section | Read it when |
|---|---|
| Known weak spots | your order touches the crate/content pipeline, asset loading, or the hybrid visual pipeline |
| Design pass checklist | you are in DESIGN mode |
| Integration review checks | you are in INTEGRATION mode |
| When the test gate does not reach the change | the change touches a package no test assembly references, or codegen/baking |

## Package dependency graph

The real graph is the table under `project.md` § Hard guardrails, read from
the `.asmdef` files. `PACKAGE_ARCHITECTURE.md`'s diagram is wrong about one
edge: it draws `athena.charactercontroller` as depending on `athena.shared`.
In fact `athena.shared` references charactercontroller, not the reverse.

- Check the direction before approving a contract, not just its shape.
- A design that needs charactercontroller to read an `athena.shared` type is
  a cycle. The shape belongs lower down (charactercontroller or core), or
  shared pushes the data down.
- `athena.gameplay` sees only `Athena.Shared.Components`, not
  `Athena.Shared.Runtime`. A contract gameplay reads must live in Components.

## Design decisions this lane owns, not the engineer

Per `phases.md` § "Why `design` fires more often than it looks like it
should": any change to a component or singleton shape more than one package
already reads. In practice, in this repo, that means:

- New or changed fields on `GameCrateSingleton`, `CharacterCrateLookupSingleton`,
  or any other type read across a package boundary.
- A change to `GameCrateLoadByGuidRequested` ownership semantics, or to how
  `LevelCrate` switching completes.
- A change to the asset-load ownership split between ECS-singleton and
  managed-service lifetime (`GameAssetLoadSystem.cs` / `ServiceProvider.cs`)
  — `ARCHITECTURE_REVIEW.md` names this as the area most likely to regress
  from an in-isolation fix.

Settle the shape once here; a `backend` dispatch that hits one of these
without a `design` order behind it should treat that as a scope violation
worth flagging, not a decision to make alone.

## Design pass checklist

- [ ] Call the Skill tool with `mattpocock-skills:codebase-design` before
      naming the component/singleton shape — every DESIGN pass.
- [ ] Record that call in your report's `skill_calls:` field.
- [ ] Name each changed component/singleton and its new fields before
      `backend` starts, with the package and assembly that owns it.
- [ ] Check every new reference against the dependency graph above.
- [ ] State the system ordering the change relies on (`UpdateInGroup`,
      `UpdateBefore`/`UpdateAfter`) — ordering is where this repo regresses.
- [ ] Say which test assembly can reach the change (`testing.md` § Which
      packages a test can see), or that none can.

## Integration review checks

- [ ] `dotnet build Impact.sln` clean, from `Impact/`.
- [ ] The test runs in § What `integration` must run passed; read the counts
      from the results XML.
- [ ] No edit under `Packages/com.projectdawn.navigation/` or
      `Library/PackageCache/` (guardrail 1).
- [ ] No new `.asmdef` reference that runs against the graph above.
- [ ] No new `IAspect` type (`AGENTS.md` § Type Usage Conventions).
- [ ] `contract_notes` from each build lane agree on any shared
      component/singleton shape.
- [ ] Before writing a reuse or consistency judgment into `risks` or the
      orchestrator brief, call `mattpocock-skills:codebase-design`.
- [ ] Record that call (or its absence) in `skill_calls:`.

## Technique skills (mattpocock-skills)

Scope constraints for the `codebase-design` calls the two checklists
require; this is not a separate trigger. Impact's `.claude/settings.json`
enables the plugin.

- Read only the main `SKILL.md` glossary and principles, not its "Going
  deeper" material.
- Do not open `DESIGN-IT-TWICE.md` — it assumes an `Agent` tool you don't
  have.
- Do not open `DEEPENING.md` — it tells the reader to delete files, which no
  lane here can do.
- Map its terms onto ECS: a *module* is a package or a system group; its
  *interface* is the components and singletons other packages read.
- A *seam* is an `.asmdef` boundary. "Deep" means few public components
  carrying a lot of behaviour behind one system group.
- This is reference vocabulary: it sharpens the TECHNICAL PLAN in DESIGN and
  the change requests in INTEGRATION.

## Known weak spots

Mirrors `backend.md`'s summary, condensed further to what a design/
integration judgment needs — `ARCHITECTURE_REVIEW.md` is the full source:

- Crate/content loading is the subsystem most likely to produce project-wide
  failures; level loading, player/character loading and skin switching all
  sit downstream of it.
- The project relies heavily on ECS singleton state, so initialization order
  and teardown order matter more than they would in a less singleton-heavy
  design — weigh that when judging whether an ordering change is safe.
- The hybrid visual pipeline (ECS state / GameObject visuals split) is
  functionally solid but still delicate and order-sensitive; a design change
  here should keep explicit logging around the transition it touches.

## What `integration` must run

Minimum: `dotnet build Impact.sln`, then
`Tools/Run-UnityTests.ps1 -Platform EditMode -CoreOnly`, both from `Impact/`.
Add `-Platform PlayMode -CoreOnly` when the change reaches runtime/session/
player flow or the crate/content pipeline. `status: DONE` requires every run
to pass; a compile-only check is not a substitute for the test gate.

`-CoreOnly` already runs every project test (`testing.md` § Running the
suite). Dropping it is not an escalation.

## When the test gate does not reach the change

- No test assembly references `athena.charactercontroller`, `athena.gameplay`
  or `athena.ai`. A change confined to them passes the test gate untested.
- Say so in `risks`, and name the missing test in a change request to the
  test lane when the change carries logic.
- Baking, source generators and `[BurstCompile]` output are not checked by
  `dotnet build`. For those, add the Unity batchmode compile
  (`AGENTS.md` § Build / Compile Commands).
