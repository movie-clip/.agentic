REPORT 2026-08-28-epic-41-and-dep-vulns/05
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only DESIGN order, no verification command named

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - T-42.1.1 to backend-engineer lane — assess the 5 backend advisories (advisory data, reachability, min safe version, throwaway-env trial bump); produces draft F-1..F-5 in its report artifact — see § Lane split
  - T-42.1.2 to frontend-engineer lane — assess @babel/core: lockfile-only resolution?, min safe version, build-only reachability; produces draft F-6; independent of T-42.1.1 — see § Lane split
  - T-42.1.3 to docs-engineer lane — write docs/product/dependency-advisory-assessment-2026-08.md consolidating F-1..F-6 + three-bucket grouping + provenance; consumes the 05 and 06 artifacts; depends on both — see § Lane split
  - dispatch order: T-42.1.1 and T-42.1.2 in parallel, then T-42.1.3; gates are integration + acceptance only, no quant-audit (owner decision) — see § Dispatch order
  - the trial bump runs in a git worktree or an out-of-repo venv so the manifests stay structurally byte-identical (AC9), not by vigilance — see § Trial-bump mechanics
  - offline degrade path: on SCAN_UNAVAILABLE or a pip failure, AC5 per-finding becomes "could not be assessed - offline", AC6 says so, and F-1..F-6 still ship from carried ids + changelogs + static import-graph analysis — see § Offline constraint
  - reachability seed naming the app/ call site for each of the 5 backend packages, so the implementer starts from a map — see § Reachability seed
  - findings-document format is the Epic 36 PRD findings-table form (one row per F-n carrying id / source / disposition), PRD-foldable at close-out — see § Findings document
  - a starlette trial bump may fail pytest collection (FastAPI 0.119.1 breaks on starlette >= 0.49.1) — that is a "blocked" finding, bucket (c), not an inconclusive trial — see § Risks

risks:
  - guardrail 1 tension: the AC5 trial bump exercises analytic output, though nothing is committed — see § Risks for the owner-waiver scope and what T-42.1.1 must carry forward
  - build lanes may run with network blocked even though this design env reached PyPI on 2026-08-28 — the § Offline constraint degrade path must be followed per-finding, not assumed either way
  - AC4 needs the full per-package advisory list, not just the one carried id; offline it is changelog-inferred and marked unverified per AC6
  - @babel/core is transitive-only (not in package.json; lockfile shows `^7.28.0` -> 7.29.0 via the Vite toolchain); whether a lockfile-only fix exists is T-42.1.2's finding, and AC10 forbids defaulting to "not reachable"
  - test fixture app/tests/test_audit_dependencies.py:43 carries a placeholder GHSA (`GHSA-xxxx-xxxx-xxxx`) for pypdf — fixture text, not a real advisory id; do not carry it into F-2

## Orchestrator brief

- D1: findings doc = `docs/product/dependency-advisory-assessment-2026-08.md` (confirmed; matches the `docs/product/review-2026-08-20-findings.md` precedent; docs lane keeps the final-name call per AC1). Not `docs/architecture/`.
- D2: format = Epic 36 PRD findings-table form — one row per F-n (id / package + advisory ids / source / severity / reachability / min-safe version / golden-analytic impact / bucket), with prose beneath each row for the AC3 reasoning a table cell cannot hold.
- D3: lane split — T-42.1.1 to backend-engineer, T-42.1.2 to frontend-engineer, T-42.1.3 to docs-engineer; no scout pass (the reachability seed plus the backend lane reading app/ covers it).
- D4: trial bump runs in a git worktree or an out-of-repo venv so AC9 is structural, not watched.
- D5: no quant-audit gate (owner); T-42.1.1 still flags any analytic-output movement as remediation-story quant input.
- D6: network treated as available (design env reached PyPI 2026-08-28); degrade per-finding on SCAN_UNAVAILABLE or a pip / npm failure.
- D7: contract — zero manifest, schema and code change; the only new artifact is the Markdown findings doc; nothing for integration to mirror; backend + frontend goldens byte-identical.
- dispatch: T-42.1.1 and T-42.1.2 in parallel, then T-42.1.3; gates = integration + acceptance only.
- sections below: TECHNICAL PLAN (contract / reuse / lanes / decisions) · Lane split · Offline constraint · Trial-bump mechanics · Findings document · Reachability seed · AC traceability · Dispatch order · Risks.
- blocks dispatch: none. The plan is buildable as written; story owner-approval remains the human's step.

