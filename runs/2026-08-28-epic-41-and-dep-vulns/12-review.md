REPORT 2026-08-28-epic-41-and-dep-vulns/12
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   python scripts/run_all_tests.py
  result:    PASS
  detail:    Full suite green — backend pytest 949 passed (45 warnings); desktop vitest 359 passed across 40 files; tsc --noEmit clean; dead-code strict gate (ruff+vulture+knip) clean. Satisfies US-41.3 AC7 and US-42.1 AC11.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - AC3 (US-41.3): the full line-by-line re-audit of current-product-state.md's body is not independently re-verifiable at this gate; the checkable recorded specifics (25 non-__init__ service modules, 15 route modules) hold and no methodology/trust claim was edited.
  - AC5 (US-42.1): the trial bump ran a 16-file / 437-test sensitive subset, not the full suite — disclosed in the doc as carried-forward-unverified. Accepted as honest scoping, not an AC failure.
  - test_roadmap_epic_ordering._MIN_EXPECTED_HEADINGS = 20 against 33 actual headings (DESIGN said ~25) — a looser non-vacuity floor than designed but still non-vacuous; acceptable.
  - US-41.3 leaves AC7 and T-41.3.4 checkboxes unticked and Status "Next phase" though the suite is green and the guard test passes — order-11 CR-2 for close-out order 13; no AC covers story status, so not an acceptance failure.
  - US-42.1 carries Status "Done" while keeping its draft/not-owner-approved banner and stale Open decisions — order-11 CR-1 for close-out order 13; no AC covers story status, so not an acceptance failure.
  - current-product-state.md / epic-roadmap.md working-tree diffs also carry 2026-08-27 US-41.2 close-out residue (header dates, seam paragraph) outside this run and excluded per the work order.

## Orchestrator brief

- Overall verdict: PASS. US-41.3: PASS (AC1-AC7 all SATISFIED). US-42.1: PASS (AC1-AC11 all SATISFIED). No AC failure in either story.
- Suite run at this gate: backend 949 passed, frontend 359 passed, tsc clean, dead-code clean. This is the AC7 / AC11 evidence.
- Both test plans delivered: US-41.3 ships the roadmap-ordering guard (test_roadmap_epic_ordering.py — strictly-descending assert that names the offending pair + non-vacuous scan) confirmed red-before / green-after by order 11; US-42.1's assessment method is recorded with exact commands (pip_audit==2.10.1, api.osv.dev, GitHub Advisory DB REST API, npm audit) and the named 16-file subset — reproducible.
- Two known SHOULD_FIX items (order 11 CR-1 / CR-2 — US-42.1 draft banner vs Status:Done, US-41.3 Status:Next phase) are close-out hygiene for order 13, noted in risks, NOT counted against acceptance.
- Sections below: per-AC evidence for both stories. No sections beyond this brief, the per-AC tables and the report block.

---

## US-41.3 — per-AC verdict

