<!-- Single source of truth for the agentic message contract.
     Every agent reads this during binding. Nothing else in the network
     restates it — the agentic-protocol skill and every agent file point here. -->

# Agentic protocol

Version 0.3. Three message shapes, one binding rule, one relay rule.

---

## Binding: how an agent finds its project context

Every specialist agent, as its **first action**, before reading any source file:

1. Find `.agentic.json`. Start at the current working directory and **walk up**
   until you find it, or until you reach a filesystem root. Do not assume cwd is
   the repo root — a session started in a subdirectory is normal.
   ```json
   { "agenticRoot": "../.agentic", "project": "portfolio" }
   ```
   `agenticRoot` is relative **to the directory containing `.agentic.json`**,
   not to your cwd. Resolve it against that directory.
2. Read `<agenticRoot>/PROTOCOL.md` — this file. It is the only place the
   message shapes are defined.
3. Read `<agenticRoot>/projects/<project>/project.md` — the project profile
   (stack, paths, commands, hard guardrails). In full.
4. Read `<agenticRoot>/projects/<project>/capabilities/<your-lane>.md` — your
   capability pack. In full.
5. Only then start work.

If `.agentic.json` is not found by the time you reach a filesystem root, **stop
and report `BLOCKED`**. Do not guess the project layout — a specialist working
from inference is exactly the failure mode this network exists to prevent.

Your capability pack and the repo's own docs (`CLAUDE.md`, `docs/`) will often
cover the same ground. The pack is agent-facing and carries the friction the
repo docs do not record; the repo docs are richer and more current on the code
itself. Read the pack first, and when they disagree on a *fact about the code*,
trust the code — then emit a `pack_corrections` entry so the pack gets fixed.

---

## The run ledger: where a slice's state actually lives

A run's state is **not** the orchestrator's memory. The main session compacts,
restarts and loses things; a slice that only exists in a transcript cannot
survive that, and a lost contract note ships as inconsistency.

Every slice gets a directory:

```
<agenticRoot>/runs/<YYYY-MM-DD>-<slug>/
  run.md                        the ledger — see below
  01-delivery-brief.md          producer
  02-quant-research.md          quant-analyst RESEARCH
  03-technical-plan.md          tech-lead DESIGN
  04-backend.md                 lane reports, numbered in dispatch order
  05-frontend.md
  ...
  cr/CR-1.md                    change requests, one file each
  pack-corrections.md           appended by the orchestrator as they arrive
```

**`run.md` is the ledger.** The orchestrator creates it at Step 0 and updates it
after every report. It is the file that lets a fresh session resume:

```markdown
# RUN <run-id>
request:      <the user's original words, verbatim>
agentic_root: <the RESOLVED ABSOLUTE path — see below>
story:        <path, or NONE>
status:       PLANNING | DISPATCHING | GATING | BLOCKED | CLOSED
blocked_on:   <one line, only when status is BLOCKED; otherwise omit>
route:        recon | express | audit | review | story | full
express:      yes | no        (see "The express lane" in orchestrate-feature)

## Artifacts
| # | lane | mode | agent | artifact | status | verdict |
|---|------|------|-------|----------|--------|---------|
| 01 | product | — | producer | 01-delivery-brief.md | DONE | — |

## Open
- contract notes not yet absorbed by a downstream order
- SHOULD_FIX items carried to close-out
- PARTIAL lanes

## Rounds
- CR-1 (backend): round 1 of 2
```

**`status` takes the bare enum value and nothing else.** Not
`BLOCKED (awaiting the human's epic decision)` — that is `status: BLOCKED` plus
`blocked_on: awaiting the human's epic decision`. A field that sometimes holds
an enum and sometimes holds a sentence cannot be read by anything, including a
future session of yourself resuming this run.

**`agentic_root` is written once, resolved and absolute.** Resolve
`agenticRoot` against the directory containing `.agentic.json` and record the
result — `C:\projects\investments\.agentic`, not `../.agentic`. Every
`run_dir`, `report_to` and `inputs` path in every work order is then built by
appending to that recorded string, never by re-joining a relative fragment.
Relative-path arithmetic repeated across a dozen work orders is how a run ends
up dispatching against `C:\projects\investments.agentic\...` — a path that is
one missing separator from correct and silently wrong.

**Every agent writes its own artifact.** The work order carries a `report_to:`
path; the agent writes its full report there itself and *also* returns the
report block as its final message. The orchestrator never transcribes a report
into a file — transcription is paraphrase with extra steps.

Because of this, every agent is granted `Write`. That grant exists for **exactly
one purpose**: your own artifact under `<agenticRoot>/runs/<run-id>/`. Read-only
lanes (`scout`, `producer`, `quant-analyst`, `tech-lead`, `reviewer`) writing
anywhere else — including any file in the bound repo — is a protocol violation,
not a judgment call.

