REPORT 2026-10-21-s5-2-home-category-tree/02
status:      DONE
verdict:     NONE

changed:
  - C:\projects\investments\.agentic\projects\los-tres\runs\2026-10-21-s5-2-home-category-tree\02-design.md — this technical plan (no repo file edited)

verification:
  command:   python C:\projects\investments\.agentic\scripts\check_report.py C:\projects\investments\.agentic\projects\los-tres\runs\2026-10-21-s5-2-home-category-tree\02-design.md --lane design
  result:    PASS
  detail:    check_report.py exits 0 on this artifact. Plan drawn against visibility.ts, catalogue/category-page.ts, schema/catalogue.ts, seed/demo-data.ts, SiteHeader.tsx, globals.css, (public)/page.tsx and the current tests.

contract_notes:
  - New src/server/catalogue/category-tree.ts exports getPublicCategoryTree() and two types; see § Contract.
  - CategoryEmpty.homeLabel becomes optional (link omitted when absent); category page call is unchanged. See § Decisions D-6.
  - SiteHeader moves its styles from globals.css (.site-header*) into src/components/SiteHeader.module.css. See § Decisions D-7.
  - messages/es-ES.json gains Home.categoriesHeading, Home.productCount, Home.emptyHeading, Home.emptyBody (01-ux § Copy).
  - tests/unit/seams.test.ts must add category-tree.ts to the "goes through the shared visibility scope" assertion.

pack_corrections:
  - capabilities/architecture.md § The seams the product forces — Public visibility lists reads in product-page.ts only. Replace with: "product read in src/server/catalogue/product-page.ts, category listing in category-page.ts, home tree in category-tree.ts; all call visibleProductWhere()".

handoff:
  - Backend (T5.2.1): build § Contract and § Lanes L1 exactly; no schema or migration change.
  - Frontend (T5.2.2): build § Lanes L2 against the § Contract types and the § Testids table; 01-ux § Screens/States/Copy is the visual spec.
  - Test (T5.2.3): build § Lanes L3; § Broken tests names the existing tests this change breaks.
  - Integration: the invariant check is § Contract I-1; confirm the integration test in L3 iterates every returned node.

skill_calls:
  - mattpocock-skills:codebase-design — not called, the shape follows the existing sibling category-page.ts; no new module seam was in question
  - engineering:system-design — not called, one read function on a recorded stack; no architecture choice open

risks:
  - The invariant holds by shared scope plus a test, not by one shared query; a later edit to inSubtree that tree.ts does not mirror would break it silently without the I-1 test. See § Risks.
  - A category slug that fails isWellFormedSlug would 404 on its page; the tree drops such nodes (D-4) so home never links to it.
  - Ordering by name uses the database collation; demo order is decided by position, so tests must not assert name tie-break order across locales.
  - 01-ux run.md carried item names SiteHeader.module.css, which does not exist; header styles live in globals.css today (D-7 resolves).
  - Each home request runs two queries with a recursive CTE over all categories; fine at ~30 categories, S10.1 owns caching.

## Orchestrator brief

Decisions: one new read `getPublicCategoryTree()` in `src/server/catalogue/category-tree.ts`; returns exactly two levels, already filtered (count >= 1) and ordered (position, name, id).
Counts use `visibleProductWhere()` and the same recursive subtree rule as `getPublicCategoryPage`; invariant I-1 (on home ⇒ its page has productCount >= 1 and equal count) is enforced by an integration test over every node.
No schema/migration change. No caching. Empty array = no-products state.
CategoryEmpty gets optional homeLabel (home variant); header styles move to SiteHeader.module.css.
Lanes, in order: L1 backend (T5.2.1) → L2 frontend (T5.2.2) → L3 test (T5.2.3); L2 may start once L1's types file exists.
Blocks dispatch: nothing.
Sections: § Contract (types, signature, query, I-1) · § Data needs answers · § Decisions (D-1..D-8) · § Lanes (files and verification per lane) · § Testids · § Broken tests · § Risks.

---

## Contract

### Read function (backend, T5.2.1)

New file `src/server/catalogue/category-tree.ts`, `import 'server-only'`, sibling of `category-page.ts`.

