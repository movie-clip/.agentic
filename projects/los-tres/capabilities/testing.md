# Capability pack: testing — project `los-tres`

For the `test-engineer` lane.

**No test infrastructure exists yet.** The first build slice chooses the runner
together with the stack. Whoever sets it up records the runner, the commands
and the directory layout here through `pack_corrections`.

---

## Index

Read this block first. You are not expected to read this file end to end — read
what your order touches. Reading one extra section is cheap; acting on a
convention you never read is not.

**Always read:** **What must always be covered** · **Definition of done for this lane**

| Section | Read it when |
|---|---|
| Running tests | you are running or adding tests — empty until the first build slice fills it |

---

## Running tests

*Not yet established.* `CLAUDE.md` § Commands is the authority once it lists a
test command. If it lists none and your order needs one, report `BLOCKED`
rather than choosing a runner.

## What must always be covered

These are the guardrails' tests. A slice that touches a seam owes the
matching test, and it should be one that would fail if the rule broke:

- **(1)** No public read (search, category, product page, sitemap,
  `/go/<offer>`) returns an offer from an unapproved or disabled feed, a hidden
  product or offer, or a product waiting in the matching queue.
- **(2)** The importer refuses a source that is not a registered feed.
- **(3)** An anonymous request cannot reach any admin route or server action.
- **(4)** Feed prices parse to integer cents. Include a case where float
  parsing would round wrongly (for example `19.99`, `0.29`).
- **(5)** A `/go/<offer>` click row holds no IP, user agent or cookie, and the
  response sets no cookie.
- **Matching (0008):** EAN match, brand + normalised part number match, and
  conflict → queue, each with a fixture.

Never call a live affiliate network in a test. Import from local fixture feed
files.

## Definition of done for this lane

- [ ] Every seam the slice touched has its guardrail test above
- [ ] Tests assert the contract, not the implementation
- [ ] Any runner, fixture or command convention you established written as a
      `pack_corrections` entry for this file
