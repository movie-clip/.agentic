# `.agentic`

An orchestrated agent network for the repos under `C:\projects\investments\`.
Design rationale in [`ARCHITECTURE.md`](./ARCHITECTURE.md); plans in
[`ROADMAP.md`](./ROADMAP.md); open problems in
[`TECH-DEBT.md`](./TECH-DEBT.md). Version history is `git log`.

```
.agentic/
├─ ARCHITECTURE.md                        ← the current design and why (human-facing)
├─ ROADMAP.md                             ← what comes next, ordered
├─ TECH-DEBT.md                           ← what is wrong or missing now + the enforcement map
├─ PROTOCOL.md                            ← THE contract, core. Everyone reads this.
├─ protocol/                              ← role-scoped extensions. Read exactly one.
│  ├─ orchestrator.md      ledger · phases · control loop · relay rule
│  ├─ gates.md             verdicts · gate independence · change requests
│  ├─ packs.md             applying pack_corrections at close-out
│  └─ authoring.md         rules for writing agents, packs and protocol
├─ scripts/check_report.py                ← validates an artifact, its head, and the run ledger
├─ scripts/ledger.py                      ← applies one head's worth of ledger updates in a call
├─ scripts/check_network_edit.py          ← a network-layer edit with no passing protocol-lint
├─ scripts/pine_check.py                  ← tradingview's Pine linter
├─ scripts/test_*.py                      ← pins each of the four above
├─ scripts/hooks/report_artifact_gate.py  ← PostToolUse: checks an artifact as it is written
├─ scripts/hooks/report_head_gate.py      ← SubagentStop: no lane finishes on a bad head
├─ scripts/hooks/network_edit_gate.py     ← Stop: says so when a network edit has no lint
├─ scripts/hooks/test_hooks.py            ← pins all three hooks' exit codes and bounds
├─ .claude/settings.json                  ← this repo's own session: plugins + the Stop hook
├─ .claude-plugin/marketplace.json        ← makes this dir a local marketplace
├─ plugins/agentic-core/                  ← project-AGNOSTIC layer
│  ├─ .claude-plugin/plugin.json
│  ├─ skills/
│  │  ├─ orchestrate-feature/SKILL.md     ← the entry point; runs in the main session
│  │  └─ agentic-protocol/SKILL.md        ← a stub that points at PROTOCOL.md
│  └─ agents/
│     ├─ producer.md                sonnet/high    roadmap · epics · stories · sequencing
│     ├─ quantitative-researcher.md opus/medium    formulas · trust classes · financial gate
│     ├─ story-author.md            sonnet/medium  drafts the ticketed story (human approves)
│     ├─ scout.md                   sonnet/medium  read-only recon
│     ├─ tech-lead.md               sonnet/high    design pass + integration gate
│     ├─ backend-engineer.md        sonnet/high
│     ├─ frontend-engineer.md       sonnet/high
│     ├─ test-engineer.md           sonnet/medium
│     ├─ docs-engineer.md           sonnet/medium
│     ├─ reviewer.md                sonnet/high    acceptance gate
│     └─ protocol-linter.md         opus/medium    authoring gate — network files vs authoring.md
├─ projects/portfolio/                    ← project-SPECIFIC layer
│  ├─ project.md                          ← the binding profile
│  ├─ runs/<date>-<slug>/                 ← run ledgers — a slice's state on disk
│  └─ capabilities/
│     ├─ product.md               for the producer
│     ├─ quant.md                 for the quantitative researcher
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
agentic-core v<version> · project <name> · phases <...> · budget <n>
```

then either the skill did not load or you are on a pre-0.3 copy. Either way,
stop and check before trusting anything that follows.

**While iterating on the network**, use the local path source. Edits to a
`SKILL.md` take effect immediately; changes under `agents/` or
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
/agentic-core:orchestrate-feature add a per-sector drawdown breakdown to the Risk tab
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

## Current state

v0.8.0 — `plugins/agentic-core/.claude-plugin/plugin.json` is the authority.
Eleven agents. Five bound projects, each with its own profile and packs under
`projects/`: `portfolio`, `budget`, `impact`, `tradingview` and `datoro`.

- **What is wrong or missing:** [`TECH-DEBT.md`](./TECH-DEBT.md), including the
  enforcement map — which rules a script backs and which rest on trust.
- **What comes next:** [`ROADMAP.md`](./ROADMAP.md).
- **How it got here:** `git log`.

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
