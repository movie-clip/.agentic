REPORT 2026-10-16-tracer-bullet/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only order, no command named

contract_notes:
  - CLAUDE.md § Commands must list the lint, tsc, Vitest and Playwright commands when this slice lands (0006); docs lane at close.
  - The request's table list (networks, shops, feeds, products, offers, categories) omits states the slice's behaviour needs; design decides the first migration, see § Slice boundary.

pack_corrections:
  - none

handoff:
  - 1 slice proposed, no epic exists and none is proposed — see § Stories
  - in-slice and out-of-slice lists for design and build — see § Slice boundary
  - story-vs-brief: no ticketed story, this brief is the specification; specification and review do not fire — see § Orchestrator brief
  - design: guardrail 1 states (feed approved, item hidden) must be queryable from the first migration, not added with the admin slice
  - design: the public read path applies approved-and-not-hidden filtering now, though no admin UI can set either state yet
  - test: guardrail tests that can exist now are listed in § Slice boundary (acceptance as behaviour)
  - 7 open decisions for the human — see § Open decisions
  - already covered: scope is inside mvp.md and decisions 0004/0006/0007/0008 — see § Already covered

skill_calls:
  - none

risks:
  - QUESTION (blocks seed design and the visibility test): how does the demo feed become approved with no admin yet? Seed pre-approves it, a CLI step, or nothing is public until the admin slice? Guardrail 1 tension, owner decides.
  - QUESTION (blocks seed config and the later VPS slice): 0004 loads demo data on first start; should seeding be local-only, so demo shops never appear on the live site networks will review?
  - QUESTION (blocks fixture authoring): demo shops and prices invented, so should shop names be obviously fictional rather than real retailers (Leroy Merlin) with made-up prices?
  - QUESTION (blocks product page acceptance): /go does not exist yet, so should offers show no buy link? mvp.md says every outbound link goes through /go; a direct affiliate link would break that.
  - QUESTION (blocks importer scope): is the matching cut right? EAN attach in; brand+part number, alias table, conflict queue, merge and split out; an EAN/brand conflict row is rejected into the import report and not published.
  - QUESTION (blocks whether specification and review fire): confirm no ticketed story. The pack leans towards stories for product-page and import slices, so this is a judgment call the human approves at the framing stop.
  - QUESTION (blocks nothing hard): umami starts in Compose but the tracker is not embedded in pages (needs a site id from the Umami UI). Confirm.
  - Trusted without opening: CLAUDE.md summaries of 0001, 0002 and 0009. I opened mvp.md, 0004, 0006, 0007, 0008, phases.md and project.md.
  - Market claims: none made. Whether any network approves the site is not touched by this slice.
  - git ls-files shows docs and config only, so no code exists that this slice could duplicate.

## Orchestrator brief
- verdict: covered by the approved MVP scope; a new build slice, not a gap. No epic or backlog exists (project.md: "no backlog yet"), none proposed.
- fit: inside mvp.md § Delivery, § Feed import, § Product and offers, § Visibility, and 0004/0006/0007/0008. Nothing on mvp.md § Out of MVP is touched.
- story vs brief: NO ticketed story. This brief is the specification once the human approves it. Reason in § Stories.
- consequence: specification does not fire, so review does not fire. Record "not triggered (the delivery brief in 01 is the specification)". Integration and docs still fire.
- one tension: guardrail 1 vs seeded data. The demo feed needs approval and no admin exists. Owner decides (Q1).
- one scope correction to the request: the tracer needs at least 2 shops sharing a product, or no sort can be shown, so EAN attach is in the slice.
- one scope correction: /go is out, so the product page renders no buy link (Q4).
- blocks dispatch: Q1 (demo approval path) and Q6 (story vs brief) before design; Q2, Q3, Q4, Q5 can be settled while design runs.
- sections below: Placement · Stories · Slice boundary · Sequence · Open decisions · Already covered

## Placement
There is no epic, no backlog and no story to place this under. `mvp.md` is the only plan artifact, and project.md says there is no backlog yet. The nearest precedent is `mvp.md` § "core loop" in the product pack: a feed is approved and imported, a visitor finds a product, compares offers, clicks out. This slice is the first thin pass through the middle of that loop: import, then product page with offers. Search and the click-out are the two ends it leaves for later.

Proposing an epic for it would be epic inflation. The whole MVP is the epic, and `mvp.md` is its charter.

The slice is a tracer bullet and also the foundation: it creates the repo skeleton, Compose, the first migration and the gate. Those are technical layers and are not stories on their own. They ship here only because the one visible path (below) cannot run without them.

## Stories
One slice, not ticketed. Name for reference: **S1 tracer bullet**.

