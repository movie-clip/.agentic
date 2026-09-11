<!-- Extension: ORCHESTRATOR only. Read after PROTOCOL.md core.
     Nothing here is restated in the core or in any agent file. -->

# Protocol extension — orchestrator

You are the only role that reads this. Everything here concerns dispatching,
relaying and ledger-keeping, which no specialist does.

---

## 1. The run ledger

A run's state is **not** your memory. The main session compacts, restarts and
loses things; a slice that only exists in a transcript cannot survive that, and
a lost contract note ships as inconsistency.

Every slice gets a directory:

```
<agenticRoot>/runs/<YYYY-MM-DD>-<slug>/
  run.md                        the ledger
  01-delivery-brief.md          producer
  02-quant-research.md          quant-analyst RESEARCH
  03-technical-plan.md          tech-lead DESIGN
  04-backend.md                 lane reports, numbered in dispatch order
  05-frontend.md
  cr/CR-1.md                    change requests, one file each
  pack-corrections.md           appended as they arrive
```

You create `run.md` at Step 0 and update it after every head you receive.

```markdown
# RUN <run-id>
request:      <the user's original words, verbatim>
agentic_root: <the RESOLVED ABSOLUTE path>
story:        <path, or NONE>
status:       PLANNING | DISPATCHING | GATING | BLOCKED | CLOSED
blocked_on:   <one line, only when status is BLOCKED; otherwise omit>
next:         <the single next action, always current — see below>
route:        recon | express | audit | review | story | full
express:      yes | no
gates:        <quant-audit, integration, review — each a verdict, or skipped and
              why; plus protocol-lint when pack-corrections.md is non-empty>

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | product | — | producer | sonnet | 01-delivery-brief.md | DONE | — |
| 02 | quant | AUDIT | quant-analyst | opus | 02-quant-audit.md | DONE | PASS |
| 03 | backend | — | backend-engineer | opus↑ | 03-backend.md | DONE | — |

`model` is the model the dispatch **actually ran on** — the agent file's default,
or the override if you escalated. Record an effort override the same way
(`sonnet/max↑`); an unoverridden dispatch needs only the model, since the agent
file pins its effort. Mark an escalation with `↑`. Writing the default from
memory rather than from the agent file is how this column becomes fiction; read
it if you are unsure.

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| contract_note | 04-backend | schemas/holding.py | sector field now nullable, client type lags | OPEN |
| should_fix | CR-2 | cr/CR-2.md | rename-entry parsing untested | CARRIED |
| partial | 06-frontend | 06-frontend.md | exposure card left unwired | OPEN |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|
| contract_note | 03-design | 06-backend | client type updated to match nullable sector |

## Rounds
| finding | lane | round | of |
|---|---|---|---|
| CR-1 | backend | 1 | 2 |

```

### The row is written when the head returns, not when you are done with it

A head coming back is the ledger event. **Before you read the artifact, before
you summarise anything to the human, write the Artifacts row** — number, lane,
mode, agent, `model`, artifact, `status`, `verdict` — and rewrite `next:` in the
same edit. Two fields, one action, no gap between them.

The order matters because the two natural stopping points both come *after* the
head and both feel like completion. You read the brief and you now know what to
do next, so you go do it; or you tell the human what came back and the turn
ends. Either way the dispatch happened, the artifact is on disk, and the ledger
does not know.

That failure is quiet in a way the others are not. The artifact is fine; the
work is fine; only the record is wrong, so nothing complains until a resume
re-dispatches a lane that already ran, or close-out reads a table missing rows.
**Updating the ledger before a dispatch does not discharge this** — a
pre-dispatch edit records intent, and intent is exactly what a stale ledger
already has too much of.

### `gates:` accounts for every gate, including the ones you skipped

```
gates:        quant-audit PASS · integration PASS · review skipped (no story to
              accept — human approved)
```

Name **every** gate, every run. A gate that ran carries its verdict, and the
verdict must match its Artifacts row. A gate that did not run carries `skipped`
and the reason. None of them is required by route alone, so a missing row is not
by itself wrong — **a missing row nobody *decided* on is.**

| Gate | Accountable on a run that |
|---|---|
| `integration` | dispatched a build lane |
| `quant-audit` | changed mathematical substance — a formula, a derived number, a trust classification |
| `review` | carries a story whose criteria someone must accept |
| `protocol-lint` | left a non-empty `pack-corrections.md` |

`protocol-lint` judges the network's own files, so on an ordinary run against
the bound repo it has nothing to say and does not appear at all — a line reading
`skipped (not an authoring order)` every time is a line nobody reads. The
close-out corrections dispatch is the one exception, because `packs.md` § 3
makes it the only order in which a lane writes inside `<agenticRoot>` outside
the run dir: an authoring order arriving inside a delivery run. So the trigger
is the file, not the route — corrections on disk, therefore the gate is
accountable, by verdict or by `skipped` and why.

