# Pack corrections — run 2026-08-27-next-epic-or-story

## From 03-delivery-brief.md (producer)

**File:** projects/portfolio/project.md § "`build-story` is superseded and must not run"

**False premise:** the paragraph claims build-story's description "still triggers on *build US-X.Y*" and that "two architectures compete for the same request and which one answers is a coin flip." That is no longer true — `.claude/skills/build-story/SKILL.md` frontmatter now opens "SUPERSEDED - do not use for implementation" and explicitly routes "build US-X.Y" / "pick up ticket T-..." / "implement the next story" to orchestrate-feature.

**Replacement wording (for the two stale sentences):**

> The repo skill's own description (`.claude/skills/build-story/SKILL.md` frontmatter) now opens "SUPERSEDED - do not use for implementation" and explicitly routes "build US-X.Y" / "pick up ticket T-..." / "implement the next story" to `orchestrate-feature`, so the trigger collision is closed at the skill itself. Residual prose telling agents to run `build-story` survives only in `docs/product/stories/README.md` and `docs/product/prd/README.md` — a docs-lane reconciliation.

Applied by docs-engineer at close-out per project.md lane-routing (docs lane may touch capabilities/** / the pack when applying pack-corrections.md).

## From 07-technical-plan.md (tech-lead DESIGN, US-41.2)

**File:** projects/portfolio/capabilities/architecture.md — "The seams" section

**False premise:** its `/engines/{...}` route-prefix brace list omits `currency-risk`.

**Fact:** `POST /engines/currency-risk/run` is registered (app/api/routes/currency_risk.py:6,9).

**Fix:** add `currency-risk` to that brace list.

Applied by docs-engineer at close-out.
