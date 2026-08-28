REPORT 2026-08-28-epic-41-and-dep-vulns/08
status:      PARTIAL
verdict:     NONE

changed:
  - none

verification:
  command:   cd services/quant-engine && python -m pytest -q
  result:    FAIL
  detail:    1 failed, 948 passed in 94.78s. Sole failure test_roadmap_epic_ordering.py::test_epic_sections_are_in_descending_order (epic-roadmap.md Epic 23 precedes Epic 24) — an untracked sibling Epic-41 lane test/doc in the shared working tree, not dependency-related; this lane wrote nothing and both requirements files are byte-identical.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - F-2 pypdf 6.9.1 -> 6.15.0, F-3 python-multipart 0.0.20 -> 0.0.31, F-4 pydantic-settings 2.13.1 -> 2.14.2, F-5 python-dotenv 1.1.1 -> 1.2.2 are all bucket (a) golden-safe: trial-bumped one at a time in an isolated venv, 437-test sensitive subset (goldens + route inventory + analytics + all engine tests + importer tests) identical to baseline in every case — see § Findings.
  - No analytic-output movement observed in ANY assessable bump, so no F-2..F-5 remediation needs a quant-audit gate (per DESIGN § Risks guardrail-1 carry-forward: nothing to carry — the trial bumps moved zero goldens and zero analytic outputs).
  - F-1 starlette 0.48.0 -> 1.3.1 (min-safe) is bucket (c) blocked: FastAPI 0.119.1 pins starlette<0.49.0; even the lowest single-advisory fix 0.49.1 breaches it, and 1.3.1 fails pytest collection with `Router.__init__() got an unexpected keyword argument 'on_startup'` (reproduced in the isolated venv) — remediation must bump FastAPI first, as its own story.
  - Advisory data is from a LIVE `pip_audit==2.10.1 -r requirements.txt` run on 2026-08-28 (network was available), not the offline degrade path; severity bands are from api.osv.dev CVSS vectors — see § Provenance for what is marked unverified.
  - The docs lane (order 10) should transcribe § Findings F-1..F-5 and § Three-bucket grouping verbatim into the consolidated findings doc; F-6 (@babel/core) comes from the frontend lane (order 09).

risks:
  - verification FAIL is exogenous: the failing test `test_roadmap_epic_ordering.py` plus ~13 modified docs and 6 untracked files in the working tree are in-flight sibling Epic-41 lane work (US-41.1/41.2/41.3) sharing this run's tree; the session-start `git status: (clean)` snapshot was already stale.
  - This lane wrote nothing to the repo; `git status --porcelain services/quant-engine/requirements.txt services/quant-engine/requirements-dev.txt` is empty, so AC9 holds. Non-goal "Do NOT touch anything about Epic 41 / US-41.3" forbids me fixing the sibling failure.
  - AC5 trial bumps ran a 16-file sensitive subset, not the full suite, per DESIGN § Trial-bump mechanics; a bump that moves an output only covered by an excluded test would be missed. The subset covers every golden, route-inventory, analytics and importer test — the paths the manifest header calls FMP/FastAPI/Pydantic-internals-sensitive.
  - Severity for pypdf advisories scored only with a CVSS 4.0 vector in OSV, and for PYSEC-2026-161 (no vector), is marked unverified — no qualitative band is asserted for those beyond "availability-only impact".
  - pip-audit surfaced 37 advisory records across the 5 packages (22 distinct for pypdf alone) — far more than the "5 advisories" the story's carried US-36.2 list implied; the story framing of one-advisory-per-package is inaccurate, though the one-finding-per-package (F-1..F-5) structure still holds.

## Orchestrator brief

- Non-planning lane, but this artifact carries sections beyond the report block: **§ Findings** (F-1..F-5 drafts, one per backend package), **§ Three-bucket grouping** (AC7), **§ Provenance** (AC6). Route these three to order 10 (docs).
- Verdict of the assessment: 4 of 5 backend bumps are golden-safe with confirmed zero movement; 1 (starlette) is blocked on a FastAPI upgrade. No bump needs quant-audit.
- `status: PARTIAL` only because the order's `pytest -q` verification shows one pre-existing sibling-lane failure unrelated to this work; all AC2-AC7 deliverables for the 5 backend packages are complete in § Findings.
- Nothing for integration to mirror: zero schema/route/service/test/manifest edits.

## Findings

