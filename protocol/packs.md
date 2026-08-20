<!-- Extension: DOCS LANE, on a close-out order. Read after PROTOCOL.md core. -->

# Protocol extension — pack maintenance

The capability packs are the fastest-decaying artifact in the network. They name
paths, fixture modules, environment flags and commands — every one of which can
silently go false, after which an agent works from a confidently-stated wrong
premise that arrived in its order as fact.

So the loop is closed mechanically:

1. Any agent that finds its pack contradicted by the code emits a
   `pack_corrections` entry naming the pack file, the false premise, and the
   **exact replacement wording**. Not a complaint — a patch.
2. The orchestrator appends every such entry to `<run_dir>/pack-corrections.md`
   as it arrives.
3. At close-out the orchestrator dispatches the `docs` lane with that file as an
   input and `<agenticRoot>/projects/<project>/capabilities/` in scope, to apply
   them. **This is the only order in which a lane may write inside
   `<agenticRoot>` outside the run dir.**
4. Unapplied corrections are surfaced to the human alongside `SHOULD_FIX` items.

A pack correction is not a side note. It is frequently the most valuable thing
an order produces, because it prevents every future dispatch from repeating the
same false framing.

---

## Applying corrections

You are the docs lane holding `pack-corrections.md`. For each entry:

- **Verify the premise is actually false** before editing. A correction is a
  claim like any other, and the lane that emitted it may have been looking at
  the wrong file. Check the code. If the premise holds, record that in `risks`
  and leave the pack alone.
- **Apply the replacement wording as given**, into the section it belongs in.
  Do not rewrite the surrounding paragraph while you are there.
- **Keep the pack's `## Index` accurate.** If a correction adds, removes or
  renames a section, the index must move with it, or every future reader
  navigating by index will miss it.
- If a correction contradicts another correction in the same file, apply
  neither, and report both in `risks` for the human.

## Keeping a pack readable by index

Packs are read by index now, not end to end. That puts two obligations on
whoever edits one:

- Every section is findable from the index by the name a lane would search for.
- A fact belongs in exactly one section. A gotcha duplicated into two sections
  will be corrected in one of them and go stale in the other — the same drift
  the single-copy protocol rule exists to prevent, one layer down.
