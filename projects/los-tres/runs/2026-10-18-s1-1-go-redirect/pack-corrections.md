# Pack corrections — 2026-10-18-s1-1-go-redirect

Requested by the human in the run request (close-out). The stack is recorded (CLAUDE.md § Stack), so conditions keyed on § Stack reading *not chosen* are stale.

- projects/los-tres/phases.md:13-14 — § Contents bullet "The stack run" describes a state that no longer exists. Replacement: delete the bullet.
- projects/los-tres/phases.md:32 — design row's first trigger clause "`CLAUDE.md` § Stack reads *not chosen* and the request needs code, or" is stale. Replacement: delete that clause, leaving the trigger to start "the change crosses the frontend/backend contract".
- projects/los-tres/phases.md:41-52 — § The stack run section keys entirely on § Stack reading *not chosen*. Replacement: delete the section; keep the pure-scope sentence (":51-52") only if it still fits elsewhere, otherwise delete it too.
- projects/los-tres/capabilities/architecture.md:22 — routing row "Proposing a stack | your mode is DESIGN and `CLAUDE.md` § Stack reads *not chosen*" is stale. Replacement: delete the row (project.md § Building before the stack exists already covers proposing an option a recorded decision does not cover).
- projects/los-tres/project.md:12-13 — "the rules for building before a stack decision exists" is dated. Replacement: reword to match project.md § Building before the stack exists as it now reads (building on the recorded stack, and what to do when no decision covers a choice).

From 01-design.md § pack_corrections (exact wording in 01-design.md § Docs and pack corrections owed):

- projects/los-tres/capabilities/backend.md — Layout lacks `src/server/clicks/`; guardrail 5 bullet lacks the click-row rule. See 01-design.md § Docs and pack corrections owed.
- projects/los-tres/capabilities/frontend.md — guardrail 2 bullet says offer rows render no link until /go ships; now false. See 01-design.md § Docs and pack corrections owed.
- projects/los-tres/capabilities/testing.md — guardrail 5 bullet and scaffolding list lack the /go helpers and the console-spy rule. See 01-design.md § Docs and pack corrections owed.
- projects/los-tres/capabilities/architecture.md — Click log seam names no file. See 01-design.md § Docs and pack corrections owed.

From 02-backend.md § pack_corrections (exact wording there; supersedes the backend.md line from 01-design where they overlap):

- projects/los-tres/capabilities/backend.md § Layout — add `src/server/clicks/` files, `error-code.ts`, and the /go route rule. See 02-backend.md § pack_corrections bullet 1.
- projects/los-tres/capabilities/backend.md § Guardrails (5) — click-row rule replacement. See 02-backend.md § pack_corrections bullet 2.
- projects/los-tres/capabilities/backend.md § Guardrails — demo-feed rule: no counted click in dev or e2e databases. See 02-backend.md § pack_corrections bullet 3.

From 03-frontend.md § pack_corrections (exact wording there; same change as the frontend.md line from 01-design):

- projects/los-tres/capabilities/frontend.md § Guardrails, in code terms (2) — replace the "until the /go slice ships" sentence. See 03-frontend.md § pack_corrections.

From 04-test.md § pack_corrections (exact wording there; covers the testing.md line from 01-design):

- projects/los-tres/capabilities/testing.md § What must always be covered (5) — counting-rules and privacy-test note. See 04-test.md § pack_corrections bullet 1.
- projects/los-tres/capabilities/testing.md § Shared scaffolding and gotchas — tests/support/go.ts helpers. See 04-test.md § pack_corrections bullet 2.
- projects/los-tres/capabilities/testing.md § Shared scaffolding and gotchas — forcing failures with vi.mock; the `\b` gotcha. See 04-test.md § pack_corrections bullet 3.
- projects/los-tres/capabilities/testing.md § Running tests — page.route does not intercept a redirect target. See 04-test.md § pack_corrections bullet 4.
