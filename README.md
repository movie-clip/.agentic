# `.agentic`

An orchestrated agent network for the repos under `C:\projects\investments\`.
Design rationale in [`ARCHITECTURE.md`](./ARCHITECTURE.md).

```
.agentic/
├─ ARCHITECTURE.md
├─ PROTOCOL.md                            ← THE contract. Single copy, by design.
├─ runs/<date>-<slug>/                    ← run ledgers — a slice's state on disk
├─ .claude-plugin/marketplace.json        ← makes this dir a local marketplace
├─ plugins/agentic-core/                  ← project-AGNOSTIC layer
│  ├─ .claude-plugin/plugin.json
│  ├─ commands/feature.md                 ← /agentic-core:feature "..."
│  ├─ skills/
│  │  ├─ orchestrate-feature/SKILL.md     ← the router; runs in the main session
│  │  └─ agentic-protocol/SKILL.md        ← a stub that points at PROTOCOL.md
│  └─ agents/
│     ├─ producer.md              roadmap · epics · stories · sequencing
│     ├─ quant-analyst.md         formulas · trust classes · financial gate
│     ├─ story-author.md          drafts the ticketed story (human approves)
│     ├─ scout.md                 read-only recon
│     ├─ tech-lead.md             design pass + integration gate
│     ├─ backend-engineer.md
│     ├─ frontend-engineer.md
│     ├─ test-engineer.md
│     ├─ docs-engineer.md
│     └─ reviewer.md              acceptance gate
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

## Current state (v0.3)

All ten roles live, each with a capability pack for `portfolio`.

v0.3 is the design review's structural pass — run ledger, relay by path, one
copy of the protocol, the express lane, separated status/verdict fields, pack
corrections with an owner, and `build-story` retired. Details in
`ARCHITECTURE.md` §7.

**Still not validated: no real story has been through this end to end.** Every
shape here remains a guess until something real passes through it, and v0.3
changed the shapes rather than testing them. The next move is one *small* slice,
chosen so the cost model in `orchestrate-feature` § Step 1 gets measured instead
of asserted — then correct the protocol where it chafed.

### Not yet mechanical

Honest list of what is still enforced by asking an agent nicely:

| Rule | Backed by |
|---|---|
| No agent commits | **hook** — `pre_commit_gate.py`. Real. |
| Read-only lanes don't edit the repo | **tool grant** — no `Edit` tool. Mostly real; `Bash` can still write. |
| `scope` fences a work order | prose only. v0.5. |
| Reports use the protocol shape | prose only; nothing parses them. |
| The express lane isn't abused | prose only — but it self-voids on any contract note. |

Knowing which line is which is the point of the table. A rule you believe is
enforced, and isn't, is worse than one you know is on trust.

## Extending

Adding a project: create `projects/<name>/project.md` + capability packs, drop
`.agentic.json` in that repo. The `plugins/` layer is untouched — that is the
whole reason for the split.

Adding an agent: agent files carry **zero** repo specifics. If you are writing
`pytest` into an agent file, that line belongs in a capability pack. See
`agentic-protocol` § "Authoring rules".

Keeping a pack honest: when a run surfaces something the pack failed to warn
about, the agent reports it in `risks`. Those entries are the pack's maintenance
backlog — fold them in, or the pack decays into a document that describes the
repo as it was.
