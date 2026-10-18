REPORT 2026-10-17-tracer-bullet-b/08
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   claude plugin validate <agenticRoot>/plugins/agentic-core; python <agenticRoot>/scripts/check_network_edit.py --verbose
  result:    PASS
  detail:    validate: passed. check_network_edit: 4 UNLINTED (the 4 packs judged here; warning, exit 0). Anchor: protocol/authoring.md. 1 BLOCKING (testing.md, rule 9); 8 SHOULD_FIX (5 carried from 13, 3 new); 11 UNVERIFIED premise groups.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Verdicts: backend.md PASS, frontend.md PASS, architecture.md PASS, testing.md FAIL (one BLOCKING finding, below).
  - BLOCKING new, rule 9 (authoring.md § Two instructions may not disagree): testing.md § What must always be covered l.65 says "a test never runs against the development database", unscoped and always-read.
  - BLOCKING cont.: testing.md § Running tests l.27 and l.33 send e2e against the Compose app, whose data globalSetup writes via import-feeds, and l.33 calls that database "the development database". An e2e helper cannot obey both.
  - BLOCKING fix (docs lane): reword l.65 to "Any integration test or helper that writes to the database calls assertTestDatabase() first; e2e writes only through import-feeds in globalSetup (§ Running tests)." Rule and exception then sit in one bullet.
  - SHOULD_FIX carried from 13, rule 8: testing.md § Running tests l.27 is now a ~1,100-char multi-fact paragraph; the commands-to-needs part belongs in a table.
  - SHOULD_FIX carried from 13, rule 8: testing.md states the e2e base-URL rule twice, l.27 (E2E_BASE_URL default) and l.35 (never a literal base URL); keep it once.
  - SHOULD_FIX carried from 13, rule 8: frontend.md § Next.js and i18n l.52-55 bullets each exceed 200 chars and carry several facts; l.55 (new) adds timezone, ICU and the product route in one bullet.
  - SHOULD_FIX carried from 13, rule 8: "no literal site name" is in frontend.md l.46 (Spanish market conventions) and l.52 (Next.js and i18n); keep it in the always-read one.
  - SHOULD_FIX carried from 13, rule 8: backend.md § Layout l.28-36 are multi-fact paragraphs; l.28 is ~900 chars. Split into bullets; pinned versions (l.30) as a table.
  - SHOULD_FIX new, rule 8: testing.md l.35 "(`appBaseUrl()` is gone)" is change history; it belongs in the commit message. Delete the parenthesis.
  - SHOULD_FIX new, rule 8: backend.md l.22 and frontend.md l.26 keep the heading "Before the stack is recorded" over text saying the stack is recorded; rename, e.g. "When to report BLOCKED".
  - SHOULD_FIX new, rule 8: architecture.md § The seams l.34-43: adding paths pushed the Visibility, Feed ingestion and Matching bullets past 200 chars, unwrapped; move the paths into a seam-to-file table.

skill_calls:
  - none

risks:
  - This verdict certifies authoring only; no path, version, API name or behaviour below was opened in the bound repo.
  - UNVERIFIED: backend.md Layout paths and exports (src/config, src/db, src/server/*, src/cli, tsconfig.cli.json, docker-entrypoint.sh verbs, exit 64).
  - UNVERIFIED: backend.md pinned versions (TypeScript 5.9, ESLint 9, Next 16, Postgres 17, Umami postgresql-v2.20.2, drizzle-kit ^0.31.11, drizzle-orm 0.45.4).
  - UNVERIFIED: backend.md npm run db:generate -- --name flag form, and that the app container migrates on every server start.
  - UNVERIFIED: backend.md Guardrail 2 says the importer parses "CSV or XML"; 07-docs risks says slice B is CSV only.
  - UNVERIFIED: frontend.md formatEuroCents behaviour (useGrouping 'always', U+00A0) and the Intl.NumberFormat four-digit claim.
  - UNVERIFIED: frontend.md next-intl API names (createNextIntlPlugin, getTranslations, getLocale, getRequestConfig timeZone) and the producto/[slug] route path.
  - UNVERIFIED: testing.md test-support file names and exports (global-setup.ts, db.ts resetDatabase/closeDb/assertTestDatabase, catalogue.ts, feeds.ts, network-off.ts, messages.ts).
  - UNVERIFIED: testing.md Vitest 5 version, vitest.config.mts, E2E_BASE_URL default and the Umami 307 at / claim.
  - UNVERIFIED: testing.md tests/unit/seams.test.ts scan list and the ESLint-in-Vitest 60 s timeout.
  - UNVERIFIED: architecture.md seam paths, including src/server/catalogue/product-page.ts.
  - UNVERIFIED: the CRLF tips disagree as facts: backend.md l.36 and frontend.md l.36 prescribe Edit, testing.md l.89 says multi-line Edit fails. Different lanes, so not rule 9; one is likely wrong.
  - Seam paths appear in both architecture.md and backend.md, which tech-lead reads together; consistent today, but rule 5's one-section test is stated per pack, so not filed.
  - Out of scope: project.md § Mechanical gates says "There is no gate command yet" and l.17-22 call the repo greenfield; both are stale against CLAUDE.md npm run gate.
  - check_network_edit.py warns until a PASS lint names these 4 packs; this FAIL does not clear it.
