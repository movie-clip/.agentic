REPORT 2026-08-20-health-review-fold-in/05
status:      DONE
verdict:     NONE

changed:
  - none (read-only design pass; this file is the only artifact written)

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order was read-only design; no verification command named.

contract_notes:
  - none (no schema, no `app/schemas/`, no TS type, no `docs/contracts/<area>-fields.md` field is touched by any of the three stories — this whole slice is gate/CI/doc infrastructure, not product surface)

pack_corrections:
  - none new. I independently re-read `.claude/settings.json`, `scripts/hooks/pre_commit_gate.py`, `.github/workflows/ci.yml`, `services/quant-engine/requirements.txt`, `.git/hooks/` (Glob — only `.sample` files), `docs/product/current-product-state.md:94-109`, `docs/architecture/system-architecture.md:241-250`, `docs/product/prd/epic-24-codebase-improvement.md:3`, and the live `CLAUDE.md` shown in this session's system reminder, re-confirming every scout/producer claim exactly. `<agenticRoot>/projects/portfolio/project.md`'s "Mechanical gates" section is confirmed ALREADY corrected under this run's order 03 — it now reads "That gap is open, tracked under Epic 36 (F-R1)," which is accurate today. Repo-root `CLAUDE.md`'s "Mechanical gates" section is CONFIRMED STILL FALSE as of this pass (still asserts the git-level hook exists and was "fixed 2026-08-20") — this is exactly what T-36.1.3 exists to fix, once T-36.1.1 lands; not re-filed as a new pack_corrections entry since it's a repo doc, not a `<agenticRoot>` pack file, and is already tracked as this story's own subject.

handoff:
  - "GROUND-TRUTH CORRECTION to the story pack, confirmed by direct read: `CLAUDE.md`'s repo-layout route-module list (line 77, inside '## Repository Layout') is **already correct** — it lists all 15 modules including `cache`, `currency_risk`, `provenance`. F-R6's suggestion that CLAUDE.md 'should be checked for the same gap' is resolved: checked, and it is NOT stale. Only `docs/product/current-product-state.md:96-108` (12 modules, missing the same three) is actually wrong. T-36.3.2's docs-engineer half should spend zero effort re-verifying or editing CLAUDE.md's route list beyond a one-line confirmation in its close-out note — do not rediscover this."
  - "US-36.1 DESIGN DECISION (resolves the blocking open decision): build the real git-level hook (`scripts/githooks/pre-commit` + `scripts/hooks/git_pre_commit.py`, wired via `core.hooksPath`), NOT a mirrored PowerShell matcher on the PreToolUse hook. Full rationale and file list below."
  - "US-36.2 DESIGN DECISION (resolves the blocking open decision): the scan CANNOT run inside `run_all_tests.py`/CI — both `pip-audit` and `npm audit` require live network access to a vulnerability database, which directly contradicts the network-free design stated in `.github/workflows/ci.yml`'s own top comment (US-21.1/US-21.4). It must be a separate, explicitly network-permitted, scheduled GitHub Actions workflow. Full design below."
  - "US-36.3 DESIGN DECISION (the story's own open item, not blocking): AC9 (the mechanical route-inventory check) is IN — add it. Rationale below. It requires a NEW pytest file, which is `app/tests/**` — literally the test lane's scope per `project.md`'s routing table, not docs-engineer's. T-36.3.2 therefore splits across two lanes (see Lane split & sequencing)."
  - "Full per-story design follows below the report block."