Advisory IDs, affected/fixed versions: **live `python -m pip_audit==2.10.1 -r services/quant-engine/requirements.txt --format json`, 2026-08-28**, PyPI reachable (backing DB: PyPI Advisory DB / OSV). Severity: **api.osv.dev per-advisory CVSS vectors**, same date; qualitative band derived from CVSS 3.1 base score. "Min safe version" = highest `fix_versions` entry across every advisory affecting that package.

### F-1 — starlette==0.48.0

**Advisory ids / severity (AC2).** Six distinct advisories:

| id | aliases | vulnerable behaviour | CVSS 3.1 (OSV) | fix |
|---|---|---|---|---|
| PYSEC-2026-161 | CVE-2026-48710, GHSA-86qp-5c8j-p5mr, X41-2026-002 | `Host` header not validated before `request.url` reconstruction; path prepended into host part | no vector in OSV — **unverified** | 1.0.1 |
| PYSEC-2026-248 | CVE-2026-54282, GHSA-jp82-jpqv-5vv3 | HTTP request path not validated in `request.url` rebuild; authority-boundary shift (`@google.com`) | 5.3 Medium | 1.3.0 |
| PYSEC-2026-249 | CVE-2026-54283, GHSA-82w8-qh3p-5jfq | `request.form()` `max_fields` / `max_part_size` silently ignored for `application/x-www-form-urlencoded` → unauth memory-exhaustion DoS | 7.5 High | 1.3.1 |
| PYSEC-2026-1942 | CVE-2025-62727, GHSA-7f5h-v6xp-fcq8 | crafted `Range` header → quadratic-time `FileResponse` range parse/merge → CPU-exhaustion DoS | 7.5 High | 0.49.1 |
| PYSEC-2026-2281 | CVE-2026-48818, GHSA-wqp7-x3pw-xc5r | `StaticFiles` on Windows: UNC path → `os.path.realpath` outbound SMB → NTLMv2 credential leak (SSRF) | 7.5 High | 1.1.0 |
| PYSEC-2026-2280 | CVE-2026-48817, GHSA-x746-7m8f-x49c | `HTTPEndpoint` picks handler by lowercased method via `getattr`, no verb allowlist | 5.3 Medium | 1.1.0 |

**Min non-vulnerable version (AC4): `1.3.1`.**

**Reachability (AC3): none of the six surfaces are exercised by `services/quant-engine/app/`.**
- `request.url` reconstruction (PYSEC-2026-161, -248): `app/api/main.py` builds a bare `FastAPI()` with only `CORSMiddleware` (origins locked to `localhost:5173` / `127.0.0.1:5173`); no `TrustedHostMiddleware`. grep for `request.url` / `starlette...Request` in `app/` (non-test) returns only Pydantic-model params named `request`. No app code reads the reconstructed URL.
- `request.form()` urlencoded limits (PYSEC-2026-249): the only form route is `POST /portfolios/import/interactive-brokers/analyze-upload` (`app/api/routes/imports.py:71-101`), `multipart/form-data` via `File(...)` / `Form(...)`; no urlencoded parsing, no `max_fields` / `max_part_size` set.
- `FileResponse` Range (PYSEC-2026-1942): no `FileResponse` / `StaticFiles` / file-serving anywhere in `app/`.
- `StaticFiles` SSRF (PYSEC-2026-2281): no `StaticFiles` mount.
- `HTTPEndpoint` verb lookup (PYSEC-2026-2280): every route is a function-style `@router.post`; no `HTTPEndpoint` subclass.
- Posture: localhost-bound, single-user, local-first (F-R8 accepted tradeoff) — no network-exposed attacker path.

**Golden / analytic impact (AC5): could not be assessed — BLOCKED.** In the isolated venv `pip install starlette==1.3.1` reports a resolver conflict (`fastapi 0.119.1 requires starlette<0.49.0,>=0.40.0`). `pytest --co app/tests/test_routes.py` then fails at collection: `TypeError: Router.__init__() got an unexpected keyword argument 'on_startup'` from `fastapi/routing.py` on the first `APIRouter(...)` — every test importing `app.api.main` fails to collect. This is the incompatibility already recorded in `requirements-dev.txt:17-24`. Not "golden moved" — no assertion runs.

**Bucket: (c) blocked.** Min-safe 1.3.1 (and even the single lowest fix, 0.49.1) exceeds FastAPI 0.119.1's `starlette<0.49.0` ceiling. Remediation = bump FastAPI to a release admitting starlette 1.x, then re-run the full golden + route-introspection suite; a story of its own.