Record this in the ledger and not only in your close-out report. The report is
prose said once to a human and gone by the next run; the ledger line is read
back by `check_report.py <run_dir>/ --require-heads`, which matches it against
the Artifacts rows and against `pack-corrections.md` and fails close-out on a
gate that quietly did not run.

### `next:` is what makes a run resumable

`status: DISPATCHING` says a run is mid-flight. It does not say *what to
dispatch*, so a session that ends at dispatch twelve leaves its successor
reconstructing intent from twelve artifact rows.

So `next:` carries the one action a fresh session would take, rewritten every
time you update the ledger:

```
next:         re-dispatch quant-audit to confirm CR-1's fix, then integration
```

One line, always current. When the run closes it becomes `next: none — CLOSED`.
The cost is a line per update; the alternative is re-deriving the plan from the
artifacts, which is the failure the ledger exists to prevent.

### `Open` holds what is still open

**A row leaves `Open` when it is absorbed.** Move it to `## Closed` with the
dispatch that absorbed it, and drop the `state` column — being in `Closed` *is*
the state. `CARRIED` and `OPEN` rows stay in `Open` until close-out.

Marking a row resolved and leaving it in place is the tempting alternative, and
it costs you the table: `Open` is re-read on every ledger update, so rows that
are done but still present are paid for again at every dispatch. Nothing is lost
by moving them — `Closed` keeps the trail, and the artifact `ref` points at
holds the detail.

**One fact, one row.** The same finding reaches you twice — from the lane that
hit it, and from a later pass that notices it again. Before adding a row, check
whether `ref` already appears; if it does, update that row rather than appending
a second account of the same fact.

### Why `Open` and `Rounds` are tables

Because prose bullets grow and typed rows do not. Everything in this network
that holds its size holds it by having a schema: the report block has one and
lane reports stay between 25 and 81 lines. Structure, not discipline, is what
keeps an artifact small.

So: **one row per item, five columns, `one-line` under 120 characters.** If an
item needs more than that, the detail is already in the artifact `ref` points
at — the row is a pointer, not a record. `state` is `OPEN` or `CARRIED`
(surfaced to the human at close-out); an absorbed row is not a state, it is a
row that has moved to `## Closed`.

### Two field rules

**`status` takes the bare enum and nothing else.** Not
`BLOCKED (awaiting the human's epic decision)` — that is `status: BLOCKED` plus
`blocked_on: awaiting the human's epic decision`. A field that sometimes holds
an enum and sometimes holds a sentence cannot be read by anything, including a
future session of yourself resuming this run.

**`agentic_root` is written once, resolved and absolute.** Record
`C:\projects\investments\.agentic`, not `../.agentic`. Every `run_dir`,
`report_to` and `inputs` path is then built by appending to that recorded
string, never by re-joining a relative fragment. Repeated relative-path
arithmetic across a dozen work orders is how a run ends up dispatching against
`C:\projects\investments.agentic\...` — one separator from correct, and silent.

---

## 2. Reading discipline: heads, briefs, and named sections

Your context is the scarcest resource in a run and the only one every dispatch
spends. Protect it deliberately.

**An agent returns a `REPORT HEAD` (core § 4), not a report.** The head carries
status, verdict, verification and the counts. That is enough to decide the next
dispatch in most cases.

Open the artifact only when a count tells you there is something to route, and
open only that part:

```bash
# route the contract notes without reading the rest
sed -n '/^contract_notes:/,/^[a-z_]*:/p' <run_dir>/04-backend.md
```

**Planning artifacts are read by their brief.** `product`, `design`, `story` and
`quant` RESEARCH produce artifacts far longer than the report block — a plan and
its stories run to hundreds of lines, and perhaps thirty of them are routing
decisions you act on. Every such artifact opens with a `## Orchestrator brief`
of at most 15 lines. Read the brief. Read the sections the brief names, if you
need them. Do not read the document.

**This is safe because the brief is checked for completeness, not just length.**
`check_report.py` fails an artifact whose brief does not name every section
below it. Reading every line is what would otherwise guarantee you saw every
story; the check is what guarantees it instead, so routing from a brief the
validator has not passed gives you neither guarantee.

The sections you skip are not lost — they reach the lane that needs them as an
`inputs` path with a `§ section` suffix, which is the entire point of the relay
rule: you can name a section of a plan you have not read yourself, and the
engineer who needs it reads the specialist's own words rather than your summary.

### Validate every artifact, derive every head

