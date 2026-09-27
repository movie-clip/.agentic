# Project profile: `impact`

Repo: `C:\projects\impact` (Impact — Unity 6 / DOTS game project, Athena
Framework). The git root is the repo above; the Unity project itself is one
level down, at `Impact/`.
Bound via `.agentic.json` (repo root).

**`Impact/CLAUDE.md` and `AGENTS.md` (repo root) are already in your
context.** The repo-root `CLAUDE.md` `@`-imports both, so Claude Code loads
them into every dispatched lane at startup.
`AGENTS.md` is the deep house-style source — build/test commands, C# style,
naming, ECS/DOTS patterns, error handling, files to treat carefully.
`CLAUDE.md` is the shorter entry point and points to it. Treat both as read,
and go to them for anything about the code this file does not carry. (If
either is genuinely not in your context, read it — that is the one case where
it is worth a tool call.)

This file carries what neither repo doc does: the lane map, the **numbering**
a `REFUSED` cites, and the friction not already recorded there. Phase
bindings live in `phases.md`, which the orchestrator reads at intake and no
specialist lane needs.

**This profile is new.** It is grounded in what `AGENTS.md`, `CLAUDE.md` and
the repo layout actually establish — not in hard-won incident history the way
`portfolio`'s packs are, because none has accumulated here yet. Expect
thinner gotcha sections than a mature project's packs, and expect
`pack_corrections` to do real work over the first several runs.
`protocol/packs.md` is the loop that closes that gap; use it rather than
treating the current thinness as a finding.

---

## Index

Read this block first. You are not expected to read this file end to end —
read what your order touches. Reading one extra section is cheap; acting on a
convention you never read is not.

**Always read:** **Hard guardrails — no plan or lane may violate these** · **Mechanical gates — never bypass** · **Skills: mattpocock-skills only**

| Section | Read it when |
|---|---|
| Delivery model | you are the producer, or shaping a request into work |
| Lane routing | you are choosing which lane owns a piece of work |
| Why `frontend` and `quant` are not bound | you are about to propose either lane |

Elsewhere: **`phases.md`** — which lane fills each phase and the clause that
fires it (orchestrator, at intake). **`CLAUDE.md`** / **`AGENTS.md`** —
product, stack, layout, conventions, commands (already in your context).

---

## Hard guardrails — no plan or lane may violate these

1. **Third-party packages are read-only.** `Packages/com.projectdawn.navigation/**`
   and `Library/PackageCache/**` (Entities, Physics, CharacterController),
   unless the order targets that package.
2. **Respect assembly boundaries.** Read the target `.asmdef` before adding a
   reference or unsafe code; direction follows the graph table below.
3. **Compile before calling anything done.** `dotnet build Impact.sln` at
   minimum; Unity batchmode compile (`AGENTS.md` § Build/Compile Commands)
   when the change touches codegen, baking, or package-generated assemblies.
4. **No roadmap, backlog, or ticket docs.** `Impact/CLAUDE.md` states this
   deliberately — a solo project starting fresh, planned as work comes up.
   Never create one even if asked to draft a plan; hand the plan back as a
   chat answer or a run artifact instead.
5. **No agent edits to generated/output paths.** `Library/`, `Temp/`, `obj/`,
   `Logs/`, and generated `.csproj` files are never touched unless the human
   explicitly asks.

Assembly graph for guardrail 2, read from the runtime `.asmdef` files (tests
and editor assemblies omitted). `PACKAGE_ARCHITECTURE.md`'s diagram is wrong
about `athena.charactercontroller`; this table is the authority.

| Package | References (Athena/AI only) |
|---|---|
| `athena.core` | — |
| `athena.contentmanagement` | — |
| `athena.charactercontroller` | — |
| `athena.sceneslice` | — |
| `athena.shared` | core, contentmanagement, charactercontroller |
| `athena.gameplay` | shared (`Athena.Shared.Components` only), contentmanagement, charactercontroller |
| `com.ai.shared` | — |
| `athena.ai`, `com.ai.utility` | `com.ai.shared` |

- Never add a reference from `athena.charactercontroller` to `athena.shared`.
  Shared already references it, so the new reference would be an assembly
  cycle.

An order that requires breaking one of these gets `status: REFUSED` naming the
guardrail. **This is the system's only numbered copy** — `AGENTS.md` §
"Files and Paths to Treat Carefully" and its build/test sections restate the
same substance unnumbered, so a session working the repo outside the network
still sees the rule and a cited number still resolves to exactly one.

## Delivery model

**Request → change.** Same shape as `datoro`/`tradingview`: no PRD or epic
tree, and no roadmap is kept in this repo by deliberate choice (guardrail 4).
`story` is the rare exception — a slice that crosses more than one lane's
contract with no existing brief covering it: a change to the crate/content-
loading pipeline's shared singleton shape, for instance, since both gameplay
and character-controller code depend on it. One system, one component, one
bug fix does not need a story; the delivery brief (or the human's own
request) is the specification.

## Lane routing

