# Capability pack: `architecture` (Impact)

Read by `tech-lead` in both modes: `DESIGN` (before the build lane, when
`phases.md`'s `design` row fires) and `INTEGRATION` (after it, as the
engineering gate).

## Index

**Always read:** **Package dependency chain** · **What `integration` must
run** · **Design decisions this lane owns, not the engineer**

| Section | Read it when |
|---|---|
| Known weak spots | your order touches the crate/content pipeline, asset loading, or the hybrid visual pipeline |
| Escalating past `-CoreOnly` | a failure needs a fuller run to localise, or the order's scope suggests one up front |

## Package dependency chain

`athena.core` (no deps) → `athena.contentmanagement` → `athena.shared`
(gameplay/runtime orchestration core) → `athena.gameplay` /
`athena.charactercontroller` / `athena.sceneslice`. A design decision that
would make a lower package depend on a higher one is wrong by construction —
check the direction before approving a contract, not just its shape.
Full map: `PACKAGE_ARCHITECTURE.md`.

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
`Tools/Run-UnityTests.ps1 -Platform EditMode -CoreOnly`.
Add `-Platform PlayMode -CoreOnly` when the change reaches runtime/session/
player flow. `status: DONE` requires both to pass; a compile-only check is
not a substitute for the test gate.

## Escalating past `-CoreOnly`

Drop `-CoreOnly` for the fuller suite when: the order's own `verification`
field says so, the change touches the crate/content pipeline directly (see
Known weak spots), or a `-CoreOnly` run passed but the change's blast radius
(per the dependency chain above) reaches a package the Core tag does not
cover. Note the escalation and why in the report's `risks`.