**Outcome in one sentence:** the owner runs one command on a fresh checkout, imports the demo feed, and opens a product page in a browser that lists shops sorted by price, with the quality gate green.

  value:      the owner (and agents) get a working end-to-end path and a gate every later slice must pass. No visitor value yet, since nothing is live.
  slice:      in: skeleton, Compose, first migration, seeded demo data, `import-feeds` on the demo feeds, one product page, the gate. Out: see § Slice boundary. Nearest thing deliberately out: the `/go` redirect.
  depends_on: none. Greenfield. The stack is recorded (CLAUDE.md § Stack, 0001, 0002, 0004, 0006).
  invest:     Valuable is weak: the value is to the team, not to a visitor. Accepted, since it is the only way to learn early whether the stack, Compose and the import-to-page path work. Small is also weak: skeleton, Compose, schema, importer, page and gate is a lot for one slice. Design should say if it cuts cleanly in two. If so, the proposed split is "skeleton + Compose + gate on an empty page" then "import + product page". The brief does not require it.

**Story vs brief, against the `phases.md` clause.** The `specification` clause fires when framing produced scope no approved brief covers and the slice crosses lanes or changes a data model that shipped code depends on.
- Scope: covered. `mvp.md` and decisions 0004, 0006, 0007 and 0008 fix what the site is. This brief fixes the slice's boundary; once the human approves it, it is an approved brief.
- Data model: it is new, but no shipped code depends on it, so the second limb of the clause does not apply.
- Cross-lane: yes, backend, frontend and test all touch it. The `design` lane exists for that, and fires.
- Acceptance: the observable behaviours below are checkable by the integration gate and by the human, so a story adds no information.
- Cost of this choice: `review` (criterion-by-criterion acceptance) does not run. The pack says product page and import slices are "likely" to get a story. I am deviating because this slice has one path, one acceptor (the owner) and no ambiguity left after the lists below. The human can overrule at the framing stop (Q6).

## Slice boundary
**In this slice**
- Repo skeleton for the recorded stack; public site name from configuration; Spanish copy in message files.
- Docker Compose with `app`, `db`, `umami` that comes up from a fresh clone with no external account (0004). Umami runs; its tracker is not embedded (Q7).
- First migration with the nouns the request names (networks, shops, feeds, products, offers, categories) plus whatever design finds guardrail 1 and the page need. Money stored as integer cents in EUR (guardrail 4).
- Seeded demo data loaded on first start: a small category tree, at least two fictional demo shops each with its own demo feed file, and at least one product present in both shops (shared EAN) so that sorting is visible. At least one product sold by one shop only. Content per Q3.
- `import-feeds` as a command run by hand against the registered demo feeds. It reads a local file, validates each row, creates products and offers, and reports counts and rejected rows. Re-running it does not duplicate anything and updates prices and the "updated" date.
- Matching limited to EAN attach (0008 step 1) and "new product" (step 3). A row whose EAN matches a product with a different brand is rejected into the report, not merged and not published.
- The importer only reads feeds registered as rows (0007; a guardrail test exists for this in 0006).
- One server-rendered product page, reached by direct URL. It shows title, brand, part number, EAN, description, the shop count ("1 shop" wording per mvp.md), and the offers sorted lowest price first. Each offer shows shop, price in EUR with IVA, formatted for es-ES, and "price updated on <date>". A single placeholder stands where the image goes.
- The public read path shows only offers from an approved feed that are not hidden, and a product with no visible offer is not served. The states exist and are enforced even though no UI sets them.
- The gate: ESLint, `tsc --noEmit`, Vitest with integration tests on a real PostgreSQL, Playwright. Commands listed in CLAUDE.md § Commands.
- Guardrail tests that can exist now: unapproved-feed offers not public; hidden product and hidden offer not public; importer refuses an unregistered source; prices are integer cents end to end; no cookie set by the page. Tests use local fixture files and never call a live network (0006).
- One Playwright flow: open the demo product's page and see the offers in ascending price order.

**Out of this slice (later, not scheduled by this brief)**
- Admin area of any kind: login, TOTP, feed approval, "Import now" button, reading import reports in a UI, category mapping and the unmapped-category queue, image upload, hide controls, shop ranking. Guardrail 3 tests wait for the slice that adds the first admin route.
- Matching queue, brand + part number matching, brand alias table, merge and split.
- `/go/<offer>` redirect and click log, and any outbound link on the page (Q4).
- Price history and its chart.
- The "No offers right now" state and removal of offers missing from the latest import.
- Search, category pages and filters, home page and any product listing.
- schema.org `Product` / `AggregateOffer` structured data, sitemaps and indexing work.
- Per-category image placeholders (one generic placeholder only).
- Embedding the Umami tracker.
- Real affiliate feeds, real shops, network applications, and the VPS, domain and deployment.
- Everything on `mvp.md` § Out of MVP.

