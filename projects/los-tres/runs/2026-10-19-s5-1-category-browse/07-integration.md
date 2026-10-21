REPORT 2026-10-19-s5-1-category-browse/07
status:      DONE
verdict:     PASS

changed:
  - C:\projects\investments\.agentic\projects\los-tres\runs\2026-10-19-s5-1-category-browse\07-integration.md — this integration review (the only artifact)

verification:
  command:   npm run gate
  result:    PASS
  detail:    gate exit 0: lint and typecheck clean; vitest 42 files, 705 tests passed; playwright 63 passed (8.2s). Consistency check against 03-design § Contract, no external anchor applies.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - No change requests; ux-review and review may run.
  - Docs close-out: src/cli/seed.ts does not print SeedReport.categoryMappings; small follow-up, not blocking (04-backend risks).

skill_calls:
  - none

risks:
  - SHOULD_FIX: src/cli/seed.ts omits categoryMappings from its printed counts; the report field exists and is tested, only the CLI output lags.
  - Pagination at 390 px has about 7 px slack on Segoe UI (05-frontend risks); a Linux CI font may overflow. Rendered check belongs to ux-review.
  - tests/unit/feed-source.test.ts was outside 03-design § Affected tests; the test lane fixed it and the gate is green, so the plan list was incomplete, not the work.

## Orchestrator brief

Verdict PASS; no CR files written; gate green (705 vitest, 63 playwright).
Contract C-3/C-4 matches field by field: page.tsx reads only slug, name, page, pageCount, productCount, products and the card fields as defined.
Guardrail 1: the mapped condition lives only in visibleProductWhere (src/server/visibility.ts); category-page.ts, product-page.ts and /go all call it; no second filter.
Guardrail 4: lowestPriceCents is min(price_cents)::int; the page formats with formatEuroCents; no float or arithmetic on money in components.
Importer stays the only writer; assignCategory only sets from null; seed inserts mappings only.
One SHOULD_FIX (seed CLI does not print categoryMappings) is in risks for the Open table.
Sections: § Findings — the per-stage review.

## Findings

1. Contract: CategoryProductCard and PublicCategoryPage in src/server/catalogue/category-page.ts match 03-design C-3 exactly; parsePageParam matches C-4; testids match C-5. Counts cast ::int, so no bigint string drift.
2. Design: D-1 (unique feed_id, feed_category), D-3 (isNull guard in assignCategory), D-4, D-6 (order by min price, id), D-7 (pageCount max 1; page > pageCount → null), D-8 all followed. Deviations are declared in lane risks.
3. Reuse: isWellFormedSlug extracted to src/server/slug.ts and used by product-page.ts — one copy. Same join shape as product-page.ts.
4. Guardrails: 1 and 4 as in the brief; no fetch added (2); route is public, no admin surface (3); no logging added (5).
5. Verification: full gate run by me, exit 0.
6. Coverage: test lane covers unmapped-not-public on the shared scope, product page, /go and the listing, plus seams.test.ts pinning isNotNull to visibility.ts — contract-level, not implementation-level.
7. Skill-call fidelity: the backend, frontend and test packs name no skill conditions; every report's skill_calls: none is consistent.
