# Capability pack: `docs` (Impact)

Owns `Impact/*.md` and `Impact/Packages/*/PACKAGE_DOCUMENTATION.md`, and —
at close-out only — `<agenticRoot>/projects/impact/capabilities/**` when
applying a `pack-corrections.md` a lane emitted. No `Bash` on this lane — every
command a report references must have been run by the lane that ran it, not
by you.

## Index

**Always read:** **Doc map** · **The one rule that overrides normal docs
judgment** · **Definition of done for this lane**

| Section | Read it when |
|---|---|
| Close-out: applying pack corrections | your order is a close-out dispatch and a build lane emitted `pack_corrections` |

## Doc map

- `ARCHITECTURE_REVIEW.md` — current-state architecture review, read first
  for "what's true right now".
- `PACKAGE_ARCHITECTURE.md` — package map, "where do I find X" tables,
  workflows, code-quality checklist.
- `Packages/athena.*/PACKAGE_DOCUMENTATION.md` — per-package docs.
- `CHARACTER_ANIMATION_SETUP.md` — character animation setup.
- `Tools/TESTING.md` — test tooling detail, current `Core`-tagged fixtures.
- `AGENTS.md` (repo root) — the deep house-style source; `CLAUDE.md` is the
  entry point that points to it.

## The one rule that overrides normal docs judgment

**Never create a roadmap, backlog, or ticket doc in this repo — not even a
"future work" or "known issues going forward" section that reads like one.**
`project.md` guardrail 4 is absolute here, and this lane is the one most
likely to be tempted into it, since "what's left to clean up" is a natural
thing to write while reconciling docs with shipped code. If a close-out
surfaces genuinely open follow-up work, put it in the run's `handoff` or
`risks`, not in a file that outlives the run.

## Close-out: applying pack corrections

Same mechanism as every other project (`protocol/packs.md`): a build lane's
`pack_corrections` entry names a pack file and the false premise; apply the
exact replacement the entry gives, don't re-derive a different fix from
first principles, and don't touch a section the entry didn't name.

## Definition of done for this lane

- Every doc edit reflects what was actually shipped in this run, not what
  was planned — check `changed` in the build lanes' reports, not the order's
  `goal` line, for what to reconcile against.
- No new roadmap/backlog/ticket content was introduced, including inside an
  edit to an existing file.
- A `pack_corrections` entry was applied verbatim, or `risks` says why not.