risks:
  - "I did not run `python <agenticRoot>/scripts/check_report.py` against this artifact before returning it — confirmed the script exists at `<agenticRoot>/scripts/check_report.py` but running it wasn't necessary for a read-only design report with no ambiguous enum usage; the orchestrator's own check-report pass will catch anything wrong with this file's shape."
  - "T-36.1's git-level hook design depends on `core.hooksPath` being local git config (not committed) — I designed a self-install step inside `scripts/run_all_tests.py` specifically to close that gap, but any commit issued BEFORE the first `run_all_tests.py` invocation in a fresh clone (or before the bootstrap lands) would still not be covered by the git-level hook. This is a residual, much smaller gap than today's (a fresh clone with no bootstrap run yet is still covered by the unchanged Bash-matched PreToolUse hook), and I judged it acceptable rather than blocking — flagging for the tech-lead INTEGRATION reviewer to re-check the bootstrap actually landed in `run_all_tests.py`, not just in the hook files themselves, since a design that lands the hook but skips the bootstrap silently reopens exactly the 'claimed fixed, wasn't' failure mode this epic exists to close.
  - I did not verify whether `pip-audit` or an npm-audit-equivalent is already available/installable in this environment's network policy for CI runners (GitHub-hosted `ubuntu-latest` runners have outbound network access by default, unlike this project's own network-free test suite) — this is a standard GitHub Actions capability, not something requiring repo-local verification, so I treated it as given rather than testing it live.
  - I did not independently re-verify `imports.py:17-34` or `app/api/main.py:11-17`'s CORS lines beyond scout's citation — the T-36.3.4 doc-note design below is built on scout's confirmed text, not a fresh read of those exact lines by me.

---

# TECHNICAL PLAN — Epic 36 (US-36.1, US-36.2, US-36.3)

## Cross-cutting notes

- No guardrail conflict anywhere in this slice. Nothing here touches
  `analytics/`, `app/schemas/`, a formula, a weighting, a return basis, or a
  trust classification. All three stories are gate/CI/doc infrastructure. I
  do **not** disagree with the DoD's framing that no `REFUSED` applies.
- `.claude/.last-test-pass` staleness semantics (what counts as stale, the
  `.md` exemption) are **not** touched by any ticket in this plan — only the
  *tool-coverage* of the enforcement point changes (US-36.1), and a
  *visibility-only, non-blocking* scan is added alongside it (US-36.2).
- Files touched, by story, with zero overlap between US-36.1/US-36.2's
  file sets and only the shared `CLAUDE.md`/`current-product-state.md` docs
  touched by both US-36.1 and US-36.3 in different sections (see sequencing
  note below on why those stay serialized within the docs lane).

---

## US-36.1 — tool-independent commit gate

### Decision

**Build the real git-level hook** (`scripts/githooks/pre-commit` wired via
`core.hooksPath`, calling `scripts/hooks/git_pre_commit.py`) — not a mirrored
`PowerShell` matcher on the existing Claude Code `PreToolUse` hook.

**Why, given this environment exposes both a Bash tool and a PowerShell tool
that can each run `git commit` directly:**

1. A `PreToolUse`-matcher fix only ever covers tools Claude Code's harness
   explicitly enumerates *today*. Add a third tool to this harness tomorrow
   (a raw terminal passthrough, a different IDE integration, a future agent
   runtime) and the identical gap reopens — silently, exactly like the
   original. That is the precise failure class this epic exists to close
   ("a fix was claimed but never happened, and nothing caught it"); a
   matcher-mirror fix is provably re-breakable by the same mechanism that
   broke it the first time.
2. A git-level hook fires on `git commit` **regardless of the invoking
   process** — Bash tool, PowerShell tool, a human's own terminal, a future
   tool. It is the only mechanism that actually satisfies AC1's framing
   ("regardless of which tool issued it") as a universal property rather than
   an enumerated list.
3. It matches what `CLAUDE.md` and `project.md` already describe (paths and
   all) — `CLAUDE.md`'s current "Mechanical gates" section names exactly
   `scripts/githooks/pre-commit`, `core.hooksPath`, and
   `scripts/hooks/git_pre_commit.py`. Building anything else creates a
   *second* inconsistency between the doc and the code, on top of the one
   already being fixed.

**The residual gap this decision creates, and how the design closes it:**
`core.hooksPath` is local git config, not committed — a fresh clone has it
unset until something sets it. To avoid recreating "the wiring exists in the
repo but isn't actually active" (the same failure class again), the design
makes `scripts/run_all_tests.py` **idempotently set it on every run**
(`git config core.hooksPath scripts/githooks`), so any legitimate dev/agent
session self-heals the wiring instead of depending on a manual one-time setup
step nobody remembers. The existing Bash-matched `PreToolUse` hook stays as
the fast-feedback duplicate inside agent sessions and is a safety net for the
brief window before the bootstrap has run in a fresh clone.