## TECHNICAL PLAN

    contract:   US-42.1 changes NO dependency manifest, NO Pydantic schema, NO
                code. `services/quant-engine/requirements.txt`,
                `requirements-dev.txt`, `apps/desktop/package.json` and
                `apps/desktop/package-lock.json` are byte-identical before and
                after. The single new artifact is one Markdown file,
                `docs/product/dependency-advisory-assessment-2026-08.md`. There
                is no backend/frontend boundary crossing here and nothing for
                the integration gate to align field-by-field. Backend goldens
                and `apps/desktop/src/test/dashboardGoldens.ts` stay
                byte-identical.
    reuse:      `scripts/audit_dependencies.py` (the live confirming scan; its
                `classify()` -> CLEAN | VULNERABILITIES_FOUND | SCAN_UNAVAILABLE
                is the offline/online signal); US-36.2 § Out of scope and the
                Epic 36 PRD Non-goals bullet (the carried 6-advisory list and
                its exact wording); `docs/product/review-2026-08-20-findings.md`
                (findings-doc location precedent); Epic 36 PRD
                "### Findings and disposition" table (the F-n row format AC8
                folds in).
    lanes:      T-42.1.1 -> backend-engineer; T-42.1.2 -> frontend-engineer;
                T-42.1.3 -> docs-engineer. Detail + justification in § Lane
                split. Verification: none per ticket (read/assess only); the
                human runs `python scripts/run_all_tests.py` once after
                T-42.1.3 for AC11.
    decisions:  D1..D7 in the Orchestrator brief. The load-bearing ones:
                findings doc lives in `docs/product/` (D1); the trial bump is
                isolated by a git worktree / out-of-repo venv, not by care
                (D4); network is treated as available with a per-finding
                degrade path (D6); no quant-audit gate but analytic-output
                movement is carried forward as remediation input (D5).
    risks:      In § Risks and the report `risks` block — guardrail-1 tension
                on the trial bump, the environment's network being
                indeterminate for build lanes, the starlette/FastAPI
                collection incompatibility turning a trial into a blocked
                finding, and @babel/core being transitive-only.

## Lane split

**T-42.1.1 — five backend advisories -> `backend-engineer` lane.**
The ticket couples three activities on one package set: (a) source advisory
id / severity / affected range; (b) trace reachability through
`services/quant-engine/app/`; (c) run a throwaway-env trial bump exercising the
golden, route-introspection and methodology pytest subsets. (b) and (c) both
require reasoning about engine internals and running pytest against them —
`backend-engineer` owns `services/quant-engine/app/**` (non-test) and carries
`Bash` plus `mcp__project__run_tests` / `probe_engine` / `build_snapshot`. The
`scout` could do (b) but is read-only and shell-less, so it cannot do (c), and
splitting (b) from (c) would put two lanes on the same five packages. The
`test-engineer` owns *editing* test files; nothing here edits a test, so it is
not the owner. Output: draft `F-1..F-5` written as a section of the 05 report
artifact, each finding carrying a recommended remediation bucket (a/b/c per
AC7) and, if the trial bump moved any analytic output, an explicit handoff
flag for the remediation story's quant routing.

**T-42.1.2 — `@babel/core` -> `frontend-engineer` lane.**
Transitive, dev / build-time, low severity. Determining whether a lockfile-only
resolution exists needs `npm ls @babel/core` / `npm audit` / an `overrides`
trial in `apps/desktop`, which is `frontend-engineer` territory (`Bash`, owns
`apps/desktop/src/**`, knows the npm toolchain). Independent of T-42.1.1 — do
not block it on the backend work. Output: draft `F-6` as a section of the 06
report artifact, with the AC10 statement (build-time surface only, no shipped
runtime surface) and — per AC10 — an explicit "cannot be determined" if
reachability is genuinely unresolvable, never a silent default to "not
reachable".

