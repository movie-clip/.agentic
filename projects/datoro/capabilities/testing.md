# Capability pack: testing — project `datoro`

For the `test-engineer` lane. This is a record of documented friction
(`AGENTS.md` § "Test Commands", "Running A Single Test", "E2E And Environment
Notes", "Testing Expectations"), not a tutorial. Where it contradicts your
general Vitest instincts, this file wins.

---

## Index

Read this block first. You are not expected to read this file end to end — read
what your order touches. Reading one extra section is cheap; acting on a
convention you never read is not.

**Always read:** **Running tests** · **Gotchas that will bite you** · **Definition of done for this lane**

| Section | Read it when |
|---|---|
| Where things live | you are adding a test file |
| Mocking conventions | your test touches FMP, Redis, Prisma or auth |

---

## Where things live

| Path | Purpose |
|---|---|
| `tests/unit/` | Vitest unit tests — the default fast feedback loop |
| `tests/unit/calculations/`, `tests/unit/services/`, `tests/unit/stores/` | existing subdirectories, for prior art |
| `tests/e2e/` | API-style integration/E2E tests |
| `tests/load/` | k6 load testing scripts — not run by the default suite |
| `tests/__mocks__/` | shared mocks |
| `tests/manual/` | manual test notes, not part of the automated suite |
| `tests/setup.ts` | Vitest setup — **not** `tests/setup.js`, see Gotchas |

## Running tests

```bash
npm test                          # tests/unit — the default suite
npm run test:all                  # everything Vitest config matches
npm run test:unit                 # explicit unit run
npm run test:watch
npm run test:coverage

npm run server                    # start backend first — e2e needs it running
npm run test:e2e                  # tests/e2e
npm run test:e2e:auth
npm run test:e2e:ticker
npm run test:e2e:dcf
npm run test:e2e:watchlist

# one file / one test
npx vitest run tests/unit/path/to/file.test.ts
npx vitest run tests/unit/services/cacheService.test.ts -t "should set and get from memory cache"
```

Use narrow mode while working; run what the work order's `verification` field
names before reporting `PASS`.

## Gotchas that will bite you

**`vitest.config.js` points at `./tests/setup.js`; the file on disk is
`tests/setup.ts`.** If test bootstrap behaves unexpectedly on a fresh run,
verify this mismatch first rather than assuming your test is wrong.

**E2E tests are sequential and can conflict with shared DB state.** They
expect the backend already running (`npm run server` / `server:dev`) against
`http://localhost:7071` unless `TEST_API_URL` overrides it, and may need
`DATABASE_URL`, Redis, and `FMP_API_KEY` set locally. Keep e2e test data
isolated and clean it up; a test that leaves rows behind can fail a later,
unrelated e2e run in a way that looks like that run's own bug.

**CI does not enforce lint or type-check reliably.** `.github/workflows/ci.yml`
tries `npm run lint` (the actual script is `lint:check`) and is
`continue-on-error`; `.github/workflows/pr-checks.yml` runs tests and build but
not lint or type-check. Do not treat a green CI run as proof the type-checkers
passed — run `npm run type-check`, `type-check:server`, `type-check:tests`
yourself when the order touched TypeScript.

## Mocking conventions

Per `AGENTS.md` § "Testing Expectations":

- Mock external systems in unit tests: FMP HTTP, Redis, Prisma, and auth
  boundaries already have examples in `tests/unit/services/` — follow an
  existing one rather than inventing a new mocking shape.
- New backend behaviour gets at least one service-level unit test.
- A critical user flow or API contract gets an e2e test added or extended.

## Definition of done for this lane

- [ ] Tests exist for every behaviour the work order names, including the
      missing/partial-data path (guardrail 5)
- [ ] Existing mocking patterns reused for FMP/Redis/Prisma/auth rather than
      re-implemented
- [ ] E2E additions clean up their own test data
- [ ] The order's `verification` command was actually run and passed
- [ ] No production code was modified — defects found are reported, not
      patched
