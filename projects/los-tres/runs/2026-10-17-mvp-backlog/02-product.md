REPORT 2026-10-17-mvp-backlog/02
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only planning order, no command named

contract_notes:
  - Several stories change shipped contracts (visibility scope, PublicProductPage, importer reject path); each such story is marked "Story file: yes" in § Backlog and its design must name the matching test and doc updates.
  - docs/product/mvp.md disagrees with itself on unmapped products (publishes automatically vs waits in a queue) and with src/server/visibility.ts on products that lose all offers; see § Open decisions OD3 and OD4.

pack_corrections:
  - none

handoff:
  - 10 epics, 38 stories and 131 tickets proposed, plus epic E0 shown as done - see § Backlog
  - Create every issue in Backlog on Project 3; none Ready until the human approves (CLAUDE.md § Git and tickets) - see § Backlog
  - Build order is 38 numbered slices; first to run is slice 1, S1.1 the /go redirect and click log, after the human merges PR #7 - see § Sequence
  - Critical path to a live VPS with real feeds, with the external wait for network approval marked - see § Sequence
  - Non-code work on the critical path (VPS, domain, network applications, legal text, category list) is not ticketed - see § Owner tasks
  - 9 owner decisions, none blocks issue creation; OD1 and OD2 block the first admin and deploy slices - see § Open decisions
  - Every ABSENT or PARTIAL capability row maps to one story, and the out-of-MVP and dismissed items are listed - see § Capability coverage and § Not in backlog
  - Issue dedupe: recon did not read Project 3, so the orchestrator must search existing issues before creating any - see § Backlog

skill_calls:
  - none

