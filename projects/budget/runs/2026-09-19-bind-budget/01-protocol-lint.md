REPORT 2026-09-19-bind-budget/01
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   claude plugin validate C:\projects\investments\.agentic\plugins\agentic-core
  result:    PASS
  detail:    Anchor: protocol/authoring.md (subject is a new project profile, not authoring.md itself, so the rule text is the valid anchor). Manifest + all 11 agent frontmatter blocks parse. 12 scope files read end to end. 3 BLOCKING, 2 SHOULD_FIX.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - FINDING 1 (BLOCKING, budget/CLAUDE.md:25-39) — the five guardrails are restated as a numbered 1-5 list, while project.md:74-76 asserts CLAUDE.md carries them unnumbered and that the profile holds "the system's only numbered copy". Two numbered copies, one of them uncited. See § FINDING 1.
  - FINDING 2 (BLOCKING, capabilities/docs.md:36-42) — § "Read the diff, not the story" tells the docs lane to work from the build lanes' diffs; `docs-engineer.md` declares no `Bash`, so it cannot produce one, and the pack never says where the diff comes from. See § FINDING 2.
  - FINDING 3 (BLOCKING, capabilities/docs.md:49-59) — § "Close-out order" states its own three-step procedure for applying pack corrections and never cites `protocol/packs.md` § "Applying corrections". The copy drops two of that section's rules. See § FINDING 3.
  - FINDING 4 (SHOULD_FIX, project.md:108) — the `protocol-lint` routing row ends "Not a delivery phase — see `phases.md`", and `phases.md` never mentions `protocol-lint`. See § FINDING 4.
  - FINDING 5 (SHOULD_FIX, capabilities/docs.md:18) — `Where things live`, the four-doc update map, is filed conditional on "you are adding a doc"; a close-out order updating an existing doc evaluates that as false. See § FINDING 5.

