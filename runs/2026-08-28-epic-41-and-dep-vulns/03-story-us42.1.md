REPORT 2026-08-28-epic-41-and-dep-vulns/03
status:      DONE
verdict:     NONE

changed:
  - docs/product/stories/US-42.1-assess-outstanding-dependency-advisories.md — new story draft (findings-first dependency-advisory audit, no version change)

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order named no verification command (verification: NONE); this lane writes a story draft only

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Story drafted: docs/product/stories/US-42.1-assess-outstanding-dependency-advisories.md — draft for human review, NOT owner-approved; do not dispatch build lanes until approved
  - Tickets: T-42.1.1 assess the 5 backend advisories; T-42.1.2 assess the frontend advisory (@babel/core, independent, non-blocking on T-42.1.1); T-42.1.3 write up F-1..F-6 + remediation grouping
  - Open decision still blocking this story's gate line: whether the trial-bump observations need a quant sign-off (producer-escalated; owner's call) — ticket authoring is not blocked by it
  - Open, non-blocking: Epic 42 PRD not yet on disk — docs lane writes docs/product/prd/epic-42-dependency-vulnerability-remediation.md at close-out and folds in F-1..F-6
  - Open, non-blocking: remediation stories deliberately unscoped until this audit lands

risks:
  - The six-advisory list was not re-verified against a live vulnerability database (offline constraint, 01-delivery-brief.md § risks); story AC6 forces the assessment to confirm it, but if a current live scan reports a different set the ticket scope shifts
  - Assumed the findings live in a new standalone doc under docs/product/ (working name dependency-advisory-assessment-2026-08.md), mirroring Epic 36's review-2026-08-20-findings.md; the docs lane may prefer to draft straight into the Epic 42 PRD — AC1 names the final path as the docs lane's call
  - Assumed Status "Next phase" per the DoD's "ready-to-build convention"; the producer brief confirmed only the epic number (42), not that the human pulled Epic 42 into the active phase
  - Did not resolve whether a quant-audit gate applies to this audit story — the producer escalated it and it stays open (see handoff)

## Orchestrator brief