| AC | Verdict | Evidence |
|---|---|---|
| AC1 — DriftWindow/coverage TS columns match the shipped type | SATISFIED | Confirmation record present in story `## Notes / decisions` (2026-08-28 docs-engineer entry). Verified independently: `correlation-fields.md`'s `DriftWindow` table matches `apps/desktop/src/features/portfolio/types.ts:1517-1528` field-for-field (`label:string`; `start_date/end_date:string\|null`; `portfolio/benchmark/spread_pct:number\|null`; `trust:'synthetic'\|'unavailable'`; `note:string\|null`). Relocated `coverage` row matches `coverage?: SyntheticHistoryCoverage \| null` at types.ts:1601 (doc's `\| null \| undefined` = the `?`+`\|null` shape). Columns predate this run; the deliverable is the record — present, dated, correct. |
| AC2 — schema citations name the defining module | SATISFIED | `docs/contracts/correlation-fields.md:84` now reads `**Backend schema:** services/quant-engine/app/schemas/reconciliation.py — RollingRiskPoint (series assembled by analytics/risk.py — build_rolling_risk_series)`. `class RollingRiskPoint` confirmed at `schemas/reconciliation.py:122`; not in `analytics/risk.py`. `docs/contracts/factor-drift-fields.md:4` reads `**Backend schema:** _none_ — this card has no backend route or schema`; cites no Pydantic class, so N/A — recorded as such in the story. |
| AC3 — current-product-state.md body re-audited | SATISFIED | Outcome recorded in story `## Notes / decisions` as option (a) confirmed-accurate + one non-methodology correction: `~16 service files` → `~25 service files`. Verified: `ls app/services/*.py \| grep -v __init__` = 25. Diff scanned for trust/methodology terms — the only hits are prior-run US-41.2 residue (header date, seam paragraph), not new edits. No methodology/trust claim altered; no quant referral raised (methodology $-figure item was routed, not touched — see AC6). |
| AC4 — epic-roadmap.md sections in one consistent order | SATISFIED | `grep -nE '^## .*Epic [0-9]+'` → per-epic headings run strictly descending 40,39,…,9,8 (33 headings, no transposition). `git diff` shows the Epic 23 section block removed at ~L1288 and re-inserted byte-identically at ~L1367 (after Epic 24) — no `### Goal`, PRD link, story-snapshot row or slice-log row reworded or dropped. Epic 33 heading normalised from `## Epic 33 — … (complete)` to the majority `## Completed Epic: Epic 33 —` form. |
| AC5 — CLAUDE.md doc map lists currency-risk-fields.md | SATISFIED | `git diff CLAUDE.md`: one row added directly after the `docs/contracts/risk-fields.md` row, same table form, describing the Currency Risk Contribution contract (return-decomposition + component-covariance variance shares, Epic 26). Target file `docs/contracts/currency-risk-fields.md` exists and is that contract (header: "Currency Risk Contribution (Epic 26 / US-26.2)"). |
| AC6 — no stale pointer/label/ordering residue | SATISFIED | Every "already closed" claim in the story's AC6 table re-verified in the repo: `stories/README.md` epic headings all read `(complete)` (no `(active)`/`(backlog)`, no `(completed)` spelling); `### Epic 30` heading present (L167); `build-story` in `stories/README.md` is only the historical US-32.3 slice-log row (L149); `prd/README.md:31` = "The old build-story skill is superseded and must not run."; `prd/README.md` § Index defers to `epic-roadmap.md` as authoritative, no "Active" assertion; `stories/README.md` sections descending 40→8. Two items correctly left un-edited: CLAUDE.md Epic-34 pointer (out of scope — surfacing only) and the `financial-methodology.md` −$53.13/−$58.11/−$19.98 figure (methodology claim — routed to quant lane, not a docs edit). |
| AC7 — full suite green | SATISFIED | `python scripts/run_all_tests.py` → backend 949 passed, frontend 359 passed (40 files), `tsc --noEmit` clean, dead-code strict gate clean. |

