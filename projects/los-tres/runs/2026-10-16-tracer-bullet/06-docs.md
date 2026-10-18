REPORT 2026-10-16-tracer-bullet/06
status:      DONE
verdict:     NONE

changed:
  - C:\projects\investments\los-tres\CLAUDE.md — § Commands only: "None yet" and the "first slice adds" sentence replaced by the gate, prerequisites, command table and helper list

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order verification was NONE (no shell); every command name was checked by reading package.json scripts

contract_notes:
  - 01-product contract_note 1 (CLAUDE.md § Commands must list lint, tsc, Vitest, Playwright) is absorbed: all four are in the table.
  - 03-backend contract_note 11 absorbed: dev, build, lint, typecheck, env:init, db:up, stack:up, stack:down listed; env:init exit 1 on existing .env stated.
  - 05-test contract_notes 3 and 4 absorbed: test, test:unit, test:integration, test:e2e, test:e2e:install, gate listed; chromium install named as a prerequisite.
  - 03-backend contract_notes 1 to 10 and 05-test contract_notes 1 and 2 are dismissed here: they bind code and test lanes, not § Commands.

pack_corrections:
  - none

handoff:
  - integration runs `npm run gate`; the stack stays up afterwards, so `npm run stack:down` ends the session.
  - the section says Node 22 via `.nvmrc`, as 03-backend lists .nvmrc among its changed files; not re-read by this lane.
  - the close-out order applies the pack_corrections from 02-design, 03-backend and 05-test (testing.md, backend.md, frontend.md).

skill_calls:
  - none

risks:
  - 03-backend risk 1 and 05-test risk 5 (host port 3000 held locally) are reflected only as a generic note that APP_PORT, DB_HOST_PORT, UMAMI_PORT in .env change host ports, per the non_goals.
  - Design said "a free port 3000, 3001, 5433"; the section words it generically with variable names so it does not go stale if defaults change.
  - 03-backend risk 6: `npm run env:init` exits 1 on a second run, so chaining it with && in a repeat setup stops; the section states the exit behaviour.