**T-42.1.3 — write-up + remediation grouping -> `docs-engineer` lane.**
This ticket writes an actual file under `docs/**`, which is the docs lane's
fence (the routing table); `backend-engineer`'s scope stops at
`services/quant-engine/app/**`, so it cannot author the doc. `docs-engineer`
consumes the 05 and 06 report artifacts as `inputs`, transcribes `F-1..F-6`
into `docs/product/dependency-advisory-assessment-2026-08.md` in the Epic 36
table form, assembles the three-bucket grouping from the per-advisory bucket
recommendations the two upstream lanes emitted (it does not itself make the
golden-safety call), and writes the AC6 provenance paragraph from the upstream
lanes' sourcing notes. `docs-engineer` has no `Bash`; that is fine — this
ticket runs no command. Depends on both T-42.1.1 and T-42.1.2.

No scout recon pass. The reachability seed below plus the backend lane reading
`app/` directly is sufficient; a separate `scout` investigation would
duplicate it.

## Offline constraint

The story and `01-delivery-brief.md` assert an offline constraint. This design
environment on 2026-08-28 reached `https://pypi.org`, has `pip-audit==2.10.1`
installed and `npm 11.12.0` present — so the live path is likely available to
build lanes, but a sandboxed lane may still have network blocked. Both cases
are in scope:

**Network available (expected).**
- Confirm the advisory set: run `python scripts/audit_dependencies.py` (or
  `python -m pip_audit -r services/quant-engine/requirements.txt` for the
  backend alone, `npm audit --prefix apps/desktop --json` for the frontend).
  Cross-check the output against US-36.2 § Out of scope and the Epic 36 PRD
  Non-goals bullet — those three must agree, and any advisory only one source
  names is flagged.
- AC4 minimum safe version: take pip-audit's fix recommendation, corroborate
  with `pip index versions <pkg>` and the package changelog.
- AC5: run the real trial bumps per § Trial-bump mechanics.

**Network absent (degrade, do not block).**
- `audit_dependencies.py` returns SCAN_UNAVAILABLE (exit 3) / `pip install`
  from PyPI fails. The story degrades to a documented-limitation finding; it is
  not blocked.
- AC2 / AC4: source advisory ids, severity and affected/fixed ranges from the
  carried US-36.2 list, an offline OSV / GHSA mirror if one is reachable, and
  the packages' own release notes / changelogs. Mark every value not confirmed
  against a live database **unverified**, per AC6.
- AC5: each backend `F-n` records "could not be assessed — offline"; the AC5
  reason is the offline state. The fallback evidence is upstream changelogs
  between the pinned and fixed versions, the packages' own behaviour/test
  notes, and whether the bump is patch / minor / major.
- AC3 reachability is unaffected — the import-graph analysis is static and
  needs no network.
- AC6 provenance paragraph states the offline state plainly and lists which
  fields are unverified.

## Trial-bump mechanics

Goal: observe golden / analytic movement from each candidate bump while
`requirements.txt` and `requirements-dev.txt` stay byte-identical (AC9).

1. **Isolate the tree.** `git worktree add ../us42-trial-tree HEAD` (or work
   from a copy outside the repo). All trial work happens there; the bound
   working tree is never touched. `git worktree remove ../us42-trial-tree`
   at the end.
2. **Isolate the interpreter.** In the worktree, `python -m venv .trial-venv`
   (a path already git-ignored, or under the system temp dir — never the
   committed `.venv`). `pip install -r services/quant-engine/requirements.txt`
   for the baseline.
3. **One candidate at a time.** `pip install <pkg>==<AC4 version>` (letting pip
   resolve transitive deps), then run the sensitive subsets. Reset with
   `pip install -r services/quant-engine/requirements.txt` before the next
   candidate so bumps are not compounded.
4. **What to run.** From `services/quant-engine`: the golden-fixture assertion
   tests, the route-introspection / route-inventory tests
   (`test_route_inventory.py` and siblings), and the methodology / analytics
   regression tests. Run the *assertion* tests (which fail if output moved) —
   not any golden-regeneration step — so nothing writes a fixture. The
   backend lane picks the exact pytest node ids from the test tree.
5. **Record.** Per candidate: PASS (no movement observed) / FAIL naming the
   golden or analytic output that moved / could-not-assess with the reason
   (e.g. tests failed to *collect* — see § Risks on starlette).