**Test plan:** delivered. `services/quant-engine/app/tests/test_roadmap_epic_ordering.py` — `test_epic_sections_are_in_descending_order` (asserts strictly descending, names the specific out-of-order heading pair on failure) + `test_the_scan_is_not_vacuous` (>=20 headings, Epic 40 present, file exists). Red-before / green-after documented in the module and confirmed by order 11 (RED before order 06's block swap, GREEN after). Falsifiability holds: a transposed pair or a drifted heading regex both fail loudly.

---

## US-42.1 — per-AC verdict

| AC | Verdict | Evidence |
|---|---|---|
| AC1 — one finding per advisory, bijective | SATISFIED | `dependency-advisory-assessment-2026-08.md` L20-21 states the bijection; findings table has exactly 6 rows: F-1 starlette, F-2 pypdf, F-3 python-multipart, F-4 pydantic-settings, F-5 python-dotenv, F-6 @babel/core. Each maps to exactly one named package and back. |
| AC2 — advisory id and severity | SATISFIED | F-1: 6 PYSEC ids + per-id CVSS 3.1 table (PYSEC-2026-161 marked **unverified** — no OSV vector). F-2: 22 distinct ids listed by fix version + CVSS 3.1 3.3–6.5, CVSS-4.0-only records marked unverified. F-3: 6 PYSEC ids + CVSS table. F-4: GHSA-4xgf-cpjx-pc3j, 5.3 Moderate. F-5: PYSEC-2026-2270 / CVE-2026-28684 / GHSA-mf9w-mj56-hr94, 6.6 Medium. F-6: GHSA-4x5r-pxfx-6jf8 / CVE-2026-49356, low, CVSS 3.2 + vector. |
| AC3 — reachability with reasoning | SATISFIED | Each F-n names the vulnerable API/behaviour and traces repo usage with `file:line` / grep evidence, not a bare yes/no. Spot-checked: F-2 `PdfReader` at `importers/espp.py:8,30`, `freedom24.py:8,55`, `interactive_brokers.py:8,75` — accurate; F-3 single `File(...)`/`Form(...)` route at `api/routes/imports.py:73-75` — accurate; F-5 no `import dotenv` in `app/` (only an unrelated test name) — accurate; F-6 build-time-only, `sourceMappingURL` path not reached, trusted-input reasoning. |
| AC4 — minimum non-vulnerable version | SATISFIED | F-1 `1.3.1`, F-2 `6.15.0`, F-3 `0.0.31`, F-4 `2.14.2`, F-5 `1.2.2`, F-6 `7.29.6`. F-1's min-safe has no FastAPI-compatible in-range fix → placed in blocked bucket (c) per AC7. |
| AC5 — golden/analytic impact assessed, not applied | SATISFIED | F-2..F-5: "no movement observed — 16-file / 437-test sensitive subset byte-identical to baseline" from one-package-at-a-time trial bumps in an out-of-repo venv. F-1: "could not be assessed — BLOCKED" (resolver conflict `fastapi 0.119.1 requires starlette<0.49.0` + `Router.__init__() … 'on_startup'` collection failure) — reason recorded. Subset-not-full-suite limit disclosed. No bump committed (AC9). |
| AC6 — advisory-data provenance stated | SATISFIED | Dedicated provenance section: ran the **live** path (network available 2026-08-28) — `pip_audit==2.10.1 -r requirements.txt --format json`, severity from `api.osv.dev/v1/vulns/<id>`, frontend from GitHub Advisory DB REST API cross-checked against `npm audit`. Unverified items enumerated (PYSEC-2026-161 no vector; pypdf CVSS-4.0-only records; the 37-record vs "five advisories" gap; the 16-file subset). |
| AC7 — three-bucket grouping, bijective | SATISFIED | (a) golden-safe: F-2, F-3, F-4, F-5, F-6. (b) needs quant-audit: none (no assessable trial bump moved a golden/analytic output). (c) blocked: F-1 (FastAPI `starlette<0.49.0` pin; needs a FastAPI-bump story first). Every finding in exactly one bucket. |
| AC8 — PRD-foldable form | SATISFIED | "PRD fold-in list (AC8)" table carries id / source / disposition per finding, matching the Epic 36 / Epic 32 findings-list convention. |
| AC9 — no manifest change | SATISFIED | `git status --porcelain` on `requirements.txt`, `requirements-dev.txt`, `package.json`, `package-lock.json` → empty. Working tree adds `docs/product/dependency-advisory-assessment-2026-08.md` (plus US-41.3's doc edits and 2 test files — unrelated). |
| AC10 — frontend advisory's limited surface stated | SATISFIED | F-6 § AC3/AC10: transitive (via `@vitejs/plugin-react@4.7.0` → `@babel/core ^7.28.0`), dev/build-time-only, **no shipped runtime surface** (`grep dist/` for babel/sourceMappingURL → no matches). Lockfile-only resolution confirmed — `7.29.6`/`7.29.7` satisfy `^7.28.0`, no `package.json`/`overrides`/toolchain bump. Reachability reasoned, not defaulted to "not reachable". |
| AC11 — suite stays green | SATISFIED | Same run as US-41.3 AC7 — `python scripts/run_all_tests.py` green with the findings doc in place and manifests unchanged. |

**Test plan:** delivered. No new test code (it is an audit); the assessment method is recorded and reproducible — exact commands (`pip_audit==2.10.1`, `api.osv.dev/v1/vulns/`, GitHub Advisory DB REST API, `npm audit`), the named 16-file sensitive subset, the throwaway-venv one-package-at-a-time procedure, and the working-tree-clean check.
