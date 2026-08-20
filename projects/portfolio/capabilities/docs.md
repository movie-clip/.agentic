# Capability pack: docs — project `portfolio`

For the `docs-engineer` lane. Runs at close-out, after both gates pass.

Mirrors `portfolio/.claude/skills/update-docs/SKILL.md` — read that skill for
the full templates.

**Never run this lane on unverified work.** This lane propagates correctness
into the docs. Run it on a broken implementation and it propagates broken
claims into the project's sources of truth, which is worse than no docs at all.

---

## Index

Read this block first. You are not expected to read this file end to end — read
what your order touches. Reading one extra section is cheap; acting on a
convention you never read is not.

**Always read:** **Auto-update vs flag-for-human** · **What not to do** · **Definition of done for this lane**

| Section | Read it when |
|---|---|
| Where things live | you are looking for which doc owns a fact |
| The second close-out order: applying pack corrections | your order is a close-out pack-corrections order |
| Step 1 — Read the story and the diff | your order is a story close-out |
| Step 2 — Never tick an unsatisfied box | your order is a story close-out |
| You own the roadmap and the index — nobody upstream does | your order is a story close-out |
| Step 3 — The slice log | your order is a story close-out |
| Step 4 — Contract docs | your order changes a contract doc |

---

## Where things live

| Path | What lives there |
|---|---|
| `docs/product/stories/<story>.md` | status, ACs, tickets, last-updated |
| `docs/product/stories/README.md` | story index with status column |
| `docs/product/epic-roadmap.md` | epic snapshot table + slice log + epic header |
| `docs/product/current-product-state.md` | shipped-state inventory by tab/area |
| `docs/finance/financial-methodology.md` | formula sections |
| `docs/contracts/<area>-fields.md` | schema field tables (backend ↔ TS ↔ UI) |
| `docs/tech-debt-register.md` | deferred improvements |

## Auto-update vs flag-for-human

The split is deterministic-vs-judgment, and it is not negotiable.

**Auto:** story status → `Done`; `Last updated:` → today (ISO 8601); tick ACs and
tickets that the reviewer marked satisfied; story index status; epic snapshot
row; slice log entry; `current-product-state.md` entry; contract field table
when fields were added or removed; epic Active → Completed when every story is
done.

**Flag for a human:** any new methodology section, and any edit to an existing
one. Formula phrasing, citation choice and edge-case framing are judgment calls,
and `financial-methodology.md` is the source of truth every other doc defers to.

**Never:** create a PRD file. That belongs to story authoring.

## The second close-out order: applying pack corrections

You are the only lane that may write inside `<agenticRoot>` outside the run
dir, and only when a work order explicitly scopes you to
`<agenticRoot>/projects/portfolio/capabilities/` with
`<run_dir>/pack-corrections.md` as its input.

Each entry names a pack file, a premise in it that the code contradicts, and
replacement wording. Apply it:

- **Verify before applying.** The reporting agent saw one code path; check the
  claim against the code yourself. A correction that is itself wrong is worse
  than the stale line, because it arrives with a run behind it.
- **Apply the replacement wording**, not your own paraphrase. The agent that hit
  the friction phrased it in the terms that would have helped.
- **A correction that no longer reproduces gets recorded, not applied.** Say so
  in `handoff` — it usually means two runs disagreed and a human should look.

The packs are the fastest-decaying thing in the network: they name paths,
fixture modules, env flags and commands, and every one of those can silently go
false. When it does, the wrong line arrives at a specialist as a stated premise
in its work order. This order is the only mechanism that stops that, so an
unapplied correction is a real defect, not a tidy-up.

When you flag, produce an **editable suggestion** — file path, exact location,
proposed text. "Please update the methodology doc" is not a handoff; it is a
note to write the handoff later.

## Step 1 — Read the story and the diff

```bash
git diff main...HEAD --name-only
git log main..HEAD --oneline
```

| Changed path | Doc impact |
|---|---|
| `app/schemas/` | contract doc |
| `app/analytics/` | methodology doc (flag) |
| `app/api/routes/` | API surface in current-product-state |
| `features/portfolio/*.tsx` (non-test) | current-product-state + contract doc UI column |
| `features/portfolio/types.ts` | contract doc |
| `features/portfolio/portfolioAnalysisAdapter.ts` | none |

**Read the diff, not the story.** Document what shipped. Stories routinely come
out smaller or differently-shaped than written, and a doc describing the plan
rather than the code is the exact drift this lane exists to prevent.

## Step 2 — Never tick an unsatisfied box

If the reviewer marked any AC as `GAP` or `DRIFTED`, **abort and report**. The
story is not done, and ticking its boxes makes it permanently look done. This is
the one place where a docs error is unrecoverable by later inspection.

## You own the roadmap and the index — nobody upstream does

The story author does not touch `epic-roadmap.md` or `stories/README.md`, and
neither does the producer. Those files record what **shipped**, so they are
written here, at close-out, from the diff.

If you arrive and find a roadmap entry already exists for this story, that is a
finding: someone upstream wrote an intention into a state record. Report it in
`risks` and reconcile the entry against what actually shipped rather than
assuming it is correct.

Watch for two specific corruptions this causes: an epic marked `Active` while
its only story is still `Next phase`, and two epics marked active at once
because a new section was inserted above a closed one without flipping it.

## Step 3 — The slice log

`epic-roadmap.md` slice entries in this project carry real narrative weight —
read the existing ones before writing. They record not just what shipped but
what was *found*: premise corrections caught before implementing, defects
surfaced by the work, decisions deliberately not taken and why.

Row form:

```
| YYYY-MM-DD | US-X.Y | <what shipped + test count delta> |
```

Test totals come from the last verification run. Draft the one-liner from the
diff and the story; confirm with the user before writing.

If every story in the epic is now done, flip
`## Active Epic: Epic N — <title>` to `## Completed Epic: …`.

## Step 4 — Contract docs

For each schema change named in the backend lane's `contract_notes`, update
`docs/contracts/<area>-fields.md`: the backend field, the TS type, the UI
display. All three columns, or the traceability the doc exists to provide is
broken.

Every `contract_note` from every lane must land in a doc or be explicitly
dismissed with a reason in your report. An unabsorbed note is undocumented
drift.

## What not to do

- **Never invent a formula, a field, or a trust rule.** If the implementation is
  unclear, that is a `risks` entry, not a guess in a source-of-truth doc. A
  plausible-sounding wrong formula in `financial-methodology.md` is worse than
  an acknowledged gap, because everything downstream defers to it.
- **Do not tidy adjacent docs.** Out-of-scope doc changes hide the real diff.
- **Do not report success on a partial reconciliation.** Say which items landed
  and which were flagged.

## Definition of done for this lane

- [ ] Story status, ACs, tickets, `Last updated:` reconciled — nothing ticked that the reviewer did not confirm
- [ ] Story index and epic snapshot rows updated
- [ ] Slice log entry written in the house style, confirmed with the user
- [ ] `current-product-state.md` reflects the new user-visible surface
- [ ] Every `contract_note` from every lane landed or explicitly dismissed with a reason
- [ ] Methodology changes flagged as editable suggestions, never silently written
- [ ] Epic header flipped if the epic is now complete