```ts
export type CategoryTreeChild = {
  /** categories.slug; link target /categoria/<slug>. Always well-formed (isWellFormedSlug). */
  slug: string;
  /** categories.name. Never empty. */
  name: string;
  /** Public products in this category and every descendant at any depth. Integer >= 1. */
  productCount: number;
};

export type CategoryTreeGroup = CategoryTreeChild & {
  /** Direct children with productCount >= 1, ordered. Empty array when none (heading row only). */
  children: CategoryTreeChild[];
};

/** Top-level categories (parent_id is null) with productCount >= 1, ordered. [] = no-products state. */
export async function getPublicCategoryTree(): Promise<CategoryTreeGroup[]>;
```

No field is nullable. No id, parentId or position leaves the function. No money field.

### How it computes

Two queries, no transaction needed:

1. **Counts.** One SQL query: a recursive closure over `categories` producing `(ancestor_id, descendant_id)` pairs, every category paired with itself and with every descendant at any depth, built with `UNION` (not `UNION ALL`) so a parent cycle terminates — the same rule as `inSubtree` in category-page.ts. Join `products` on `products.category_id = closure.descendant_id`, `where(visibleProductWhere())`, `group by ancestor_id`, select `count(distinct products.id)::int`. Built with drizzle `sql` for the CTE and `visibleProductWhere()` for the condition — **the condition is never restated** (guardrail 1; seams test).
2. **Categories.** `select id, parent_id, slug, name from categories order by position asc, name asc, id asc`.

Assembly in TypeScript: roots = `parentId === null`; children = rows whose `parentId` is a root id; attach `productCount` from query 1 (absent → 0); drop every node with count 0 or `!isWellFormedSlug(slug)`; drop a root's children list entries likewise. Order is the order of query 2, preserved at both levels.

Third-level and deeper categories are never returned but are counted in their ancestors through the closure.

### I-1 — the invariant

For every group `g` and every child `c` returned by `getPublicCategoryTree()`, `getPublicCategoryPage(node.slug, 1)` is non-null and its `productCount` equals `node.productCount` (and so is >= 1). A category appears on home if and only if its category page shows productCount >= 1 (01-ux § Which categories appear), restricted to depth 2.

It holds because both reads count `products` under the same `visibleProductWhere()` with the same subtree definition (self plus all descendants, UNION). It is checked by an integration test that iterates every returned node (§ Lanes L3).

## Data needs answers

1. **Depth.** The function returns exactly two levels; the page does no truncation. Deeper categories count into their ancestors.
2. **Consistency.** The count and the "has products" test are the same number from one query, computed under the same `visibleProductWhere()` and the same subtree rule the category page uses. It is not literally the same function call (that would be one count query per category per request), so I-1 is pinned by a test that compares each node to `getPublicCategoryPage`.

## Decisions

- D-1 Name and file: `getPublicCategoryTree` in `src/server/catalogue/category-tree.ts`; types `CategoryTreeGroup`, `CategoryTreeChild`.
- D-2 Filtering and ordering happen in the read function, not the page. The page renders what it is given.
- D-3 Order: `position asc, name asc, id asc` at both levels (01-ux § Which categories appear, plus id as the stable tie-break, like OD-B).
- D-4 A node whose slug fails `isWellFormedSlug` (src/server/slug.ts) is dropped, with its children, so home never links to a 404.
- D-5 `count(distinct products.id)::int` — cast to int because Postgres count is bigint and node-postgres returns it as a string.
- D-6 Home empty state reuses `CategoryEmpty`: `homeLabel?: string`; when undefined, the link paragraph is not rendered. Testid stays `category-empty`. Copy from `Home.emptyHeading` / `Home.emptyBody`.
- D-7 Header: `SiteHeader` gets an inner `<div>` column and its styles move to `src/components/SiteHeader.module.css` (CSS Modules, decision 0011); remove `.site-header` and `.site-header__name` from `globals.css`. Spec: 01-ux § Screens E.
- D-8 The home page (`src/app/(public)/page.tsx`) calls `getPublicCategoryTree()` once per request; `dynamic = 'force-dynamic'` stays; no `cache`, no `loading.tsx`. The populated home has exactly one `<p>` (the tagline): counts and names are `<span>`s inside links.