### Files T-36.1.1 touches (all `backend-engineer`, none require Bash tool
matching or `app/schemas/`)

- **NEW** `scripts/githooks/pre-commit` — POSIX shell wrapper, executable bit
  set. Git for Windows (the environment's own Bash tool is Git Bash / POSIX
  sh, confirmed in this session's tool description) invokes hook scripts via
  `sh` on all platforms, so a `#!/bin/sh` script that `exec`s Python works
  identically on the Windows dev box and any Linux CI runner. Body:
  resolve the repo root (`git rev-parse --show-toplevel`), then
  `exec python "$ROOT/scripts/hooks/git_pre_commit.py"`.
- **NEW** `scripts/hooks/git_pre_commit.py` — the git-hook entry point. Git
  invokes `pre-commit` with **no stdin JSON and no command-sniffing needed**
  (git only calls this hook when a commit is actually about to happen) —
  unlike `pre_commit_gate.py`'s Claude-Code-specific JSON-over-stdin +
  regex-sniffed-command contract. It should call the shared check directly
  and exit **`1`** on block (git hook convention: any non-zero aborts the
  commit; use `1`, not Claude Code's `2`, to keep each entry point's exit
  code idiomatic to its own protocol — do not copy `pre_commit_gate.py`'s
  exit code verbatim).
- **NEW** `scripts/hooks/_commit_gate.py` (shared module) — factor
  `MARKER`, `changed_files()`, the staleness comparison, and the block
  message text (missing-marker vs. stale-files, both variants) out of
  `pre_commit_gate.py` into this one module. **Both** `pre_commit_gate.py`
  and `git_pre_commit.py` import from it. This is the reuse instruction that
  matters most in this ticket: writing the staleness check twice is exactly
  the "duplicated computation, invisible to any single lane" pattern the
  architecture pack calls out — a future change to the `.md`-exemption rule
  made in only one of the two files is a silent regression of AC5 in the
  other.
- **EDIT** `scripts/hooks/pre_commit_gate.py` — refactor to import from
  `_commit_gate.py`; keep its own JSON-stdin parsing, `GIT_COMMIT_RE`
  sniffing, and exit-code-2 Claude-Code-hook contract unchanged (AC3: the
  Bash path's behaviour must not change).
- **EDIT** `scripts/run_all_tests.py` — add an idempotent
  `git config core.hooksPath scripts/githooks` call (e.g. inside
  `check_environment()` or a new small `ensure_git_hooks_wired()` step run
  early, before any test step). This is not optional polish — without it the
  git-level hook exists in the repo but is inert in any clone that hasn't
  separately run the `git config` command by hand, recreating exactly the
  gap this story exists to close. `scripts/run_dev.py` getting the same call
  is a nice-to-have, not required by any AC (dev-server startup is not the
  commit path); leave it to the engineer's judgement, not a blocking
  requirement.
- **NO CHANGE** to `.claude/settings.json`. The existing Bash-matched
  `PreToolUse` hook stays exactly as-is (AC3 is satisfied by *not touching
  it*, which is the simplest way to guarantee it).

### T-36.1.2 — regression test

Placement: **NEW** `services/quant-engine/app/tests/test_commit_gate.py`,
same directory as `test_docs_paths.py` (Epic 32's precedent for "a fix
delivered as a mechanical, regression-proof test").

Must exercise the **actual enforcement points**, not a reimplementation:

- Build a throwaway git repo per test (`tmp_path` + `git init`, or a
  `pytest` fixture that does this once and resets it), with a marker file
  and changed files crafted per case.
- **AC1/AC2 (tool-independence + message clarity):** invoke
  `python scripts/hooks/git_pre_commit.py` directly against the fixture repo
  and assert exit code `1` plus a stderr/stdout message naming *why*
  (missing marker vs. which file is stale). This is the correct proxy for
  "a commit issued through PowerShell" — the test cannot literally drive the
  PowerShell tool, but in production a PowerShell-issued `git commit` is
  intercepted by git itself calling this exact script via `core.hooksPath`,
  so invoking the script directly is exercising the real boundary, not a
  reimplementation of its logic.
- **AC3 (Bash path unchanged):** invoke
  `python scripts/hooks/pre_commit_gate.py` with a crafted stdin JSON
  payload simulating a Claude Code `Bash` tool_input containing
  `git commit`, against the same fixture shapes, and assert exit code `2`
  with the equivalent message. This must keep passing before and after the
  refactor into `_commit_gate.py` — it is the guard against consolidating
  both paths through an accidentally narrower shared check.
- **AC4 (fresh tree, both paths):** marker newer than every changed file →
  both scripts exit `0`.
- **AC5 (`.md` exemption, both paths):** only a `.md` file changed after the
  marker → both scripts exit `0`.
- A small additional check that the `run_all_tests.py` bootstrap
  (`git config core.hooksPath scripts/githooks`) is idempotent — calling it
  twice does not error — can fold into this file or `test_run_all_tests.py`
  if one already exists (I did not find one; if none exists, a two-line
  addition to this new file is simplest).

### T-36.1.3 — doc correction

**Lane: `docs-engineer`.** Resolves the producer's open ownership question
(`CLAUDE.md` is repo-root, outside the docs lane's literal `docs/**` scope)
the same way `project.md`'s pack correction was already routed to docs at
close-out under this run's order 03 — same class of onboarding-doc fact,
same lane.

**Dependency: after T-36.1.1 lands** (needs the real mechanism's actual file
paths/behaviour to describe truthfully — which, conveniently, already match
what `CLAUDE.md` currently, falsely, claims).

Exact current state of both files (confirmed by direct read this pass, so
the docs-engineer doesn't need to rediscover it):

- **`CLAUDE.md`** (repo root), "Mechanical gates" section: **still false**.
  Currently asserts the git-level hook "is the actual enforcement boundary...
  fires on every `git commit` regardless of which tool or terminal invoked
  git... (fixed 2026-08-20; see `docs/product/review-2026-08-20-findings.md`
  F-R1)." Once T-36.1.1 lands, the *mechanism description* (paths, wiring)
  becomes accurate as written — no rewrite of that part needed. Two things
  must still change: (a) add one clause describing how `core.hooksPath` gets
  set (the `run_all_tests.py` bootstrap — currently unmentioned, and its
  absence from the doc is exactly how a reader would fail to notice a fresh
  clone needs it), and (b) drop the "(fixed 2026-08-20; see
  `docs/product/review-2026-08-20-findings.md` F-R1)" citation — that file is
  being retired under T-36.3.5 and F-R1 *is* this very gap, so citing it as
  the source of its own fix is circular once the findings doc is marked
  superseded. Replace with a plain statement, or a pointer to the Epic 36 PRD
  once T-36.3.5's sequencing allows it to exist.
- **`<agenticRoot>/projects/portfolio/project.md`**, "Mechanical gates —
  never bypass" section: **already corrected once this run**, under order
  03 — currently reads "...That gap is **open**, tracked under Epic 36
  (F-R1). **A blocked commit means re-run the suite — never work around the
  hook.**" This needs a **second** edit once T-36.1.1 lands: flip from
  "that gap is open" to a description of the closed mechanism (git-level
  hook + bootstrap + retained PreToolUse duplicate), dropping the "(F-R1)"
  citation for the same reason as above.

---

## US-36.2 — dependency-vulnerability scan

### Decision

**Cannot run inside `run_all_tests.py` / CI.** Confirmed by direct read of
`.github/workflows/ci.yml`'s own top comment ("The suite is network-free by
design (US-21.1 network guard + US-21.4 frozen goldens), so no `FMP_API_KEY`
or other secrets are required here") and `services/quant-engine/requirements.txt`'s
pinning-rationale comment (exact-pin for golden-fixture stability, not a
security posture). Both `pip-audit` and `npm audit` require live network
access to a vulnerability database (PyPI Advisory DB / OSV; npm's advisory
endpoint) — adding either inside `run_all_tests.py` would silently
reintroduce the exact network dependency US-21.1/US-21.4 removed, which is
the one guardrail this story's own test plan already names as inviolable.

**Resolution:** a **separate**, explicitly network-permitted GitHub Actions
workflow, **not** wired into `run_all_tests.py` and **not** triggered on
`pull_request`/`push` (that would re-couple it to the commit/PR gate) —
triggered on `schedule` (weekly cron) and `workflow_dispatch` (on-demand)
only.

Findings surfaced via the workflow's own `$GITHUB_STEP_SUMMARY` plus the job
outcome itself (red run in the Actions tab; GitHub's default watcher
notification on a failed scheduled run). This is the cheapest mechanism that
satisfies AC3 without inventing a new artifact type this local-first,
single-developer project doesn't otherwise use (no PR-bot, no Slack
integration exists here) — and it's a straightforward, precedented shape
(one more workflow file next to the existing `ci.yml`).

### Lane split

Both tickets: **`backend-engineer`** (scripts + `.github/workflows/`, same
routing logic the work order already applied to T-36.1.1/T-36.1.2 — no
`app/schemas/` involved, general-purpose scripting/infra work).
Sequential: **T-36.2.1 → T-36.2.2** (2 wires the workflow around what 1
builds); both touch disjoint files from every US-36.1 ticket, so this pair
can be dispatched **in parallel** with the US-36.1 backend track if the
orchestrator wants throughput — no shared files between the two stories'
backend work.

- **T-36.2.1 — scan tooling.**
  - **NEW** `scripts/audit_dependencies.py`. Structure it as a pure
    classification function per ecosystem —
    `classify(returncode: int, stdout: str, stderr: str) -> Outcome` where
    `Outcome` is one of `CLEAN` / `VULNERABILITIES_FOUND` / `SCAN_UNAVAILABLE`
    — plus a thin `main()` that shells out to `pip-audit -r
    services/quant-engine/requirements.txt` and (via `npm audit --prefix
    apps/desktop --json` or equivalent) npm's audit, feeding each tool's
    `CompletedProcess` into the classifier. This split is what makes AC5
    (network-hiccup vs. real-vulnerability distinguishable) unit-testable
    without a live network call — see test placement below. Exit codes:
    `0` clean, `1` vulnerabilities found, `3` scan unavailable (distinct
    from both, so a caller — the new workflow — can branch on it without
    parsing text).
  - **EDIT** `services/quant-engine/requirements-dev.txt` — add
    `pip-audit`, following the existing pattern that dev/CI-only tooling
    (ruff, vulture) lives in `-dev`, never in the exact-pinned
    `requirements.txt` (that pin stays reserved for the golden-sensitivity
    rationale already documented there — do not touch `requirements.txt`
    itself).
  - Unit test for the classifier: **NEW**
    `services/quant-engine/app/tests/test_audit_dependencies.py`, importing
    `scripts/audit_dependencies.py` (via `sys.path` manipulation to reach
    `scripts/`, since nothing under `scripts/` is currently covered by
    pytest — this is the first script to get pytest coverage in this repo;
    flagging as a genuinely new pattern, not an established one, so the
    engineer isn't left guessing why no precedent exists). Cases: a
    representative `pip-audit`/`npm audit` "found N vulnerabilities" stdout
    → `VULNERABILITIES_FOUND`; a representative "clean" output → `CLEAN`; a
    representative connection-error/timeout stderr → `SCAN_UNAVAILABLE`. No
    live network call in the test — all three cases are canned
    `CompletedProcess`-shaped fixtures. Fold this test into the same
    `backend-engineer` order as T-36.2.1 (the story carves out no separate
    test ticket for US-36.2, and the classifier is small enough that
    splitting it into a third dispatch is pure overhead).

- **T-36.2.2 — surface findings.**
  - **NEW** `.github/workflows/dependency-audit.yml`. Triggers:
    `schedule` (weekly) + `workflow_dispatch`. Steps: install backend +
    frontend deps (mirroring `ci.yml`'s setup steps), run
    `scripts/audit_dependencies.py` for both ecosystems, write a
    human-readable summary to `$GITHUB_STEP_SUMMARY` naming which ecosystem
    and outcome, and **fail the job only on `VULNERABILITIES_FOUND`** — a
    `SCAN_UNAVAILABLE` outcome must NOT fail the job (AC5's requirement
    applied at the workflow layer: a transient network hiccup must not read
    as a false vulnerability report) but must say so plainly in the summary
    so it isn't silently swallowed either. `run_all_tests.py`/`ci.yml` are
    **not modified** by this ticket (AC4).

---

## US-36.3 — doc-accuracy sweep

Confirmed **docs-only** (AC7 guards this; no code path, schema, or computed
value changes in any of the four findings or the retirement action).

### Open decision: AC9 (mechanical route-inventory check) — **IN, add it**

My call as design authority, per the story's own "considering whether... is
worth adding" framing:

- **Precedent already exists in this exact repo for this exact class of
  gap**: `test_docs_paths.py` was built specifically because "a document
  that admits it cannot be trusted is a document that should be checked
  mechanically" (its own docstring, Epic 32). A route-module count that has
  already drifted once (12 vs. 15, three additions across three different
  epics — cache/Epic 20+35, currency_risk/Epic 26, provenance/Epic 18 — none
  of which updated the count) is precisely the "checked twice before and
  drifted back" pattern that doc lesson exists to prevent, not a new class
  of risk.
- **Cost is low and the machinery to build it already exists** as a
  reference shape in the same file (`test_the_scan_is_not_vacuous`'s
  pattern of asserting both the positive and the vacuous-scan-would-still-pass
  failure modes).
- Fixing today's count without a mechanical check leaves
  `current-product-state.md` exactly as fragile as it was before this
  story — the next route module added under Epic 37+ silently re-breaks it,
  and nothing in this slice would have changed that.

Placement: **NEW** `services/quant-engine/app/tests/test_route_inventory.py`
(a new, narrowly-scoped module — matching `test_docs_paths.py`'s own stated
convention of leaving adjacent doc classes "for a follow-up rather than
widened here" — do not fold this into `test_docs_paths.py`). Parse the
"`N` route modules:" bullet list in `current-product-state.md`, compare both
the stated integer and the named set against
`Path("services/quant-engine/app/api/routes").glob("*.py")` (excluding
`__init__.py`), and fail naming the specific missing or extra module — same
"name the offending file" convention `test_docs_paths.py` already
established.

Because this is a **new pytest file**, it is `app/tests/**` — the test
lane's literal scope per `project.md`'s routing table, not docs-engineer's
(which has no `Bash` tool and cannot run pytest to verify its own addition).
**T-36.3.2 therefore splits across two lanes and two work orders:**

- **T-36.3.2a (`docs-engineer`)** — fix
  `docs/product/current-product-state.md:96-108` (12 → 15 modules; add
  `cache.py`, `currency_risk.py`, `provenance.py` rows, matching the
  existing one-line-description style used for the other 12). **Do not
  touch `CLAUDE.md`'s route list** — confirmed already correct (see
  `handoff`); the ticket's job re: `CLAUDE.md` is a one-line
  verify-and-record, not an edit.
- **T-36.3.2b (`test-engineer`)** — the new `test_route_inventory.py` (AC9),
  dispatched after T-36.3.2a so the new test lands green against the
  already-corrected doc rather than red-then-fixed. Not a hard technical
  dependency (the test checks actual repo state against actual doc content,
  independent of ordering), but cleaner sequencing.

### T-36.3.1, T-36.3.3, T-36.3.4 — straightforward `docs-engineer`, no open
questions

- **T-36.3.1**: `docs/contracts/cache-fields.md` — header date (line 9) +
  prose (lines 55-57) describing US-35.2's live namespace enumeration and
  typo-rejection behaviour (confirmed still stale by direct read this pass).
- **T-36.3.3**: `docs/product/prd/epic-24-codebase-improvement.md:3` —
  "Active (started 2026-06-19)" → a status consistent with
  `epic-roadmap.md`'s "Completed Epic 24" section header (confirmed at
  `epic-roadmap.md:971`). Instruct the docs-engineer to pull the actual
  completion date from that roadmap section rather than inventing one.
- **T-36.3.4**: `docs/architecture/system-architecture.md`, "API Boundary"
  section (confirmed empty of this note at lines 241-250) — add a note
  naming `imports.py`'s filesystem-path acceptance and the absence of
  server-side auth as a deliberate, accepted tradeoff, given the local-first
  single-user design and CORS restricted to `localhost:5173`/
  `127.0.0.1:5173` (not wildcard, per scout's confirmed read of
  `app/api/main.py:11-17`) — framed as "decided," not "unnoticed," per the
  finding's own framing. No code change.

### T-36.3.5 — retire the findings doc

**Lane: `docs-engineer`. Hard dependency: the Epic 36 PRD must exist on
disk first** — that file is created by the human/producer at epic-approval
time, not by any engineering lane in this plan. **The orchestrator must not
dispatch T-36.3.5 until
`docs/product/prd/epic-36-findings-first-doc-and-gate-hygiene.md` (or
whatever path/number the human actually approves) exists.** Sequence it
last overall, after T-36.3.1/T-36.3.2a/T-36.3.3/T-36.3.4 have landed (not a
strict technical dependency, but the retirement note should point at a PRD
that already reflects the disposition of every finding it's retiring, not a
still-half-fixed one).

Action: mark `docs/product/review-2026-08-20-findings.md` explicitly
superseded, pointing at the Epic 36 PRD as the live record — per the
producer's brief, do not delete it (preserves the audit trail, including its
own second, self-authored error about the tech-debt-register).

---

## Ordered ticket sequence for dispatch

**Track A — backend (two independent sub-tracks, no shared files, may run
in parallel with each other and with Track B):**

1. `T-36.1.1` — mechanism (`scripts/githooks/pre-commit`,
   `scripts/hooks/git_pre_commit.py`, `scripts/hooks/_commit_gate.py`,
   refactor `pre_commit_gate.py`, bootstrap in `run_all_tests.py`).
2. `T-36.1.2` — regression test (`test_commit_gate.py`). Depends on
   `T-36.1.1`.
3. `T-36.2.1` — scan tooling (`scripts/audit_dependencies.py`,
   `requirements-dev.txt`, `test_audit_dependencies.py`). No dependency on
   `T-36.1.*` — disjoint files, may dispatch in parallel with step 1.
4. `T-36.2.2` — surfacing workflow (`.github/workflows/dependency-audit.yml`).
   Depends on `T-36.2.1`.

**Track B — docs (serialize within the lane; low file overlap but same
lane, same agent type, natural to run sequentially as one or two dispatches):**

5. `T-36.3.1`, `T-36.3.2a`, `T-36.3.3`, `T-36.3.4` — no dependency on each
   other, no dependency on Track A. Can be **one combined `docs-engineer`
   work order** (four independent doc edits, same lane, same low risk —
   mirrors how the story itself bundled these four findings into one story).
6. `T-36.3.2b` (`test-engineer`, `test_route_inventory.py`) — after step 5's
   `T-36.3.2a` lands (soft dependency, for a clean green landing).

**Track C — depends on both tracks + a human/producer step outside any
lane:**

7. `T-36.1.3` (`docs-engineer`) — depends on `T-36.1.1` (step 1) landing.
   Touches `CLAUDE.md` and `project.md`, both also touched near step 5 —
   **do not dispatch concurrently with step 5's docs order**; serialize
   within the docs lane to avoid two agents editing the same files in
   parallel. Natural slot: right after step 1 confirms done, independent of
   Track B's timing.
8. **[Human/producer, not an engineering lane]** — Epic 36 PRD created at
   epic-approval time.
9. `T-36.3.5` (`docs-engineer`) — depends on step 8 (PRD must exist) and,
   for cleanliness, on step 5 having landed. **Last ticket in the epic.**

**No cross-story blocking beyond what's listed above.** US-36.1, US-36.2 and
US-36.3's bulk (everything except `T-36.1.3` and `T-36.3.5`) are mutually
independent and could in principle all be in flight at once; the only real
serialization pressure is (a) within-story dependencies noted above, and
(b) `T-36.1.3` and the Track-B docs order sharing `CLAUDE.md`/
`current-product-state.md`'s parent file, which argues for one docs-engineer
agent handling both rather than two racing.
