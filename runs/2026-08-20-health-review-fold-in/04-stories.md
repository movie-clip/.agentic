REPORT 2026-08-20-health-review-fold-in/04
status:      DONE
verdict:     NONE

changed:
  - none (this file only — draft story content below; no repo file under docs/product/stories/ or docs/product/epic-roadmap.md was touched, per scope)

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order was read-only drafting; no verification command named.

contract_notes:
  - none

pack_corrections:
  - none new this pass. I independently re-read `.claude/settings.json:19-29` and `scripts/hooks/pre_commit_gate.py` in full and confirm the `pack_corrections` entries already filed by scout (01-scout.md) and producer (02-delivery-brief.md) against `<agenticRoot>/projects/portfolio/project.md` and repo-root `CLAUDE.md` — the "fixed 2026-08-20" / `scripts/githooks/` claim is false; only the Bash-matched PreToolUse hook exists. I did not re-file it a third time; treat the existing two entries as live and unresolved (see `open_decisions` below on Step-0 ownership).

handoff:
  - "**This is a draft for human review, not an approved story set.** All three stories below are `Backlog`. Nothing has been written into `docs/product/stories/`, `docs/product/epic-roadmap.md`, or a new epic PRD — that happens only after human approval, per this lane's scope."
  - "Epic framing used throughout: **Epic 36 — Findings-First Doc & Gate Hygiene**, explicit sibling to Epic 32 (`Project Hygiene & Agent-Facing Doc Accuracy`), per the delivery brief's rationale (`02-delivery-brief.md` handoff). No PRD file exists yet — the human/producer creates it at epic-approval time; these three story drafts are written as if `docs/product/prd/epic-36-findings-first-doc-and-gate-hygiene.md` will be its path, matching the naming convention of `epic-32-project-hygiene-and-agent-docs.md`."
  - "Full draft story text follows this report block, in three sections: US-36.1, US-36.2, US-36.3. Ticket numbering: T-36.1.x / T-36.2.x / T-36.3.x."
  - "US-36.1 tickets: T-36.1.1 (the fix itself, mechanism left to tech-lead DESIGN), T-36.1.2 (regression test in the spirit of `test_docs_paths.py`, which I confirmed exists at `services/quant-engine/app/tests/test_docs_paths.py`), T-36.1.3 (doc correction closing the loop — fix the still-false claim in `CLAUDE.md` and `project.md` that this scout/producer pass already flagged, now that the real fix exists to point at)."
  - "US-36.2 tickets: T-36.2.1 (scan step — network-free-CI shape is the tech lead's DESIGN decision), T-36.2.2 (surface findings somewhere visible — mechanism/location also open pending the network question)."
  - "US-36.3 tickets: T-36.3.1 (cache-fields.md), T-36.3.2 (current-product-state.md route inventory + mechanical check), T-36.3.3 (epic-24 PRD status header), T-36.3.4 (system-architecture.md API Boundary note), T-36.3.5 (retire/supersede `docs/product/review-2026-08-20-findings.md`)."
  - "Every open decision the producer escalated is reproduced verbatim-in-substance inside each story's own `## Open decisions` section — I did not resolve any of them. See the full list repeated below in `risks` for the orchestrator's convenience, but the story files are the authoritative record the human should read."