### F-2 — pypdf==6.9.1

**Advisory ids / severity (AC2).** pip-audit reports **22 distinct** advisories, all "attacker crafts a PDF → infinite loop / long runtime / RAM exhaustion" (availability-only; no code-exec, no disclosure). By fix version:

| fix | ids (alias CVE) | vulnerable behaviour |
|---|---|---|
| 6.9.2 | PYSEC-2026-3012 (CVE-2026-33699) | infinite loop reading a file in non-strict mode |
| 6.10.0 | PYSEC-2026-3006 (CVE-2026-40260) | RAM via XMP metadata parse |
| 6.10.1 | PYSEC-2026-3021 (CVE-2026-41168) | runtime via wrong-large `/Size` in xref streams / `/N` in object streams |
| 6.10.2 | PYSEC-2026-3007, -3011, -3026 (CVE-2026-41313/41312/41314) | runtime/RAM via trailer `/Size`, `/FlateDecode` `/Predictor`, image size |
| 6.12.0 | PYSEC-2026-3004, -3016 (CVE-2026-48156/48155) | runtime via `/W [0 0 0]` xref; RAM via layout-mode large char offsets |
| 6.12.1 | PYSEC-2026-3025 (CVE-2026-48735) | RAM via large XMP metadata |
| 6.12.2 | PYSEC-2026-3020, -3010 (CVE-2026-49461/49460) | RAM via form XObject self-reference; runtime via `/FlateDecode` PNG predictor |
| 6.13.0 | PYSEC-2026-3022, -3009 (CVE-2026-54531/54530) | infinite loop merging outlines into a writer; infinite loop extracting text in layout mode |
| 6.13.1 | PYSEC-2026-3018 (CVE-2026-54651) | infinite loop merging threads/articles into a writer |
| 6.13.3 | GHSA-jm82-fx9c-mx94 (no CVE) | `MAX_DECLARED_STREAM_LENGTH` ignored for content stream with no `/Length` |
| 6.14.0 | PYSEC-2026-3610, -3611 (CVE-2026-59937/59938) | runtime via repeated malformed xref streams; RAM via oversized declared image size |
| 6.14.1 | PYSEC-2026-3612 (CVE-2026-59936) | infinite loop, unterminated inline image in content stream |
| 6.14.2 | PYSEC-2026-3613 (CVE-2026-59935) | infinite loop, unterminated inline image, ASCII85/ASCIIHex filters |
| 6.15.0 | PYSEC-2026-3655, -3656 (CVE-2026-71870/71852) | RAM/runtime via oversized `/ToUnicode` and font-width entries during text extraction |

Severity: OSV gives CVSS 3.1 base **3.3–6.5 (Low–Medium)** where it scores a 3.1 vector; the CVSS-4.0-only records carry no comparable base here — **unverified**, characterised only as availability-impact. GHSA-jm82-fx9c-mx94 = OSV `database_specific.severity` "MODERATE". No advisory exceeds Medium. `test_audit_dependencies.py:43`'s `GHSA-xxxx-xxxx-xxxx` is confirmed fixture placeholder — not carried here.

**Min non-vulnerable version (AC4): `6.15.0`.**

**Reachability (AC3): reachable (text-extraction + xref-parsing paths); NOT the writer/merge or layout-mode paths.** pypdf is imported at `app/importers/espp.py:8,30`, `app/importers/freedom24.py:8,55`, `app/importers/interactive_brokers.py:8,75` — each `PdfReader(str(path))` then `[page.extract_text() or "" for page in reader.pages]` (`_extract_text_by_page`). Reached from `POST /portfolios/import/interactive-brokers/analyze-upload` (uploaded bytes → `tempfile.NamedTemporaryFile` → `PdfReader`) and the local-path import routes. So xref parsing, default-mode text extraction, and font / `/ToUnicode` / `/FlateDecode` stream handling are all reachable. NOT reachable: `PdfWriter` / merge paths (PYSEC-2026-3022 outlines, PYSEC-2026-3018 threads/articles — the app never writes or merges) and `extraction_mode="layout"` (PYSEC-2026-3009 layout loop, PYSEC-2026-3016 layout offsets — the app calls plain `extract_text()`). Practical threat: a malformed/hostile broker statement PDF hangs the importer, not RCE.

