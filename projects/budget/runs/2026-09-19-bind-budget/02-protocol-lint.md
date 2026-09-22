REPORT 2026-09-19-bind-budget/02
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   claude plugin validate C:\projects\investments\.agentic\plugins\agentic-core
  result:    PASS
  detail:    Anchor: protocol/authoring.md (subjects are a project profile, a capability pack and a bound-repo CLAUDE.md — not authoring.md itself, so the rule text is the valid anchor). Manifest + all agent frontmatter parse. 5 of 5 round-1 findings cleared, 0 regressions against round 1 § What passed.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - All five round-1 findings are cleared. No blocking item remains and no change request is owed. See § Finding-by-finding.
  - The unrequested `project.md` § "Mechanical gates" bullet split is structurally clean — no index reference, always-read placement or table changed. See § The unrequested cleanup.
  - Round 1's three open `risks` (runs/README.md retention copy, the cross-pack MSTest gotcha duplication, budget/CLAUDE.md § Notes provenance) are untouched by these edits and still stand as they were filed.

risks:
  - `capabilities/docs.md:70-71` — the `Definition of done` still frames the lane's source as "every `pack_corrections` entry from this run's build lanes", while the rewritten § "Close-out order" now routes through `pack-corrections.md` and `packs.md`. Cosmetic drift, no rule cited.
  - `project.md:108`'s "see below" resolves to § "Why `quant` is not bound" (:139-141), a section whose name does not contain the word `protocol-lint`. FINDING 4's own remedy prescribed this wording, so it is the accepted fix, not a residue.
  - The `project.md` § "Mechanical gates" split leaves two bullets of 244 and 231 characters. Both still exceed authoring.md's 200-character instruction-file guidance, as most of the corpus does. Not raised, on round 1's reasoning.
  - `budget/CLAUDE.md:98-101` § Notes restates the `.gitignore`/tracked-`bin` fact the split `project.md` "Why:" bullet now carries. Pre-existing in both files before this round; authoring.md does not reach a bound repo's `CLAUDE.md`.
  - I re-read only the five edited regions plus the round-1 § What passed checks they could have disturbed, per this order's scope. Files outside that list were not re-opened.
  - No `.agentic.json` exists at or above cwd (`C:\projects\investments\.agentic`); cwd is itself the agenticRoot. Bound via the order's absolute paths and `budget/.agentic.json`. Same as round 1, not a scope file, not a finding.

## Orchestrator brief

- Verdict: PASS. All five round-1 findings cleared; nothing new raised.
- FINDINGS 1, 2, 3 (BLOCKING) are each satisfied in the exact shape round 1 prescribed, including the sibling-pack wording it pointed at.
- FINDINGS 4 and 5 (SHOULD_FIX) are satisfied and can be closed in the ledger's `Open` table rather than carried forward.
- The unrequested bullet split introduced no structural problem: no section added, renamed or removed, so no index edit was owed.
- Sections: § Finding-by-finding · § The unrequested cleanup · § Regression sweep.
- No change request is owed. No lane needs dispatching off this report.

## Finding-by-finding

| # | Round-1 severity | Edit checked | Result |
|---|---|---|---|
| 1 | BLOCKING | `budget/CLAUDE.md:23-45` | cleared |
| 2 | BLOCKING | `capabilities/docs.md:35-47` | cleared |
| 3 | BLOCKING | `capabilities/docs.md:54-63` | cleared |
| 4 | SHOULD_FIX | `project.md:108` | cleared |
| 5 | SHOULD_FIX | `capabilities/docs.md:14-18` | cleared |

**FINDING 1.** `budget/CLAUDE.md:25-40` is now five `-` bullets, order and bold
lead-ins unchanged. The trailing note at :42-45 reads "Absolute, and unnumbered
on purpose: the agentic network's profile (`.agentic/projects/budget/project.md`
§ Hard guardrails) carries the same five in the numbering the protocol cites".
That target resolves: `project.md:54-72` is the `1.`–`5.` list under a heading of
that exact name. `project.md:73-76`'s warrant — "**This is the system's only
numbered copy** — `CLAUDE.md` restates the same five unnumbered" — is now true as
written and needed no edit, as round 1 predicted. One numbered source remains, so
`REFUSED: guardrail 3` resolves to one rule.

**FINDING 2.** `capabilities/docs.md:37-41` now opens the always-read section
with the constraint and its resolution: no `Bash`, the order's `inputs` name the
upstream reports and their `changed:` sections are the diff, and `status:
BLOCKED` when no upstream reports are named. `docs-engineer.md:4` still reads
`tools: Read, Write, Edit, Glob, Grep`, so the premise the pack now states about
its own lane is accurate. The following paragraph was re-anchored to "those
diffs", so the intent-versus-shipped point now refers to an artifact the lane can
actually obtain. authoring.md § "A pack may not instruct a tool the lane does not
have" is satisfied: the section names no command at all, and the artifact it does
name is reachable with `Read`.

