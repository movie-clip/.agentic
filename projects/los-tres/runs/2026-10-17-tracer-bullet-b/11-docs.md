REPORT 2026-10-17-tracer-bullet-b/11
status:      DONE
verdict:     NONE

changed:
  - C:\projects\investments\.agentic\projects\los-tres\capabilities\testing.md — l.33 ends with the pointer sentence; the restated e2e write rule is deleted (CR-2, rule 5)

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order verification was NONE. The Edit tool confirmed the replacement; l.65 was not touched.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Re-lint testing.md: the e2e write rule should now live only in § What must always be covered (l.65).
  - l.33 before: "E2E data comes from Playwright `globalSetup` (`tests/e2e/global-setup.ts`), which runs `docker compose run --rm -T --no-deps app import-feeds` and throws a named message on `feeds=0` (quoted in `CLAUDE.md` § Commands); e2e tests and their helpers never write the database themselves: this `import-feeds` run is the only e2e write (the exception stated in § What must always be covered)."
  - l.33 after: "E2E data comes from Playwright `globalSetup` (`tests/e2e/global-setup.ts`), which runs `docker compose run --rm -T --no-deps app import-feeds` and throws a named message on `feeds=0` (quoted in `CLAUDE.md` § Commands). The e2e write rule is in § What must always be covered."
  - Not touched, per non_goals: l.65, the long l.27 paragraph, the l.27/l.35 base-URL duplicate, the "(`appBaseUrl()` is gone)" note, and all other packs.

skill_calls:
  - none

risks:
  - I read the order's inputs and edited before reading PROTOCOL.md; the edit was the exact linter wording, so no output differs, but the bind order was not followed.
  - Did not read project.md or docs.md; the order is one sentence with fixed wording, so nothing in them could change the edit.