## Lanes

### L1 — backend (T5.2.1). Verification: `npm run lint`, `npm run typecheck`, `npm run db:up`, `npm test`.

May touch:
- `src/server/catalogue/category-tree.ts` (new)
- `tests/unit/seams.test.ts` — only to add category-tree.ts to the "goes through the shared visibility scope" assertion (expect `visibleProductWhere()`), so the gate keeps the seam honest.

Must not touch `visibility.ts`, `category-page.ts` (unless extracting the subtree CTE into a shared helper both use — allowed, and preferred if it stays a pure refactor; say so in risks), schema or migrations.

### L2 — frontend (T5.2.2). Verification: `npm run lint`, `npm run typecheck`, `npm run test:unit`.

May touch, in order:
1. `messages/es-ES.json` — the 4 `Home` keys from 01-ux § Copy.
2. `src/components/CategoryEmpty.tsx` — optional `homeLabel` (D-6).
3. `src/components/CategoryTree.tsx` + `CategoryTree.module.css` (new) — props: `groups: { key: string; href: string; name: string; count: string; children: { key; href; name; count }[] }[]` (finished strings; the page formats counts with `Home.productCount`). 18rem grid constant lives here.
4. `src/app/(public)/page.tsx` + `src/app/(public)/page.module.css` (new) — brand panel, h2, tree or empty state.
5. `src/components/SiteHeader.tsx` + `SiteHeader.module.css` (new); `src/app/globals.css` — remove the two header rules only (D-7).

### L3 — test (T5.2.3). Verification: `npm run gate`.

May touch:
- `tests/integration/category-tree.test.ts` (new): shape (numbers not strings, no extra fields); hidden/unapproved/in-queue/unmapped products not counted; empty child absent, root with only own products has `children: []`; root with no products absent; grandchild counted in root and child; ordering by position then name; cycle terminates; no categories/no products → `[]`; **I-1: for every node, `getPublicCategoryPage(slug,1).productCount === node.productCount`**; admin hide removes a category on the next call.
- `tests/unit/home-components.test.ts` (new): CategoryTree render (testids, heading-only group has no list), CategoryEmpty without homeLabel has no link.
- `tests/unit/messages.test.ts`: add the 4 new keys.
- `tests/e2e/home.spec.ts`: rewrite per § Broken tests; populated demo: Automóvil before Herramientas, Filtros before Escobillas y bombillas, `aceites-y-lubricantes` absent from home and 200 at `/categoria/aceites-y-lubricantes`; for every link on home, its page's `category-summary` count equals the home count; header link >= 44 px tall.
- `tests/support/catalogue.ts` only if a helper (e.g. insertCategory with parentId/position) is missing.

## Testids

| testid | element |
|---|---|
| `home-panel` | the brand panel container (holds h1 and tagline) |
| `category-tree` | the outer `<ul>` of groups (absent in the empty state) |
| `category-group` | each group `<li>` |
| `category-group-link` | the `<a>` inside the group's `<h3>` |
| `category-group-count` | the count `<span>` inside that link |
| `category-row` | each child `<li>` |
| `category-row-link` | the child `<a>` |
| `category-row-count` | the count `<span>` inside that link |
| `category-empty` | reused: home no-products state (CategoryEmpty) |
| `site-header-link` | the header site-name `<a>` |

## Broken tests

- `tests/e2e/home.spec.ts` — the h1 moves into the panel and a h2, h3s and links appear; the `p` count stays 1 only per D-8. Test lane rewrites it.
- `tests/unit/messages.test.ts` — not broken, but must list the 4 new keys.
- `tests/unit/seams.test.ts` — not broken; extended by L1.
- `tests/unit/category-components.test.ts` — CategoryEmpty with homeLabel still renders the link; should stay green.
- `tests/e2e/category.spec.ts`, `product.spec.ts` — header markup changes only; no selector there uses the header class, so expected green.

## Risks

The invariant rests on two reads agreeing on "subtree" and "public". The public half is shared code (`visibleProductWhere()`); the subtree half is two CTEs unless L1 extracts one helper. The I-1 integration test is the guard; integration review must confirm it iterates every returned node rather than one sample.