---

## The relay rule: paths, not prose

The orchestrator carries the producer's brief, the tech lead's plan and every
change request between lanes, because subagents cannot spawn subagents. If it
carries them as summarised text, the specialist works from the orchestrator's
paraphrase rather than the specialist judgment that produced it — and under
context pressure, summarising is exactly what happens.

So: **an `inputs` line names a path, never a quotation.**

```
inputs:
  - runs/2026-08-20-sector-drawdown/03-technical-plan.md   § contract
  - runs/2026-08-20-sector-drawdown/cr/CR-2.md
```

Not `inputs: - "the tech lead said the field should be nullable"`. The receiving
agent reads the file. Verbatim then becomes a property of the filesystem instead
of a hope about the model.

The one exception: `goal` and `non_goals` are the orchestrator's own words, and
should be.

---

## Shape 1 — the work order (orchestrator → agent)

Dispatch this verbatim as the subagent prompt. Never send free-form prose.

```
WORK ORDER <run-id>/<nn>
lane:        product | quant | recon | story | design | backend | frontend | test | docs | quant-audit | integration | review
mode:        <for lanes with modes — tech-lead: DESIGN | INTEGRATION; quant-analyst: RESEARCH | AUDIT>
run_dir:     <agenticRoot>/runs/<run-id>
report_to:   <agenticRoot>/runs/<run-id>/<nn>-<lane>.md
story:       <path to story file, or NONE>
tickets:     <T-x.y.z, ...  or NONE>

goal:        <one sentence, outcome not method>

scope:
  - <file / dir / glob this order may touch>

inputs:
  - <path — never a quotation. See "The relay rule".>

definition_of_done:
  - <checkable statement>

non_goals:
  - <thing an eager agent would do that it must not>

verification:  <exact command(s) to run, or NONE if read-only>
```

Rules for writing one:

- **`scope` is a fence, not a hint.** Anything outside it requires the agent to
  stop and report, not to proceed. Your `report_to` path and the run dir are
  always in scope implicitly; nothing else in `<agenticRoot>` is.
- **`goal` states an outcome.** "Cover the sector-drawdown engine's withheld
  path" — not "add three tests to test_drawdown.py".
- **`non_goals` is where you spend your effort.** It is the field that prevents
  scope creep, and the one people skip.
- One lane per order. If an order needs both a schema and a component, it is two
  orders with a dependency.

---

## Shape 2 — the report (agent → orchestrator, and → `report_to`)

Write this to `report_to`, and return it as the last thing in your run with no
trailing commentary. The two must be identical.

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
  - <pack file> — <the stated premise that is false, and the exact replacement wording>

handoff:
  - <what the next lane needs to know: new fixture names, prop shapes, route paths>

risks:
  - <anything you were unsure about, or a guardrail you had to interpret>