risks:
  - `project.md:155-161` — the "Working-tree noise" bullet is 472 characters carrying four facts, the longest bullet in `projects/budget` or `projects/datoro` (datoro's longest is 350). Not raised as a finding, on round 1 of `2026-09-17-bind-datoro`'s reasoning. See § Bullet lengths.
  - `runs/README.md:13-18` carries the retention copy that `2026-09-17-bind-datoro/02` left open as a SHOULD_FIX. budget adopted the post-fix wording ("a network-wide policy, not a budget-specific one"), so this is the same open item, not a new one. Fixing it edits `protocol/`, outside this scope.
  - `phases.md` carries no counterpart to `datoro/phases.md`'s note that `quant-audit` has no row and why. The reason is findable in `project.md` § "Why `quant` is not bound", which the orchestrator reads alongside, so not raised as a finding.
  - The MSTest parallelization and Release-CI gotchas appear in both `backend.md` (:105-113) and `testing.md` (:62-71). Cross-pack and read by different lanes, so not a one-home violation — but a `pack_corrections` entry applied to one will not reach the other.
  - `budget/CLAUDE.md`'s `## Notes` bullets 1 and 3 (the removed `.github/copilot-instructions.md`, the stray `.claude/worktrees/` entry) are provenance that changes no lane's behaviour and is paid for on every session. Worth a human's eye.
  - I cite no rule against that provenance and raise no finding: authoring.md § "Writing for the reader you actually have" scopes itself to `PROTOCOL.md`, `protocol/`, `projects/`, `agents/` and `skills/`, and does not reach a bound repo's `CLAUDE.md`.
  - I did not open `C:\projects\investments\budget\src` or `tests`, per the order's non_goals. Every path, use-case name, migration filename and doc title these packs assert is unverified by me — this gate judges authoring, not fact.
  - No `.agentic.json` exists at or above cwd (`C:\projects\investments\.agentic`). I bound by the order's absolute paths and `budget/.agentic.json`, which resolves to this agenticRoot. Not a scope file, so not a finding.

## Orchestrator brief

- Verdict: FAIL. Three BLOCKING findings, two SHOULD_FIX. Two of the three BLOCKING sit in one file, `capabilities/docs.md`.
- The profile's structure is sound: every index block is complete, every conditional condition but one is evaluable, the lane map and the phase table both resolve, and no pack names a tool its lane lacks except the one in FINDING 2.
- Owner for FINDINGS 2-5: whichever lane authored the profile. FINDING 1 is an edit to `C:\projects\investments\budget\CLAUDE.md`, a bound-repo file — scope-fence it separately.
- Sections: § FINDING 1 · § FINDING 2 · § FINDING 3 · § FINDING 4 · § FINDING 5 · § What passed · § Bullet lengths.
- FINDINGS 2 and 3 touch the same file and are dispatchable in one order. FINDING 1 is independent.

## FINDING 1

`C:\projects\investments\budget\CLAUDE.md:23-40` — `## Hard guardrails` is a
numbered list, `1.` through `5.`, identical in substance to
`projects/budget/project.md:54-72`.

`projects/budget/project.md:73-76` says:

```
An order that requires breaking one of these gets `status: REFUSED` naming the
guardrail. **This is the system's only numbered copy** — `CLAUDE.md` restates
the same five unnumbered, so a session working the repo outside the network
still sees them and a cited number still resolves to exactly one rule.
```

**Rule:** `protocol/authoring.md` § "One rule, one home" — "place it in exactly
one file". The guardrails are a deliberate, declared exception to that rule, and
the sentence above is the entire warrant for the exception: the duplication is
safe *because* only one copy is numbered.

**Why it matters.** The warrant is now false, and false in the direction that
breaks it. `CLAUDE.md` is loaded into every dispatched lane at startup —
`project.md:6-11` says so and tells lanes to treat it as read — so a lane citing
`REFUSED: guardrail 3` has two numbered sources in context, not one. Today they
agree. The moment either list gains, loses or reorders an entry, a cited number
resolves to two different rules depending on which copy the reader anchored on,
and nothing in the network compares them.

`datoro` gets this right and is the pattern to copy. `datoro/CLAUDE.md:9-24`
uses unnumbered bullets and closes at :26-30 with:

```
Absolute, and unnumbered on purpose: the agentic network's profile
(`.agentic/projects/datoro/project.md` § Hard guardrails) carries the same five
in the numbering the protocol cites, so a `REFUSED: guardrail 3` from a
dispatched lane names exactly one thing.
```

**What would satisfy it:** convert `budget/CLAUDE.md:25-39` from `1.`–`5.` to
`-` bullets, keeping the order and the bold lead-ins unchanged, and replace the
trailing line at :42 with the two-sentence note above, retargeted at
`.agentic/projects/budget/project.md` § Hard guardrails. `project.md` is then
correct as written and needs no edit.

## FINDING 2

`projects/budget/capabilities/docs.md:36-42`:

```
## Read the diff, not the story

Document what the build lanes' diffs actually show — the migration file, the
use-case's real output shape, the view model's real behavior — not what the
delivery brief predicted before implementation.
```

This is an always-read section (`docs.md:14`), so every dispatch of this lane
reads it.

**Rule:** `protocol/authoring.md` § "A pack may not instruct a tool the lane
does not have" — "Before writing a command into a capability pack, open the
agent file and read its `tools:` line."

`plugins/agentic-core/agents/docs-engineer.md:4`:

```
tools: Read, Write, Edit, Glob, Grep
```

No `Bash`. The lane cannot run `git diff`, `git show` or `git status`.

**Why it matters, not just which rule.** The section names the only thing this
lane's `Definition of done` measures against — `docs.md:63`, "Updated doc
matches the actual diff, not the original delivery brief" — and then names an
artifact the lane has no instrument to obtain. authoring.md predicts exactly
what happens next: "an agent that cannot run a command tends to substitute
something and mention it in `risks`, not to emit a correction. In the first
closed run the docs lane hit exactly this three times." The available
substitutes are both wrong here: reading `src/**` current-state shows what the
file says today, not what this run changed, and falling back on the delivery
brief is precisely what the section exists to forbid.

The instrument does exist, and the sibling pack names it.
`datoro/capabilities/docs.md:48-51`:

```
**You have no `Bash`, so you cannot run `git diff` yourself.** You do not need
to: your order's `inputs` name the upstream lanes' reports, and their
`changed:` sections **are** the diff — one line per file, written by the lane
that touched it.
```

and closes at :64-66 with "If your order names no upstream reports and you
genuinely cannot tell what shipped, that is `status: BLOCKED` — not a guess."

**What would satisfy it:** open `budget/capabilities/docs.md` § "Read the diff,
not the story" with that constraint stated and resolved — no `Bash`, the
upstream reports' `changed:` sections are the diff, `BLOCKED` when the order
names none — before the existing paragraph about intent versus what shipped.

## FINDING 3

`projects/budget/capabilities/docs.md:49-59`:

```
## Close-out order

When dispatched at `close` with a `pack-corrections.md` to apply:

1. Read every build lane's report from the run for a `pack_corrections` entry.
2. Apply each entry to the exact capability pack section it names — a
   correction to `backend.md`'s Reuse section does not become a rewrite of
   the whole file.
3. Leave sections the run's lanes did not touch alone, even if they look thin
```

**Rule:** `protocol/authoring.md` § "One rule, one home", and § "The four-layer
split" — the Capability layer holds "paths, frameworks, fixtures, commands,
gotchas, external anchors", not procedure the protocol already owns.

Step 2 is `protocol/packs.md` § "Applying corrections", second bullet: "**Apply
the replacement wording as given**, into the section it belongs in. Do not
rewrite the surrounding paragraph while you are there." That file is the docs
lane's protocol extension on exactly this order — `PROTOCOL.md:16` routes
`docs-engineer`, on a close-out order, to read it.

**Why it matters.** This copy is lossy, and the losses are the two rules that
prevent damage. `packs.md` § "Applying corrections" opens with "**Verify the
premise is actually false** before editing. A correction is a claim like any
other, and the lane that emitted it may have been looking at the wrong file."
It closes with "**Keep the pack's `## Index` accurate.** If a correction adds,
removes or renames a section, the index must move with it, or every future
reader navigating by index will miss it." Neither survives into `docs.md`'s
three steps. A lane that reads this section as its instructions — which is what
a numbered procedure in its own pack reads as — applies unverified corrections
and leaves the index behind.

`datoro/capabilities/docs.md:76-79` shows the shape that does not drift:

```
**How to apply an entry is `protocol/packs.md` § Applying corrections**, which
you read on this order. Work from that file, not from memory of this one.
```

**What would satisfy it:** replace steps 1 and 2 with that pointer. Keep step 3
— "leave sections the run's lanes did not touch alone, even if they look thin"
plus the reference to `project.md` § "This profile is new" — because that one is
a fact about *this* project's packs and belongs in the capability layer.

## FINDING 4

`projects/budget/project.md:108`, the last row of `## Lane routing`:

```
| protocol-lint | `protocol-linter` | — | **authoring gate**: network files under `<agenticRoot>` against `protocol/authoring.md`. Not a delivery phase — see `phases.md` |
```

`grep -n "protocol-lint" projects/budget/phases.md` returns nothing. The word
does not appear in the file, and the `## Phases` table has no row for it.

**Rule:** `protocol/authoring.md` § "Indexing a pack or profile", rule 1 —
"Every section is findable by the name a lane would search for." A cross-file
pointer is how one-rule-one-home stays navigable; one that resolves to nothing
is worse than no pointer, because a reader who follows it and finds an absence
cannot tell whether the claim is wrong or the file is incomplete.

**Why it matters.** The claim the pointer supports — that `protocol-lint` is not
a delivery phase — is true, and `phases.md`'s table not carrying the row is the
evidence for it. But the row is aimed at a reader deciding which lane owns a
piece of work, and `phases.md` is declared orchestrator-only at :1-2 and :7. So
the pointer sends a specialist to a file its own header tells it not to read, to
confirm a fact by its absence.

The statement does exist in `project.md` itself, at :139-141: "Three gates, not
four, therefore apply here: `integration`, `review` when a story exists, and
`protocol-lint` on an authoring order."

**Severity is SHOULD_FIX:** nothing reads this cell mechanically and no lane is
misrouted by it.

**What would satisfy it:** change the trailing clause to name the section that
actually carries the fact — `Not a delivery phase — see § "Why quant is not
bound"` — or use `datoro/project.md:105`'s wording, `see below`, which resolves
within the same file.

## FINDING 5

`projects/budget/capabilities/docs.md:14-19`, the `## Index` block:

```
**Always read:** **Read the diff, not the story** · **Definition of done for this lane**

| Section | Read it when |
|---|---|
| Where things live | you are adding a doc, or looking for where one lives |
```

`Where things live` (:23-34) is a four-row table mapping each of this repo's
docs to the change that obliges an update — `PROJECT_GUIDE.md` when a flow or
the category model changed, `TECHNICAL_DESIGN.md` when a use case or the data
model changed, and so on.

**Rule:** `protocol/authoring.md` § "Indexing a pack or profile", rule 3 — "A
section goes in 'always read' unless the agent can evaluate its condition
before reading it."

**Why it matters.** The stated condition is about *adding* a doc or *locating*
one. The lane's actual close-out question is neither: it is "this run changed a
migration and a view model — which of the four docs now lag?" That question is
what the section answers and it is not what the condition describes, so a lane
dispatched to update existing docs reads the condition, correctly judges it
false, and skips the table that decides its entire scope. It then falls back on
`## Definition of done` (:63-69), which names `RELEASE_NOTES.md` and the
four-file constraint but not the mapping — so the choice of which doc to edit
gets made from the repo's directory listing instead of from the pack.

`datoro/capabilities/docs.md:20` places its equivalent `Where things live`
under **Always read**, not in the table. Two docs packs in the same network
disagree about the same section name.

**Severity is SHOULD_FIX:** the fallback path produces a plausible edit rather
than a wrong one, and FINDING 2 is the blocking defect in this lane's
always-read set.

**What would satisfy it:** move `Where things live` out of the table and into
the `Always read:` line at `docs.md:14`, beside the two sections already there.

## What passed

Recorded so the next round does not re-derive it.

| Check | Result |
|---|---|
| `claude plugin validate plugins/agentic-core` | passed — manifest and all 11 agent frontmatter blocks parse |
| Model / effort declarations | not applicable — no agent file in scope. The roster's 11 files all declare both; none is `inherit` or `fable`; `protocol-linter` and `quantitative-researcher` are the two `opus` lanes, per authoring.md's table |
| Four-layer split | no message shape, report block or role definition in any budget pack. No repo path, framework or command reached an agent file — none was edited |
| Tool premises — `Bash` lanes | `architecture.md`'s `dotnet` commands → `tech-lead` (has `Bash`); `testing.md`'s eight `dotnet test` forms → `test-engineer` (has `Bash`); `backend.md`'s `dotnet build` → `backend-engineer` (has `Bash`). `product.md` and `frontend.md` name no command |
| Tool premises — no-`Bash` lanes | `docs.md` names no command, but see FINDING 2 — the premise is the artifact, not the command |
| Tool premises — MCP | `grep -rn "mcp__" projects/budget` returns one hit, `project.md:116-120`, which *denies* the grant. `budget/.mcp.json` does not exist, matching the claim. No lane is told to call an `mcp__project__*` tool |
| Index present | all seven indexed files carry `## Index`; `phases.md` carries `## Contents`, correct per authoring.md's full-read exception |
| Index completeness | every `##` section in `project.md` (6), `product.md` (6), `architecture.md` (5), `backend.md` (6), `frontend.md` (5), `testing.md` (5) and `docs.md` (4) appears in that file's index, as always-read or as a table row. No orphans |
| `phases.md` `## Contents` | names all five sections below it |
| Always-read placement | `backend.md:20` has `Reuse` and `Gotchas` always-read; `testing.md:16` has `Gotchas`; every pack has its `Guardrails, in code terms` always-read. These are the rule-3 traps and all are placed correctly. The one exception is FINDING 5 |
| Repo wiring | `budget/.agentic.json` resolves `../.agentic` to this agenticRoot with `"project": "budget"`, matching `projects/budget/`. `.claude/settings.json` is structurally identical to `datoro/.claude/settings.json`; both hook scripts and the `agentic-core@agentic` plugin exist |

**Lane routing (`project.md:96-108`) against `plugins/agentic-core/agents/`.**
All eleven rows resolve to a file in that directory, and the two mode
annotations are the two core § 2 allows for `tech-lead`: `design` → DESIGN,
`integration` → INTEGRATION. Every lane name in the table is a value from core
§ 2's `lane:` enum. `quantitative-researcher` is the one roster agent not
bound, and `project.md` § "Why `quant` is not bound" (:122-141) accounts for it
rather than leaving it unexplained.

**`phases.md` `## Phases` against `protocol/orchestrator.md` § 2.** Rows appear
in § 2's dependency order: ground-truth → framing → specification → design →
build → verify → close. No phase is out of order and no row names a phase § 2
does not define. Both `verify` rows carry a lane `check_report.py` can read —
`integration` and `review`. `intake` has no row, correct on the same grounds
`datoro` and `tradingview` omit it.

**Pack-to-lane coverage.** `project.md`'s routing table names a pack for six
lanes; all six files exist under `capabilities/`, and each opens by naming the
lane it belongs to. `architecture.md` serves both `tech-lead` modes from one
file and says why at :3-6. `recon`, `story` and `review` are packless, matching
`datoro`.

## Bullet lengths

Measured across the eight indexed profile files, joining continuation lines:

| Files | bullets over 200 chars | longest |
|---|---|---|
| `projects/budget` | 17 | 472 (`project.md:155`) |
| `projects/datoro` | 16 | 350 (`project.md:139`) |

Not raised as a finding, on the reasoning round 1 of `2026-09-17-bind-datoro`
set out and round 2 upheld: `authoring.md` states the 200-character
instruction-file limit without the enforced/advisory split core § 3 gives
report bullets, so there is no basis in the rule text for failing on it, and
failing budget for a rate the whole existing corpus shares would be a change to
the standard rather than an application of it.

One bullet is worth a human's eye anyway. `project.md:155-161`, at 472
characters, is the longest in either profile and carries four separable facts:
what `.gitignore` excludes, that `bin/`/`obj/`/`artifacts/` are tracked, that
any `dotnet` command dirties them, and what a lane's `changed:` list may
therefore contain. The fourth is the instruction; the first three are its
justification. Splitting it into an instruction bullet and a why-bullet would
make the instruction survive a skim, which at 472 characters it currently does
not.