| Lane | Agent | Pack | Owns |
|---|---|---|---|
| recon | `scout` | — | read-only exploration: what already exists for X, localize a bug |
| product | `producer` | `product.md` | is this already covered, where "no" lives, given no roadmap exists |
| story | `story-author` | — | drafts the rare ticketed slice |
| design | `tech-lead` (DESIGN) | `architecture.md` | package/contract seam, ECS/DOTS design decisions |
| backend | `backend-engineer` | `backend.md` | `Impact/Packages/**`, `Impact/Assets/**` (non-test) — all gameplay/systems C# |
| test | `test-engineer` | `testing.md` | `Impact/Tools/**`, `*Tests*` assemblies |
| docs | `docs-engineer` | `docs.md` | `Impact/*.md`, `Impact/Packages/*/PACKAGE_DOCUMENTATION.md`, and — at close-out only — `<agenticRoot>/projects/impact/capabilities/**` when applying `pack-corrections.md` |
| integration | `tech-lead` (INTEGRATION) | `architecture.md` | engineering gate: PASS / CHANGES_REQUESTED |
| review | `reviewer` | — | acceptance gate: PASS / FAIL — only where a story exists |
| protocol-lint | `protocol-linter` | — | **authoring gate**: network files under `<agenticRoot>` against `protocol/authoring.md`. Not a delivery phase — see below |

Nine agents fill these ten lanes — `tech-lead` fills two, and
`plugins/agentic-core/agents/` is the authority on the roster. This table
says what each lane **owns**; `phases.md` says when it fires.

## Why `frontend` and `quant` are not bound

**`frontend`:** Impact has no first-party UI layer for `frontend-engineer` to
own — no `uGUI`/`UI Toolkit` screens of its own exist yet. The only UI
namespaces in the repo are in the vendored navigation package's editor code
and samples, plus one unused `UnityEngine.UIElements` using in
`athena.contentmanagement`'s `UnsafeSlotMap.cs`. A lane with nothing to own is a dispatch that
produces a `REFUSED`. If a HUD/menu layer is added later, that is when this
row is added — `protocol/authoring.md` § "Adding a project" applies equally
to adding a lane to one already onboarded.

**`quant`:** `quantitative-researcher` gates financial mathematics shown to a
user. This is a game project with no such surface — unlike `datoro`, where
the lane is *deferred* pending a methodology doc, this one is never
applicable here at all, and no future state changes that.

Three gates therefore apply here: `integration`, `review` (only where a story
exists), and `protocol-lint` on an authoring order. `phases.md`'s `verify`
rows are the authority `check_report.py` reads.

## Skills: mattpocock-skills only

The repo-root `.claude/settings.json` enables `agentic-core` and
`mattpocock-skills`, and nothing else. The lanes that hold the `Skill` tool
are `backend-engineer`, `test-engineer` and `tech-lead`. Their packs name each
call and its trigger:

| Skill | Lane | Pack section |
|---|---|---|
| `mattpocock-skills:diagnosing-bugs` | backend | `backend.md` § Diagnosing a stuck bug |
| `mattpocock-skills:diagnosing-bugs`, `mattpocock-skills:tdd` | test | `testing.md` § Technique skills (mattpocock-skills) |
| `mattpocock-skills:codebase-design` | tech-lead (DESIGN, INTEGRATION) | `architecture.md` § Technique skills (mattpocock-skills) |

- Do not call any skill outside this table. Its trigger and lane adaptations
  have not been written for Impact.
- The skills that need a human interview, an issue tracker or the `Agent` tool
  (`grill-*`, `to-spec`, `to-tickets`, `triage`, `wayfinder`) do not fit a
  dispatched lane.
- `unity-agent-plugin` is deliberately not enabled. It has no DOTS, Entities
  or Unity Physics coverage, and its PhysX skill contradicts this project's
  physics.
- For version-exact Unity API facts, read the package's `Documentation~/` under
  `Impact/Library/PackageCache/<package>@<hash>/`, e.g. Entities'
  `common-errors.md`.
- Reading it is allowed; guardrail 1 forbids only edits.
- The Unity CLI (`unity`) is installed for the human, but no pack instructs it
  and no gate depends on it.

## Mechanical gates — never bypass

- **`dotnet build Impact.sln`** must be clean before a build lane's report
  claims `status: DONE` on anything that touches C#. Run it from `Impact/`,
  where the solution lives.
- **`Tools/Run-UnityTests.ps1 -Platform EditMode -CoreOnly`** (and `PlayMode`
  when the change reaches runtime/session flow) is this project's test gate.
  No CI is wired for this repo — it is a solo project with no Actions
  workflow — so `integration` running this locally **is** the gate, not a
  faster stand-in for one.
- **No agent commits.** The human commits.
- **No project tool server.** The repo has no `.mcp.json`, so no
  `mcp__project__*` tools exist here.
- Every lane runs the plain `dotnet`/`Unity.exe`/PowerShell commands named in
  `AGENTS.md`, `Impact/CLAUDE.md` and the packs, from `Impact/`.