- Decision: drafted US-42.1 as a findings-only audit — assess the six advisories, change no version. Status: Next phase. Draft for human review, not approved.
- Decision: findings recorded as F-1..F-6 in a new docs/product/ findings doc (final name the docs lane's call), foldable into the Epic 42 PRD at close-out per Epic 36 / 32 convention.
- Decision: 3 tickets — T-42.1.1 backend (5 advisories), T-42.1.2 frontend (@babel/core, independent, non-blocking), T-42.1.3 write-up + remediation grouping. Lane split left to tech-lead DESIGN.
- Open, blocks the gate line only: does the trial-bump observation need a quant sign-off (producer-escalated). Ticket authoring is not blocked.
- Open, non-blocking: Epic 42 PRD not yet written (docs lane, close-out); remediation stories deliberately unscoped.
- Story file: docs/product/stories/US-42.1-assess-outstanding-dependency-advisories.md
- Sections below: "Story draft" — the full story text as written to the repo (Open decisions, Context, ACs AC1–AC11, test plan / assessment method with no new test code, tickets, out-of-scope, notes).
- No contract notes, no pack corrections.

## Story draft

The full text below is what was written to
`docs/product/stories/US-42.1-assess-outstanding-dependency-advisories.md`. It is
reproduced here so the tech-lead and downstream lanes receive it as an `inputs`
path without opening the repo file.

---

# US-42.1: Assess the six outstanding dependency advisories before any version is changed

**Epic:** Epic 42 — Dependency Vulnerability Remediation
**PRD:** `epic-42-dependency-vulnerability-remediation.md` — not yet on disk; the docs lane writes it at close-out. `F-n` references resolve against that expected path.
**Status:** Next phase
**Last updated:** 2026-08-28

> Draft for human review. Authored by the `story-author` lane; not owner-approved.
> Do not dispatch build lanes until the owner has approved this file and the open
> decision below is closed.

### Open decisions

- **Does this audit's trial-bump observation require a quant sign-off?** Blocks
  finalising the gate line for this story — not ticket authoring. The trial bump
  (AC5) exercises analytic output; guardrail 1 / `project.md` route
  return-basis / weighting / trust-classification changes through the quant lane.
  Nothing is committed and no analytic code changes, so a full quant-audit gate
  may be unwarranted — but whether the observations need a quant reviewer's
  sign-off before they are trusted as remediation input is the owner's call.
  Producer-escalated (`01-delivery-brief.md` § Open decisions).
- **The Epic 42 PRD does not exist yet.** Context; does not block. Epic 42 is the
  owner's confirmed number. Docs lane writes the PRD at close-out and folds in
  `F-1..F-6`.
- **The remediation stories are deliberately unscoped.** Context; does not block.
  Their scope is the safe-bump table this audit produces.

### Story

As a **developer or agent responsible for this project's dependency hygiene**, I
want each of the six outstanding dependency advisories assessed and recorded —
reachability, minimum safe version, and golden / analytic impact — **without
changing any version**, so that the remediation that follows is scoped against
fact instead of guesswork.

### Context

US-36.2 built the scheduled `dependency-audit.yml` workflow and deliberately
deferred acting on its findings. The first real run surfaced six advisories.

Backend (`services/quant-engine/requirements.txt`, pinned exact):
`starlette==0.48.0`, `pypdf==6.9.1`, `python-multipart==0.0.20`,
`pydantic-settings==2.13.1`, `python-dotenv==1.1.1`.

Frontend (transitive, dev / build-time, low severity): `@babel/core`.

Backend versions are pinned exact because the suite's route-introspection and
golden tests are sensitive to FastAPI / Pydantic internals; `starlette`,
`pydantic-settings` and `python-dotenv` sit on that path. Scoping a bump before
knowing whether it moves a golden is the failure the findings-first pattern
prevents.

Offline constraint: live `pip-audit` / `npm audit` could not be re-run at drafting
time (`01-delivery-brief.md` § risks). The six-advisory list is carried from
US-36.2 § Out of scope, the `2026-08-27-next-epic-or-story` brief, and the roadmap
open-items bullet — agreeing, none re-verified against a current database. The
assessment must state its advisory-data provenance and flag anything it cannot
confirm.

Precedent: Epic 36 (built the scan, deferred the fix) and Epic 21 (hardening).
Findings recorded as `F-1..F-n`, folded into the epic PRD at close-out per Epic 32
/ Epic 36.

### Acceptance criteria

- **AC1 — One finding per advisory.** A findings document (working name
  `docs/product/dependency-advisory-assessment-2026-08.md`; final name the docs
  lane's call) records `F-1..F-6`, one for each named advisory. Each advisory maps
  to exactly one `F-n` and back.
- **AC2 — Advisory id and severity recorded.** Each `F-n` records the CVE /
  advisory identifier(s) and the severity as stated by the cited source.
- **AC3 — Reachability recorded with reasoning.** Each `F-n` states whether the
  vulnerable code path is reachable from this repo's actual usage — naming the
  vulnerable API / behaviour and whether this repo exercises it (directly or
  transitively) — with the reasoning, not a bare yes / no.
- **AC4 — Minimum non-vulnerable version recorded.** Each `F-n` records the lowest
  version resolving every advisory affecting that package. If no fixed version
  exists, the finding says so and goes in the "blocked" group (AC7).
- **AC5 — Golden / analytic impact assessed, not applied.** Each backend `F-n`
  records whether bumping to the AC4 version moves any golden fixture or shifts
  any analytic output, observed from a throwaway-env trial bump. Result is one of:
  no movement observed; movement observed (named); could not be assessed (reason).
  No trial bump is committed.
- **AC6 — Advisory-data provenance stated.** The document states how it obtained
  advisory data under the offline constraint. Any advisory not confirmable
  against a source is marked unverified, not presented as current.
- **AC7 — Remediation grouping recommended.** All six advisories grouped into
  exactly three buckets: (a) golden-safe → plain remediation ticket; (b) may move
  analytic output → route through quant-audit, named individually; (c) blocked →
  with reason. Every advisory in exactly one bucket.
- **AC8 — PRD-foldable form.** The `F-1..F-6` list carries id, source and
  disposition, matching the Epic 36 / Epic 32 findings-list convention.
- **AC9 — No manifest change.** `requirements.txt`, `requirements-dev.txt`,
  `apps/desktop/package.json` and `apps/desktop/package-lock.json` are
  byte-identical before and after this story.
- **AC10 — Frontend advisory's limited surface stated.** `F-6` (`@babel/core`)
  states it is a transitive, dev / build-time-only advisory with no shipped
  runtime surface, and whether a lockfile-only resolution exists. If reachability
  is undeterminable it says so rather than defaulting to "not reachable".
- **AC11 — Suite stays green.** `python scripts/run_all_tests.py` passes with the
  findings document in place and the manifests unchanged.

### Test plan

An audit — no new test code. The "test" is the assessment method, recorded in the
document so it is reproducible:

- **Advisory-data lookup** — source id / severity / affected range from the
  carried US-36.2 design-verification output, cross-checked against any offline
  advisory-database mirror and package changelogs; mark anything unconfirmed. A
  live `python scripts/audit_dependencies.py` / the `dependency-audit.yml`
  workflow is the confirming source when network is available.
- **Reachability / import-graph check** — for each backend package, trace whether
  `services/quant-engine/app/` exercises the vulnerable API (`python-multipart` /
  `starlette` request parsing on the import routes; `pypdf` in
  `app/importers/`; `pydantic-settings` / `python-dotenv` in `app/core/` settings
  loading). Record call sites found or their absence.
- **Trial-bump observation** — in a throwaway virtualenv (never the committed
  one), bump each candidate to its AC4 version, run the golden /
  route-introspection / methodology suites, record any diff. Discard the env and
  bump; committed manifests stay byte-identical (AC9).

Regression / guardrail: `run_all_tests.py` green against the unchanged repo;
backend goldens and `dashboardGoldens.ts` byte-identical; no methodology or
contract doc changes.

### Tickets

Ordered. Lane split is the tech lead's call at DESIGN.

- **T-42.1.1 — Assess the five backend advisories.** Confirm the set against
  `dependency-audit.yml` / a current run and US-36.2; source id + severity +
  affected range per the offline method; import-graph reachability check against
  `services/quant-engine/app/`; determine each minimum non-vulnerable version;
  throwaway-env trial bump recording golden / analytic movement. Produces draft
  `F-1..F-5`. Traces AC1–AC6, AC9.
- **T-42.1.2 — Assess the frontend advisory (`@babel/core`).** Confirm transitive
  + dev / build-time-only; whether a lockfile-only resolution exists and the
  minimum safe version; record reachability (build-time only). Produces draft
  `F-6`. Independent of T-42.1.1. Traces AC1–AC4, AC9, AC10.
- **T-42.1.3 — Write up the findings and remediation grouping.** Consolidate
  `F-1..F-6` in the Epic 36 / 32 findings-list form; add the three-bucket
  remediation grouping with reasons; state advisory-data provenance and limits.
  Traces AC6, AC7, AC8, AC10.

No ticket commits, self-gates, or edits a manifest.

### Out of scope

- Applying any version bump or editing any requirements / package / lock file.
- Scoping or writing the remediation stories.
- Writing the Epic 42 PRD, `epic-roadmap.md`, or the story index — docs lane, at
  close-out.
- Choosing the epic number (42 is set) or the exact target versions (a finding,
  not an input).
- Re-running live `pip-audit` / `npm audit` inside `run_all_tests.py` or CI.
- Anything about Epic 41, US-41.1, US-41.2 or US-41.3.

### Notes / decisions

- Why findings-first: three of the five backend advisories sit on the
  golden-sensitive FastAPI / Pydantic path; assess reachability and golden impact
  before scoping a bump.
- Why the frontend advisory is its own ticket: `@babel/core` is transitive,
  low-severity, dev / build-time — likely a lockfile-only bump, kept off the
  backend critical path.
- Offline sourcing: the six-advisory list agrees across three prior artifacts but
  was not re-verified against a live database at drafting; AC6 forces the document
  to be explicit.
- Precedent: Epic 36 built the scan and deferred the fix; Epic 21 is the hardening
  sibling; findings fold into the PRD as `F-n` at close-out.