**Golden / analytic impact (AC5): no movement observed.** Isolated venv, `pip install pypdf==6.15.0` (`pip check` clean), 16-file sensitive subset → **437 passed**, identical to the 6.9.1 baseline. `test_importer.py` alone = 28 passed, 0 skipped — the real IBKR / Freedom24 / ESPP statement PDFs are present in this checkout and their extracted text + parsed positions are unchanged under 6.15.0.

**Bucket: (a) golden-safe.**

### F-3 — python-multipart==0.0.20

**Advisory ids / severity (AC2).** Six advisories:

| id | alias | vulnerable behaviour | CVSS 3.1 | fix |
|---|---|---|---|---|
| PYSEC-2026-1852 | CVE-2026-24486, GHSA-wp53-j4wj-2cfg | path traversal when `UPLOAD_DIR` set + `UPLOAD_KEEP_FILENAME=True`; crafted filename writes anywhere | 8.6 High | 0.0.22 |
| PYSEC-2026-3038 | CVE-2026-40347 | DoS via large multipart preamble/epilogue | 5.3 Medium | 0.0.26 |
| PYSEC-2026-3039 | CVE-2026-42561 | DoS: no limit on count/size of part headers | 7.5 High | 0.0.27 |
| PYSEC-2026-3037 | CVE-2026-53538 | `QuerystringParser` treats `;` as separator in urlencoded bodies | 3.7 Low | 0.0.30 |
| PYSEC-2026-3036 | CVE-2026-53539 | quadratic separator lookup in `QuerystringParser` for `;`-separated bodies | 7.5 High | 0.0.30 |
| PYSEC-2026-3040 | CVE-2026-53540 | `parse_form()` doesn't validate `Content-Length`; negative → read-until-EOF, whole body one read | 3.7 Low | 0.0.31 |

**Min non-vulnerable version (AC4): `0.0.31`.**

**Reachability (AC3): multipart-parsing DoS surface reachable; querystring + UPLOAD_DIR paths not.** python-multipart is pulled by FastAPI for `multipart/form-data`. Single consumer: `POST /portfolios/import/interactive-brokers/analyze-upload` (`app/api/routes/imports.py:71-101`) — the only `File(...)` / `Form(...)` route. So `MultipartParser` (part-header DoS PYSEC-2026-3039, preamble/epilogue PYSEC-2026-3038) is reachable. NOT reachable: `QuerystringParser` (PYSEC-2026-3037, -3036 — no urlencoded form route in the app) and the `UPLOAD_DIR` / `UPLOAD_KEEP_FILENAME` traversal (PYSEC-2026-1852 — legacy `python_multipart` options the app never sets; FastAPI spools to its own temp file and the route writes via `tempfile.NamedTemporaryFile`). Same localhost-bound single-user posture as F-1 — reachable only by the local user's own upload.

**Golden / analytic impact (AC5): no movement observed.** Isolated venv, `pip install python-multipart==0.0.31`, 16-file subset → **437 passed**, identical to baseline.

**Bucket: (a) golden-safe.**

### F-4 — pydantic-settings==2.13.1

**Advisory id / severity (AC2).** One advisory:
- **GHSA-4xgf-cpjx-pc3j** (no CVE alias). `NestedSecretsSettingsSource`: with `secrets_nested_subdir=True`, a symlink inside `secrets_dir` pointing outside it is followed, reading external files into settings values. OSV CVSS 3.1 base **5.3**, `database_specific.severity` "MODERATE", CWE-22 / 400 / 59. Fix **2.14.2**.

**Min non-vulnerable version (AC4): `2.14.2`.**

**Reachability (AC3): not reachable.** Used only at `app/core/settings.py:6,29` — `class Settings(BaseSettings)` with `model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")`, built once via `get_settings()` (`@lru_cache`). The vulnerable feature is `secrets_dir` + `secrets_nested_subdir` (`NestedSecretsSettingsSource`). The app sets neither — only `env_file`. That code path is never constructed.

**Golden / analytic impact (AC5): no movement observed.** Isolated venv, `pip install pydantic-settings==2.14.2` (pydantic core stayed `2.12.3`, `pip check` clean), 16-file subset → **437 passed**, identical to baseline.

**Bucket: (a) golden-safe.**

### F-5 — python-dotenv==1.1.1

**Advisory id / severity (AC2).** One advisory:
- **PYSEC-2026-2270** / CVE-2026-28684 / GHSA-mf9w-mj56-hr94. `set_key()` and `unset_key()` follow symlinks when rewriting a `.env` file; a local attacker can overwrite an arbitrary file via a crafted symlink when a cross-device rename falls back to copy. OSV CVSS 3.1 base **6.6 Medium** (`AV:L`, local; `UI:R`). Fix **1.2.2**.