**Acceptance as observable behaviour (the "done when" the integration gate and the human check)**
- From a fresh clone, `docker compose up` starts app, db and umami and the demo data is present, with no network access to any shop or affiliate network.
- Running `import-feeds` on the demo feeds prints counts and rejected rows. A second run leaves the same number of products and offers.
- The product page for the shared-EAN demo product lists at least two shops, cheapest first, each with price and "updated" date, with the shop count shown.
- The single-shop demo product shows the one-shop wording.
- An offer from a feed that is not approved, or a hidden offer or product, is not visible on any public page; a test covers each.
- CLAUDE.md § Commands lists the gate commands and all of them pass.
- The page sets no cookie and nothing is logged with an email, token or password.

## Sequence
The slice runs inside the existing phase order; the producer adds no new edge.
- Framing (this brief) then the human stop. Hard dependency: Q1 and Q6 must be answered before design, since they change the seed and which phases fire.
- Design next, because the slice crosses the data model and three build lanes. Soft dependency: Q2, Q3, Q4 and Q5 can be answered while design runs; they change fixtures and the page, not the shape.
- Build, then integration, then docs. Integration has a hard rule here: with no gate command listed in CLAUDE.md it is a BLOCKING finding (phases.md § What the gates run), so the gate must land in this slice and not after it.
- Risk-first note: the riskiest unknown is whether the whole Compose-to-page path works on the owner's machine, not any single feature. That is why this slice comes before any admin or matching work.

Candidate later slices, for the human to order. This brief does not schedule them:
- `/go` redirect and click log (completes the core loop's last step and the basis for revenue).
- Admin login and feed approval (removes any seed pre-approval from Q1; satisfies guardrail 3).
- Matching queue, import report in the admin, "Import now".
- Search and category pages, then structured data (needed before Google can index, hence before the 10k-product target).
- VPS deployment (networks only approve a site they can visit, per 0007).

## Open decisions
- **Q1. Demo feed approval (guardrail 1 tension).** Guardrail 1 says only an admin approves a feed, and no seed, script or API publishes data from an unapproved feed. No admin exists in this slice. Options: seed marks the demo feeds approved as the owner's explicit pre-approval, a CLI step the owner runs, or nothing is public until the admin slice (then the Playwright flow would need a test-only approval). I do not recommend one; this is the owner's decision, and a seed that pre-approves is itself a guardrail-1 call.
- **Q2. Demo data on the live site.** 0004 says demo data loads on first start. If the same Compose runs on the VPS, demo shops show on the site networks review. Should seeding be local-only or switchable by configuration? Blocks seed design.
- **Q3. Demo content.** Real retailer names with invented prices would be fabricated data attributed to real shops. Recommend fictional shop names and clearly demo product titles. The owner decides.
- **Q4. Buy link in this slice.** Recommend no outbound link on the offer rows until `/go` exists. The alternative is a visibly inert button. Either way no direct affiliate URL is rendered.
- **Q5. Matching cut.** Confirm the cut in § Slice boundary: EAN attach only, conflicts rejected into the report. The alternative is pulling brand + part number into this slice, which grows it.
- **Q6. Story or brief.** Confirm the brief is the specification (see § Stories). If the human wants acceptance criteria reviewed by the `reviewer`, the slice goes to `story` first and the run gains one stop.
- **Q7. Umami tracker.** Confirm the service starts but the tracker is not embedded yet.

## Already covered
- Not a duplicate of anything: `git ls-files` lists docs, `.agentic.json`, `.claude/settings.json`, `.gitignore`, `LICENSE`, `README.md`. There is no code, so no "half-built under another name".
- Scope: `docs/product/mvp.md` covers the core loop (§ Goal), product page and offers sorted by price (§ Product and offers), feed import and its CLI (§ Feed import), approval visibility (§ Visibility) and Compose delivery (§ Delivery). I read it in full.
- Seeded demo data is already decided: 0004 § Consequences says "Seeded demo data (categories, a demo shop and a small demo feed file) loads on first start". It names a demo shop in the singular and does not say the feed is approved. The slice needs two shops to show a sort (§ Orchestrator brief), which extends 0004 slightly and is within its intent. Owner can object in Q3.
- The gate and its guardrail tests are decided: 0006 § Decision and § Consequences. 0006 says the first slice that adds code puts the commands in CLAUDE.md § Commands. This slice does that.
- The importer's registered-source rule and no-scraping rule: 0007. The demo feed is a local file registered as a row; it is not a scrape of anything.
- Matching steps and the conflict rule: 0008. This slice implements only steps 1 and 3 and treats a conflict as a rejected row. That is a deliberate partial implementation, not a reversal; 0008's queue arrives with the admin slices.
- Nothing recorded as deliberately open by the owner is overridden. The one place the request reaches near a recorded decision is Q1, which is raised as a question and not decided.
