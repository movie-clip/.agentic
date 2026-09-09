# Pack corrections — 2026-09-07-new-epic-perf-benchmark-trust

## From 03-delivery-brief.md (producer)

- **Files:** `projects/portfolio/capabilities/product.md` ("Where the plan lives"),
  `projects/portfolio/project.md` ("Sources of truth (check before assuming)").
- **False premise:** both name `docs/product/epic-roadmap.md` as "the authority",
  plus `docs/product/prd/**` and `docs/product/stories/**` as the story surface.
- **Reality:** all of `docs/product/` (roadmap, every PRD, every story file, the
  full tech-debt-register) was deleted in portfolio repo commit `ce9c97d`
  ("cleanup", HEAD, 2026-09-07). `CLAUDE.md` now states roadmaps are "not
  maintained as active documentation". `docs/agents/issue-tracker.md` points at
  GitHub Issues but `gh issue list` (all states) is empty and no epic/story
  convention is defined there.
- **Replacement wording:** BLOCKED on run Open decision 1 — the human must
  designate the new plan surface before these pack sections can be rewritten to
  point at it. Docs lane applies this at close-out once decision 1 is answered.

## From 04-stories.md (story-author)

- **File:** `projects/portfolio/capabilities/story.md` § Files.
- **False premise:** lists `docs/product/stories/_TEMPLATE.md` ("the shape to
  follow"), `docs/product/stories/README.md` ("read for numbering") and
  `docs/product/epic-roadmap.md` as present.
- **Reality:** all removed in portfolio repo commit `ce9c97d`; absent from the
  working tree.
- **Replacement wording:** "No story template or index exists in-tree (removed in
  ce9c97d). Follow the two most recent sibling stories for house format;
  numbering is `US-<epic>.<n>-<slug>.md` with tickets `T-<epic>.<story>.<n>`."
  Docs lane applies at close-out alongside the run-1 correction (both wait on
  Open decision 1, now resolved: fresh minimal skeleton).
