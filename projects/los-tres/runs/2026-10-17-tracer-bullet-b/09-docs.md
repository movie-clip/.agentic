REPORT 2026-10-17-tracer-bullet-b/09
status:      DONE
verdict:     NONE

changed:
  - C:\projects\investments\.agentic\projects\los-tres\capabilities\testing.md — l.65 (§ What must always be covered) reworded: integration-scoped rule with the e2e exception in one bullet.
  - C:\projects\investments\.agentic\projects\los-tres\capabilities\testing.md — l.33 (§ Running tests) last clause reworded so it no longer calls the e2e target "the development database" and points at the l.65 exception.
  - BEFORE l.65: "Any helper that writes to the database calls `assertTestDatabase()` (`tests/support/db.ts`) first; a test never runs against the development database."
  - AFTER l.65: "Any integration test or helper that writes to the database calls `assertTestDatabase()` (`tests/support/db.ts`) first, so it only ever writes `${DB_NAME}_test`; e2e writes only through `import-feeds` in `globalSetup` (§ Running tests)."
  - BEFORE l.33 (final clause): "e2e tests never write the development database themselves."
  - AFTER l.33 (final clause): "e2e tests and their helpers never write the database themselves: this `import-feeds` run is the only e2e write (the exception stated in § What must always be covered)."

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Wording fix only. Re-run protocol-lint on testing.md rule 9 to confirm CR-1 is cleared.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Re-lint testing.md for rule 9 to close CR-1; the l.65 wording is the linter's fix wording extended with the `${DB_NAME}_test` target, same meaning.
  - The SHOULD_FIX items (l.27 length, duplicated base-URL rule, CRLF tip) were left untouched per non_goals.

skill_calls:
  - none

risks:
  - I also edited l.33, which the linter named as part of the conflict but the order's fix wording covered only l.65; revert it if the l.65 change alone is wanted.
