# Capability pack: product — project `datoro`

For the `producer` lane. How requests get shaped here, since there is no PRD or
epic tree to place them against.

---

## Index

Read this block first. You are not expected to read this file end to end — read
what your order touches. Reading one extra section is cheap; acting on a
convention you never read is not.

**Always read:** **Where the plan lives (it mostly doesn't)** · **Guardrails you must respect when briefing** · **Definition of done for this lane**

| Section | Read it when |
|---|---|
| Finding precedent | you need to check whether something is already shipped or already flagged |
| What is a story here, and what is not | you are deciding whether this needs a ticketed story |
| The AI insights boundary | the request touches AI-generated content |

---

## Where the plan lives (it mostly doesn't)

There is no `docs/product/` corpus, no `ROADMAP.md`, no epic tree. The nearest
things to a backlog:

| Doc | Role |
|---|---|
| `docs/PROJECT_REVIEW_PLAYBOOK.md` | recurring review checklist — read for what the team already watches for |
| `docs/reviews/` | archived review and audit records, dated — `ARCHITECTURE_REVIEW_*`, `PROJECT_AUDIT_*`, `PROJECT_REVIEW_*` |
| `docs/operations.md` | admin endpoints, analytics surface, operations notes |
| `docs/tech-debt-register.md`, if it exists at request time | deferred improvements — check before proposing one lives here; if the file is absent, say so rather than assuming there is nowhere to record debt |

A request that already appears in a dated review under `docs/reviews/` is not
new — cite the review and say what, if anything, has changed since.

## Finding precedent

```bash
ls docs/reviews/
grep -ril "<topic>" docs/reviews/ docs/PROJECT_REVIEW_PLAYBOOK.md
```

There is no generated index to substitute for reading the review files
directly — unlike `portfolio`'s `ROADMAP.md`, nothing here derives from
frontmatter. A grep across `docs/reviews/` is the actual search.

## What is a story here, and what is not

Per `phases.md` § "When the brief is the specification", a story is the
exception. Most requests are a delivery brief the human approves directly at
the `framing` stop, with no separate ticketed document.

A story is warranted when the slice crosses more than one lane's contract with
no existing brief covering the shape, or changes a route response / Prisma
model that shipped frontend code already depends on. Say explicitly in your
brief which of those applies, or that neither does — that is what lets
`phases.md`'s `specification` clause be evaluated rather than guessed.

Not a story, ever, here: a refactor with no user-visible change (note it
instead, and say where — this repo has no tech-debt register convention yet,
so name that gap rather than inventing a destination for the note); a bug with
an obvious, localized fix; a copy or styling change.

## Guardrails you must respect when briefing

The five guardrails are in the project profile. Two shape scope decisions
specifically:

- **Auth boundary.** A request to relax `requireAuth` on a route "just for
  testing" or "just for this one case" is declined, not deferred.
- **External data validated and degrades honestly.** A request to "just show
  something" where the current behaviour is to surface missing data as missing
  is a request to weaken a guardrail. It may still be legitimate, but the brief
  must name it as exactly that and let the human decide — not quietly ship a
  fabricated fallback.

## The AI insights boundary

`public/ai-insights.json` is a static bundle; the main app never calls an LLM
at runtime (`docs/development.md` § AI Insights). A request that sounds like
"make the app call an AI service live" is almost always actually a request to
regenerate the bundle in `ai-insights-tool/` and re-copy it — confirm which one
is meant before briefing either, since they are very different slices of work
and `ai-insights-tool/` sits outside this project's normal lint/build config.

## Definition of done for this lane

- [ ] `docs/reviews/` and `docs/PROJECT_REVIEW_PLAYBOOK.md` checked for existing
      coverage of the request
- [ ] Verdict stated plainly, including "already covered", "already flagged
      and open" or "decline" when true
- [ ] Story-vs-brief decision stated explicitly against the `phases.md` clause,
      not left implicit
- [ ] Any guardrail tension named as such, with the decision left to the human
- [ ] No implementation specified, no files written outside the report artifact
- [ ] **Every claim about the code cited from a `recon` artifact named in your
      `inputs`, or marked as unverified in `risks`.** Reading source files to
      establish current behaviour is the `recon` lane's dispatch; if the fact
      you need is not in an input, say which fact and let the orchestrator
      dispatch for it.