```

### The three result fields are not the same thing

They were conflated in v0.2, which made gate outcomes unrepresentable.

| Field | Question | Who fills it |
|---|---|---|
| `status` | Did this **order** run to completion? | every lane |
| `verdict` | What is the **judgment** this lane was asked for? | gate lanes only — everyone else writes `NONE` |
| `verification.result` | What did the **command** print? | every lane that ran one |

A gate that completed its review and found problems is
`status: DONE` + `verdict: FAIL` (reviewer) or `verdict: CHANGES_REQUESTED`
(tech lead INTEGRATION). It is **not** `status: PARTIAL` — the order succeeded;
the thing it judged did not.

Only `tech-lead` in `INTEGRATION` mode may emit `CHANGES_REQUESTED`. Only
`reviewer`, `tech-lead` and `quant-analyst` in `AUDIT` mode may emit `PASS` or
`FAIL`. Every other lane writes `verdict: NONE`.

### The report is checked, not trusted

```bash
python <agenticRoot>/scripts/check_report.py <run_dir>/<nn>-<lane>.md --lane <lane>
```

The orchestrator runs this on every artifact as it arrives, before routing
anything out of it. Exit 0 or the lane is not closed.

It checks what prose could not: the enums are real values, every section is
present, an empty section says `- none`, `status: DONE` is not paired with
`verification.result: NOT_RUN` on an order that named a command, and a
non-gate lane has not issued a verdict. It does **not** check whether the
content is true — no script can. It checks that the report is routable.

An agent may run it on its own artifact before returning. That is cheaper than
being sent back, and the failures it reports are unambiguous.

### Field discipline

- `status: PARTIAL` is honourable. Claiming `DONE` on unverified work is the
  single most expensive failure in this network.
- **`status: DONE` requires `verification.result: PASS`**, unless the order's
  `verification` field was `NONE`. `DONE` with `NOT_RUN` on an order that named
  a command is a protocol violation, not a shortcut.
- `REFUSED` when the order contradicts a project guardrail — say which one.
- `contract_notes` is how cross-lane drift gets caught. A backend agent that
  changes a schema **must** emit a contract note naming the client type and the
  contract doc that now lag.
- `pack_corrections` is how the packs stay alive. See "Pack maintenance".
- Empty sections stay in with `- none`. Silence is ambiguous.

---

## Shape 3 — the change request (tech lead → engineer, relayed)

The tech lead cannot dispatch. It writes each change request to
`<run_dir>/cr/CR-<n>.md` and names those paths in `handoff`; the orchestrator
relays each as a fresh work order whose `inputs` carries **the path to that
file**.

```
CHANGE REQUEST <n>
lane:     <owning lane>
severity: BLOCKING | SHOULD_FIX
round:    <1 | 2>
finding:  <what is wrong — file:line, specific>
why:      <the consequence, not the rule>
expected: <what would satisfy it>
```

- Only `BLOCKING` holds the slice. `SHOULD_FIX` is recorded in `run.md` under
  **Open** and surfaced to the human at close-out.
- An engineer receiving a change request fixes **only** what it names. Adjacent
  improvements are a new order, not a bonus.
- Two rounds maximum on the same finding. The count lives in `run.md` under
  **Rounds**, not in anyone's memory. A third means the request is unclear or
  the design is wrong — escalate to the human rather than looping.

---

## Gate rules

- A lane is not closed until its `verification.result` is `PASS`, or the order
  was explicitly read-only.
- The mechanical gates in the repo (test runner, pre-commit hook, CI) are the
  final authority. No agent may bypass, weaken, or work around a hook. If a
  commit is blocked, the answer is to fix the work, never to skip the gate.
- Three gates, in order, checking different things. The **quant analyst** gates
  the mathematics: are the numbers correct and honestly labelled. The **tech
  lead** gates engineering: contracts aligned across lanes, design followed. The
  **reviewer** gates acceptance: does this satisfy the story.
  They are not substitutes. A wrong formula can be engineered perfectly, tested
  thoroughly, and satisfy every acceptance criterion — and every gate but the
  first will pass it. Where a change touches analytics, the quant gate runs
  first, because the others are meaningless if it fails.
- **A gate that reads only the same source the work was built from is not an
  independent check.** It catches slips, not wrong premises. Where a lane's
  capability pack names an external anchor — a reference implementation, a
  textbook definition, hand-computed known values, a second data source — the
  gate must use it and say in `detail` which anchor it used. "Recomputed from
  the methodology doc" is a consistency check; label it as one rather than
  reporting it as independent verification.
- The reviewer's `FAIL` blocks close-out. The orchestrator re-dispatches to the
  owning lane with the failure artifact's path as an input — it does not fix
  things itself.

---

## Pack maintenance

The capability packs are the fastest-decaying artifact in the network. They name
paths, fixture modules, environment flags and commands — every one of which can
silently go false, after which an agent works from a confidently-stated wrong
premise that arrived in its order as fact.

So the loop is closed mechanically:

1. An agent that finds its pack contradicted by the code emits a
   `pack_corrections` entry naming the pack file, the false premise, and the
   **exact replacement wording**. Not a complaint — a patch.
2. The orchestrator appends every such entry to
   `<run_dir>/pack-corrections.md` as it arrives.
3. At close-out, the orchestrator dispatches the `docs` lane with that file as
   its input and `<agenticRoot>/projects/<project>/capabilities/` in scope, to
   apply them. This is the **only** order in which a lane may write inside
   `<agenticRoot>` outside the run dir.
4. Unapplied corrections are surfaced to the human alongside `SHOULD_FIX` items.

A pack correction is not a side note. It is frequently the most valuable thing
an order produces, because it prevents every future dispatch from repeating the
same false framing.

---

## Authoring rules for new agents and packs

**Agent file** (`plugins/agentic-core/agents/<name>.md`) is project-agnostic.
It contains: the role, a pointer to the binding steps above, tool discipline,
and what this lane judges. It must contain **zero** paths, framework names, or
conventions from any specific repo. If you are tempted to write `pytest` in an
agent file, that line belongs in a capability pack.

**Agent files do not restate the shapes.** The work-order, report and
change-request blocks are defined here and nowhere else. An agent file that
pastes the report block creates a copy that will drift from this one — v0.2 had
eleven such copies, and two of them already had. Point at this file instead.

**Capability pack** (`projects/<project>/capabilities/<lane>.md`) is where all
repo specifics live: paths, frameworks, fixtures, gotchas, commands, the
"things that bit us before" list, and any external anchor the lane's gate should
check against. This is the file that goes stale — treat it as documentation of
hard-won friction, and update it from `pack_corrections` every run.