risks:
  - I did not read GitHub issues or Project 3, and neither did the recon; issues for these items may already exist, so search before creating.
  - PR #7 (slice B, issue #6) is not merged: git shows main at b45ea15 (the PR #5 merge) and five #6 commits only on the current branch. Every later slice assumes it is merged first.
  - Verified myself: visibility.ts:30-38 and product-page.ts:60-72 return null for a product with no visible offer, which contradicts mvp.md "page stays when a product loses all offers" (S8.4, OD4).
  - Taken on trust from 01-recon: all other ABSENT/PARTIAL evidence in the capability map; I opened none of those files.
  - Market claims are unverified: that networks approve a site with demo content, how long approval takes, and that a live site is required first (0007 says so; I did not check any network's terms).
  - Legal claim unverified: that LSSI/RGPD require aviso legal, privacy and affiliate disclosure pages on this site. Not in mvp.md; raised as OD5, not as settled scope.
  - Sizes are relative judgments with no velocity data; XL means "split again at its run if design finds more".
  - project.md lane table has no ops lane; the 6 ops tickets are human or owner-run, or fall to backend (Compose) and docs (runbooks). The orchestrator should confirm.
  - The mvp.md done-definition (10k products indexed by Google, first commission) depends on networks and Google, not on code; the backlog delivers the means only.

## Orchestrator brief
- verdict: new backlog; no existing epic. Slices A and B (#4, #6) are shown as done; #6 awaits the human merge of PR #7.
- totals: 10 epics (E1-E10) + done epic E0, 38 stories (S1.1-S10.3), 131 tickets. Sizes XS-XL; priorities P0/P1/P2 on epics and stories.
- Backlog: one heading per epic, one sub-heading per story, a ticket list under each, laid out for mechanical issue creation. Tickets are expected work units, not a design.
- Sequence: 38 slices; slice 1 = S1.1 (/go + clicks); slices 1-9 give a reviewable live site; admin and import machinery follow while networks review; slice 23 = S9.4 first real feed.
- Owner tasks: non-code critical-path work (VPS, domain, network applications, legal text, category tree, sample feeds) is listed apart and not sized.
- Open decisions: OD1-OD9, each with a recommendation. None blocks issue creation. OD1 blocks S2.1; OD2, OD5, OD6 block S9.1; OD3 blocks S5.1; OD4 blocks S8.4.
- Story files at run time: S2.1 S3.2 S3.5 S5.1 S5.4 S7.2 S7.4 S8.1 S8.3 S8.4 S9.1 only; every other story runs on the delivery brief.
- Carried ledger rows: F-1 into S3.4, F-3 / copy review / Stack line into S10.2, URL encryption into S10.3; 3 dismissed with reasons (§ Not in backlog).
- sections below: Backlog · Sequence · Owner tasks · Open decisions · Capability coverage · Not in backlog

## Backlog

Tickets are the expected work units for each story, not a design. The story's own run (design, then build lanes) may merge, split or rename them. Issue titles below are in English and carry no personal data or UI copy. Create all issues in status Backlog.

Ticket line format: `T<story>.<n> | lane | size | title - intent`. Lanes: backend, frontend, test, docs, ops.

### E0 Tracer bullet (DONE, not re-planned)

Priority: P0. Covers mvp.md § Goal (the core loop's middle), § Delivery (Compose, gate), § Product and offers, § Feed import (basic), § Visibility. Outcome: skeleton, Compose, gate, six-table schema, demo seed, `import-feeds` (CSV, EAN matching) and one product page.

- #4 Slice A, skeleton, Compose, gate: DONE (PR #5 merged).
- #6 Slice B, schema, demo seed, importer, product page: DONE on branch 6-tracer-bullet-slice-b, PR #7 open. All later slices branch from main after the human merges PR #7.

### E1 Outgoing clicks and analytics

Priority: P0. Covers mvp.md § Outgoing clicks, § Analytics, § Revenue. Outcome: every outbound link goes through our redirect, is counted without personal data, and traffic is measured by cookieless Umami, so the first click and later commission can be seen.

#### S1.1 Visitor goes to a shop through a logged redirect
- As a visitor, I click "go to shop" on an offer and arrive at the shop's page, while the site logs the click without any personal data.
- Size: M · Priority: P0 · Depends on: none · Story file: no (decision 0009 and mvp.md fix the shape; the design lane still fires for the new table and the offer link field)
- Acceptance outline:
  - Each offer row links to `/go/<offer>`; the shop URL is never rendered directly.
  - A visible offer answers 302 to its stored URL; hidden, unapproved, in-review or unknown offers answer 404 (guardrail 1).
  - One click row holds offer, shop, product, time and source page only; no IP, user agent or cookie is stored, set or logged (guardrail 5).
  - Outbound links are marked as sponsored for search engines.
  - The guardrail-5 test deferred from slice B lands here.
- Tickets:
  - T1.1.1 | backend | S | Clicks table and write path - migration plus a write that stores only the permitted fields
  - T1.1.2 | backend | S | Redirect route - visibility-scoped lookup, 302, 404 otherwise, no URL in logs
  - T1.1.3 | frontend | S | Offer link through the redirect - go-to-shop control on offer rows with es-ES copy
  - T1.1.4 | test | S | Guardrail 1 and 5 tests for the redirect plus an e2e click-through

#### S1.2 Umami tracker on public pages
- As the owner, I see visits in Umami without the site setting any cookie.
- Size: S · Priority: P1 · Depends on: none · Story file: no
- Acceptance outline:
  - The tracker script is included only when its website id and script URL are configured.
  - Public pages still set no cookie with the tracker on (test).
  - The new settings are documented in `.env.example`.
  - A runbook step creates the Umami website and changes the default admin login (carried risk).
- Tickets:
  - T1.2.1 | backend | XS | Umami settings - website id and script URL in config, Compose and `.env.example`
  - T1.2.2 | frontend | XS | Conditional tracker script in the root layout
  - T1.2.3 | test | XS | No cookie and no script when unset; no cookie when set
  - T1.2.4 | docs | XS | Umami runbook - create the website, change the default login

#### S1.3 Admin sees click counts per shop and product
- As an admin, I see clicks per shop and per product over a date range, so I can confirm the first clicks and reconcile with network reports.
- Size: S · Priority: P2 · Depends on: Visitor goes to a shop through a logged redirect; Admin signs in with email and password · Story file: no
- Acceptance outline:
  - Admin-only page with counts by shop and by product for a chosen range.
  - Reads only the click table; there is no personal data to show.
  - Empty state when there are no clicks.
- Tickets:
  - T1.3.1 | backend | XS | Click aggregate queries by shop, product and range
  - T1.3.2 | frontend | S | Admin clicks page
  - T1.3.3 | test | XS | Role check and counts

### E2 Admin access and moderation

Priority: P0. Covers mvp.md § Admin area (accounts, login, approve or disable, hide), § Visibility. Outcome: the three team members sign in with password and authenticator code, and from the server-protected admin area control what the public sees.

#### S2.1 Admin signs in with email and password
- As an admin, I sign in with email and password and reach the admin area; no one else can reach any admin route or action.
- Size: L · Priority: P0 · Depends on: none (OD1 decides the approach) · Story file: yes (security-critical, new tables, new command, three lanes)
- Acceptance outline:
  - Accounts exist only if created by a command; there is no sign-up route.
  - Session is an HttpOnly cookie set for admins only; public pages still set none.
  - Every admin route and action checks the role on the server and refuses an anonymous request (guardrail 3).
  - Passwords are stored hashed; emails, passwords and tokens never reach logs (guardrail 5).
  - Admin pages are marked noindex; the guardrail-3 tests deferred from slice A land here.
- Tickets:
  - T2.1.1 | backend | S | Users and sessions tables - migration
  - T2.1.2 | backend | S | Password hashing and verification module
  - T2.1.3 | backend | S | Create-admin command verb - prompts for secrets, never echoes or logs them
  - T2.1.4 | backend | M | Sessions and the server-side admin guard used by every admin route and action
  - T2.1.5 | frontend | M | Login, logout and admin shell with navigation, es-ES copy
  - T2.1.6 | test | M | Guardrail 3 suite - every admin route and action refuses anonymous; no public cookie
  - T2.1.7 | docs | XS | Decision record for the auth approach; create-admin in CLAUDE.md § Commands

#### S2.2 Admin sign-in requires an authenticator code
- As an admin, I must also enter a code from my authenticator app, so a stolen password alone is not enough.
- Size: M · Priority: P0 · Depends on: Admin signs in with email and password · Story file: no (extends the S2.1 contract)
- Acceptance outline:
  - Login needs email, password and a valid TOTP code; the failure message does not say which factor failed.
  - Create-admin shows the enrolment secret once and never again.
  - Repeated failures lock the account for a while, without storing any IP address.
  - This story must be done before any admin route is deployed to the VPS.
- Tickets:
  - T2.2.1 | backend | S | TOTP secret storage, enrolment output and verification
  - T2.2.2 | backend | S | Failed-attempt limiting per account
  - T2.2.3 | frontend | S | Authenticator-code step on the login page
  - T2.2.4 | test | S | Wrong, reused and missing code cases; lockout; secrets absent from logs

#### S2.3 Admin approves and disables shops and feeds
- As an admin, I approve or disable a shop or a feed, and the public site follows at once.
- Size: S · Priority: P0 · Depends on: Admin sign-in requires an authenticator code · Story file: no
- Acceptance outline:
  - Admin page lists shops and feeds with their approval state.
  - Toggling is a server action behind the admin guard.
  - Disabling a feed or shop removes its offers from every public page immediately; an unapproved feed is skipped by import.
  - New feeds start unapproved.
- Tickets:
  - T2.3.1 | backend | S | Approve and disable actions for shops and feeds
  - T2.3.2 | frontend | S | Shops and feeds list with toggles
  - T2.3.3 | test | S | Guardrail 1 through the action: disabled feed vanishes, anonymous refused

#### S2.4 Admin hides and unhides products and offers
- As an admin, I find a product and hide it or one of its offers, and it stays off the public site, including after the next import.
- Size: M · Priority: P0 · Depends on: Admin sign-in requires an authenticator code · Story file: no
- Acceptance outline:
  - Admin product list with search by title, EAN, part number or slug.
  - Hide and unhide a product; the product's admin view lists all its offers with a hide toggle each.
  - A hidden item never appears on any public surface.
  - A re-import never un-hides.
- Tickets:
  - T2.4.1 | backend | M | Admin product list query and hide actions
  - T2.4.2 | frontend | M | Admin product list and product detail with offers
  - T2.4.3 | test | S | Hidden stays hidden across re-import; actions role-checked

### E3 Feeds, shops and imports

Priority: P0. Covers mvp.md § Shops and feeds are data, § Feed import, § Data sources. Outcome: the admin enters real networks, shops and feeds as data, imports them from a button or the command in real network formats, reads stored reports, and stale offers disappear.

#### S3.1 Admin manages networks, shops and feeds
- As an admin, I add a network, a shop and a feed without a code change, and a new feed starts unapproved.
- Size: M · Priority: P0 · Depends on: Admin sign-in requires an authenticator code · Story file: no (logo, link pattern and format arrive in S8.2, S3.6, S3.5)
- Acceptance outline:
  - Create, edit and list networks, shops and feeds, with validation (https URL, network required for an affiliate feed).
  - A shop with offers cannot be deleted, only disabled.
  - A feed URL is shown masked in lists and never logged (it may hold an API key).
  - Seeded demo rows remain and stay marked as demo.
- Tickets:
  - T3.1.1 | backend | M | Create and edit actions for networks, shops and feeds
  - T3.1.2 | frontend | M | Forms and lists with masked feed URL
  - T3.1.3 | test | S | Role checks, validation, URL never in logs

#### S3.2 Admin runs imports and reads their reports
- As an admin, I press "Import now" for one feed or all feeds and read what happened.
- Size: L · Priority: P0 · Depends on: Admin approves and disables shops and feeds · Story file: yes (new table, execution model, three lanes)
- Acceptance outline:
  - The buttons and the `import-feeds` command run the same code.
  - Every run, from either, stores a report: time, feed, outcome, row counts, rejected rows with reason codes.
  - A report list and detail page; one broken feed does not hide the others' results.
  - An import does not block the site or time out the request; a running state is visible and one feed cannot run twice at once.
- Tickets:
  - T3.2.1 | backend | M | Persist import runs from the shared importer
  - T3.2.2 | backend | M | Import-now action with per-feed lock and non-blocking execution
  - T3.2.3 | frontend | M | Feeds page with Import now, status, report list and detail
  - T3.2.4 | test | M | Report stored, lock, isolation; e2e of the button

#### S3.3 Offers missing from the latest import are removed
- As a visitor, I never see an offer the shop has stopped listing.
- Size: M · Priority: P0 · Depends on: none · Story file: no
- Acceptance outline:
  - After a successful import, a feed's offers absent from the file stop being public.
  - A failed, empty or suspiciously small import removes nothing and is flagged in the report.
  - The report shows the removed count.
  - An offer that returns is restored; an admin's hide is never undone.
- Tickets:
  - T3.3.1 | backend | M | Removal pass in the per-feed transaction with the safeguards above
  - T3.3.2 | test | M | Removal, safeguard, return and hide-preservation cases

#### S3.4 Import XML and compressed feeds safely
- As the owner, I can import the formats real networks serve: CSV or XML, plain or gzip, over https.
- Size: L · Priority: P0 · Depends on: none · Story file: no (shape fixed by decision 0007 and the canonical layout; OD7 covers the parser dependency)
- Acceptance outline:
  - XML rows go through the same row validation as CSV; gzip is decompressed under a size cap.
  - A feed of 10,000+ rows imports without holding the whole file in memory.
  - A redirect from https to http or to another host fails the feed (carried finding F-1).
  - Fetching stays in the one allowed module; the seam test allow-list is updated deliberately.
- Tickets:
  - T3.4.1 | backend | M | XML reader and gzip handling with size caps
  - T3.4.2 | backend | S | Streaming read for large feeds
  - T3.4.3 | backend | XS | Redirect policy for the https fetch
  - T3.4.4 | test | M | XML, gzip, oversize and redirect fixtures; seam allow-list update
  - T3.4.5 | docs | XS | Decision record for the XML parser dependency

#### S3.5 Per-feed field mapping for network feed layouts
- As an admin, I tell the system which columns or elements of a network's feed hold title, brand, part number, EAN, price, URL and category, so a new network needs no code change.
- Size: L · Priority: P0 · Depends on: Import XML and compressed feeds safely; Admin manages networks, shops and feeds · Story file: yes (changes the feed contract, importer and admin UI)
- Acceptance outline:
  - Each feed has a format and an admin-editable field mapping instead of the single canonical layout.
  - Price parsing handles the network's decimal and currency conventions, and whether the price includes IVA is recorded and checked per network (guardrail 4).
  - A wrong mapping rejects rows with clear codes and never publishes partial garbage.
  - The demo feeds keep working; real fixtures per network are added when samples exist.
- Tickets:
  - T3.5.1 | backend | M | Feed format and mapping storage, importer applies it
  - T3.5.2 | backend | S | Price and IVA handling per feed
  - T3.5.3 | frontend | M | Mapping editor with a preview of the first rows
  - T3.5.4 | test | M | Mapping tests with per-network fixtures
  - T3.5.5 | docs | XS | Record each network's IVA and field findings

#### S3.6 Affiliate link pattern per shop
- As the owner, I record a shop's affiliate link pattern so outgoing links carry our tracking when the feed's own link does not.
- Size: M · Priority: P1 · Depends on: Visitor goes to a shop through a logged redirect; Admin manages networks, shops and feeds · Story file: no
- Acceptance outline:
  - A shop or feed can hold an optional link pattern, managed in admin.
  - The redirect builds the destination from the pattern and the offer URL, and uses the feed's own URL when no pattern exists.
  - The destination is built only from stored data, never from the request, so it cannot be an open redirect.
  - May turn out unnecessary where a network's feed already carries tracked links; check at the first real feed and pull forward if not.
- Tickets:
  - T3.6.1 | backend | M | Pattern storage and destination builder in the redirect
  - T3.6.2 | frontend | S | Pattern field in the feed form
  - T3.6.3 | test | S | Pattern, fallback and open-redirect cases

### E4 Categories

Priority: P0. Covers mvp.md § Catalogue scope (the category tree and feed-category mapping). Outcome: the admin defines the fixed tree of about 30 categories and maps each feed category once; unmapped products wait in a queue.

#### S4.1 Admin maintains the category tree
- As an admin, I create, rename, reorder and remove categories without a code change.
- Size: M · Priority: P0 · Depends on: Admin sign-in requires an authenticator code · Story file: no
- Acceptance outline:
  - Edit parent, name and position; a published category's URL slug does not change when it is renamed.
  - A category that has children or products cannot be removed.
  - All actions are admin-guarded.
  - The demo tree stays for demo data; the real tree is entered by the owner (owner task O3).
- Tickets:
  - T4.1.1 | backend | M | Category create, rename, move and remove actions
  - T4.1.2 | frontend | M | Tree editor
  - T4.1.3 | test | S | Slug stability, removal rules, role checks

#### S4.2 Admin maps feed categories and clears the unmapped queue
- As an admin, I map each category a feed uses to one of ours once, and products from unmapped feed categories wait in a queue until I do.
- Size: M · Priority: P0 · Depends on: Admin maintains the category tree; Visitor browses products in a category · Story file: no (S5.1's story file fixes the model)
- Acceptance outline:
  - Lists each feed's distinct categories with product counts and current mapping.
  - A mapping applies to existing and future products of that feed category.
  - The unmapped queue lists categories with waiting products; those products are not public (OD3).
  - Changing a mapping moves the products.
- Tickets:
  - T4.2.1 | backend | M | Mapping edit actions that re-apply to existing products
  - T4.2.2 | frontend | M | Mapping screen and unmapped queue
  - T4.2.3 | test | S | Mapping applies, queue behaviour, role checks

### E5 Browse and search

Priority: P0. Covers mvp.md § Search and browsing, § Catalogue scope (categories). Outcome: a visitor reaches products from the home page, a category with filters, or free-text search that also matches EAN and part numbers.

#### S5.1 Visitor browses products in a category
- As a visitor, I open a category and see its products with the lowest price and shop count, and open one.
- Size: L · Priority: P0 · Depends on: none (OD3 decides unmapped products) · Story file: yes (adds a product-category link and a mapping table, changes the visibility contract and the importer). Weak on Small; accepted since the model change has no visible value without the page.
- Acceptance outline:
  - A server-rendered, paginated category page includes the products of its subcategories.
  - Lists only public products; a product with no category mapping is not public (OD3).
  - Each card shows title, brand, lowest visible price, shop count and links to the product page.
  - The importer records the feed's category per product; the demo seed and demo feeds supply categories and mappings.
  - Empty category shows an empty state; unknown category answers 404.
- Tickets:
  - T5.1.1 | backend | M | Product-category link and feed-category mapping tables; importer captures and assigns
  - T5.1.2 | backend | S | Visibility rule for products without a mapped category
  - T5.1.3 | backend | M | Category listing read function - lowest price, shop count, subtree, pagination
  - T5.1.4 | backend | S | Demo seed and demo feeds carry categories
  - T5.1.5 | frontend | M | Category page and product card with es-ES copy
  - T5.1.6 | test | M | Visibility, listing and e2e tests

#### S5.2 Home page shows the category tree
- As a visitor, I open the site and see the categories I can browse.
- Size: S · Priority: P0 · Depends on: Visitor browses products in a category · Story file: no
- Acceptance outline:
  - Home lists top-level categories with their children, each linking to its category page.
  - The site name comes from configuration and the header links home.
  - Shows a sensible state when no category has products.
- Tickets:
  - T5.2.1 | backend | XS | Category tree read function
  - T5.2.2 | frontend | M | Home page and header navigation
  - T5.2.3 | test | XS | Home e2e

#### S5.3 Visitor filters a category by brand, price and shop
- As a visitor, I narrow a category by brand, price range and shop.
- Size: M · Priority: P0 · Depends on: Visitor browses products in a category · Story file: no
- Acceptance outline:
  - Brand, minimum and maximum price (entered in euros, handled in cents) and shop filters, with counts per brand and shop.
  - Filters live in the URL, are shareable and work server-rendered.
  - The price filter uses each product's lowest visible offer.
  - Invalid input is ignored safely.
- Tickets:
  - T5.3.1 | backend | M | Filter and facet queries
  - T5.3.2 | frontend | M | Filter controls and URL state
  - T5.3.3 | test | S | Filter combinations and invalid input

#### S5.4 Visitor searches by text, EAN or part number
- As a visitor, I type a product name, an EAN or a part number in any spacing and find the product.
- Size: L · Priority: P0 · Depends on: none · Story file: yes (relevance rules and new indexes; decision 0002 fixes only the engine)
- Acceptance outline:
  - A search box on every page leads to a paginated results page of public products.
  - Text matches title and brand with Spanish language handling; an exact EAN and a part number with spaces, dashes or dots removed also match.
  - Search terms are not stored or logged (guardrail 5).
  - Empty-result state; results pages are not indexed.
- Tickets:
  - T5.4.1 | backend | M | Search index migration for text, normalised part number and EAN
  - T5.4.2 | backend | M | Search query with text ranking and EAN or part number detection
  - T5.4.3 | frontend | M | Search box and results page
  - T5.4.4 | test | M | Relevance fixtures, e2e, and no-query-logging test

### E6 Search engine visibility

Priority: P0. Covers mvp.md § Search and browsing (structured data), § Goal (10k products indexed). Outcome: Google can discover every public product and category and show prices in results.

#### S6.1 Product pages carry structured price data
- As a searcher on Google, I see the price and number of shops in the result.
- Size: S · Priority: P0 · Depends on: none · Story file: no
- Acceptance outline:
  - JSON-LD Product with AggregateOffer (low price, high price, offer count, currency EUR) in the server-rendered HTML.
  - Built from visible offers only; omitted when there are none.
  - Prices formatted from integer cents without floating-point (guardrail 4).
  - Owner spot-checks it in a schema validator.
- Tickets:
  - T6.1.1 | frontend | S | JSON-LD component on the product page
  - T6.1.2 | test | S | Cents-to-string unit tests; e2e parses the JSON-LD

#### S6.2 Sitemap, robots rules and canonical URLs
- As a search engine, I can discover and index every public product and category and nothing else.
- Size: M · Priority: P0 · Depends on: Visitor browses products in a category · Story file: no
- Acceptance outline:
  - A chunked sitemap lists only public products and categories; hidden, unmapped and unapproved items are excluded (guardrail 1).
  - robots rules allow public pages and disallow admin, the redirect and search results.
  - Product, category and filtered pages carry a canonical URL; the public site URL is configuration.
  - Generation stays fast with 10,000 products.
- Tickets:
  - T6.2.1 | backend | M | Sitemap generation queries with chunking
  - T6.2.2 | frontend | S | robots, canonical and noindex metadata
  - T6.2.3 | test | S | Hidden and unmapped items absent; robots rules

### E7 Matching and review

Priority: P1. Covers mvp.md § Matching, decision 0008. Outcome: offers from different feeds land under one product by EAN or brand and part number; conflicts wait for an admin, who can also merge, split and keep brand aliases.

#### S7.1 Match offers by brand and part number
- As a visitor, I see one product page for a part even when a shop's feed has no EAN.
- Size: M · Priority: P1 · Depends on: none · Story file: no
- Acceptance outline:
  - Step 2 of decision 0008: same normalised brand and part number attaches; both must be present.
  - The lookup is indexed; EAN-first order is unchanged.
  - Rows without EAN from two shops converge on one product (closes TD-25).
  - A brand and part number hit whose EAN disagrees keeps today's rejection until the review queue exists.
- Tickets:
  - T7.1.1 | backend | M | Matching step 2 and index migration
  - T7.1.2 | test | S | Matching table tests and importer integration

#### S7.2 Conflicting offers wait in an admin review queue
- As an admin, I resolve offers whose EAN and brand disagree, or whose EAN and part number point at different products, instead of the system guessing.
- Size: L · Priority: P1 · Depends on: Match offers by brand and part number; Admin sign-in requires an authenticator code · Story file: yes (stored decisions, importer behaviour change, may replace the offer-level review flag)
- Acceptance outline:
  - Both conflict cases in decision 0008 put the offer in a queue and off the public site (guardrail 1) instead of rejecting it.
  - The queue shows the offer beside its candidate product or products.
  - The admin attaches to one candidate, creates a new product, or discards; the decision is stored and re-applied on the next import.
  - The import report counts queued offers.
- Tickets:
  - T7.2.1 | backend | M | Queue storage; importer routes conflicts to it
  - T7.2.2 | backend | M | Resolve actions and stored decisions re-applied on import
  - T7.2.3 | frontend | M | Review queue screen
  - T7.2.4 | test | M | Both conflict cases, re-import stickiness, guardrail 1

#### S7.3 Admin maintains brand aliases
- As an admin, I declare that two brand spellings are the same brand (for example BOSCH and Robert Bosch) so matching treats them alike.
- Size: M · Priority: P1 · Depends on: Match offers by brand and part number; Admin sign-in requires an authenticator code · Story file: no
- Acceptance outline:
  - Add and remove alias groups in admin.
  - Matching maps brands through the aliases before comparing.
  - Effect applies from the next import; design states what happens to already-created products.
- Tickets:
  - T7.3.1 | backend | M | Alias storage and use in the matcher
  - T7.3.2 | frontend | S | Alias screen
  - T7.3.3 | test | S | Alias matching and role checks

#### S7.4 Admin merges two products
- As an admin, I merge a duplicate product into another so its shops sit under one page and the old link still works.
- Size: L · Priority: P1 · Depends on: Conflicting offers wait in an admin review queue; Admin hides and unhides products and offers · Story file: yes (new decision store, redirect semantics, affects search and sitemap)
- Acceptance outline:
  - Offers move to the surviving product (history and image move once those exist).
  - The old URL redirects permanently to the survivor.
  - The decision is stored and re-applied on the next import, so offers do not drift back.
  - Role-checked, with a confirmation step.
- Tickets:
  - T7.4.1 | backend | M | Merged-into state and permanent redirect from the old URL
  - T7.4.2 | backend | M | Merge action and stored decision
  - T7.4.3 | frontend | M | Merge screen
  - T7.4.4 | test | M | Merge, redirect, sitemap exclusion and re-import stickiness

#### S7.5 Admin splits offers off a product
- As an admin, I move wrongly grouped offers into a new product.
- Size: M · Priority: P1 · Depends on: Admin merges two products · Story file: no
- Acceptance outline:
  - Select offers on a product; they become a new product with its own URL.
  - The split is stored and re-applied on the next import.
  - Role-checked.
- Tickets:
  - T7.5.1 | backend | M | Split action and stored decision
  - T7.5.2 | frontend | S | Split screen
  - T7.5.3 | test | S | Split and re-import stickiness

### E8 Product page depth

Priority: P1. Covers mvp.md § Product and offers (images, price history, no-offers state, text ranking), § Shops and feeds are data (logo). Outcome: the product page has an image or category placeholder, a price history chart, survives losing all offers, and takes its text from the admin's highest-ranked shop.

#### S8.1 Admin uploads product images; categories have placeholders
- As an admin, I upload an image for a product; until then visitors see its category's placeholder.
- Size: L · Priority: P1 · Depends on: Admin sign-in requires an authenticator code · Story file: yes (storage volume, upload security, three lanes)
- Acceptance outline:
  - Upload from the admin product page; type and size validated on the server, images only.
  - Stored on a Docker volume behind a storage interface (decision 0004) and served with cache headers.
  - Product page shows the uploaded image, else its category's placeholder, else a generic one.
  - Feed images are never used (decision 0007); upload actions are role-checked.
- Tickets:
  - T8.1.1 | backend | M | Storage interface, volume implementation and Compose volume
  - T8.1.2 | backend | M | Upload action and serving route with validation
  - T8.1.3 | frontend | M | Upload control, product page image, per-category placeholders
  - T8.1.4 | test | S | Upload validation and role checks

#### S8.2 Shop logos on offers
- As a visitor, I recognise a shop in the offer list by its logo.
- Size: S · Priority: P2 · Depends on: Admin uploads product images; categories have placeholders; Admin manages networks, shops and feeds · Story file: no
- Acceptance outline:
  - Admin uploads a logo on the shop form, through the same storage.
  - Offer rows show the logo, and the shop name when there is none.
- Tickets:
  - T8.2.1 | backend | S | Logo field and upload through the storage interface
  - T8.2.2 | frontend | S | Logo on offer rows and in the shop form
  - T8.2.3 | test | XS | Logo upload and fallback

#### S8.3 Price history chart
- As a visitor, I see how a product's lowest price moved over time.
- Size: L · Priority: P1 · Depends on: none (ship before the first real feed so history starts at launch) · Story file: yes (new table, changes the product page contract)
- Acceptance outline:
  - One point per day per product, the lowest visible offer price that day, recorded by the import.
  - Running imports twice in a day never adds a second point.
  - A chart on the product page drawn from cents without third-party scripts (OD7); fewer than two points shows text instead.
  - No personal data is involved.
- Tickets:
  - T8.3.1 | backend | M | Price history storage and recording after import
  - T8.3.2 | backend | S | History in the product page read function
  - T8.3.3 | frontend | M | Chart component and copy
  - T8.3.4 | test | M | Recording idempotency, day minimum, page rendering

#### S8.4 Product page stays when offers disappear
- As a visitor, a product I found on Google keeps its page when no shop lists it, and says so with the last known lowest price.
- Size: M · Priority: P1 · Depends on: Price history chart; Offers missing from the latest import are removed · Story file: yes (reverses TD-31 and the visibility contract; OD4)
- Acceptance outline:
  - A product that has been public keeps its page, text, image and history while it has no visible offers.
  - The offer area says there are no offers right now and shows the last known lowest price and its date.
  - A product that was never public stays hidden; an admin-hidden product stays hidden; unmapped and queued products stay non-public.
  - JSON-LD and the sitemap handle zero offers.
- Tickets:
  - T8.4.1 | backend | M | Visibility rule for previously public products; last-known-price read
  - T8.4.2 | frontend | S | No-offers state
  - T8.4.3 | test | M | Rewrite the guardrail 1 visibility tests for the new rule
  - T8.4.4 | docs | XS | Record the decision that supersedes TD-31

#### S8.5 Admin ranks shops for product text
- As an admin, I rank shops so the best source's wording wins when feeds disagree about a product's text.
- Size: M · Priority: P1 · Depends on: Admin sign-in requires an authenticator code · Story file: no
- Acceptance outline:
  - Each shop has an admin-editable rank.
  - A product's title, brand and description come from its highest-ranked shop's offer, recalculated on import and on rank change.
  - Identity fields (EAN, part number) are not rewritten by the ranking.
  - Replaces today's first-import-wins text.
- Tickets:
  - T8.5.1 | backend | M | Rank storage and text selection on import and rank change
  - T8.5.2 | frontend | S | Ranking screen
  - T8.5.3 | test | S | Text precedence cases

### E9 Go live

Priority: P0. Covers mvp.md § Delivery, § Goal (site live, at least 3 approved feeds), § Data sources (first shops), decisions 0004 and 0007. Outcome: the site runs on an EU VPS with a domain so networks can review it, real feeds go live, and data is backed up.

#### S9.1 Site is live on an EU VPS over HTTPS
- As a network reviewer, I open the domain and see the working site; as the owner, I redeploy by a documented procedure.
- Size: L · Priority: P0 · Depends on: Sitemap, robots rules and canonical URLs; Legal and affiliate disclosure pages; Home page shows the category tree · Story file: yes (ops, Compose, docs; records hosting decisions)
- Acceptance outline:
  - Production Compose setup: app behind a reverse proxy with TLS on the domain; the database and Umami are not reachable from the internet.
  - No secret in git; demo data setting follows OD2.
  - A written deploy and rollback procedure that has been run once.
  - Dependency audit with dev packages omitted is clean at deploy time (carried risk, dev-only advisories accepted).
  - A smoke check covers home, a product page, health, no cookie on public pages, and no admin route open before S2.2 is deployed.
- Tickets:
  - T9.1.1 | ops | S | Provision the VPS, DNS and firewall (owner, per runbook)
  - T9.1.2 | backend | M | Production Compose overrides, reverse proxy and TLS
  - T9.1.3 | backend | S | Production environment template, secrets handling and Umami login hardening
  - T9.1.4 | docs | S | Deploy and rollback runbook, plus decision record for hosting
  - T9.1.5 | ops | S | First deploy and smoke run
  - T9.1.6 | test | S | Post-deploy smoke script

#### S9.2 Database and uploads are backed up and restorable
- As the owner, I can restore the site's data after losing the server.
- Size: M · Priority: P1 · Depends on: Site is live on an EU VPS over HTTPS · Story file: no
- Acceptance outline:
  - Daily dumps of the app and Umami databases are copied off the server, encrypted, with a retention period.
  - The image volume is included once S8.1 exists.
  - A restore has been rehearsed on a scratch machine.
  - Backups hold admin password hashes, so their storage is private.
- Tickets:
  - T9.2.1 | ops | S | Backup job and off-server copy with retention
  - T9.2.2 | docs | S | Restore runbook
  - T9.2.3 | ops | S | Restore rehearsal

#### S9.3 Legal and affiliate disclosure pages
- As a visitor, I can read who runs the site, how data is handled, and that outgoing links earn a commission.
- Size: S · Priority: P0 · Depends on: none · Story file: no. HOLD: scope addition pending OD5; do not start until the owner answers.
- Acceptance outline:
  - Legal notice, privacy policy and affiliate disclosure pages, linked from the footer of every page.
  - The privacy text states that no cookies are set for visitors and what the click log holds.
  - Text is supplied by the owner in Spanish; no cookie banner (decision 0009).
- Tickets:
  - T9.3.1 | frontend | S | Static pages and footer links, text from message files
  - T9.3.2 | test | XS | Pages render and the footer links to them

#### S9.4 First real affiliate feed goes live
- As the owner, I approve a real shop's feed and its products appear on the live site with working outgoing links.
- Size: M · Priority: P0 · Depends on: Site is live on an EU VPS over HTTPS; Admin maps feed categories and clears the unmapped queue; Database and uploads are backed up and restorable; Per-feed field mapping for network feed layouts; Offers missing from the latest import are removed; Admin hides and unhides products and offers · Story file: no (a checklist run; new defects found become new tickets)
- Acceptance outline:
  - The shop and feed are entered in admin and stay unapproved until the import report is reviewed.
  - IVA-inclusive pricing is confirmed against the shop for this network (guardrail 4).
  - Categories are mapped and the unmapped queue cleared; the demo feeds are disabled on the live site.
  - One product is checked end to end, including that the redirect reaches the shop with tracking.
  - Repeat per feed until three feeds are approved.
- Tickets:
  - T9.4.1 | ops | S | Enter the shop and feed, import, review the report, disable demo feeds (owner)
  - T9.4.2 | ops | S | Check price, IVA and tracking on sample products against the shop (owner)

### E10 Hardening and carried findings

Priority: P2 (S10.1 is P1). Covers mvp.md § Goal (10k products), the carried rows from the two closed runs. Outcome: pages stay fast at target size, and open findings from slices A and B are closed or consciously kept.

#### S10.1 Catalogue pages stay fast at 10,000 products
- As a visitor and as Googlebot, I get fast responses at the target catalogue size.
- Size: M · Priority: P1 · Depends on: Visitor searches by text, EAN or part number; Visitor filters a category by brand, price and shop; Sitemap, robots rules and canonical URLs · Story file: no
- Acceptance outline:
  - A reproducible generated dataset of 10,000 products and about 30,000 offers (generated, never scraped).
  - Product, category, search and sitemap meet response-time targets fixed at design.
  - Indexes are added where query plans show scans; findings recorded.
- Tickets:
  - T10.1.1 | test | S | Synthetic 10k dataset generator and timing check
  - T10.1.2 | backend | M | Index and query tuning from the findings

#### S10.2 Close carried findings from slices A and B
- As the owner, the findings carried out of the first two runs are fixed or consciously closed.
- Size: S · Priority: P2 (its copy ticket should be done before the first deploy) · Depends on: none · Story file: no
- Acceptance outline:
  - The e2e setup's failure branches are covered by a test (finding F-3).
  - The owner has reviewed the Spanish copy and the corrections are applied.
  - CLAUDE.md § Stack lists npm and Node 22, if the owner agrees.
- Tickets:
  - T10.2.1 | test | S | Cover the e2e global-setup failure branches
  - T10.2.2 | frontend | XS | Apply the owner's es-ES copy corrections
  - T10.2.3 | docs | XS | Add the npm and Node 22 line to CLAUDE.md § Stack (owner's call)

#### S10.3 Feed URLs holding API keys are encrypted at rest
- As the owner, a database dump does not expose network API keys.
- Size: S · Priority: P2 · Depends on: Admin manages networks, shops and feeds · Story file: no
- Acceptance outline:
  - Feed URLs are stored encrypted with a key held in configuration, and decrypted only inside the importer.
  - Existing rows are converted by the migration.
  - Backups and logs show no plaintext URL.
- Tickets:
  - T10.3.1 | backend | S | Encrypt and decrypt feed URLs; migrate existing rows
  - T10.3.2 | test | XS | Round trip and no plaintext in dumps or logs

## Sequence

Build order, one story per slice. Branch and run per slice as before.

Phase A, a reviewable live site (no admin yet; demo data):
1. S1.1 Visitor goes to a shop through a logged redirect. First to run: small, independent, completes the core loop's last step, and lands the deferred guardrail-5 test.
2. S5.1 Visitor browses products in a category (fixes the category data model and the unmapped rule).
3. S5.2 Home page shows the category tree.
4. S6.1 Product pages carry structured price data.
5. S6.2 Sitemap, robots rules and canonical URLs.
6. S1.2 Umami tracker on public pages.
7. S10.2 Close carried findings from slices A and B (copy review lands before deploy).
8. S9.3 Legal and affiliate disclosure pages (HOLD on OD5).
9. S9.1 Site is live on an EU VPS over HTTPS. Milestone M1: owner applies to the networks (owner task O2). Network approval is an external wait of unknown length.

Phase B, admin and import machinery while networks review:
10. S2.1 Admin signs in with email and password.
11. S2.2 Admin sign-in requires an authenticator code (no admin route is deployed before this).
12. S2.3 Admin approves and disables shops and feeds.
13. S2.4 Admin hides and unhides products and offers.
14. S3.1 Admin manages networks, shops and feeds.
15. S3.2 Admin runs imports and reads their reports.
16. S3.3 Offers missing from the latest import are removed.
17. S3.4 Import XML and compressed feeds safely.
18. S3.5 Per-feed field mapping for network feed layouts.
19. S4.1 Admin maintains the category tree.
20. S4.2 Admin maps feed categories and clears the unmapped queue.

Phase C, before real data:
21. S8.3 Price history chart (so history starts at launch).
22. S9.2 Database and uploads are backed up and restorable.
23. S9.4 First real affiliate feed goes live. Milestone M2. Blocked on network approval and a real sample feed.

Phase D, MVP completeness:
24. S5.4 Visitor searches by text, EAN or part number.
25. S5.3 Visitor filters a category by brand, price and shop.
26. S10.1 Catalogue pages stay fast at 10,000 products.
27. S3.6 Affiliate link pattern per shop (pull before slice 23 if the first real feed lacks tracked links).
28. S7.1 Match offers by brand and part number.
29. S7.2 Conflicting offers wait in an admin review queue.
30. S7.3 Admin maintains brand aliases.
31. S8.4 Product page stays when offers disappear.
32. S8.1 Admin uploads product images; categories have placeholders.
33. S7.4 Admin merges two products.
34. S7.5 Admin splits offers off a product.
35. S8.5 Admin ranks shops for product text.
36. S8.2 Shop logos on offers.
37. S1.3 Admin sees click counts per shop and product.
38. S10.3 Feed URLs holding API keys are encrypted at rest.
Milestone M3 is owner-tracked: three feeds approved, 10k products indexed, first clicks, first commission.

Critical path to "site live on a VPS with real feeds": slices 1, 2, 3, 5, 8, 9, then the external wait, then 10 to 20, 22, 23. Not on it, though cheap and recommended: 4, 6, 7 (7's copy review), 21 (starts the history; do it before 23 if possible). Search (24) and filters (25) are not needed to be live with real feeds but are needed for the MVP done-definition.

Reasons for the edges:
- Slice 1 first: independent, small, and every later offer-facing slice then renders the link.
- Slices 2 and 5 before 9: networks only approve a site they can visit (0007); a visitor needs somewhere to go, and the sitemap needs category URLs.
- 10 before 12 to 14 and 19 to 20: every admin action needs the guard. 11 before any admin deploy.
- 12 and 14 before 15: Import now needs approved feeds that exist as rows.
- 17 and 18 before 23: real feeds arrive as XML or gzip and in network column layouts.
- 19 and 20 before 23: real products arrive in feed categories nobody has mapped, and unmapped products are not public.
- 21 before 23, 22 before 23: history cannot be backfilled, and admin settings are not reproducible from feeds.
- 28 before 29 and 30: queue and alias are refinements of the brand and part number step.
- 31 after 16 and 21: it needs removal to create the case and history to supply the last price.
- 33 after 29: merge reuses the decision store.

## Owner tasks

Not code, not sized. Needed on the critical path unless marked.

- O1. Choose a VPS provider and buy a domain; point DNS. Before slice 9. Recorded as a decision when done (decision 0004).
- O2. Register publisher accounts and apply to the five first shops (Awin: Leroy Merlin, ManoMano, Brico Depot; Kwanko: Oscaro; Effinity: Norauto) once the site is live. After slice 9. Approval time is unknown.
- O3. Write the list of about 30 categories (names and hierarchy, Spanish). Before slice 19.
- O4. Supply the legal text (legal notice, privacy policy, affiliate disclosure) and decide when to register as autónomo or use a company; the legal notice may need the owner's identity before launch (OD5). Before slice 8.
- O5. Review the Spanish copy in the message files. Before slice 9 (carried finding).
- O6. Obtain a sample feed and format documentation from each network after the publisher account exists. Before slice 17 for realistic fixtures; slice 18 needs it.
- O7. Run the create-admin command for the three members and store their authenticator secrets safely. After slice 11.
- O8. Verify the domain in Google Search Console and submit the sitemap. After slice 9.
- O9. Register as payee with a network when it asks (decision 0007). Before first payout.
- O10. Create the Umami website and change its default login. With slice 6 locally and slice 9 live.
- O11. Track the done-definition: three approved feeds, 10k products indexed, first clicks, first commission.

## Open decisions

Each has my recommendation. None blocks issue creation; the blocked slice is named.

- OD1. How should admin authentication be built? Options: a small purpose-built module (Node's built-in password hashing, one maintained TOTP library, server-stored opaque sessions in an HttpOnly cookie) or an off-the-shelf auth framework. Recommendation: the small purpose-built module, since there are three users and no OAuth, and record it as a decision. Needs a new dependency decision (TOTP library). Blocks S2.1 design, not before.
- OD2. What does the live site show while networks review it? Options: demo catalogue on (fictional shops), empty catalogue, or a notice-only site. Recommendation: demo catalogue on with a visible notice that it is a demo, demo offers pointing nowhere real, disabled once the first real feed is approved. Unverified: whether networks accept this; the owner should ask each network's publisher support what it needs. Blocks S9.1.
- OD3. Are products from unmapped feed categories public? mvp.md says products from approved feeds publish automatically and also that unmapped ones wait in an admin queue. Recommendation: not public until mapped, since a category-less product cannot be browsed and would pollute the sitemap. This changes the visibility contract and the `Visibility` wording; the owner confirms. Blocks S5.1 (slice 2).
- OD4. When a product loses all offers, does its page stay even if the cause was an admin disabling the feed? Today it returns 404 (TD-31), against mvp.md. Recommendation: keep the page in all cases except admin-hidden; price points are only recorded from visible offers, so what is shown was public when recorded. Blocks S8.4 (slice 31).
- OD5. Add legal and affiliate disclosure pages to the MVP scope? They are not in mvp.md. Recommendation: yes; a Spanish affiliate site that keeps admin emails and records clicks should state who runs it and how data is handled, and networks commonly ask for a visible policy (unverified). Ask a gestor whether identity must be shown before the autónomo registration. This is a scope addition, so it is the owner's call. Blocks S9.3, and S9.1 in practice.
- OD6. VPS provider, domain and reverse proxy; who performs server work. Recommendation: the owner performs server tasks following the runbook, since no ops lane exists; use a reverse proxy with automatic TLS (Caddy), recorded as a decision. Blocks S9.1.
- OD7. New runtime dependencies that each need a decision record: an XML parser (S3.4), a TOTP library (S2.1), image handling (S8.1), a chart approach (S8.3). Recommendation: one streaming XML parser; no chart library (server-drawn SVG); validate images but do not process them in the MVP. Each blocks only its own story's design.
- OD8. Admin interface language. Recommendation: Spanish, in message files under a separate admin section, same rule as the public site. Blocks S2.1 design, trivially.
- OD9. Add a CI workflow so the gate runs on pull requests? There is no `.github`, and the gate needs Docker. Recommendation: defer; the orchestrator already runs the gate before each pull request. Blocks nothing.

## Capability coverage

Every ABSENT or PARTIAL row in 01-recon § Capability map, and where it lands.

- Categories tree, feed-category mapping, unmapped queue (PARTIAL): S5.1 (data model), S4.1 (tree editing), S4.2 (mapping and queue).
- Product text from feeds, ranking decides (PARTIAL): S8.5.
- Product images, category placeholder (PARTIAL): S8.1.
- Price history and chart (ABSENT): S8.3.
- No-offers state with last known price (ABSENT): S8.4 (OD4).
- Matching by brand and part number (PARTIAL): S7.1.
- Matching conflict to review queue (PARTIAL): S7.2.
- Admin merge and split, stored decisions, old-URL redirect (ABSENT): S7.4, S7.5.
- Brand alias table (ABSENT): S7.3.
- Search including EAN and part number (ABSENT): S5.4.
- Category pages with filters (ABSENT): S5.1, S5.3.
- Home and product listing (ABSENT): S5.2, S5.1.
- JSON-LD (ABSENT): S6.1.
- Sitemap, robots, canonical (ABSENT): S6.2.
- First shops and networks (ABSENT): S9.4 plus owner tasks O2, O6.
- Shops and feeds as data: logo, link pattern, format, admin screens (PARTIAL): S8.2, S3.6, S3.5, S3.1.
- Import command formats XML and gzip (PARTIAL): S3.4, S3.5.
- Import report stored and readable (PARTIAL): S3.2.
- "Import now" button (ABSENT): S3.2.
- Removal of offers missing from the latest import (ABSENT): S3.3.
- Admin accounts by command, login with TOTP, server role check (ABSENT): S2.1, S2.2.
- Approve and disable shops and feeds (ABSENT): S2.3.
- Run imports and read reports (ABSENT): S3.2.
- Hide any product or offer (PARTIAL): S2.4.
- Upload product images (ABSENT): S8.1.
- Rank shops (ABSENT): S8.5.
- `/go` redirect and click log (ABSENT): S1.1.
- Umami tracker (PARTIAL): S1.2.
- Delivery on a VPS with domain (ABSENT): S9.1, S9.2, S9.3 (OD5).
- Shipped, nothing planned: site name, language, no fitment, product page and offers sorted, single-offer wording, cents and IVA display, EAN matching, SEO server rendering, no scraping, shop-upload source type, import isolation and idempotency, visibility read side, no ads, local Compose, the gate.

## Not in backlog

Out of MVP (mvp.md § Out of MVP), none planned: shops uploading their own feeds and per-click billing; ads and cookie banner; public accounts, alerts, reviews, ratings, favourites; shipping costs; fitment search and TecDoc; tyres, building materials, plumbing and electrical; Amazon; Open Icecat; scheduled imports; languages other than Spanish.

Carried ledger rows (01-recon § Open ledger rows):
- Importer https redirect policy (F-1): ticket T3.4.3.
- e2e global-setup failure branches (F-3): ticket T10.2.1.
- Spanish copy is the lane's own wording: ticket T10.2.2 and owner task O5.
- CLAUDE.md § Stack lacks npm and Node 22: ticket T10.2.3, the owner's call.
- Umami default admin login: tickets T1.2.4 and T9.1.3.
- Feed URL may hold an API key: masking in S3.1, encryption in S10.3.
- Dismissed, 9 dev-only advisories via drizzle-kit (and the earlier 5 in the lint chain): dev-only, none in a production install; a check at deploy time is an acceptance bullet of S9.1.
- Dismissed, the 8 pack style items and the CRLF tip disagreement: they concern the agentic network's own files outside the repo, not product work; they stay in the run ledger for a protocol close-out.
- Dismissed, the missing decision numbers 0003 and 0005: a numbering gap with no consequence; no ticket.
- Closed already, per the 2026-10-17 ledger: Vite ESM warning, entrypoint and init-env tests, scraping-lint regression test, e2e base-URL duplicate, CSS Modules choice.
