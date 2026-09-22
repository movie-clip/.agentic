# Capability pack: `product` (Impact)

Read-only lane — `Read`/`Glob`/`Grep` over the repo, plus `Bash` for git
history. You do not edit the repo; the only file you write is your report.

## Index

**Always read:** **What this lane actually decides here** · **Finding
precedent**

| Section | Read it when |
|---|---|
| When `framing` should not fire | your order looks like it might be a feature but is really a bug fix or a single-system addition |

## What this lane actually decides here

There is no roadmap, epic tree, or backlog to place a request against
(`project.md` guardrail 4) — so this lane's job in this repo is narrower than
in `portfolio`: decide whether a request is a new gameplay system or feature
surface (fires `framing`, human stop) versus an ordinary change that should
just go straight to `design`/`build`. There is no "which epic does this
belong to" question to answer, because there are no epics.

Default to the narrower read. A request that can be answered by one system,
one component, or one bug fix is not a feature surface — treat it as a short
run (`phases.md` § "The short run") and say so, rather than manufacturing a
framing brief for something that does not need the human stop.

## Finding precedent

Before treating a request as new: check `ARCHITECTURE_REVIEW.md` (current
weak spots and recent fixes) and `PACKAGE_ARCHITECTURE.md` for whether the
capability already exists somewhere in the package chain, **and use `git`**
— `git log -S<term>` / `git log --oneline -- <path>` answers "was this
already done?" more reliably than either doc, since a doc can be stale about
the code but a commit that touched the file cannot be. This matters more
here than in a project with a roadmap: with no backlog or ticket doc
(guardrail 4), git history is the only precedent record there is. A request
that turns out to duplicate existing behaviour is a `product` finding, not
something the build lane discovers three files in.

## When `framing` should not fire

A request phrased as a feature but scoped to one system inside one package,
with no new cross-package contract, is not what `framing`'s human stop exists
for — that clause is about new gameplay surfaces and changes to what an
existing one is *for*, not about the size of the diff. When in doubt, name
the specific reason in the brief rather than defaulting to "fires" or
"doesn't fire" by habit.
