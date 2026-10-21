REPORT 2026-10-21-s5-2-home-category-tree/03
status:      DONE
verdict:     NONE

changed:
  - C:\projects\investments\los-tres\src\server\catalogue\category-tree.ts — new: getPublicCategoryTree(), CategoryTreeGroup, CategoryTreeChild per 02-design § Contract
  - C:\projects\investments\los-tres\tests\unit\seams.test.ts — one new assertion: category-tree.ts contains visibleProductWhere()

verification:
  command:   cd C:\projects\investments\los-tres && npm run lint && npm run typecheck && npm run db:up && npm test
  result:    PASS
  detail:    lint clean, both tsc projects clean, db healthy, npm test 42 files / 706 tests passed. A throwaway integration smoke (since removed) also passed: tree shape, grandchild counted in ancestors, empty child absent, I-1 per node.

contract_notes:
  - Frontend imports getPublicCategoryTree, CategoryTreeGroup and CategoryTreeChild from src/server/catalogue/category-tree.ts; productCount is a number, no nullable field.
  - Test lane writes tests/integration/category-tree.test.ts including I-1 over every node against getPublicCategoryPage(slug, 1).productCount.
  - Pack capabilities/architecture.md seam list and capabilities/backend.md Layout (catalogue/ files) lag: category-tree.ts is a third catalogue read.
  - No schema, migration, seed or demo-data change, so no schema type or contract doc lags.

pack_corrections:
  - capabilities/backend.md § Layout — catalogue/ lists product-page.ts, category-page.ts, page-param.ts. Replace with: "catalogue/ (product-page.ts, category-page.ts, category-tree.ts, page-param.ts)".

handoff:
  - category-tree.ts runs two queries: a raw sql recursive closure via db.execute (UNION, so a parent cycle terminates) with visibleProductWhere() in its where, then a select ordered position, name, id.
  - Nodes with count 0 or a slug failing isWellFormedSlug are dropped; a root with only its own products returns children: [].
  - Test for ordering must set categories.position directly; tests/support insertCategory has no position option, so the test lane may extend it (L3 allows).
  - Test for I-1 must iterate every returned group and child, not a sample.
  - Ties in name use database collation; assert position order, not cross-locale name order.

skill_calls:
  - mattpocock-skills:tdd — not called, tests are the test lane's by order; verified with a throwaway smoke test instead
  - mattpocock-skills:codebase-design — not called, the file mirrors its sibling category-page.ts and no seam was in question

risks:
  - The subtree rule is a second CTE, not a shared helper: category-page.ts was left untouched. A later edit to inSubtree without mirroring it here breaks I-1 silently, so only the I-1 integration test guards it.
  - The closure is built over all categories on every call and counted by raw sql, not the drizzle builder; fine at about 30 categories, caching is S10.1.
  - Raw sql references products and categories columns by qualified name; renaming either table in the schema would not be caught by tsc inside the sql template, only by the integration test.
