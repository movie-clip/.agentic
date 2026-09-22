# Capability pack: docs — project `datoro`

For the `docs-engineer` lane. Runs at close-out, after the `integration` gate
(and `review`, when a story exists) passes.

**Never run this lane on unverified work.** This lane propagates correctness
into the docs. Run it on a broken implementation and it propagates broken
claims into the project's sources of truth, which is worse than no docs at all.

---

## Index

Read this block first. You are not expected to read this file end to end — read
what your order touches. Reading one extra section is cheap; acting on a
convention you never read is not.

**Always read:** **Where things live** · **What not to do** · **Definition of done for this lane**

| Section | Read it when |
|---|---|
| Step 1 — read the diff, not the story | any close-out order |
| Story close-out | your order is a story close-out |
| The second close-out order: applying pack corrections | your order is a close-out pack-corrections order |

---

## Where things live

| Path | What lives there |
|---|---|
| `docs/development.md` | local setup, env vars, structure, AI-insights workflow |
| `docs/testing.md` | unit/e2e/load testing model |
| `DEPLOYMENT.md` | deployment and pre-deploy checks |
| `docs/operations.md` | analytics, admin endpoints, operations notes |
| `docs/PROJECT_REVIEW_PLAYBOOK.md` | recurring review checklist |
| `docs/reviews/` | archived, dated review and audit records |
| `AGENTS.md` | house style; not owned by this lane's routine edits — treat as stable unless an order specifically targets it |

There is no `docs/product/`, no `ROADMAP.md`, no contract-doc directory here.
Do not invent one to mirror `portfolio` — if an order asks you to write a
contract-tracking doc that does not exist yet, that is a new-document decision
for the human, not a routine close-out edit; say so in `handoff` rather than
creating it.

## Step 1 — read the diff, not the story

**You have no `Bash`, so you cannot run `git diff` yourself.** You do not need
to: your order's `inputs` name the upstream lanes' reports, and their
`changed:` sections **are** the diff — one line per file, written by the lane
that touched it.

| Changed path | Doc impact |
|---|---|
| `server/routes/**`, `server/schemas/**` | `docs/operations.md` if it adds an admin/analytics-visible endpoint; otherwise usually none |
| `prisma/schema.prisma` | note the model change in `docs/development.md` only if it changes local setup (a new required env var, a new required service) |
| `src/**` (new user-facing surface) | none by default — this repo has no shipped-state inventory to update; say so rather than inventing one |
| `docs/development.md`-listed commands (`package.json` scripts) | `docs/development.md` and `AGENTS.md`'s command tables, if a script was added, renamed or removed |

If your order names no upstream reports and you genuinely cannot tell what
shipped, that is `status: BLOCKED` — not a guess.

## Story close-out

Per `phases.md`, most runs here have no story. When one does exist:

- Never tick an acceptance criterion the reviewer marked `GAP` or `DRIFTED` —
  abort and report instead.
- There is no generated roadmap index to regenerate here. If the story lives
  as a standalone file (the human's own convention, not a network default),
  update its own status field from the diff; do not invent a second index.

## The second close-out order: applying pack corrections

This order scopes you to `<agenticRoot>/projects/datoro/capabilities/`, with
`<run_dir>/pack-corrections.md` as its input. Nothing else under
`<agenticRoot>` is in scope on it.

**How to apply an entry is `protocol/packs.md` § Applying corrections**, which
you read on this order. Work from that file, not from memory of this one.

This project's packs are new and thin by design (see `project.md`'s opening
note) — expect more corrections here in the first several runs than a mature
project like `portfolio` generates, and treat that as the loop working, not as
a finding about the packs' quality.

## What not to do

- **Never invent a field, an endpoint, or a guardrail.** If the implementation
  is unclear, that is a `risks` entry, not a guess written into a doc.
- **Do not tidy adjacent docs.** Out-of-scope doc changes hide the real diff.
- **Do not report success on a partial reconciliation.** Say which items
  landed and which were flagged.
- **Do not create `docs/product/**` structure, a contract-doc directory, or a
  generated roadmap** to mirror another project in this network. This project
  does not have that model; introducing it is a decision for the human.

## Definition of done for this lane

- [ ] `docs/development.md`, `docs/operations.md`, `AGENTS.md`'s command
      tables reconciled against any script or env-var change in the diff
- [ ] Every `contract_note` from every lane landed or explicitly dismissed
      with a reason
- [ ] No new document structure invented without a `handoff` flag to the human
- [ ] Story status reconciled against the diff, when a story exists — nothing
      ticked the reviewer did not confirm
