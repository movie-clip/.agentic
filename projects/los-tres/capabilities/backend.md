# Capability pack: backend — project `los-tres`

For the `backend-engineer` lane. Server code, the data schema and migrations.

**No backend exists yet.** This pack carries the constraints and no code
conventions. The slice that creates the server writes the conventions it set
(layout, route shape, migration command) here through `pack_corrections`.

---

## Index

Read this block first. You are not expected to read this file end to end — read
what your order touches. Reading one extra section is cheap; acting on a
convention you never read is not.

**Always read:** **Before the stack is recorded** · **Guardrails, in code terms** · **Definition of done for this lane**

| Section | Read it when |
|---|---|
| Layout | you are adding a file — empty until the first build slice fills it |

---

## Before the stack is recorded

If `CLAUDE.md` § Stack reads *not chosen*, or the tech-lead plan in your
`inputs` does not name the framework and directory you are to use, report
`BLOCKED` and name the missing decision. Do not choose one.

## Layout

*Not yet established.* The first build slice records it here.

## Guardrails, in code terms

- **(1) Visibility.** Every public read goes through the one visibility scope
  the plan names: approved feed, not hidden, not in the matching queue. Only
  admin-scoped paths approve feeds or hide items. Seeds create feeds as not
  approved, except the demo feed the seed marks as demo.
- **(2) No scraping.** The importer fetches only the URL of a feed registered in
  the database, and parses it as CSV or XML feed data. Never add a crawler, a
  headless browser or an HTML parser for shop pages.
- **(3) Roles.** Every route declares whether it is public or admin. Admin
  routes and server actions check the session on the server.
- **(4) Money.** Integer cents, through the single money helper the plan names.
  Feed prices are parsed from their decimal text straight to cents, never
  through a float. No float column and no float arithmetic.
- **(5) Personal data.** The click row has no IP, user agent or cookie field.
  Log ids, not emails. Read secrets from the environment, and add each new
  variable to `.env.example` with no value.
- **Imports are isolated.** One failing feed records its error in its import
  report and never stops the other feeds.
- **Migrations.** Every schema change is a migration, never a hand edit to
  the database.

## Definition of done for this lane

- [ ] Every guardrail above checked against your diff, with any tension named
      in `risks`
- [ ] Lint and test commands from `CLAUDE.md` § Commands run and passing, or
      their absence reported
- [ ] Contract notes emitted for every field the frontend will consume
- [ ] Any convention you established (path, command, pattern) written as a
      `pack_corrections` entry for this file