**FINDING 3.** `capabilities/docs.md:58-59` now reads "**How to apply an entry is
`protocol/packs.md` § Applying corrections**, which you read on this order. Work
from that file, not from memory of this one." The three-step copy is gone, so the
two rules it dropped — verify the premise is actually false, keep the `## Index`
accurate — reach the lane from their one home (`packs.md:36-38` and :51-53). The
retained point at :61-63 is the project-specific one round 1 said to keep, with
its `project.md` § "This profile is new" reference intact. The dropped step 1
(read each build lane's report) is not a loss: `packs.md:15-23` makes
`pack-corrections.md` the aggregate the close-out order carries as an input.

**FINDING 4.** `project.md:108` now ends "Not a delivery phase — see below". The
fact is at :139-141 in the same file: "Three gates, not four, therefore apply
here: `integration`, `review` when a story exists, and `protocol-lint` on an
authoring order." The pointer resolves within the file the reader is already in,
so it no longer sends a specialist to `phases.md`, which :1-2 and :7 declare
orchestrator-only. This is the second of the two remedies round 1 named, matching
`datoro/project.md:105`.

**FINDING 5.** `capabilities/docs.md:14` now reads `**Always read:** **Where
things live** · **Read the diff, not the story** · **Definition of done for this
lane**`, and the conditional table at :16-18 retains only the `Close-out order`
row, whose condition ("your order is a `close` phase dispatch applying
`pack-corrections.md`") is evaluable from the order alone. The four-doc update
map is therefore read on every dispatch, including a close-out order updating an
existing doc. authoring.md § "Indexing a pack or profile" rule 3 is satisfied,
and the pack now agrees with `datoro/capabilities/docs.md:20` on the same section
name.

## The unrequested cleanup

`project.md:155-162` is now two bullets where round 1 measured one of 472
characters:

- :155-158, the instruction — a lane's `changed:` list names only intentional
  edits under the five source directories, never incidental `bin/`/`obj/`/
  `artifacts/` diffs. 244 characters.
- :159-162, `**Why:**` — the `.gitignore` contents, the tracked build outputs,
  and that any `dotnet` command dirties them. 231 characters.

Nothing structural moved with it. No section was added, renamed or removed, so
`## Index` (:33-50) owed no change and got none; `## Mechanical gates` is still
one of the two always-read entries at :39, and the bullet stayed inside it rather
than migrating to a table. The surrounding bullets (:145-154, :163) are
unchanged. The instruction now survives a skim, which was the point.

No new problem introduced. The two residual notes are in `risks`: both halves
still exceed 200 characters, and the `**Why:**` half carries three facts rather
than one — an improvement on four in one bullet, not a fix of the underlying
rate, which the whole corpus shares.

## Regression sweep

Each row is a round-1 § What passed check that one of these six edits could have
disturbed. Rows that could not be touched by a `docs.md`, `project.md` or
`CLAUDE.md` edit were not re-derived.

| Check | Re-verified | Result |
|---|---|---|
| `claude plugin validate plugins/agentic-core` | re-run this round | passed — manifest and all agent frontmatter parse |
| Four-layer split | `docs.md`, `project.md` | holds. The FINDING 3 edit *removes* protocol procedure from the capability layer and replaces it with a citation — the correcting direction. No message shape, report block or role definition was added; no repo path or command reached an agent file |
| One rule, one home | `docs.md` § Close-out order vs `packs.md` § Applying corrections | holds. The duplicated procedure is gone; one home, one pointer |
| Tool premises — `docs` lane | `docs-engineer.md:4` re-read against `docs.md` | holds. `tools: Read, Write, Edit, Glob, Grep`. `docs.md` still names no command, and now states the `Bash` absence explicitly rather than assuming an artifact the lane cannot produce |
| Index present | `docs.md`, `project.md` | both still carry `## Index` |
| Index completeness | `docs.md` | all four `##` sections below the index — Where things live, Read the diff not the story, Close-out order, Definition of done for this lane — appear in it: three always-read, one table row. No orphans |
| Index completeness | `project.md` | unchanged; the cleanup added no section. Six sections, six index entries |
| Always-read placement | `docs.md` | improved by FINDING 5 and otherwise unchanged. The one remaining conditional row is evaluable from the order |
| Always-read placement | `project.md` | unchanged — `Hard guardrails` and `Mechanical gates` are still the two always-read entries |
| Lane routing table | `project.md:96-108` | unchanged except FINDING 4's trailing clause. All eleven rows still resolve to an agent file; every lane name is still a core § 2 enum value |
| Guardrail parity | `CLAUDE.md:25-40` against `project.md:56-71` | the same five, same order, same substance. Exactly one copy is numbered |
| Cross-file pointers | `docs.md` → `packs.md` § Applying corrections; `docs.md` → `project.md` § "This profile is new"; `CLAUDE.md` → `project.md` § Hard guardrails; `project.md:108` → below | all four resolve to a section that exists and carries the claimed fact |

Not re-opened, per this order's scope: `phases.md`, `product.md`,
`architecture.md`, `backend.md`, `frontend.md`, `testing.md`, `runs/README.md`,
the agent roster beyond `docs-engineer.md`, and the repo wiring files. Round 1's
verdicts on those stand; nothing in these six edits reaches them.
