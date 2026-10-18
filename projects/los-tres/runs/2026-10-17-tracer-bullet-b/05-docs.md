REPORT 2026-10-17-tracer-bullet-b/05
status:      DONE
verdict:     NONE

changed:
  - los-tres/CLAUDE.md § Commands — table rows for migrate, seed, import feeds, new migration, build CLI; typecheck, e2e and gate rows updated
  - los-tres/CLAUDE.md § Commands — first-run steps for demo data and the demo page URL, SEED_DEMO_DATA paragraph, Compose verb forms, gate coverage note

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order verification NONE (no shell); command-to-script mapping in handoff

contract_notes:
  - CLAUDE.md § Stack still lacks the CSS Modules line (decision 0011); close docs owns it, deliberately not touched here.
  - CLAUDE.md § Canonical documentation is unchanged; if close docs adds decision 0011 the table needs no row, since docs/decisions/ is already listed.
  - All 01-design and 02-backend contract notes about CLAUDE.md § Commands (SEED_DEMO_DATA, verbs migrate/seed/import-feeds, stale .env) are absorbed.
  - Design contract notes on schema, product-page type, messages, feed CSV and vitest.config.mts are not docs-lane items and are dismissed here; close docs and the pack-corrections order carry them.
  - Pack corrections listed by 01, 02 and 04 are not applied by this lane; they go to the close-out pack-corrections order.

pack_corrections:
  - none

handoff:
  - Documented command to package.json script, exact names: `npm run db:migrate` to db:migrate; `npm run db:seed` to db:seed; `npm run import-feeds` to import-feeds; `npm run db:generate` to db:generate; `npm run cli:build` to cli:build.
  - Existing rows re-checked against package.json: lint, typecheck, test, test:unit, test:integration, test:e2e, test:e2e:install, env:init, db:up, stack:up, stack:down, dev, build, gate.
  - Compose forms documented from design § Paths: `docker compose run --rm app migrate`, `seed`, `import-feeds [--feed <id>]`, with -T and --no-deps for scripts; unknown verb exits 64.
  - Demo page URL documented: `http://127.0.0.1:3000/producto/demo-filtro-de-aceite-oc-1234`, port is APP_PORT. The first-run steps use `npm run stack:up` in place of the design's `docker compose up -d --build --wait`, which is the same command.
  - Integration should check the first-run block end to end from a fresh `.env`, and that the e2e failure message quoted in CLAUDE.md matches tests/e2e/global-setup.ts.
  - Not documented because package.json has no script for them: the exit codes 1 and 2 of import-feeds; the design lists them but they are CLI detail, left out to keep § Commands short.

skill_calls:
  - none

risks:
  - The quoted e2e failure message comes from design TD-38; I did not open tests/e2e/global-setup.ts, so wording may differ slightly from what shipped.
  - The Compose verbs reach the Compose database by design; I did not run them. The statement that `npm run` forms use the host database rests on `.env` DATABASE_URL pointing at the host port, which I did not verify.
  - New lines were inserted into a CRLF working copy through single Edit calls, so some inserted lines may carry LF endings; git diff may show mixed endings.
  - I did not read project.md; the order and the design carried everything the edit needed.