6. **Discard.** Remove `.trial-venv` and the worktree. Confirm
   `git status --porcelain` in the bound repo shows only the new
   `docs/product/*.md` file (added later by T-42.1.3).

`apps/desktop` goldens are not exercised by a backend bump — no frontend
rebuild needed. If PyPI is unreachable, steps 2-5 collapse to the changelog
review described in § Offline constraint.

## Findings document

**Home:** `docs/product/dependency-advisory-assessment-2026-08.md` (D1). This
matches the one existing precedent, `docs/product/review-2026-08-20-findings.md`
— a between-work findings doc that lives in `docs/product/` and is later folded
into an epic PRD and marked superseded. Not `docs/architecture/` (that dir is
seams / route inventory / truth classes, not point-in-time findings). The docs
lane keeps the final-name latitude AC1 grants it.

**Format:** the Epic 36 PRD "### Findings and disposition" table form — a
Markdown table, one row per finding:

`| # | Package | Advisory id(s) | Source | Severity | Reachable? | Min safe version | Golden / analytic impact | Bucket |`

with `F-1 .. F-6` in column 1 (`F-1` starlette, `F-2` pypdf, `F-3`
python-multipart, `F-4` pydantic-settings, `F-5` python-dotenv, `F-6`
@babel/core — a bijection to the six named advisories, AC1). Below the table,
one prose paragraph per finding carrying the AC3 reachability reasoning (the
vulnerable API named, and whether this repo exercises it) that a table cell
cannot hold. Then the AC7 three-bucket section and the AC6 provenance
paragraph. This table is the PRD-foldable form AC8 requires — each row already
carries id, source and disposition.

## Reachability seed

A starting map, not the finding. Each backend package, and the module(s) under
`services/quant-engine/app/` where its vulnerable surface would be exercised if
at all:

- **starlette==0.48.0** — request routing / `UploadFile` / multipart form
  handling. Only consumer of that surface:
  `app/api/routes/imports.py:71-101` (`analyze-uploaded-...`, `list[UploadFile]
  = File(...)`, `Form(...)`). Also the app object and CORS middleware in
  `app/api/main.py`. Local-first single-user server, not network-exposed
  (F-R8 accepted tradeoff).
- **pypdf==6.9.1** — malformed-PDF parsing (historic advisories: infinite
  loop / excessive RAM on crafted PDFs). Call sites: `app/importers/espp.py:30`,
  `app/importers/freedom24.py:55`, `app/importers/interactive_brokers.py:75` —
  all `PdfReader(str(path))` on broker-supplied statement PDFs. Reachable;
  input is the user's own broker statements.
- **python-multipart==0.0.20** — multipart/form-data parsing DoS on malformed
  input. Single call site: the same `app/api/routes/imports.py` upload
  endpoint; it is the only route using `File(...)` / `Form(...)`.
- **pydantic-settings==2.13.1** — env-file / settings parsing. Call site:
  `app/core/settings.py:6,29` — `Settings(BaseSettings)` with
  `SettingsConfigDict(env_file=".env")`, loaded once via `get_settings()`
  (`lru_cache`). Exercised only at startup, input is a local `.env`.
- **python-dotenv==1.1.1** — `.env` parsing. No direct `import dotenv` in
  `app/` (grep: only the `pydantic_settings` usage) — reached transitively via
  pydantic-settings' `env_file` handling. Startup only, local file.

## AC traceability