risks:
  - "I did not re-verify scout's file:line citations myself beyond the handful I re-read directly for grounding (`.claude/settings.json`, `scripts/hooks/pre_commit_gate.py`, `docs/contracts/cache-fields.md`, `docs/product/current-product-state.md:94-109`, `docs/product/prd/epic-24-codebase-improvement.md:3`, `docs/architecture/system-architecture.md:241-250`, `.github/workflows/ci.yml`). All matched scout's claims exactly. I did not re-verify `imports.py:17-34` (F-R8) or the exact route-module Glob count independently — I am relying on scout's confirmed 15-vs-12 count and the tech-debt-register US-26.3 cross-reference, per the work order's instruction that `01-scout.md` is ground truth.
  - "US-36.1's AC set assumes the tech lead will pick *one* mechanism (mirror-the-matcher or move to a real `core.hooksPath` git-level hook) and implement it fully — I did not hedge the ACs to cover both possible shapes simultaneously, since the story instructs 'leave the mechanism open' at the *story* level (open decision), not 'write ACs that are agnostic to any implementation.' The ACs are observable-behaviour statements (a PowerShell-issued commit is blocked) that hold true regardless of which mechanism the tech lead picks, so I believe this satisfies both the work order and the story-author's guardrail against specifying implementation — flagging this reasoning explicitly since it is the trickiest AC/mechanism boundary in this batch.
  - "US-36.2's ACs are deliberately thin (scan step exists + findings surfaced somewhere) precisely because the network-free-CI shape is unresolved — I considered adding an AC asserting *where* findings surface (PR comment vs. log artifact vs. a new doc) and did not, since that is exactly the design question the brief flags as open. If the tech lead resolves it before ticketing, the AC should likely be sharpened; I left it a Backlog-level story rather than pre-guessing.
  - "US-36.3 bundles four independent doc-accuracy findings into one story per the producer's explicit direction (mirroring Epic 32's own bundling precedent) — I did not second-guess or re-split this, per the work order's non_goals ('sequencing and shape were already decided'). The story runs to 9 ACs across 4 findings + 1 retirement action, which is within this pack's 'roughly a dozen AC' sizing guidance, so I did not flag a split.
  - "Open decisions reproduced from the producer's brief, unresolved in every story that touches them: (1) US-36.1 — mirror-the-PowerShell-matcher vs. real git-level `core.hooksPath` hook, tech lead's call. (2) US-36.2 — can the vulnerability scan run inside the deliberately network-free `run_all_tests.py`/CI gate at all, or must it be a separate, explicitly network-permitted, possibly-scheduled check; this may reshape or split the story. (3) US-36.3 — whether a mechanical route-inventory-count check is worth adding (I recorded it as a considered-not-mandated AC, matching the brief's 'considering whether' phrasing, not a hard requirement). (4) Cross-cutting, not owned by any one story — who owns the CLAUDE.md correction at Step 0 (repo-root, outside the docs lane's literal `docs/**` scope per `project.md`'s routing table) and what 'retiring' `docs/product/review-2026-08-20-findings.md` means concretely (marked superseded/historical vs. deleted) — I recorded the producer's own recommendation (mark superseded, point at the new epic PRD, don't delete) inside US-36.3 as the assumption the story drafts against, but left it explicitly open since it's a docs-lane/human judgment call, not mine to settle.
  - "F-R2 and F-R4 are recorded as explicitly out of scope inside a shared preamble note at the top of this file (see below) rather than repeated inside each of the three stories, since neither maps to any single one of the three — F-R2 is a pure duplicate-of-US-26.3 record and F-R4 is a dropped false claim, and inventing a story-level 'out of scope: F-R2/F-R4' line in all three risked implying they were considered-and-rejected scope for that specific story rather than for the epic as a whole. If the human wants them repeated per-story instead, that's a one-line addition to each.
  - "I did not create the Epic 36 PRD file itself, per this lane's explicit non-goal — the epic framing (number 36, title, sibling-to-32 rationale) is stated in each story's header/context section as read-only context, sourced from the delivery brief, not authored by me as a new epic decision."

---

# DRAFT — not yet approved. Human review required before ticketing.

**Epic (proposed, not yet created):** Epic 36 — Findings-First Doc & Gate Hygiene
(sibling to Epic 32 — Project Hygiene & Agent-Facing Doc Accuracy)
**PRD:** not yet created — `docs/product/prd/epic-36-findings-first-doc-and-gate-hygiene.md` (proposed path, for the human/producer at epic-approval time)
**Source:** `docs/product/review-2026-08-20-findings.md` (F-R1, F-R3, F-R5, F-R6, F-R7, F-R8), folded in per `02-delivery-brief.md`

**Out of scope for this epic (recorded once, applies to all three stories below):**
- **F-R2** (currency-less request-path positions fabricate a currency) — confirmed exact duplicate of already-tracked **US-26.3** in `docs/tech-debt-register.md` (logged 2026-08-11). No new story or record; US-26.3 remains the owning entry.
- **F-R4** (claimed: `portfolio_return_trust` missing from `dashboard-fields.md`) — **false as written**. `docs/contracts/dashboard-fields.md:289` already contains a full, substantive entry matching the schema's docstring. Dropped — no story, no register entry. If a genuinely undocumented field surfaces later, it should be re-verified fresh, not assumed still open from this review.