**Min non-vulnerable version (AC4): `1.2.2`.**

**Reachability (AC3): not reachable.** No `import dotenv` / `from dotenv` / `load_dotenv` / `set_key` / `unset_key` anywhere in `services/quant-engine/app/` (grep — the only `unset_key` hit is an unrelated FMP-cache test name). python-dotenv is reached transitively only, via pydantic-settings' `env_file=".env"` handling, which calls the read-only parse (`dotenv_values()`). The vulnerable write functions `set_key()` / `unset_key()` are never invoked, directly or transitively. Startup-only, local `.env`.

**Golden / analytic impact (AC5): no movement observed.** Isolated venv, `pip install python-dotenv==1.2.2`, 16-file subset → **437 passed**, identical to baseline.

**Bucket: (a) golden-safe.**

## Three-bucket grouping (AC7)

Every one of the 5 backend packages in exactly one bucket.

**(a) golden-safe — plain remediation ticket, no quant-audit:**
- F-2 pypdf `6.9.1 -> 6.15.0`
- F-3 python-multipart `0.0.20 -> 0.0.31`
- F-4 pydantic-settings `2.13.1 -> 2.14.2`
- F-5 python-dotenv `1.1.1 -> 1.2.2`

**(b) may move analytic output -> route through quant-audit:**
- none. All four assessable bumps showed zero movement across the golden / route-inventory / analytics / importer subset (437 passed, byte-identical to baseline each time).

**(c) blocked:**
- F-1 starlette `0.48.0 -> 1.3.1`. FastAPI 0.119.1 pins `starlette<0.49.0`; the lowest single-advisory fix (0.49.1, PYSEC-2026-1942) already breaches that, and min-safe 1.3.1 breaks pytest collection (`Router.__init__() got an unexpected keyword argument 'on_startup'`, reproduced). Blocking reason: needs a coordinated FastAPI upgrade to a release admitting starlette 1.x, then a full golden + route-introspection re-run (the manifest header calls that path FastAPI/Pydantic-internals-sensitive). Separate story.

## Provenance (AC6)

- **Advisory set, ids, affected/fixed ranges:** live `python -m pip_audit==2.10.1 -r services/quant-engine/requirements.txt --format json`, run 2026-08-28 with PyPI reachable (`urllib` GET `pypi.org` returned 200; `audit_dependencies.classify()` would return `VULNERABILITIES_FOUND`). Backing DB: PyPI Advisory DB / OSV. This supersedes the carried US-36.2 list, which named the 5 packages but carried no ids and implied one advisory each (actual: 37 records, 22 distinct for pypdf).
- **Severity:** `https://api.osv.dev/v1/vulns/<id>` `severity` field (CVSS vectors), fetched 2026-08-28; qualitative band computed from the CVSS 3.1 base score. **Unverified:** any advisory where OSV carries only a CVSS 4.0 vector (all such are availability-only, `VA:H`/`VA:L`) or no vector (PYSEC-2026-161) — no band asserted beyond "availability impact". pip-audit itself emits no severity.
- **Reachability:** static import-graph read of `services/quant-engine/app/` at working-tree HEAD — no network. Call sites cited by `file:line`; absence confirmed by `grep` over `app/` excluding `tests/`.
- **Golden / analytic impact:** trial bumps in a throwaway venv **outside the repo** (`<scratch>/trialvenv`, since removed), one candidate at a time, `pip install -r requirements.txt` baseline restored between each. Sensitive subset (16 files): `test_golden_market_data_basis`, `test_golden_pipeline_determinism`, `test_route_inventory`, `test_architecture_doc_route_inventory`, `test_routes`, `test_analytics`, `test_engine_response_integrity`, `test_distribution_engine`, `test_drawdown_engine`, `test_stress_engine`, `test_correlation_engine`, `test_drift_engine`, `test_exposure_engine`, `test_importer`, `test_importer_csv`, `test_import_admission`. `requirements.txt` / `requirements-dev.txt` never edited — `git status --porcelain` on both is empty (AC9).
- **Not researched (out of scope):** the specific FastAPI version that first admits starlette 1.x — the F-1 "no compatible bump" conclusion rests on the observed resolver conflict + collection failure, not a survey of FastAPI releases.
