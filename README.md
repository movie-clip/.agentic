# `.agentic`

An orchestrated agent network for the repos under `C:\projects\investments\`.
Design rationale in [`ARCHITECTURE.md`](./ARCHITECTURE.md).

```
.agentic/
├─ ARCHITECTURE.md                        ← design rationale + provenance (human-facing)
├─ PROTOCOL.md                            ← THE contract, core. Everyone reads this.
├─ protocol/                              ← role-scoped extensions. Read exactly one.
│  ├─ orchestrator.md      ledger · relay rule · reading discipline
│  ├─ gates.md             verdicts · gate independence · change requests
│  ├─ packs.md             applying pack_corrections at close-out
│  └─ authoring.md         rules for writing agents, packs and protocol
├─ runs/<date>-<slug>/                    ← run ledgers — a slice's state on disk
├─ scripts/check_report.py                ← validates an artifact, and its head
├─ scripts/test_check_report.py           ← pins the validator's own behaviour
├─ scripts/run_cost.py                    ← derives a run's cost from its ledger
├─ scripts/test_run_cost.py
├─ .claude-plugin/marketplace.json        ← makes this dir a local marketplace
├─ plugins/agentic-core/                  ← project-AGNOSTIC layer
│  ├─ .claude-plugin/plugin.json
│  ├─ commands/feature.md                 ← /agentic-core:feature "..."
│  ├─ skills/
│  │  ├─ orchestrate-feature/SKILL.md     ← the router; runs in the main session
│  │  └─ agentic-protocol/SKILL.md        ← a stub that points at PROTOCOL.md
│  └─ agents/
│     ├─ producer.md        sonnet/high  roadmap · epics · stories · sequencing
│     ├─ quant-analyst.md   OPUS/medium    formulas · trust classes · financial gate
│     ├─ story-author.md    sonnet/medium  drafts the ticketed story (human approves)
│     ├─ scout.md           haiku/medium   read-only recon
│     ├─ tech-lead.md       sonnet/high  design pass + integration gate
│     ├─ backend-engineer.md   sonnet/high
│     ├─ frontend-engineer.md  sonnet/high
│     ├─ test-engineer.md      sonnet/medium
│     ├─ docs-engineer.md      sonnet/medium
│     └─ reviewer.md        sonnet/high  acceptance gate
├─ projects/portfolio/                    ← project-SPECIFIC layer
│  ├─ project.md                          ← the binding profile
│  └─ capabilities/
│     ├─ product.md               for the producer
│     ├─ quant.md                 for the quant analyst
│     ├─ story.md                 for the story author
│     ├─ architecture.md          for the tech lead
│     ├─ backend.md · frontend.md · testing.md · docs.md
└─ _repo-patch/.agentic.json              ← copy this into the repo root
```

## Install

**1. Drop the pointer file into the repo.**

```
copy .agentic\_repo-patch\.agentic.json C:\projects\investments\portfolio\.agentic.json
```

This one file is the entire binding. Commit it — it is how any agent, in any
session, finds its context pack.

**2. Register the marketplace and install the plugin.** From Claude Code with
`C:\projects\investments\portfolio` open:

```
/plugin marketplace add C:\projects\investments\.agentic
/plugin install agentic-core@agentic
```

**3. Verify — and this step is not optional.** Run `/plugin`; `agentic-core`
should show as installed. (`/agents` no longer lists them; ask Claude "which
subagents do you have?" instead.)

Then check **which copy is actually installed**:

```bash
cat ~/.claude/plugins/installed_plugins.json
```

Read three fields: `version`, `installPath`, and the marketplace `source` in
`known_marketplaces.json`.

### The version trap

`/plugin marketplace add <local path>` and `/plugin marketplace add <git url>`
produce marketplaces that look identical in `/plugin` and behave completely
differently:

| Source | Where the code comes from | Effect of editing this directory |
|---|---|---|
| **local path** | this working directory | live after `/reload-plugins` |
| **git url** | a clone under `~/.claude/plugins/marketplaces/` | **none.** Edits do nothing until committed *and pushed*, then re-installed. |

If a git-sourced marketplace is registered, `/reload-plugins` reloads the clone,
not your work. This bit us on the first real run: `v0.2.3` from a stale GitHub
clone answered a request while `v0.3.0` sat uncommitted on disk, and nothing in
the output revealed the mismatch — it just produced a plausible answer to a
question the current architecture would have handled differently.

**Which is why the orchestrator now announces its version as its first line of
output.** If you do not see

```
agentic-core v<version> · project <name> · route <...>
```

then either the skill did not load or you are on a pre-0.3 copy. Either way,
stop and check before trusting anything that follows.

**While iterating on the network**, use the local path source. Edits to a
`SKILL.md` take effect immediately; changes under `agents/`, `commands/` or
`.mcp.json` need `/reload-plugins` or a restart.

### Fallback wiring

If the marketplace route gives you trouble on Windows, a directory junction
works and needs no plugin machinery at all:

```
mklink /J C:\projects\investments\portfolio\.claude\agents C:\projects\investments\.agentic\plugins\agentic-core\agents
```

Same for `skills`. You lose namespacing and versioning; you keep everything
else. Fine for evaluating whether the design earns its keep.

## Use

```
/agentic-core:feature add a per-sector drawdown breakdown to the Risk tab
```

Or just describe what you want — `orchestrate-feature`'s description is written
to trigger on ordinary phrasing.

What happens:

1. The orchestrator binds to the project via `.agentic.json`.
2. **Producer** reads the roadmap and returns a delivery brief: already shipped,
   fits an active story, new story, new epic, or decline. You approve it.
3. If new stories are needed, you run the repo's story-authoring skill. This is
   a deliberate human gate — acceptance criteria are the contract everything
   downstream is measured against.
4. **Quant analyst (research)**, if the substance is mathematical, establishes
   the formulas, trust classes and metrics inventory *before* the story is
   written — so the acceptance criteria are groundable.
5. **Tech lead (design)** settles the contract, the reuse, and the lane split
   before any engineer starts. You approve the lane plan.
6. **Engineers** run one order at a time, each in its own context. Contract
   notes route forward between lanes.
7. **Quant analyst (audit)** independently recomputes any changed number.
8. **Tech lead (integration)** gates the engineering; change requests are
   relayed verbatim to the owning lane.
9. **Reviewer** gates acceptance against the story.
10. You run the suite and commit. No agent commits.

## What is deliberately not automated

**Story authoring.** A vertical slice with no ticketed story stops the
orchestrator. That gate exists to catch bad acceptance criteria before code, and
automating past it would remove the only cheap place to catch them.

**Commits.** The repo's `pre_commit_gate.py` hook and CI are the real authority.
The network never touches that boundary.

**The final test run.** The reviewer agent is a cheap pre-check for things a
green suite cannot see — a missing acceptance criterion, a lagging contract doc.
It is not a substitute for `python scripts/run_all_tests.py`.

## Current state (v0.4.1)

All ten roles live, each with a capability pack for `portfolio`.

**One route is validated.** A `review` run (health-review fold-in) went through
end to end on 2026-08-20: skill loaded, banner printed, ledger written, two
lanes dispatched, zero repo edits by the orchestrator, both artifacts conforming
to Shape 2 on first contact, stopped correctly at the human gate. Its ledger and
artifacts are in `runs/2026-08-20-health-review-fold-in/` — read them before
changing the protocol, they are the only ground truth this design has.

That run also produced the argument for the whole thing. The same request run
*without* the network (v0.2.3, which silently no-op'd) took **25 minutes**,
edited four repo files directly, left no record, and propagated a false finding
— it logged a debt item asserting a field was undocumented that is documented at
`dashboard-fields.md:289`. The orchestrated run took **10 minutes**, dispatched
two lanes, touched nothing, and caught both that false finding and a second-order
one the first run had introduced. Faster *and* more accurate; the ceremony was
not the cost.

**Still not validated: the implementation lanes.** No story has been through
`backend → frontend → test → docs` with the three gates. Everything about the
work order, the change request and the gate handshake remains a guess. The next
move is one *small* slice.

### Not yet mechanical

Honest list of what is still enforced by asking an agent nicely:

| Rule | Backed by |
|---|---|
| No agent commits | **hook** — `pre_commit_gate.py`. Real. |
| Reports use the protocol shape | **script** — `scripts/check_report.py`, run by the orchestrator on every artifact and by agents on their own. Real. |
| A run's cost tally matches its rows | **script** — `scripts/run_cost.py`. Real. Catches a Cost block that disagrees with the Artifacts table, and a dispatch with no model. |
| Every lane runs on a chosen model | **agent frontmatter** — all ten pinned explicitly, no `inherit`. Real. |
| Every lane runs at a chosen effort | **agent frontmatter** — all ten pinned (`high` for the 5 deciding lanes, `medium` for the rest); the implicit default was `xhigh`. Real. |
| A report head's counts match its artifact | **script** — `check_report.py --head`, and `--emit-head` derives the head so it cannot disagree. Real. |
| Planning artifacts carry a ≤15-line brief | **script** — `check_report.py`. Real. It cannot check the brief is *useful*. |
| An agent reads only the pack sections it needs | prose + the pack's `## Index`. Trust. |
| The validator itself is correct | **tests** — `scripts/test_check_report.py`, 23 cases. Real, and it exists because a review pass found six bugs in the validator. |
| Read-only lanes don't edit the repo | **tool grant** — no `Edit` tool. Mostly real; `Bash` can still write. |
| A run survives a session restart | **the ledger on disk.** Real, and exercised. |
| `scope` fences a work order | prose only. v0.5. |
| The express lane isn't abused | prose only — but it self-voids on any contract note. |
| A report's *contents* are true | nothing, and nothing can. The validator checks routability, not honesty — that is what the three gates and your own reading are for. |

Knowing which line is which is the point of the table. A rule you believe is
enforced, and isn't, is worse than one you know is on trust.

## Extending

Adding a project: create `projects/<name>/project.md` + capability packs, drop
`.agentic.json` in that repo. The `plugins/` layer is untouched — that is the
whole reason for the split.

Adding an agent: agent files carry **zero** repo specifics. If you are writing
`pytest` into an agent file, that line belongs in a capability pack. See
`protocol/authoring.md`.

Keeping a pack indexed: every pack opens with `## Index` naming its always-read
sections and a "read it when" row for the rest, and every section must appear
there exactly once. A section is conditional **only** if an agent can evaluate
the condition before reading it — see `protocol/authoring.md`. Never rewrite an
index with a pattern that also matches the pack's own tables; that mistake
duplicated content into four packs during v0.4.

Keeping a pack honest: when a run surfaces something the pack failed to warn
about, the agent reports it in `risks`. Those entries are the pack's maintenance
backlog — fold them in, or the pack decays into a document that describes the
repo as it was.