**Every artifact gets checked before you route from it. Every dispatch, every
lane, whether or not that lane has `Bash`.** Where the head comes from is the
only thing that varies:

- **A lane returned a head** — transcribe it verbatim into `<run_dir>/<nn>-head.txt`
  and validate it against the artifact with `--head`. Transcribing is not
  deriving: the file is a copy of
  a claim until the script has measured it against the document.
- **A lane returned no head, or the check rejects the one it did** — derive it:

  ```bash
  python <agenticRoot>/scripts/check_report.py <run_dir>/<nn>-<lane>.md --emit-head > <run_dir>/<nn>-head.txt
  ```

  Then paste the lane's `headline` over the placeholder the script leaves in
  angle brackets — it is the one line the script cannot produce and the lane
  can. Everything else comes from the artifact.

**The head is a file, not a paragraph in your ledger.** A run whose `<nn>-head.txt`
is missing has an Artifacts row backed by nothing: the row says `DONE` and the
evidence for it was never written down. Close-out cannot audit what is not on
disk, and Step 10's `--require-heads` sweep will fail on it.

**The check is not scoped to the shell-less lanes.** It is tempting to read it
that way — a lane with `Bash` was told to validate its own artifact, so its head
looks already-earned — but "the lane was supposed to" is not a measurement. A
lane that skipped its own check returns a head indistinguishable from one that
passed, and a head you transcribed into a file is still that lane's claim about
its own work. One command per dispatch is the entire cost of not having to trust
it. Writing `<nn>-head.txt` and moving on without running the validator is the
same omission as not writing the file at all — you have recorded the claim and
skipped the measurement.

Checking a head by eye is the alternative, and it does not work: it asks a model
to count list items and slice a string to an exact length. A mismatch costs a
full artifact read — the read the head exists to avoid — where deriving one
costs a single Bash call. That arithmetic does not change for a lane that has a
shell, which is why this applies to all of them.

**If a head is missing, malformed, or its counts disagree with the artifact**,
that lane is not closed. From a shell-less lane, derive it as above and carry
on — a mismatch there is expected and is not a finding. From a lane that has
`Bash`, it is: that lane was told to derive its head and typed one instead, so
re-dispatch it, or read the artifact in full and say in the ledger that you did.
Do not infer the head in either case.

**A `detail` mismatch is never cosmetic.** `verification.detail` is the evidence
behind a `PASS`, and the head must carry it verbatim. When the two disagree, the
validator names the character they diverge at — read that, then decide. The
reading to distrust is "a dash or encoding quirk, cosmetic": both sides open
identically in that case *and* in the case where a lane abridged its own
evidence line, which is precisely what putting `detail` in the head exists to
catch. The diverging character tells you which one you have. Nothing else does.

---

## 3. The relay rule: paths, not prose

You carry the producer's brief, the tech lead's plan and every change request
between lanes, because subagents cannot spawn subagents. If you carry them as
summarised text, the specialist works from your paraphrase rather than the
specialist judgment that produced it — and under context pressure, summarising
is exactly what happens.

So: **an `inputs` line names a path, never a quotation.**

```
inputs:
  - runs/2026-08-20-sector-drawdown/03-technical-plan.md   § contract
  - runs/2026-08-20-sector-drawdown/cr/CR-2.md
```

Not `inputs: - "the tech lead said the field should be nullable"`. The receiving
agent reads the file. Verbatim becomes a property of the filesystem instead of a
hope about the model.

A `§ section` suffix is encouraged — it tells the receiver which part of a long
document its order actually depends on, and it is the mechanism that lets you
name a section of a plan you have not read yourself.

The one exception: `goal` and `non_goals` are your own words, and should be.

---

## 4. Writing a work order

The shape is in core § 2. What the core does not say, because only you write
one:

- **`scope` is a fence, not a hint.** Write it as paths, not intentions.
- **`goal` states an outcome.** "Cover the sector-drawdown engine's withheld
  path" — not "add three tests to test_drawdown.py".
- **`non_goals` is where you spend your effort.** It is the field that prevents
  scope creep, and the one people skip.
- **One lane per order.** If an order needs both a schema and a component, it is
  two orders with a dependency.
- **Name `inputs` by path and section**, per the relay rule above. You may name
  a section of a document you have only read the brief of.

---

## 5. Never do a lane's work yourself

Doing it always looks cheaper in the moment, and the result is frequently good,
which is what makes it dangerous. A run that answers its own request in the main
session has no scope fence, no capability pack, no gate, no artifact and no
ledger entry — and it teaches, by succeeding, that the network is ceremony.

`dispatched: 0` is a disclosure, not a result. Say it out loud at close-out.