---

## US-36.1: A blocked commit stays blocked, regardless of which tool issued it

**Epic:** Epic 36 — Findings-First Doc & Gate Hygiene
**PRD:** [`epic-36-findings-first-doc-and-gate-hygiene.md`](../prd/epic-36-findings-first-doc-and-gate-hygiene.md) *(not yet created)*
**Status:** Backlog
**Last updated:** 2026-08-20

### Story

As a **researcher relying on this project's own integrity claims**, I want the
test-freshness commit gate to hold no matter which tool issues `git commit`, so
that a stale, unverified tree can never be committed silently by tool choice
alone.

### Context

Finding **F-R1** (`docs/product/review-2026-08-20-findings.md`). The `PreToolUse`
hook that blocks `git commit` until `.claude/.last-test-pass` is fresher than
every changed non-`.md` file is wired with `"matcher": "Bash"` only
(`.claude/settings.json:19-29`, calling `scripts/hooks/pre_commit_gate.py`).
This environment also exposes a PowerShell tool that can run `git commit`
directly — a commit issued through PowerShell never triggers the hook, so the
freshness gate can be bypassed by tool choice alone, with no
`--no-verify`-style signal that it happened.

This is worse than a plain gap: both `CLAUDE.md` (repo root) and
`<agenticRoot>/projects/portfolio/project.md` currently assert, in the
"Mechanical gates" section, that a real git-level hook
(`scripts/githooks/pre-commit` wired via `core.hooksPath`, calling
`scripts/hooks/git_pre_commit.py`) already closes this gap, "fixed
2026-08-20." Confirmed by both `01-scout.md` and `02-delivery-brief.md`
(independently, via `Glob`/repo-wide `Grep`): **neither file exists anywhere
in the repo.** The claim is false. This story is the real fix; a separate,
already-flagged doc correction (see Tickets) removes the false claim once the
real fix lands.

Implementer must read: `.claude/settings.json` (PreToolUse hook wiring);
`scripts/hooks/pre_commit_gate.py` (the check's current logic — marker
existence + staleness against changed non-`.md` files); the finding text
above; `services/quant-engine/app/tests/test_docs_paths.py` (Epic 32's
precedent for "a fix delivered as a mechanical, regression-proof test, not a
one-time correction" — read for the *shape* of that precedent, not because
this story touches that file).

### Open decisions

**Blocking ticketing — the tech lead must resolve this in the DESIGN pass
before tickets are cut:**

- Which mechanism closes the gap? Two options are named in the finding, and
  neither is decided here:
  1. Mirror the existing `PreToolUse` `"Bash"` matcher to also catch the
     PowerShell tool (narrower, stays inside the Claude Code hook layer).
  2. Move the check to a real git-level `pre-commit` hook wired via
     `core.hooksPath`, so it fires on every `git commit` regardless of which
     tool or terminal invoked git (more robust — this is in fact what
     `CLAUDE.md`/`project.md` currently, falsely, claim already exists).
  This story's acceptance criteria are written to hold under **either**
  mechanism — they describe observable commit-blocking behaviour, not which
  hook layer produces it. The tech lead's DESIGN pass picks one and records
  why.

### Acceptance criteria

- [ ] AC1 — A `git commit` issued through the PowerShell tool, on a tree where
  `.claude/.last-test-pass` is missing or stale relative to a changed
  non-`.md` file, is **blocked** — the commit does not complete.
- [ ] AC2 — The block in AC1 produces a message naming why the commit was
  blocked (missing marker vs. stale-relative-to-which-file), matching the
  clarity the existing Bash-issued block already gives — no silent failure,
  no generic git error standing in for the reason.
- [ ] AC3 — A `git commit` issued through the Bash tool continues to be
  blocked under the same staleness condition, exactly as it is today — this
  story does not weaken or change the existing Bash-path behaviour.
- [ ] AC4 — A `git commit` issued through either tool **succeeds** when
  `.claude/.last-test-pass` is fresh relative to every changed non-`.md` file
  — the fix closes the tool-dependence gap without introducing a new false
  block on a legitimately green tree.
