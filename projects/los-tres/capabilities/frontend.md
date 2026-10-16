# Capability pack: frontend — project `los-tres`

For the `frontend-engineer` lane. The public catalogue (search, category and
product pages) and the admin area.

**No frontend exists yet.** This pack carries the constraints and no code
conventions. The slice that creates the client writes the conventions it set
here through `pack_corrections`.

---

## Index

Read this block first. You are not expected to read this file end to end — read
what your order touches. Reading one extra section is cheap; acting on a
convention you never read is not.

**Always read:** **Before the stack is recorded** · **Guardrails, in code terms** · **Definition of done for this lane**

| Section | Read it when |
|---|---|
| Layout | you are adding a file — empty until the first build slice fills it |
| Spanish market conventions | your order adds user-facing copy, prices or dates |

---

## Before the stack is recorded

If `CLAUDE.md` § Stack reads *not chosen*, or the tech-lead plan in your
`inputs` does not name the framework and directory you are to use, report
`BLOCKED` and name the missing decision. Do not choose one.

## Layout

*Not yet established.* The first build slice records it here.

## Spanish market conventions

- User-facing copy is Spanish (`es-ES`). Put strings where the plan says
  translations live, not inline, so a second language is possible later.
- Prices are formatted for `es-ES`, with comma decimals and a trailing `€`,
  e.g. `1.234,50 €`. Format from integer cents with the platform's locale
  formatter, never with string arithmetic.
- The public site name comes from configuration, never a literal in markup.
- Offers are sorted by price from lowest to highest. No shipping cost is shown
  anywhere.

## Guardrails, in code terms

- **(1)** Public pages show only what the server's visibility scope returned.
  The client never filters by approval or hidden state to compensate.
- **(2)** Shop links always point at `/go/<offer>`, never straight at a shop or
  affiliate URL, and the client never fetches shop pages.
- **(3)** Admin screens rely on the server's role check. Hiding a button is a
  UX choice, not access control.
- **(4)** Show the final product price with IVA included. Never do money
  arithmetic in floats on the client.
- **(5)** Set no cookie for public visitors. Only cookieless Umami analytics,
  with no PII in client logs or analytics events.

## Definition of done for this lane

- [ ] Every guardrail above checked against your diff
- [ ] Types mirror the backend contract notes exactly
- [ ] Lint and test commands from `CLAUDE.md` § Commands run and passing, or
      their absence reported
- [ ] Any convention you established written as a `pack_corrections` entry for
      this file