| AC | Ticket(s) | Method / path |
|---|---|---|
| AC1 one F-n per advisory, bijective | T-42.1.3 assembles; T-42.1.1 (F-1..F-5), T-42.1.2 (F-6) | one table row per package in the findings doc |
| AC2 advisory id + severity | T-42.1.1, T-42.1.2 | `audit_dependencies.py` / `pip-audit -r` / `npm audit` output (online) or carried US-36.2 ids + GHSA/OSV changelog (offline, marked unverified) |
| AC3 reachability + reasoning | T-42.1.1 (backend), T-42.1.2 (frontend) | static import-graph read of `app/` against the vulnerable API each advisory names; seed in § Reachability seed |
| AC4 minimum non-vulnerable version | T-42.1.1, T-42.1.2 | pip-audit fix recommendation + `pip index versions` (online) or changelog (offline, unverified); "no fixed version" -> bucket (c) |
| AC5 golden / analytic impact, not applied | T-42.1.1 only | § Trial-bump mechanics; result is one of no-movement / movement-(named) / could-not-assess-(reason) |
| AC6 advisory-data provenance | T-42.1.3 writes; sourced from T-42.1.1 / T-42.1.2 notes | provenance paragraph in the doc, lists unverified fields |
| AC7 three-bucket grouping, every advisory in exactly one | T-42.1.3 assembles from per-advisory bucket recs emitted by T-42.1.1 / T-42.1.2 | (a) golden-safe (b) may move analytic output -> quant-audit, named individually (c) blocked, with reason |
| AC8 PRD-foldable form | T-42.1.3 | Epic 36 PRD findings-table form (id / source / disposition per row) |
| AC9 no manifest change, byte-identical | all three lanes | structurally guaranteed by D4 (worktree / out-of-repo venv); no lane edits `requirements*.txt` / `package.json` / `package-lock.json` |
| AC10 @babel/core limited surface stated explicitly | T-42.1.2 | lockfile dependency trace + `npm ls`; explicit "cannot be determined" if unresolvable, never a silent "not reachable" |
| AC11 suite green | human, after T-42.1.3 | `python scripts/run_all_tests.py`; only the new `.md` file added |

## Dispatch order

1. **T-42.1.1** (backend-engineer) and **T-42.1.2** (frontend-engineer) — in
   parallel. Independent package sets, independent toolchains.
2. **T-42.1.3** (docs-engineer) — after both. Takes the 05 and 06 report
   artifacts as `inputs`, writes the findings doc.
3. **Human** runs `python scripts/run_all_tests.py` (AC11).
4. **Gates:** integration + acceptance only. No quant-audit gate for this
   story (owner decision — nothing is committed, no analytic code changes).
   Integration confirms AC9 (manifests byte-identical, goldens byte-identical,
   only the new `.md` added) and that no lane strayed outside its fence.

## Risks

- **Guardrail 1 / trial bump.** The AC5 trial bump exercises analytic output.
  The owner waived a quant-audit gate here because nothing is committed and no
  analytic code changes. But if the trial bump *observes* analytic-output
  movement (not merely serialization/formatting), that observation is
  remediation input and the remediation story that applies the bump inherits a
  quant-audit requirement. T-42.1.1 must surface such an observation in its
  report `handoff`, not bury it in the findings-doc table.
- **Network indeterminate for build lanes.** This design environment reached
  PyPI on 2026-08-28, but a build lane may be sandboxed. The degrade path in
  § Offline constraint must actually be followed per-finding when
  `audit_dependencies.py` returns SCAN_UNAVAILABLE or `pip install` fails —
  not assumed unreachable, not assumed reachable.
- **starlette bump breaks pytest collection.** `requirements-dev.txt` lines
  21-25 record that FastAPI 0.119.1 raises
  `Router.__init__() got an unexpected keyword argument 'on_startup'` on
  starlette >= 0.49.1, breaking collection of every backend test. If the AC4
  safe version for starlette is >= 0.49.1, the trial bump will fail to
  collect — that is a **blocked** finding (bucket (c): safe bump needs a
  coordinated FastAPI bump), not an inconclusive trial. The backend lane must
  distinguish "failed to collect due to incompatibility" from "golden moved".
- **@babel/core is transitive.** Not in `apps/desktop/package.json`;
  `package-lock.json` shows `@babel/core` `^7.28.0` resolved to 7.29.0, pulled
  by the Vite / dev toolchain. Whether `npm audit fix` or an `overrides` entry
  resolves it lockfile-only without a `package.json` change is T-42.1.2's
  finding. AC10 forbids defaulting to "not reachable" if it cannot be
  determined.
- **Placeholder advisory id in a fixture.**
  `services/quant-engine/app/tests/test_audit_dependencies.py:43` contains
  `pypdf 6.9.1 GHSA-xxxx-xxxx-xxxx 6.9.2` — fixture text, not a real advisory.
  Do not carry it into F-2.
