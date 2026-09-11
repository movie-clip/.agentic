<!-- CORE. Every agent reads this file and nothing else by default.
     Role-scoped rules live in protocol/*.md — see the table below.
     One rule, one home: these are partitions, not copies. -->

# Agentic protocol — core

Read this in full. It is short on purpose.

Then read **your extension**, and only yours:

| Your role | Also read |
|---|---|
| orchestrator (main session) | `protocol/orchestrator.md` |
| `tech-lead`, `reviewer`, `quant-analyst` | `protocol/gates.md` |
| `protocol-linter` | `protocol/gates.md` **and** `protocol/authoring.md` |
| `docs-engineer`, on a close-out order | `protocol/packs.md` |
| every other lane | nothing else |
| authoring a new agent or pack | `protocol/authoring.md` — the rules you write to |

Reading an extension you were not sent to is not a violation, it is just cost.
Skipping yours is a violation.

---

## 1. Binding

Every specialist agent, as its **first action**, before reading any source file:

1. Find `.agentic.json`. Start at cwd and **walk up** until you find it or reach
   a filesystem root. cwd is not necessarily the repo root.
   ```json
   { "agenticRoot": "../.agentic", "project": "portfolio" }
   ```
   `agenticRoot` is relative **to the directory containing `.agentic.json`**.
   Resolve it against that directory, not against cwd.
2. Read `<agenticRoot>/PROTOCOL.md` — this file, in full.
3. Read your extension from the table above, if you have one.
4. Read `<agenticRoot>/projects/<project>/project.md` — **the `## Index` block
   first**, then the sections it names as always-read, then any section your
   order touches.
5. Read `<agenticRoot>/projects/<project>/capabilities/<your-lane>.md` the same
   way: index first, then the sections your order touches.
6. Only then start work.

No `.agentic.json` above cwd → **stop and report `BLOCKED`**. Do not guess the
project layout; a specialist working from inference is the failure mode this
network exists to prevent.

**On steps 4 and 5.** Packs and profiles are indexed so you can read what your
order needs instead of everything. Read a section you were unsure about rather
than skipping it — the cost of one extra section is trivial next to acting on a
convention you never saw. What is not acceptable is inventing a convention you
did not read.

Your pack and the repo's own docs (`CLAUDE.md`, `docs/`) overlap. The pack is
agent-facing and carries friction the repo docs do not record; the repo docs are
richer on the code itself. Read the pack first, and when they disagree on a
*fact about the code*, trust the code — then emit a `pack_corrections` entry.

---

## 2. Shape 1 — the work order (what you receive)

```
WORK ORDER <run-id>/<nn>
lane:        product | quant | recon | story | design | backend | frontend | test | docs | quant-audit | integration | review | protocol-lint
mode:        <tech-lead: DESIGN | INTEGRATION; quant-analyst: RESEARCH | AUDIT>
run_dir:     <agenticRoot>/projects/<project>/runs/<run-id>
report_to:   <agenticRoot>/projects/<project>/runs/<run-id>/<nn>-<lane>.md
story:       <path to story file, or NONE>
tickets:     <T-x.y.z, ...  or NONE>

goal:        <one sentence, outcome not method>

scope:
  - <file / dir / glob this order may touch>

inputs:
  - <path — a path, never a quotation>

definition_of_done:
  - <checkable statement>

non_goals:
  - <thing an eager agent would do that it must not>

verification:  <exact command(s) to run, or NONE if read-only>
```

What the fields bind you to:

- **`scope` is a fence, not a hint.** Anything outside it means stop and report,
  not proceed. Your `report_to` path and the run dir are in scope implicitly;
  nothing else under `<agenticRoot>` is.
- **`inputs` are paths. Open them.** They are named rather than quoted so that
  you read the specialist's own words instead of the orchestrator's summary.
- **`non_goals` are binding.** They name what an eager agent would do anyway.
- **`verification` is the command you must actually run**, not a description of
  one.

---

## 3. Shape 2 — the report artifact (what you write to `report_to`)

The full report is a **file**, not a message. Write this block to the
`report_to` path named in your order.

```
REPORT <run-id>/<nn>
status:      DONE | PARTIAL | BLOCKED | REFUSED
verdict:     PASS | FAIL | CHANGES_REQUESTED | NONE

changed:
  - <path> — <what changed, one line>

verification:
  command:   <what you ran>
  result:    PASS | FAIL | NOT_RUN
  detail:    <failure summary, or the counts on pass>

contract_notes:
  - <any schema / type / doc that now needs a matching change elsewhere>

pack_corrections:
  - <pack file> — <the false premise, and the exact replacement wording>

handoff:
  - <what the next lane needs: fixture names, prop shapes, route paths>

risks:
  - <anything you were unsure about, or a guardrail you had to interpret>
```

Every agent is granted `Write` for **exactly one purpose**: this artifact, under
the `run_dir` your order names. Read-only lanes (`scout`, `producer`,
`quant-analyst`, `tech-lead`, `reviewer`, `protocol-linter`) writing anywhere
else — including any file in the bound repo — is a protocol violation, not a
judgment call.

### Bullet discipline

One fact per bullet. The orchestrator routes bullets individually, so a
700-character bullet carrying four facts cannot be routed to four lanes.

| lane | target | ceiling |
|---|---|---|
| gate lanes — `integration`, `review`, `quant-audit`, `protocol-lint` | 200 | **400, enforced** |
| `recon`, `quant` RESEARCH | 400 | 600, advisory |
| everything else | 200 | 400, advisory |

**The ceiling blocks on a gate lane and advises everywhere else.** A gate's
bullets are *routed*: a finding becomes a change request, a `BLOCKING` item
becomes a dispatch. One that cannot be handed to a single lane is a structural
problem there, and only there — elsewhere a long bullet is read by a human in
context.

**`recon` and `quant` RESEARCH get more room** because a bullet there carries a
claim plus the `file:line` that proves it, and the citation is the point.

A bullet that needs a paragraph is several bullets. If it genuinely needs a
paragraph — a worked example, a table, a diff — put that below the block in a
named section, keep the bullet to the one-line fact, and **end the bullet with
`see § <section name>`**. The moment you add a section you also owe the artifact
a `## Orchestrator brief` naming it (§ 4); that is not a special case, it is the
same rule, and it is what keeps the section from being invisible to routing.

---

### When the order and your capability pack disagree

Your order is written by the orchestrator, which has less domain context than
your pack. So:

- **A numbered project guardrail wins, always.** An order that requires breaking
  one gets `status: REFUSED` naming the guardrail. This is not a judgment call.
- **A pack *convention* does not block the order.** Do what the order says, set
  `status: PARTIAL`, and name the conflict in `risks`: which pack rule, what the
  order asked, and what you did. The human decides which was right.

Silently following the order is the failure to avoid: a conflict nobody
downstream can see is a conflict that gets built on.

### You cannot delete or rename files

No lane has a delete tool, deliberately — deletion is the one repo edit with no
diff to review. A rename is a create plus a delete, so **you can only do half of
one.** Do the half you can (write the new file), leave the old one in place, and
report the other half as a `should_fix` naming the exact command:

```
handoff:
  - rename incomplete — run: git rm docs/product/stories/US-24.12-<slug>.md
```

Do not leave a tombstone file that redirects to the new one without saying so:
a stub nobody was told about is indistinguishable from a duplicate.

## 4. Shape 2H — the report head (what you *return*)

**Your final message is not the report.** It is the head: a fixed-size summary
whose job is to tell the orchestrator whether it needs to open the artifact, and
which part.

End your run with exactly this block and nothing after it:

```
REPORT HEAD <run-id>/<nn>
artifact:    <the absolute report_to path you wrote>
status:      DONE | PARTIAL | BLOCKED | REFUSED
verdict:     PASS | FAIL | CHANGES_REQUESTED | NONE
verification: PASS | FAIL | NOT_RUN
detail:      <verification.detail, verbatim, first 200 characters>
changed:     <integer — number of `changed` bullets>
contract_notes: <integer>
pack_corrections: <integer>
handoff:     <integer>
risks:       <integer>
blocked_on:  <one line, only when status is BLOCKED or REFUSED; otherwise omit>
headline:    <one sentence, under 200 characters, outcome not method>
```

The counts are the point. They are how the orchestrator knows, without reading
1,000 lines, that this lane produced two contract notes it must route and no
pack corrections. A count that disagrees with the artifact is worse than no head
at all — it causes work to be silently dropped.

`detail` is in the head for a different reason, and it is the one field here
that is not about cost. `verification: PASS` is a claim; `detail` is the
evidence — "802 passed" against "802 passed, 4 skipped, 1 xfail". If the head
carried only the verdict, then "DONE on work that ran a command and misread its
own output" would become uncatchable, because nothing would give the
orchestrator a reason to open the artifact.

**Derive the head. Do not type it.** This is a rule, not a preference:

```bash
python <agenticRoot>/scripts/check_report.py <report_to path> --emit-head
```

Fill in only what the output leaves in angle brackets — `headline`, and
`blocked_on` when the status is `BLOCKED` or `REFUSED`. Every other line comes
from the artifact and must arrive unretyped.

A head is a count of list items and a string sliced to an exact length. Those
are the two things a model cannot do reliably by inspection, and no wording
fixes that. The script counts; the lane judges.

Lanes with no `Bash` (`scout`, `docs-engineer`, `story-author`) cannot run this,
and are not asked to. The orchestrator validates every artifact and derives
every head before routing from it — `protocol/orchestrator.md` § "Validate
every artifact, derive every head" — including for lanes that do have `Bash`,
because a lane's own check is something it was told to run, not something you
can see it ran. Where a bound repo also wires `scripts/hooks/` into its
`.claude/settings.json`, both checks happen earlier and mechanically: the
artifact on every write, the head when you try to finish — which you cannot do
on a head that disagrees with its artifact, you are held and handed the derived
one. Write the head as described above regardless. A hook is local
configuration and the protocol is not; a lane that assumes an enforcement it
cannot see is the failure this section exists to prevent.

**Why the head and not the body.** The orchestrator's context is the scarcest
resource in a run, and it is the one thing every dispatch spends. A body
returned in full is paid for twice: once written to disk, once again in the
coordinator's window, where most of it will never be routed anywhere. The head
is the reference; the artifact is the content.

### Artifacts with a body beyond the block

Planning lanes (`product`, `design`, `story`, `quant` RESEARCH) produce
artifacts far longer than the report block — story sets, technical plans,
metrics inventories. Those artifacts **must** open with:

```markdown
## Orchestrator brief
<15 lines maximum. What a dispatcher needs to route from this document:
 the decisions taken, the lane split, the named sections below and what
 each contains. Not a summary of the reasoning — an index with verdicts.>
```

The orchestrator reads the brief and the sections the brief names. It does not
read the document end to end, and it does not need to: the sections that matter
downstream travel as `inputs` paths to the lanes that will actually use them.

---

## 5. The three result fields are not the same thing

| Field | Question | Who fills it |
|---|---|---|
| `status` | Did this **order** run to completion? | every lane |
| `verdict` | What is the **judgment** this lane was asked for? | gate lanes only — everyone else writes `NONE` |
| `verification.result` | What did the **command** print? | every lane that ran one |

A gate that completed its review and found problems is `status: DONE` +
`verdict: FAIL` (reviewer) or `verdict: CHANGES_REQUESTED` (tech lead
INTEGRATION). It is **not** `status: PARTIAL` — the order succeeded; the thing
it judged did not.

Only `tech-lead` in `INTEGRATION` mode may emit `CHANGES_REQUESTED`. Only
`reviewer`, `tech-lead`, `quant-analyst` in `AUDIT` mode and `protocol-linter`
may emit `PASS` or `FAIL`. Every other lane writes `verdict: NONE`.

## 6. Field discipline

- `status: PARTIAL` is honourable. Claiming `DONE` on unverified work is the
  single most expensive failure in this network.
- **`status: DONE` requires `verification.result: PASS`**, unless the order's
  `verification` field was `NONE`.
- `REFUSED` when the order contradicts a project guardrail — say which one.
- `contract_notes` is how cross-lane drift gets caught. A backend agent that
  changes a schema **must** emit a contract note naming the client type and the
  contract doc that now lag.
- Empty sections stay in with a **bare** `- none`. Silence is ambiguous, and
  `- none — because X` is counted as one real entry, so your head advertises
  work that does not exist. If the reason matters, it is a `risks` bullet.

## 7. The report is checked, not trusted

```bash
python <agenticRoot>/scripts/check_report.py <report_to path> --lane <lane>
```

Run this on your own artifact before returning — **if your `tools:` includes
`Bash`.** Exit 0 means it is routable; non-zero prints exactly what is wrong.

**If you have no `Bash`, you cannot run it, and that is expected.** `scout`,
`story-author` and `docs-engineer` are deliberately shell-less; § 4 says what
happens to your artifact and your head instead. Put your effort into the
artifact rather than auditing it by hand, and say nothing about any of it in
`risks`: a bullet spent apologising for a tool you were never granted is a
bullet the next lane has to read for nothing.

It checks that the enums are real values, that every section is present, that an
empty section says `- none`, that `DONE` is not paired with `NOT_RUN` on an
order that named a command, that a non-gate lane has not issued a verdict, that
bullets are within length, and that your head's counts match your artifact. It
does **not** check whether the content is true — no script can. It checks that
the report is routable.