- [ ] AC5 — Markdown-only changes remain exempt from the staleness check,
  regardless of which tool issues the commit — the existing exemption
  (`pre_commit_gate.py`'s documented rationale: markdown cannot affect the
  suite) is preserved, not incidentally removed by whichever mechanism closes
  the gap.
- [ ] AC6 — A regression test exists that fails if tool-coverage regresses
  again — i.e. the check is mechanical, not a one-time hand-fix, in the same
  spirit as `test_docs_paths.py`'s precedent (a fix that was made once before
  and drifted back is exactly this project's own house lesson).

### Test plan

Backend (pytest):

- A new or extended test module under `services/quant-engine/app/tests/`
  covering the gate's tool-independence — exact file placement and whether it
  extends an existing gate-related test module or is new is the tech lead's
  call in DESIGN, made against whichever mechanism is chosen.
- Must cover: the PowerShell-equivalent commit path is blocked on a stale
  tree (AC1/AC2); the Bash path is still blocked (AC3, guards against
  regressing existing coverage); a fresh tree is not falsely blocked on either
  path (AC4); a markdown-only change is exempt on either path (AC5).
- Whatever mechanism is chosen, the test must exercise the **actual
  enforcement point** (the hook script or the git-level hook, not a
  reimplementation of its logic in the test) — an independent invocation, not
  a restatement, is what makes this a regression test rather than a tautology.

Regression / guardrail:

- `python scripts/run_all_tests.py` green.
- The commit-gate itself must not be weakened for the Bash path while fixing
  the PowerShell path — this is the one guardrail worth stating explicitly
  here (per this pack's guidance) because the fix mechanism could plausibly
  get this wrong by consolidating both paths through a single, accidentally
  narrower, check.

### Tickets

- [ ] **T-36.1.1 — Close the tool-coverage gap.** Implement whichever
  mechanism the tech lead's DESIGN pass selects (AC1, AC3, AC4, AC5).
- [ ] **T-36.1.2 — Regression test.** The mechanical, non-one-time-fix test
  covering AC1–AC5, mirroring the `test_docs_paths.py` precedent for "this
  drifted before, make it a test" (AC6).
- [ ] **T-36.1.3 — Correct the still-false claim.** `CLAUDE.md` and
  `<agenticRoot>/projects/portfolio/project.md` both currently claim (falsely,
  per `01-scout.md`'s and `02-delivery-brief.md`'s independent verification)
  that a git-level hook already exists and was "fixed 2026-08-20." Once
  T-36.1.1 lands, update both to describe the mechanism that now actually
  exists. Owner note: `project.md` is under `<agenticRoot>`, not this repo's
  `docs/**` — flagged for the human/orchestrator to route to the right lane
  at ticketing time, not resolved here.

### Out of scope

- Re-litigating what the gate itself checks (freshness of
  `.claude/.last-test-pass` against changed non-`.md` files) — that mechanism
  is not in question, only its tool-coverage.
- Any change to which files are exempt from the staleness check beyond
  preserving the existing markdown exemption (AC5).
- F-R2, F-R4 — see the epic-level out-of-scope note above.

### Notes / decisions

- This is the highest-severity finding in the source review (Med-high) and
  the delivery brief's recommended first story in the epic, risk-first: it is
  a security-relevant gate whose bypass is currently undetectable, and the
  class of failure — "a fix was claimed but never happened, and nothing
  caught it" — is the same failure mode the whole epic exists to close.
- No formula or methodology change; no academic citation required.

---

## US-36.2: CI flags a newly-vulnerable pinned dependency instead of staying silent forever

**Epic:** Epic 36 — Findings-First Doc & Gate Hygiene
**PRD:** [`epic-36-findings-first-doc-and-gate-hygiene.md`](../prd/epic-36-findings-first-doc-and-gate-hygiene.md) *(not yet created)*
**Status:** Backlog
**Last updated:** 2026-08-20

### Story

As a **developer or agent maintaining this project's dependencies**, I want a
known-vulnerability scan to run against the pinned backend and frontend
dependency sets, so that a dependency that goes quietly vulnerable after being
pinned does not stay invisible indefinitely.

### Context

Finding **F-R3** (`docs/product/review-2026-08-20-findings.md`). Backend
dependencies are pinned exact (`==`) in `requirements.txt`, with documented
rationale (goldens are sensitive to FastAPI/Pydantic internals); frontend
dependencies use caret ranges but are locked via a committed
`package-lock.json`, so installs are reproducible either way — pinning itself
is not the problem. But nothing in `.github/workflows/ci.yml` or
`scripts/run_all_tests.py` runs `pip-audit` / `npm audit` or equivalent, and
`.github/dependabot.yml` does not exist (confirmed absent by both scout and
producer). A pinned-exact version can go quietly vulnerable with nothing ever
flagging it.

`CLAUDE.md` and this project's own CI comment (`.github/workflows/ci.yml:1-4`)
state the network-free CI design is **deliberate** (US-21.1's network guard,
US-21.4's frozen goldens) — a vulnerability scan is inherently a
network-dependent operation (it queries a vulnerability database), so it
cannot simply be added as a step inside the existing `run_all_tests.py` gate
without contradicting that design. This tension is the open decision below,
not resolved by this story.

Implementer must read: `.github/workflows/ci.yml` (in full — current job
shape, the network-free comment at the top); `services/quant-engine/requirements.txt`
(pinning rationale, if commented); `apps/desktop/package-lock.json` (lockfile
presence); the finding text above.

### Open decisions

**Blocking ticketing — the tech lead must resolve this in the DESIGN pass
before tickets are cut:**

- Can the dependency-vulnerability scan run inside the deliberately
  network-free `run_all_tests.py` / CI gate at all, or does it need to be a
  separate, explicitly network-permitted, possibly-scheduled check (e.g. a
  second GitHub Actions workflow on a cron trigger, or a manually-invoked
  script)? This changes the story's shape materially — it may turn out to be
  two stories (add scan tooling vs. schedule/wire it) rather than one, or it
  may reshape which of the ACs below are even reachable inside CI proper vs.
  only as a local/manual command. Flagging, not deciding.

### Acceptance criteria

- [ ] AC1 — A scan step exists that checks the backend's pinned dependency set
  (`services/quant-engine/requirements.txt`) against a known-vulnerability
  source (e.g. `pip-audit` or equivalent).
- [ ] AC2 — A scan step exists that checks the frontend's locked dependency
  set (`apps/desktop/package-lock.json`) against a known-vulnerability source
  (e.g. `npm audit` or equivalent).
- [ ] AC3 — When either scan finds a known vulnerability, the finding is
  surfaced somewhere a developer or agent will actually see it before or
  around the next commit/PR — not silently logged to a location nobody reads.
  (Where exactly — CI job output, a PR annotation, a separate report file —
  is the tech lead's call per the open decision above; this AC is satisfied
  by any mechanism that makes a real finding visible, not by a specific one.)
- [ ] AC4 — When neither scan finds a known vulnerability, the scan step
  completes without blocking or altering the outcome of the existing
  `run_all_tests.py` / CI gate — this story adds visibility, it does not by
  itself change whether a commit or PR can proceed (acting on a finding, or
  deciding the scan should block, is explicitly out of scope — see below).
- [ ] AC5 — The scan step's own failure mode (e.g. the vulnerability
  database is unreachable) is distinguishable from "a real vulnerability was
  found" — a network hiccup must not read as either a false pass or a false
  vulnerability report.

### Test plan

This story is CI/infra-shaped rather than product-behaviour-shaped, so its
test plan leans on the network-free `run_all_tests.py` gate remaining green
plus a scoped check on the new step itself rather than product-facing pytest.

Backend (pytest), only if the tech lead's DESIGN puts the scan invocation
behind a wrapper script:

- A test covering the wrapper's failure-mode distinction (AC5) — a mocked
  "scan tool unreachable" case reads differently from a mocked "vulnerability
  found" case. Exact module/placement depends on where DESIGN puts the
  wrapper (may live under `scripts/` rather than `app/tests/` if it is a
  standalone script with no pytest surface — the tech lead's call).

Regression / guardrail:

- `python scripts/run_all_tests.py` stays green and stays network-free — the
  new scan step must not be silently folded into that gate in a way that
  reintroduces a network dependency into the suite CI relies on being
  network-free (US-21.1/US-21.4's existing guarantee). This is the one
  guardrail worth stating explicitly for this story, since the tension is the
  story's whole open decision.
- No behaviour-neutral / golden-diff concern — this story touches no
  analytics or schema.

### Tickets

- [ ] **T-36.2.1 — Add the scan tooling.** `pip-audit` (or equivalent) for
  backend, `npm audit` (or equivalent) for frontend, wired per the tech
  lead's DESIGN resolution of the network-free-CI open decision (AC1, AC2,
  AC5).
- [ ] **T-36.2.2 — Surface findings visibly.** Whatever mechanism DESIGN
  selects for "a developer or agent will see a real finding" (AC3), without
  changing the existing gate's pass/fail semantics on a clean scan (AC4).

### Out of scope

- Acting on any vulnerability the scan finds — that is a follow-up story if
  and when one is found, not part of this slice.
- Making the scan block the commit gate or CI on a finding — this story adds
  visibility only; whether a future finding should ever block is a separate,
  later decision once the team has seen what the scan actually reports.
- F-R2, F-R4 — see the epic-level out-of-scope note above.

### Notes / decisions

- Sequenced last in the epic per the delivery brief's rationale: this is the
  one story with a real open design question (the network-free-CI
  constraint) that may need the tech lead's or the human's input before
  scoping is final, and it neither blocks nor is blocked by the other two
  stories.
- No formula or methodology change; no academic citation required.

---

## US-36.3: The docs an agent is told to trust for "what's shipped" actually match the repo

**Epic:** Epic 36 — Findings-First Doc & Gate Hygiene
**PRD:** [`epic-36-findings-first-doc-and-gate-hygiene.md`](../prd/epic-36-findings-first-doc-and-gate-hygiene.md) *(not yet created)*
**Status:** Backlog
**Last updated:** 2026-08-20

### Story

As a **developer or agent reading this project's canonical docs to find out
what's shipped**, I want the cache CLI description, the route-module
inventory, a closed epic's PRD status header, and the API-boundary note on an
accepted security tradeoff to all match the current repo state, so that I stop
discovering the doc was wrong by reading the code myself.

### Context

Bundles findings **F-R5, F-R6, F-R7, F-R8**
(`docs/product/review-2026-08-20-findings.md`), mirroring Epic 32's
`US-32.1`/`US-32.3` bundling pattern exactly — each finding is individually too
small to be its own story, and all four are the same class of gap: a doc that
was accurate when written and has since drifted from the repo it describes.

**F-R5.** `docs/contracts/cache-fields.md` header reads "Last updated:
2026-06-05" (confirmed at line 9) — predates US-35.2 (2026-08-19) by over two
months. The `GET /cache/stats` / `POST /cache/clear` schema rows are still
accurate, but the prose at lines 55–57 still describes the pre-US-35.2
behaviour ("a specific namespace removes only `<namespace>-*.json`"), with no
mention of what US-35.2 actually shipped: namespaces enumerated live from disk
(`JsonFileCache.namespaces()`, not hardcoded), and a typo'd `--namespace` now
rejected with the present namespaces listed (previously silently reported
"Removed 0 cache file(s).").

**F-R6.** `docs/product/current-product-state.md:96-108` says "12 route
modules" and lists exactly 12 (confirmed by direct read: `exposure`,
`dashboard_history`, `diagnostics`, `drift`, `attribution`, `correlation`,
`stress`, `drawdown`, `distribution`, `imports`, `market_data`, `health`). The
actual `services/quant-engine/app/api/routes/` directory has **15** modules —
missing from the doc: `cache.py` (Epic 20/35), `currency_risk.py` (Epic 26),
`provenance.py` (Epic 18) — all three shipped and wired into
`app/api/main.py`. `CLAUDE.md`'s own repo-layout comment duplicates a route
list and should be checked for the same gap in the same pass.

**F-R7.** `docs/product/prd/epic-24-codebase-improvement.md:3` reads
"**Status:** Active (started 2026-06-19)" — confirmed by direct read.
`docs/product/epic-roadmap.md:971` has a section header "## Completed Epic:
Epic 24 — Codebase Improvement," and the story index
(`docs/product/stories/README.md`) lists every Epic 24 story as Done. The
PRD's status line was simply never flipped.

**F-R8.** `services/quant-engine/app/api/routes/imports.py:17-34`
(`InteractiveBrokersImportRequest.statement_path` /
`_resolve_statement_paths`) accepts any filesystem path with no restriction to
an app-owned directory, and the FastAPI server has no auth. Given the
local-first, single-user, no-execution design and CORS restricted to the
app's own dev origin (confirmed at `app/api/main.py:11-13`, not wildcard),
this is judged a reasonable, accepted tradeoff rather than a defect — but the
one-line note documenting that decision was never added to
`docs/architecture/system-architecture.md`'s "API Boundary" section
(confirmed absent from that section by direct read, lines 241–250). This
finding needs a documentation entry, not a code change.

Also in scope: retiring `docs/product/review-2026-08-20-findings.md` once
these findings are folded into the Epic 36 PRD — per this project's own
established convention (Epic 32's own precedent, and the guardrail that a
standalone findings file is not the permanent record), the producer's brief
recommends marking it explicitly superseded/historical, pointing at the Epic
36 PRD as the live record, rather than deleting it — preserving the
who-claimed-what-when audit trail, including its own now-void "Correction"
section (which itself inaccurately claimed 6 findings were "logged in
`docs/tech-debt-register.md`" — confirmed false by both scout's and the
producer's independent grep).

Implementer must read: `docs/contracts/cache-fields.md` (lines 9, 55–57);
`docs/product/current-product-state.md` (lines 94–109, and the matching
repo-layout section of `CLAUDE.md`); `docs/product/prd/epic-24-codebase-improvement.md`
(line 3); `docs/product/epic-roadmap.md` (the Epic 24 section header, for the
true status); `docs/architecture/system-architecture.md` ("API Boundary"
section, lines 241–250); `services/quant-engine/app/api/routes/`
(directory listing, to re-confirm the 15-module count at build time in case
another route shipped in between); `docs/product/review-2026-08-20-findings.md`
(the file being retired); `services/quant-engine/app/tests/test_docs_paths.py`
(US-32.1's precedent for a mechanical doc-fact check, read for shape only).

### Open decisions

- Whether a cheap mechanical check for the route-inventory count (F-R6's
  class of gap) is worth adding — e.g. asserting the route-module count/list
  in a test, the way `test_docs_paths.py` checks path claims, so this doc
  cannot silently drift every time a route ships. The delivery brief frames
  this as *"considering whether... is worth adding,"* not a hard requirement
  — recorded here as a considered item for the tech lead/ticketing pass to
  decide, not pre-decided as an AC. If added, AC9 below is the observable
  behaviour it would need to satisfy.
- What "retiring" `docs/product/review-2026-08-20-findings.md` means
  concretely — the producer's brief recommends marking it explicitly
  superseded/historical (pointing at the Epic 36 PRD as the live record)
  rather than deleting it, and that recommendation is what this story is
  drafted against (AC8 below). This stays a docs-lane/human judgment call at
  ticketing time, not settled here.

### Acceptance criteria

- [ ] AC1 — `docs/contracts/cache-fields.md`'s "Last updated" header reflects
  the date of its last real content change.
- [ ] AC2 — `docs/contracts/cache-fields.md`'s prose describes the shipped
  US-35.2 cache-clear behaviour: namespaces are enumerated live from disk
  (not a hardcoded list), and a typo'd `--namespace` value is rejected with
  the present namespaces listed rather than silently reporting zero removed.
- [ ] AC3 — `docs/product/current-product-state.md`'s route-module inventory
  lists every route module that exists under
  `services/quant-engine/app/api/routes/`, including `cache.py`,
  `currency_risk.py` and `provenance.py`, and its stated count matches the
  list.
- [ ] AC4 — `CLAUDE.md`'s repo-layout route list is reconciled against the
  same actual directory in the same pass, so the two documents do not
  disagree with each other immediately after this story ships.
- [ ] AC5 — `docs/product/prd/epic-24-codebase-improvement.md`'s status
  header reads a status consistent with `epic-roadmap.md`'s own record of
  Epic 24 (Completed), not "Active."
- [ ] AC6 — `docs/architecture/system-architecture.md`'s "API Boundary"
  section contains a note naming the import route's filesystem-path
  acceptance and the absence of server-side auth as a deliberate,
  accepted tradeoff (not a defect), consistent with the finding's own framing
  — i.e. the tradeoff reads as "decided," not "unnoticed."
- [ ] AC7 — None of AC1–AC6 changes any production code path, schema, or
  computed value — `dashboardGoldens.ts` stays byte-identical, and the full
  suite stays green.
- [ ] AC8 — `docs/product/review-2026-08-20-findings.md` is marked
  explicitly superseded, pointing readers at the Epic 36 PRD as the live
  record of these findings' disposition, rather than silently left in place
  reading as current.
- [ ] AC9 *(only if the open decision above resolves to "add the mechanical
  check")* — A test fails the suite if the route-module count/list named in
  `current-product-state.md` (and/or `CLAUDE.md`) disagrees with the actual
  contents of `services/quant-engine/app/api/routes/`, in the same spirit as
  `test_docs_paths.py`'s existing path-resolution check.

### Test plan

This story is primarily documentation-only, so most of its verification is a
set of checks rather than new test functions — matching US-32.3's precedent
for a docs-only story's test plan.

Backend (pytest):

- `test_docs_paths.py` (existing, from US-32.1) — must stay green; this
  story edits `CLAUDE.md` and other agent-facing docs, and the existing
  path-resolution scan is what proves the edits did not introduce a broken
  path.
- *(Only if AC9 is in scope)* a new test asserting the route-module
  inventory named in the doc(s) matches the actual directory contents,
  reporting which module is missing or extra by name — mirroring
  `test_docs_paths.py`'s "name the offending file/path" convention rather
  than a bare pass/fail.

Manual verification (recorded in the story close-out, per US-32.3's
precedent for docs-only stories):

- Direct comparison of the route-module list in `current-product-state.md`
  and `CLAUDE.md` against a fresh directory listing of
  `services/quant-engine/app/api/routes/` (AC3, AC4).
- Direct comparison of `epic-24-codebase-improvement.md`'s status header
  against `epic-roadmap.md`'s Epic 24 section header (AC5).
- A read of `system-architecture.md`'s "API Boundary" section confirming the
  new note is present and correctly frames the tradeoff as accepted, not
  flagged as an open defect (AC6).

Regression / guardrail:

- `dashboardGoldens.ts` byte-identical (AC7).
- `python scripts/run_all_tests.py` green; dead-code gate clean.

### Tickets

- [ ] **T-36.3.1 — Fix `cache-fields.md`.** Header date + US-35.2 behaviour
  description (AC1, AC2).
- [ ] **T-36.3.2 — Fix the route-module inventory.** Both
  `current-product-state.md` and `CLAUDE.md`'s duplicated route list (AC3,
  AC4); add the mechanical count/list check only if the open decision above
  resolves to include it (AC9).
- [ ] **T-36.3.3 — Fix the Epic 24 PRD status header** (AC5).
- [ ] **T-36.3.4 — Add the API-Boundary tradeoff note** to
  `system-architecture.md` (AC6).
- [ ] **T-36.3.5 — Retire the findings doc.** Mark
  `docs/product/review-2026-08-20-findings.md` explicitly superseded,
  pointing at the Epic 36 PRD (AC8). This ticket depends on the Epic 36 PRD
  existing — sequence it after the PRD is created at epic-approval time, not
  before.

### Out of scope

- Any code change — every AC in this story is documentation-only.
- Reconciling every other doc that might duplicate a route list beyond the
  two named (`current-product-state.md`, `CLAUDE.md`) — no third duplicate
  was found by scout or the producer; a follow-up if one surfaces.
- Deleting `docs/product/review-2026-08-20-findings.md` outright — the
  producer's brief explicitly recommends marking it superseded, not removing
  it, to preserve the audit trail (including its own second, self-authored
  error).
- F-R2, F-R4 — see the epic-level out-of-scope note above.

### Notes / decisions

- Sequenced second in the epic per the delivery brief's rationale: cheap,
  mechanical, no design questions, and doing it before the dependency-scan
  story means the "epic PRD folds in findings" housekeeping (retiring the
  standalone findings file) happens close to when the findings were
  verified, not stale by the time that story's open CI-design question
  resolves.
- No formula or methodology change; no academic citation required.
