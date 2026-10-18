REPORT 2026-10-17-mvp-backlog-revision/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   python C:\projects\investments\.agentic\scripts\check_report.py C:\projects\investments\.agentic\projects\los-tres\runs\2026-10-17-mvp-backlog-revision\01-product.md --lane product
  result:    PASS
  detail:    check_report exit 0 on the artifact; head derived with --emit-head

contract_notes:
  - S5.1 (unmapped products not public), S8.4 (page stays, supersedes TD-31), S1.1 (click counting rules), S8.3 (history gaps) and S8.6 (attributes and fitment text on PublicProductPage) change shipped contracts. Each design must name its test and doc updates.
  - docs/product/mvp.md needs matching edits for D-1 (legal pages, demo catalogue, unmapped products) and for the gap rules closed here; proposed text is in § mvp.md amendment. The owner decides; nothing was edited.
  - project.md guardrail 1 says a product is public only while "not waiting in the matching queue". D-1/OD3 adds the unmapped state. The wording stays true, because it is a necessary condition, but the owner may want the unmapped state named there.

pack_corrections:
  - C:\projects\investments\.agentic\projects\los-tres\project.md — line 87 ends "There is no backlog yet." Replace with: "The backlog is GitHub Project 3 (CLAUDE.md § Canonical documentation); the build order is the Slice field on each story."
  - C:\projects\investments\.agentic\projects\los-tres\capabilities\product.md — line 4 says "no code and no backlog yet". Replace with: "has an approved MVP scope, a tracer-bullet code base (slices A and B) and a backlog on GitHub Project 3."
  - C:\projects\investments\.agentic\projects\los-tres\capabilities\product.md — § Where the plan lives table has no board row. Add: "GitHub Project 3 | the backlog: epics, stories, tickets and owner tasks; the Slice field is the build order".

handoff:
  - 39 stories (38 kept, one new: S8.6), 140 tickets (131 kept, 9 new), 13 owner tasks, no issue closed and no ID renumbered; findings 1-11 answered, one row each - see § Findings resolved
  - Build order is 39 slices; S9.4 (first real feed) is slice 28; slices 1-28 are all P0 and all sit in S9.4's dependency closure; no P0 story follows slice 28 - see § Sequence
  - Board work for findings 12-15 is laid out per story: issue number, Slice, priority and depends changes, new IDs and parents - see § Board delta
  - Two new open decisions: OD10 (demo notice) and OD11 (feed-URL encryption before the first real feed). OD4 now blocks a P0 story on the critical path - see § Open decisions
  - D-1 applied: OD3 in S5.1, S4.2, S8.4, S9.4; OD5 in S9.3 (off HOLD), S9.1; OD2 in S1.1, S6.2, S8.4, S9.1, S9.4 - see § Backlog
  - Owner tasks O1-O13 each name the stories they block and are owner work, never agent work - see § Owner tasks
  - Human decides whether to apply the proposed mvp.md edits; dispatch of the board work does not depend on it - see § mvp.md amendment

skill_calls:
  - none

risks:
  - Taken on trust from 02-product.md and 01-recon: every code-state claim except the four I opened (visibility.ts:30-38, source.ts:30-60, sources.ts:44 is_demo, the two demo CSVs). GitHub issues and Project 3 were not read, per the order.
  - Unverified market fact: that Awin, Kwanko and Effinity product feeds carry tracked links. It decides whether S3.6 is needed; I made it a dependency of S9.4 rather than assume. O6 sample feeds settle it.
  - Unverified market and legal facts: that networks accept a live demo catalogue, and that LSSI-CE requires the three legal pages. D-1 rules the pages in scope; I did not check the law. O12 asks each network what it needs.
  - OD4 is still open yet S8.4 (slice 23) now sits before the first real feed. Its recommendation shows a last known price taken from a feed an admin may have disabled, which is in tension with guardrail 1. The owner should rule before slice 21.
  - S1.1 reads the user agent in memory to skip crawlers and never stores or logs it. Guardrail 5 forbids storing, not reading. Umami derives browser and system from the request by design (decision 0009); whether that meets "no user agent" is the owner's reading.
  - S7.3 (aliases) stays after S9.4. A second feed spelling a brand differently (BOSCH, Robert Bosch) fills the S7.2 queue with false conflicts and makes duplicates. S7.3 is slice 29 and gates approval of the second feed; pull it forward if O6 samples show spelling variance.
  - Beyond findings 1-11, not scheduled: demo categories stay on the home page once demo products stop being public. S5.2's empty state may cover it; design should check. Raised, not added to the backlog.
  - I made the call that price history stores no value for days without an import and the chart shows the gap. It is a display rule, easy to reverse, and not escalated as a decision.
  - Epic priorities E7, E8 and E10 were rolled up to P0 because they hold a P0 story. That is mechanical; the owner may set epic priority differently on the board.
  - Dependency edits beyond the five named: S9.4 now also depends on S2.3, S3.2, S8.3 (these were missing); S3.3 on S3.2; S7.2 on S8.4; S7.3, S8.1, S8.5 on S2.2; S8.5 on S8.6. Each is in § Board delta.
  - Further stale profile lines: project.md lines 13 and 18 and the heading "Building before the stack exists" still describe a repo with no code and no stack. Left for the close-out docs lane; not in this order's two named lines.
  - PR #7 (slice B) must be merged by the human before slice 1 starts; carried from the prior run.
  - Sizes are relative judgments with no velocity data; XL means split again at its run.

## Orchestrator brief
- verdict: revision of the existing backlog, not a new one. No epic added or closed; one new story (S8.6), 9 new tickets, no ID renumbered, nothing to close (§ Board delta).
- human reads to approve: Findings resolved · Sequence · Open decisions (OD10 and OD11 new, OD4 now blocks the critical path) · mvp.md amendment.
- orchestrator reads for board work: Backlog (revised text per story) · Board delta (issue numbers, Slice, priority and depends changes, new IDs) · Owner tasks (O1-O13 with the stories they block).
- build order: 39 slices; S9.4 is slice 28. Slices 1-28 are all P0 and all in S9.4's dependency closure; slices 29-39 are P1 then P2. No P0 follows slice 28.
- moved before S9.4 or made direct dependencies of it: S7.1, S7.2, S8.3, S8.4, S9.2, S3.6, S10.3 (provisional on OD11); S3.3 re-ordered behind S8.4.
- scope gaps closed: S8.6 (attributes and fitment text), S8.3 (gaps in history), S9.1 (no visitor IPs in logs), S1.1 (bots, prefetch, demo not counted), S6.1 with S8.4 (no JSON-LD with zero offers).
- D-1 applied: OD3 (S5.1, S4.2, S8.4, S9.4), OD5 (S9.3 off HOLD, S9.1), OD2 (S1.1, S6.2, S8.4, S9.1, S9.4).
- open: OD1, OD4, OD6-OD9 with recommendations, plus OD10 (demo notice) and OD11 (encrypt feed URLs first).
- blocks dispatch: nothing for issue updates; the human approves this brief first (D-2). Slice 1 needs PR #7 merged.
- sections below: Findings resolved · Backlog · Sequence · Owner tasks · Open decisions · Board delta · mvp.md amendment · Capability coverage · Not in backlog

## Findings resolved

One row per finding. IDs are stable; "new" means an unused ID.

| # | Finding | What changed | IDs |
|---|---|---|---|
| 1 | Matching before the first real feed | S7.1 and S7.2 move from slices 28-29 to 25-26, ahead of S9.4 (slice 28), P1 to P0. S9.4 depends on both. S7.2 also depends on S8.4 so a queued offer never shows on a kept page. Aliases (S7.3) stay after S9.4 and gate the second feed; see risks. | S7.1, S7.2, S9.4, S7.3 |
| 2 | Page stays when offers disappear | S8.4 moves to slice 23, before S9.4. S8.4 now depends only on S8.3 (the last known price comes from history), and S3.3 depends on S8.4, so offer removal never ships ahead of the rule that keeps the page. Order: S8.3 (22), S8.4 (23), S3.3 (24). S8.4 gains a demo-product exception (D-1/OD2). | S8.3, S8.4, S3.3, S9.4 |
| 3 | S9.4 and the affiliate link pattern | Dependency added; I did not take the "justify why not" option. S9.4 acceptance already requires the redirect to reach the shop with tracking, so the mechanism cannot stay optional. S3.6 goes P1 to P0 at slice 16, right after S3.1. Escape hatch: if O6 sample feeds show every first-target network already ships tracked links, the owner may demote S3.6; I recommend against, since S3.6 is M and untracked clicks earn nothing. | S3.6, S9.4 |
| 4 | Priority follows build order | P0 = sequenced at or before S9.4, and S9.4's dependency closure is exactly slices 1-28. Raised to P0: S1.2, S10.2, S9.2, S8.3, S8.4, S7.1, S7.2, S3.6, S10.3. Lowered to P1: S5.4, S5.3 (they come after go-live). No P0 story follows slice 28, so no after-go-live exception is needed; slices 10-28 sit after the site goes live (S9.1) and each carries a one-line reason in § Sequence. Epics E7, E8, E10 roll up to P0. | see § Board delta |
| 5 | Dependency mismatches | S3.2 now depends on S2.3 and S3.1. S1.3 depends on S2.2 (and S1.1), not S2.1. Critical path text and edge notes now agree: S9.4 depends on S8.3 and S8.4 directly and every slice before it is on the path. Same fix applied elsewhere: S9.4 was missing S2.3 and S3.2; S3.3 now names S3.2; every admin screen depends on S2.2, not S2.1 (S7.2, S7.3, S8.1 and S1.3). | S3.2, S1.3, S9.4, S3.3, S7.2, S7.3, S8.1, S8.5 |
| 6 | Attributes and fitment text | New story S8.6 in E8: the admin maps optional description, attributes and fitment-text fields, the importer stores them (and fills products created earlier), the product page shows them as escaped plain text. No vehicle model, no fitment search or filter (mvp.md). Slice 33, P1, after S3.5. S8.5 ranking extends to these fields. | S8.6 (new), S8.5 |
| 7 | History days without an import | Imports are manual, so no point exists for such days. Nothing is stored, carried forward or interpolated. The chart plots recorded days on a true date axis and shows a gap as a gap, with a caption that prices are recorded when the catalogue is updated. The day's point is the lowest visible price any import saw that day (mvp.md). Display rule, easy to reverse. | S8.3 (T8.3.3, T8.3.4 reworded) |
| 8 | No visitor IPs in server logs | S9.1 acceptance gains a log rule: the reverse proxy and the app write no client address or user agent, checked after deploy by a request with a known address. New ticket T9.1.7 does the check; T9.1.2 intent carries the proxy setting. | S9.1, T9.1.2, T9.1.7 (new) |
| 9 | JSON-LD with zero offers | One rule, owned by S6.1: JSON-LD is omitted when a product has no visible offers. S8.4 no longer says "JSON-LD handles zero offers"; it keeps the page indexed and in the sitemap, without structured data. Reason: Product markup without offers qualifies for no rich result, and a price built from the last known value would claim a price nobody offers. | S6.1, S8.4 |
| 10 | Bots following /go | S1.1 counts only real navigations: no HEAD or OPTIONS, no prefetch (Purpose and Sec-Purpose headers), no known crawler (user agent matched in memory against a short pattern list; never stored or logged), no offer of a demo feed (D-1/OD2). Excluded requests get the same redirect. The link is a plain anchor, not a prefetching component, and S6.2 disallows /go in robots. New ticket T1.1.5; T1.1.4 test reworded. Limit stated: unlisted bots still count; network reports stay the authority for commission. | S1.1, T1.1.4, T1.1.5 (new), S6.2, S1.3 |
| 11 | Encrypt feed URLs before the first real feed | Recommendation: yes, before. It is S-sized; no plaintext key then ever reaches production or a backup, and there is no live conversion. The protection is real only against a leaked dump or injection read, not host compromise, since the key sits in server configuration. Because it is a risk-acceptance call, it is new OD11. The backlog places S10.3 at slice 27, P0, S9.4 depends on it, provisional on OD11. | S10.3, S9.4, OD11 (new) |

## Backlog

Tickets are the expected work units for each story, not a design. The story's own run (design, then build lanes) may merge, split or rename them. Issue titles are English and carry no personal data or UI copy.

Priority follows the build order: every story in slices 1-28 (up to and including S9.4) is P0, the MVP-completeness tail is P1, polish is P2. Epic priority is the highest of its stories. Each story carries its `Slice` number (the build-order number for the board's Slice field). Existing issues are updated in place. S8.6 is the one new story; new tickets end with "(NEW)" on their line (the marker is not part of the issue title).

Ticket line format: `T<story>.<n> | lane | size | title - intent`. Lanes: backend, frontend, test, docs, ops.

### E0 Tracer bullet (DONE, not re-planned)

Priority: P0. Covers mvp.md § Goal (the core loop's middle), § Delivery (Compose, gate), § Product and offers, § Feed import (basic), § Visibility. Outcome: skeleton, Compose, gate, six-table schema, demo seed, `import-feeds` (CSV, EAN matching) and one product page.

- #4 Slice A, skeleton, Compose, gate: DONE (PR #5 merged).
- #6 Slice B, schema, demo seed, importer, product page: DONE on branch 6-tracer-bullet-slice-b, PR #7 open. All later slices branch from main after the human merges PR #7.

### E1 Outgoing clicks and analytics

Priority: P0. Covers mvp.md § Outgoing clicks, § Analytics, § Revenue. Outcome: every outbound link goes through our redirect, is counted without personal data (real navigations only, demo offers excluded), and traffic is measured by cookieless Umami, so the first click and later commission can be seen.

#### S1.1 Visitor goes to a shop through a logged redirect
- As a visitor, I click "go to shop" on an offer and arrive at the shop's page, while the site logs the click without any personal data.
- Size: M · Priority: P0 · Story file: no (decision 0009 and mvp.md fix the shape; the design lane still fires for the new table and the offer link field)
- Depends on: none
- Slice: 1
- Acceptance outline:
  - Each offer row links to `/go/<offer>` with a plain anchor (no prefetching link component); the shop URL is never rendered directly.
  - A visible offer answers 302 to its stored URL; hidden, unapproved, in-review or unknown offers answer 404 (guardrail 1).
  - One click row holds offer, shop, product, time and source page only; no IP, user agent or cookie is stored, set or logged (guardrail 5).
  - Outbound links are marked as sponsored for search engines.
  - Counting rules (finding 10, D-1/OD2): a click row is written only for a real navigation. HEAD and OPTIONS requests, prefetch requests, requests from known crawlers and offers of a demo feed are redirected as usual but not counted.
  - Crawler detection reads the user agent in memory against a short pattern list held in code; the value is never stored, logged or forwarded.
  - Stated limit: an unlisted bot still counts; the click log is a best-effort count and the network's report stays the authority for commission (decision 0009).
  - The guardrail-5 test deferred from slice B lands here.
- Tickets:
  - T1.1.1 | backend | S | Clicks table and write path - migration plus a write that stores only the permitted fields
  - T1.1.2 | backend | S | Redirect route - visibility-scoped lookup, 302, 404 otherwise, no URL in logs
  - T1.1.3 | frontend | S | Offer link through the redirect - go-to-shop control on offer rows as a plain anchor, with es-ES copy
  - T1.1.4 | test | S | Guardrail 1 and 5 tests for the redirect, counting-rule cases (HEAD, prefetch, crawler, demo offer) and an e2e click-through
  - T1.1.5 | backend | S | Counting rules - skip HEAD, prefetch, known crawlers and demo-feed offers; user agent read in memory only (NEW)

#### S1.2 Umami tracker on public pages
- As the owner, I see visits in Umami without the site setting any cookie.
- Size: S · Priority: P0 · Story file: no
- Depends on: none
- Slice: 6
- Acceptance outline:
  - The tracker script is included only when its website id and script URL are configured.
  - Public pages still set no cookie with the tracker on (test).
  - The new settings are documented in `.env.example`.
  - A runbook step creates the Umami website and changes the default admin login (carried risk; owner task O10).
- Tickets:
  - T1.2.1 | backend | XS | Umami settings - website id and script URL in config, Compose and `.env.example`
  - T1.2.2 | frontend | XS | Conditional tracker script in the root layout
  - T1.2.3 | test | XS | No cookie and no script when unset; no cookie when set
  - T1.2.4 | docs | XS | Umami runbook - create the website, change the default login

#### S1.3 Admin sees click counts per shop and product
- As an admin, I see clicks per shop and per product over a date range, so I can confirm the first clicks and reconcile with network reports.
- Size: S · Priority: P2 · Story file: no
- Depends on: S1.1, S2.2
- Slice: 39
- Acceptance outline:
  - Admin-only page with counts by shop and by product for a chosen range.
  - Reads only the click table; there is no personal data to show. The table holds no demo, prefetch or crawler rows (S1.1), so nothing is filtered here.
  - Empty state when there are no clicks.
- Tickets:
  - T1.3.1 | backend | XS | Click aggregate queries by shop, product and range
  - T1.3.2 | frontend | S | Admin clicks page
  - T1.3.3 | test | XS | Role check and counts

### E2 Admin access and moderation

Priority: P0. Covers mvp.md § Admin area (accounts, login, approve or disable, hide), § Visibility. Outcome: the three team members sign in with password and authenticator code, and from the server-protected admin area control what the public sees.

#### S2.1 Admin signs in with email and password
- As an admin, I sign in with email and password and reach the admin area; no one else can reach any admin route or action.
- Size: L · Priority: P0 · Story file: yes (security-critical, new tables, new command, three lanes)
- Depends on: none
- Slice: 11
- Acceptance outline:
  - Accounts exist only if created by a command; there is no sign-up route.
  - Session is an HttpOnly cookie set for admins only; public pages still set none.
  - Every admin route and action checks the role on the server and refuses an anonymous request (guardrail 3).
  - Passwords are stored hashed; emails, passwords and tokens never reach logs (guardrail 5).
  - Admin pages are marked noindex; the guardrail-3 tests deferred from slice A land here.
  - OD1 (approach) and OD8 (admin language) are settled before design.
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
- Size: M · Priority: P0 · Story file: no (extends the S2.1 contract)
- Depends on: S2.1
- Slice: 12
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
- Size: S · Priority: P0 · Story file: no
- Depends on: S2.2
- Slice: 13
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
- Size: M · Priority: P0 · Story file: no
- Depends on: S2.2
- Slice: 14
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

Priority: P0. Covers mvp.md § Shops and feeds are data, § Feed import, § Data sources. Outcome: the admin enters real networks, shops and feeds as data, imports them from a button or the command in real network formats, reads stored reports, and stale offers disappear without any page vanishing.

#### S3.1 Admin manages networks, shops and feeds
- As an admin, I add a network, a shop and a feed without a code change, and a new feed starts unapproved.
- Size: M · Priority: P0 · Story file: no (logo, link pattern and format arrive in S8.2, S3.6, S3.5)
- Depends on: S2.2
- Slice: 15
- Acceptance outline:
  - Create, edit and list networks, shops and feeds, with validation (https URL, network required for an affiliate feed).
  - A shop with offers cannot be deleted, only disabled.
  - A feed URL is shown masked in lists and never logged (it may hold an API key). Encryption at rest is S10.3 and lands before the first real feed (OD11).
  - Seeded demo rows remain and stay marked as demo.
- Tickets:
  - T3.1.1 | backend | M | Create and edit actions for networks, shops and feeds
  - T3.1.2 | frontend | M | Forms and lists with masked feed URL
  - T3.1.3 | test | S | Role checks, validation, URL never in logs

#### S3.2 Admin runs imports and reads their reports
- As an admin, I press "Import now" for one feed or all feeds and read what happened.
- Size: L · Priority: P0 · Story file: yes (new table, execution model, three lanes)
- Depends on: S2.3, S3.1
- Slice: 17
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
- Size: M · Priority: P0 · Story file: no
- Depends on: S3.2, S8.4
- Slice: 24
- Acceptance outline:
  - After a successful import, a feed's offers absent from the file stop being public.
  - A failed, empty or suspiciously small import removes nothing and is flagged in the report.
  - The stored report (S3.2) shows the removed count.
  - An offer that returns is restored; an admin's hide is never undone.
  - A product that loses its last offer here keeps its page (S8.4 ships first, so removal never causes a 404 on an indexed page).
- Tickets:
  - T3.3.1 | backend | M | Removal pass in the per-feed transaction with the safeguards above
  - T3.3.2 | test | M | Removal, safeguard, return and hide-preservation cases, and the page-stays case

#### S3.4 Import XML and compressed feeds safely
- As the owner, I can import the formats real networks serve: CSV or XML, plain or gzip, over https.
- Size: L · Priority: P0 · Story file: no (shape fixed by decision 0007 and the canonical layout; OD7 covers the parser dependency)
- Depends on: none
- Slice: 18
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
- Size: L · Priority: P0 · Story file: yes (changes the feed contract, importer and admin UI)
- Depends on: S3.1, S3.4
- Slice: 19
- Acceptance outline:
  - Each feed has a format and an admin-editable field mapping instead of the single canonical layout.
  - Price parsing handles the network's decimal and currency conventions, and whether the price includes IVA is recorded and checked per network (guardrail 4).
  - A wrong mapping rejects rows with clear codes and never publishes partial garbage.
  - The demo feeds keep working; real fixtures per network are added when samples exist (O6).
  - Optional fields (description, attributes, fitment text) are added to the same editor by S8.6.
- Tickets:
  - T3.5.1 | backend | M | Feed format and mapping storage, importer applies it
  - T3.5.2 | backend | S | Price and IVA handling per feed
  - T3.5.3 | frontend | M | Mapping editor with a preview of the first rows
  - T3.5.4 | test | M | Mapping tests with per-network fixtures
  - T3.5.5 | docs | XS | Record each network's IVA and field findings

#### S3.6 Affiliate link pattern per shop
- As the owner, I record a shop's affiliate link pattern so outgoing links carry our tracking when the feed's own link does not.
- Size: M · Priority: P0 · Story file: no
- Depends on: S1.1, S3.1
- Slice: 16
- Acceptance outline:
  - A shop or feed can hold an optional link pattern, managed in admin.
  - The redirect builds the destination from the pattern and the offer URL, and uses the feed's own URL when no pattern exists.
  - The destination is built only from stored data, never from the request, so it cannot be an open redirect.
  - On the path to S9.4 because that story requires tracked outgoing links. Sample feeds (O6) show which networks already carry tracked links; where they all do, the pattern may simply stay empty.
- Tickets:
  - T3.6.1 | backend | M | Pattern storage and destination builder in the redirect
  - T3.6.2 | frontend | S | Pattern field in the feed form
  - T3.6.3 | test | S | Pattern, fallback and open-redirect cases

### E4 Categories

Priority: P0. Covers mvp.md § Catalogue scope (the category tree and feed-category mapping). Outcome: the admin defines the fixed tree of about 30 categories and maps each feed category once; products from unmapped feed categories are not public until mapped (D-1/OD3).

#### S4.1 Admin maintains the category tree
- As an admin, I create, rename, reorder and remove categories without a code change.
- Size: M · Priority: P0 · Story file: no
- Depends on: S2.2
- Slice: 20
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
- As an admin, I map each category a feed uses to one of ours once, and products from unmapped feed categories wait in a queue, not public, until I do.
- Size: M · Priority: P0 · Story file: no (S5.1's story file fixes the model)
- Depends on: S4.1, S5.1
- Slice: 21
- Acceptance outline:
  - Lists each feed's distinct categories with product counts and current mapping.
  - A mapping applies to existing and future products of that feed category.
  - The unmapped queue lists categories with waiting products; those products are not public (D-1/OD3, ruled).
  - Changing a mapping moves the products.
- Tickets:
  - T4.2.1 | backend | M | Mapping edit actions that re-apply to existing products
  - T4.2.2 | frontend | M | Mapping screen and unmapped queue
  - T4.2.3 | test | S | Mapping applies, queue behaviour, role checks

### E5 Browse and search

Priority: P0. Covers mvp.md § Search and browsing, § Catalogue scope (categories). Outcome: a visitor reaches products from the home page, a category with filters, or free-text search that also matches EAN and part numbers. Browsing (S5.1, S5.2) is P0; search and filters follow go-live as P1.

#### S5.1 Visitor browses products in a category
- As a visitor, I open a category and see its products with the lowest price and shop count, and open one.
- Size: L · Priority: P0 · Story file: yes (adds a product-category link and a mapping table, changes the visibility contract and the importer). Weak on Small; accepted since the model change has no visible value without the page.
- Depends on: none
- Slice: 2
- Acceptance outline:
  - A server-rendered, paginated category page includes the products of its subcategories.
  - Lists only public products. A product whose feed category has no mapping is not public until mapped (D-1/OD3, ruled); the visibility rule is applied in the one shared visibility scope, not per page.
  - Each card shows title, brand, lowest visible price, shop count and links to the product page.
  - The importer records the feed's category per product; the demo seed and demo feeds supply categories and mappings.
  - Empty category shows an empty state; unknown category answers 404.
- Tickets:
  - T5.1.1 | backend | M | Product-category link and feed-category mapping tables; importer captures and assigns
  - T5.1.2 | backend | S | Visibility rule: products without a mapped category are not public
  - T5.1.3 | backend | M | Category listing read function - lowest price, shop count, subtree, pagination
  - T5.1.4 | backend | S | Demo seed and demo feeds carry categories
  - T5.1.5 | frontend | M | Category page and product card with es-ES copy
  - T5.1.6 | test | M | Visibility, listing and e2e tests

#### S5.2 Home page shows the category tree
- As a visitor, I open the site and see the categories I can browse.
- Size: S · Priority: P0 · Story file: no
- Depends on: S5.1
- Slice: 3
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
- Size: M · Priority: P1 · Story file: no
- Depends on: S5.1
- Slice: 31
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
- Size: L · Priority: P1 · Story file: yes (relevance rules and new indexes; decision 0002 fixes only the engine)
- Depends on: none
- Slice: 30
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

Priority: P0. Covers mvp.md § Search and browsing (structured data), § Goal (10k products indexed). Outcome: Google can discover every public product and category and show prices in results, while demo products stay out of its index.

#### S6.1 Product pages carry structured price data
- As a searcher on Google, I see the price and number of shops in the result.
- Size: S · Priority: P0 · Story file: no
- Depends on: none
- Slice: 4
- Acceptance outline:
  - JSON-LD Product with AggregateOffer (low price, high price, offer count, currency EUR) in the server-rendered HTML.
  - Built from visible offers only. With no visible offer the JSON-LD is omitted entirely; this is the single rule, and it also covers a page S8.4 keeps after its offers disappear. No Offer is ever built from a last known price.
  - Prices formatted from integer cents without floating-point (guardrail 4).
  - Owner spot-checks it in a schema validator.
- Tickets:
  - T6.1.1 | frontend | S | JSON-LD component on the product page, omitted when there is no visible offer
  - T6.1.2 | test | S | Cents-to-string unit tests; e2e parses the JSON-LD; absent when there is no offer

#### S6.2 Sitemap, robots rules and canonical URLs
- As a search engine, I can discover and index every public product and category and nothing else.
- Size: M · Priority: P0 · Story file: no
- Depends on: S5.1
- Slice: 5
- Acceptance outline:
  - A chunked sitemap lists only public products and categories; hidden, unmapped and unapproved items are excluded (guardrail 1). It uses the shared visibility scope, so a page S8.4 keeps stays listed.
  - Demo products (no offer from a non-demo feed) carry noindex and are left out of the sitemap (D-1/OD2).
  - robots rules allow public pages and disallow admin, the redirect `/go` and search results.
  - Product, category and filtered pages carry a canonical URL; the public site URL is configuration.
  - Generation stays fast with 10,000 products.
- Tickets:
  - T6.2.1 | backend | M | Sitemap generation queries with chunking
  - T6.2.2 | frontend | S | robots, canonical and noindex metadata
  - T6.2.3 | test | S | Hidden and unmapped items absent; robots rules
  - T6.2.4 | backend | S | Demo products noindex and out of the sitemap - a product with no offer from a non-demo feed (NEW)

### E7 Matching and review

Priority: P0. Covers mvp.md § Matching, decision 0008. Outcome: offers from different feeds land under one product by EAN or brand and part number; conflicts wait for an admin, who can also merge, split and keep brand aliases. Matching and the review queue (S7.1, S7.2) are P0 because they must exist before the first real feed; aliases, merge and split follow as P1.

#### S7.1 Match offers by brand and part number
- As a visitor, I see one product page for a part even when a shop's feed has no EAN.
- Size: M · Priority: P0 · Story file: no
- Depends on: none
- Slice: 25
- Acceptance outline:
  - Step 2 of decision 0008: same normalised brand and part number attaches; both must be present.
  - The lookup is indexed; EAN-first order is unchanged.
  - Rows without EAN from two shops converge on one product (closes TD-25).
  - Brands compare after normalisation only; aliases arrive with S7.3.
  - A brand and part number hit whose EAN disagrees keeps today's rejection until the review queue exists (S7.2, next slice).
  - Sequenced after S3.5 so the tests can use real column layouts; the code itself needs only the stored normalised fields.
- Tickets:
  - T7.1.1 | backend | M | Matching step 2 and index migration
  - T7.1.2 | test | S | Matching table tests and importer integration

#### S7.2 Conflicting offers wait in an admin review queue
- As an admin, I resolve offers whose EAN and brand disagree, or whose EAN and part number point at different products, instead of the system guessing.
- Size: L · Priority: P0 · Story file: yes (stored decisions, importer behaviour change, may replace the offer-level review flag)
- Depends on: S2.2, S7.1, S8.4
- Slice: 26
- Acceptance outline:
  - Both conflict cases in decision 0008 put the offer in a queue and off the public site (guardrail 1) instead of rejecting it.
  - A queued offer is never visible, including on a product page that S8.4 keeps.
  - The queue shows the offer beside its candidate product or products.
  - The admin attaches to one candidate, creates a new product, or discards; the decision is stored and re-applied on the next import.
  - The import report counts queued offers. Until aliases exist (S7.3) brand spelling differences land here as false conflicts; the count shows how many.
- Tickets:
  - T7.2.1 | backend | M | Queue storage; importer routes conflicts to it
  - T7.2.2 | backend | M | Resolve actions and stored decisions re-applied on import
  - T7.2.3 | frontend | M | Review queue screen
  - T7.2.4 | test | M | Both conflict cases, re-import stickiness, guardrail 1, queued offer on a kept page

#### S7.3 Admin maintains brand aliases
- As an admin, I declare that two brand spellings are the same brand (for example BOSCH and Robert Bosch) so matching treats them alike.
- Size: M · Priority: P1 · Story file: no
- Depends on: S2.2, S7.1
- Slice: 29
- Acceptance outline:
  - Add and remove alias groups in admin.
  - Matching maps brands through the aliases before comparing.
  - Effect applies from the next import; design states what happens to already-created products.
  - Done before a second real feed is approved; the first feed alone cannot show cross-feed spelling differences.
- Tickets:
  - T7.3.1 | backend | M | Alias storage and use in the matcher
  - T7.3.2 | frontend | S | Alias screen
  - T7.3.3 | test | S | Alias matching and role checks

#### S7.4 Admin merges two products
- As an admin, I merge a duplicate product into another so its shops sit under one page and the old link still works.
- Size: L · Priority: P1 · Story file: yes (new decision store, redirect semantics, affects search and sitemap)
- Depends on: S2.4, S7.2
- Slice: 35
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
- Size: M · Priority: P1 · Story file: no
- Depends on: S7.4
- Slice: 37
- Acceptance outline:
  - Select offers on a product; they become a new product with its own URL.
  - The split is stored and re-applied on the next import.
  - Role-checked.
- Tickets:
  - T7.5.1 | backend | M | Split action and stored decision
  - T7.5.2 | frontend | S | Split screen
  - T7.5.3 | test | S | Split and re-import stickiness

### E8 Product page depth

Priority: P0. Covers mvp.md § Product and offers (images, price history, no-offers state, text ranking, attributes), § Shops and feeds are data (logo). Outcome: the product page has an image or category placeholder, a price history chart, survives losing all offers, shows the feed's attributes and fitment text, and takes its text from the admin's highest-ranked shop. Price history and the no-offers rule (S8.3, S8.4) are P0; the rest follows go-live.

#### S8.1 Admin uploads product images; categories have placeholders
- As an admin, I upload an image for a product; until then visitors see its category's placeholder.
- Size: L · Priority: P1 · Story file: yes (storage volume, upload security, three lanes)
- Depends on: S2.2
- Slice: 34
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
- Size: S · Priority: P2 · Story file: no
- Depends on: S3.1, S8.1
- Slice: 38
- Acceptance outline:
  - Admin uploads a logo on the shop form, through the same storage.
  - Offer rows show the logo, and the shop name when there is none.
- Tickets:
  - T8.2.1 | backend | S | Logo field and upload through the storage interface
  - T8.2.2 | frontend | S | Logo on offer rows and in the shop form
  - T8.2.3 | test | XS | Logo upload and fallback

#### S8.3 Price history chart
- As a visitor, I see how a product's lowest price moved over time.
- Size: L · Priority: P0 · Story file: yes (new table, changes the product page contract)
- Depends on: none
- Slice: 22
- Acceptance outline:
  - One point per day per product (Madrid calendar day): the lowest visible offer price any import saw that day, written by the import (mvp.md).
  - Running the same import twice in a day never adds a second point.
  - Imports are manual, so days without an import have no point. Nothing is stored, carried forward or interpolated for them (finding 7).
  - The chart is drawn from cents on a true date axis with no third-party scripts (OD7). A gap between recorded days shows as a gap, and a caption says prices are recorded when the catalogue is updated. Fewer than two points shows text instead.
  - History starts before the first real feed (S9.4 depends on this story) because it cannot be backfilled. It also supplies S8.4's last known price.
  - No personal data is involved.
- Tickets:
  - T8.3.1 | backend | M | Price history storage and recording after import
  - T8.3.2 | backend | S | History in the product page read function
  - T8.3.3 | frontend | M | Chart component with gaps shown as gaps, caption and copy
  - T8.3.4 | test | M | Recording idempotency, day minimum, gap rendering, page rendering

#### S8.4 Product page stays when offers disappear
- As a visitor, a product I found on Google keeps its page when no shop lists it, and says so with the last known lowest price.
- Size: M · Priority: P0 · Story file: yes (reverses TD-31 and the visibility contract; OD4)
- Depends on: S8.3
- Slice: 23
- Acceptance outline:
  - A product that has been public keeps its page, text, image and history while it has no visible offers.
  - The offer area says there are no offers right now and shows the last known lowest price and its date (from S8.3 history).
  - A product that was never public stays hidden; an admin-hidden product stays hidden; unmapped products (D-1/OD3) stay non-public; offers in review never show.
  - Demo products, those with no offer from a non-demo feed, are not kept: they stop being public when their demo feed is disabled (D-1/OD2).
  - The page stays in the sitemap while public. JSON-LD stays omitted while there are no offers (the S6.1 rule).
  - Whether the page stays when an admin disabled the feed is OD4; its answer is needed before design.
- Tickets:
  - T8.4.1 | backend | M | Visibility rule for previously public products with the demo exception; last-known-price read
  - T8.4.2 | frontend | S | No-offers state
  - T8.4.3 | test | M | Rewrite the guardrail 1 visibility tests for the new rule; demo exception; no JSON-LD without offers
  - T8.4.4 | docs | XS | Record the decision that supersedes TD-31, and the JSON-LD rule

#### S8.5 Admin ranks shops for product text
- As an admin, I rank shops so the best source's wording wins when feeds disagree about a product's text.
- Size: M · Priority: P1 · Story file: no
- Depends on: S2.2, S8.6
- Slice: 36
- Acceptance outline:
  - Each shop has an admin-editable rank.
  - A product's title, brand, description, attributes and fitment text come from its highest-ranked shop's offer, recalculated on import and on rank change.
  - Identity fields (EAN, part number) are not rewritten by the ranking.
  - Replaces today's first-import-wins text.
- Tickets:
  - T8.5.1 | backend | M | Rank storage and text selection on import and rank change
  - T8.5.2 | frontend | S | Ranking screen
  - T8.5.3 | test | S | Text precedence cases

#### S8.6 Product page shows feed attributes and supplier fitment text
- As a visitor, I see a part's specifications and, where the shop's feed gives one, its fitment note as plain text on the product page.
- Size: M · Priority: P1 · Story file: yes (extends the feed mapping, the importer and the PublicProductPage contract)
- Depends on: S3.5
- Slice: 33
- Acceptance outline:
  - The admin maps three optional feed fields in the S3.5 editor: description, attributes (name and value pairs) and fitment text.
  - The importer stores them on the product; products created before this story are filled on re-import. Until S8.5 ranks shops, the first source wins as for other text.
  - The product page shows the description, an attributes list and the fitment text as plain text labelled as the shop's note; absent fields show no empty heading.
  - No vehicle model, no fitment search, filter or match (mvp.md): the fitment text is text and nothing more, and search does not use it.
  - Feed text is untrusted: it is rendered escaped, markup is not interpreted, and length is capped.
- Tickets:
  - T8.6.1 | backend | M | Optional description, attributes and fitment-text fields in the feed mapping; importer stores them and fills existing products (NEW)
  - T8.6.2 | backend | S | Attributes and fitment text in the product page read function (NEW)
  - T8.6.3 | frontend | M | Attributes list and fitment note on the product page, escaped, with es-ES copy (NEW)
  - T8.6.4 | frontend | S | Mapping editor fields for the three optional columns (NEW)
  - T8.6.5 | test | M | Mapping, escaping of markup in feed text, no fitment filter or search, re-import fills existing products (NEW)

### E9 Go live

Priority: P0. Covers mvp.md § Delivery, § Goal (site live, at least 3 approved feeds), § Data sources (first shops), decisions 0004 and 0007, and the legal pages added by D-1/OD5. Outcome: the site runs on an EU VPS with a domain and its legal pages so networks can review it, real feeds go live, and data is backed up.

#### S9.1 Site is live on an EU VPS over HTTPS
- As a network reviewer, I open the domain and see the working site; as the owner, I redeploy by a documented procedure.
- Size: L · Priority: P0 · Story file: yes (ops, Compose, docs; records hosting decisions)
- Depends on: S1.1, S1.2, S5.2, S6.1, S6.2, S9.3, S10.2
- Slice: 9
- Acceptance outline:
  - Production Compose setup: app behind a reverse proxy with TLS on the domain; the database and Umami are not reachable from the internet.
  - No visitor IP address or user agent in any server log (guardrail 5): the proxy access log is off or omits the client address, the app writes none, and the container log driver keeps no request lines with one. A post-deploy check makes a request from a known address and finds it in none of the logs.
  - No secret in git. Demo data is on (D-1/OD2): the live site shows the demo catalogue during network review, with demo products noindex and out of the sitemap (S6.2), demo `/go` clicks not counted (S1.1), and demo feeds disabled at S9.4. A visible demo notice is OD10.
  - A written deploy and rollback procedure that has been run once.
  - Dependency audit with dev packages omitted is clean at deploy time (carried risk, dev-only advisories accepted).
  - A smoke check covers home, a product page, health, no cookie on public pages, no admin route open before S2.2 is deployed, and no client address in the logs.
- Tickets:
  - T9.1.1 | ops | S | Provision the VPS, DNS and firewall (owner, per runbook)
  - T9.1.2 | backend | M | Production Compose overrides, reverse proxy and TLS, with the proxy set to log no client address
  - T9.1.3 | backend | S | Production environment template, secrets handling and Umami login hardening
  - T9.1.4 | docs | S | Deploy and rollback runbook, plus decision record for hosting
  - T9.1.5 | ops | S | First deploy and smoke run
  - T9.1.6 | test | S | Post-deploy smoke script
  - T9.1.7 | test | S | Log check - a request from a known address leaves no client address or user agent in proxy, app or container logs (NEW)

#### S9.2 Database and uploads are backed up and restorable
- As the owner, I can restore the site's data after losing the server.
- Size: M · Priority: P0 · Story file: no
- Depends on: S9.1
- Slice: 10
- Acceptance outline:
  - Daily dumps of the app and Umami databases are copied off the server, encrypted, with a retention period.
  - In place before the owner starts entering the category tree and mappings in production, since those are not reproducible from feeds.
  - The image volume is included once S8.1 exists.
  - A restore has been rehearsed on a scratch machine.
  - Backups hold admin password hashes, so their storage is private.
- Tickets:
  - T9.2.1 | ops | S | Backup job and off-server copy with retention
  - T9.2.2 | docs | S | Restore runbook
  - T9.2.3 | ops | S | Restore rehearsal

#### S9.3 Legal and affiliate disclosure pages
- As a visitor, I can read who runs the site, how data is handled, and that outgoing links earn a commission.
- Size: S · Priority: P0 · Story file: no. In scope by D-1/OD5 (LSSI-CE); off HOLD. Starts when the owner hands over the text (O4); no placeholder text goes live.
- Depends on: none
- Slice: 8
- Acceptance outline:
  - Legal notice, privacy policy and affiliate disclosure pages, linked from the footer of every page.
  - The privacy text states that no cookies are set for visitors, what the click log holds, that server logs keep no addresses (S9.1) and what Umami measures; admin sessions use a cookie for admins only.
  - Text is supplied by the owner in Spanish and kept in message files; no cookie banner (decision 0009).
- Tickets:
  - T9.3.1 | frontend | S | Static pages and footer links, owner-supplied text from message files
  - T9.3.2 | test | XS | Pages render and the footer links to them

#### S9.4 First real affiliate feed goes live
- As the owner, I approve a real shop's feed and its products appear on the live site with working outgoing links.
- Size: M · Priority: P0 · Story file: no (a checklist run; new defects found become new tickets)
- Depends on: S2.3, S2.4, S3.2, S3.3, S3.5, S3.6, S4.2, S7.1, S7.2, S8.3, S8.4, S9.1, S9.2, S10.3
- Slice: 28
- Acceptance outline:
  - The shop and feed are entered in admin (the URL is stored encrypted, S10.3) and stay unapproved until the import report is reviewed.
  - IVA-inclusive pricing is confirmed against the shop for this network (guardrail 4).
  - Categories are mapped and the unmapped queue cleared (unmapped products are not public, D-1/OD3); the review queue from the first import is read.
  - The demo feeds are disabled on the live site and the demo products stop being public (S8.4 demo rule, D-1/OD2).
  - One product is checked end to end, including that the redirect reaches the shop with tracking (the feed's own link or the S3.6 pattern) and that the first price-history point exists.
  - Repeat per feed until three feeds are approved; the second feed is not approved before S7.3 is done.
- Tickets:
  - T9.4.1 | ops | S | Enter the shop and feed, import, review the report, disable demo feeds (owner)
  - T9.4.2 | ops | S | Check price, IVA and tracking on sample products against the shop (owner)

### E10 Hardening and carried findings

Priority: P0 (S10.2 and S10.3 are P0; S10.1 is P1). Covers mvp.md § Goal (10k products), the carried rows from the two closed runs. Outcome: the copy is reviewed before the site is public, feed URLs holding API keys are protected before real keys arrive, pages stay fast at target size, and open findings from slices A and B are closed or consciously kept.

#### S10.1 Catalogue pages stay fast at 10,000 products
- As a visitor and as Googlebot, I get fast responses at the target catalogue size.
- Size: M · Priority: P1 · Story file: no
- Depends on: S5.3, S5.4, S6.2
- Slice: 32
- Acceptance outline:
  - A reproducible generated dataset of 10,000 products and about 30,000 offers (generated, never scraped).
  - Product, category, search and sitemap meet response-time targets fixed at design.
  - Indexes are added where query plans show scans; findings recorded.
- Tickets:
  - T10.1.1 | test | S | Synthetic 10k dataset generator and timing check
  - T10.1.2 | backend | M | Index and query tuning from the findings

#### S10.2 Close carried findings from slices A and B
- As the owner, the findings carried out of the first two runs are fixed or consciously closed.
- Size: S · Priority: P0 · Story file: no. P0 reason: S9.1 depends on it, since the Spanish copy must be reviewed before the site is public.
- Depends on: none
- Slice: 7
- Acceptance outline:
  - The e2e setup's failure branches are covered by a test (finding F-3).
  - The owner has reviewed the Spanish copy (O5) and the corrections are applied.
  - CLAUDE.md § Stack lists npm and Node 22, if the owner agrees.
- Tickets:
  - T10.2.1 | test | S | Cover the e2e global-setup failure branches
  - T10.2.2 | frontend | XS | Apply the owner's es-ES copy corrections
  - T10.2.3 | docs | XS | Add the npm and Node 22 line to CLAUDE.md § Stack (owner's call)

#### S10.3 Feed URLs holding API keys are encrypted at rest
- As the owner, a database dump does not expose network API keys.
- Size: S · Priority: P0 · Story file: no. Placement provisional on OD11: if the owner rules "after go-live", this story moves behind S9.4, becomes P1, and S9.4 drops the dependency.
- Depends on: S3.1
- Slice: 27
- Acceptance outline:
  - Feed URLs are stored encrypted with a key held in configuration, and decrypted only inside the importer.
  - Existing rows (demo URLs only at this point) are converted by the migration.
  - Backups and logs show no plaintext URL.
  - The key is kept apart from database backups and its custody is in the runbook; losing it means re-entering the feed URLs (owner task O13).
- Tickets:
  - T10.3.1 | backend | S | Encrypt and decrypt feed URLs; migrate existing rows
  - T10.3.2 | test | XS | Round trip and no plaintext in dumps or logs
  - T10.3.3 | docs | XS | Runbook lines - key custody, production environment template entry and loss recovery (NEW)

## Sequence

Build order, one story per slice. Branch and run per slice as before. P0 = sequenced at or before S9.4; no P0 story follows slice 28. Stories after the site goes live (slice 9) that are P0 carry a reason after "P0:".

Phase A, a reviewable live site (no admin yet; demo data, noindex):
1. S1.1 Visitor goes to a shop through a logged redirect. First to run: small, independent, completes the core loop's last step, lands the deferred guardrail-5 test and the click counting rules.
2. S5.1 Visitor browses products in a category (fixes the category data model and the unmapped rule, D-1/OD3).
3. S5.2 Home page shows the category tree.
4. S6.1 Product pages carry structured price data.
5. S6.2 Sitemap, robots rules and canonical URLs (demo noindex, D-1/OD2).
6. S1.2 Umami tracker on public pages.
7. S10.2 Close carried findings from slices A and B (copy review lands before the site is public).
8. S9.3 Legal and affiliate disclosure pages (needs the owner's text, O4).
9. S9.1 Site is live on an EU VPS over HTTPS. Milestone M1: owner applies to the networks (O2). Network approval is an external wait of unknown length that overlaps slices 10-27.

Phase B, admin, import machinery and the safeguards real data needs, while networks review:
10. S9.2 Database and uploads are backed up and restorable. P0: backups must exist before production admin data entry starts and before real data (S9.4 depends on it).
11. S2.1 Admin signs in with email and password. P0: every admin story needs the guard.
12. S2.2 Admin sign-in requires an authenticator code (no admin route is deployed before this). P0: gate for all admin stories.
13. S2.3 Admin approves and disables shops and feeds. P0: S9.4 approves the first feed through it.
14. S2.4 Admin hides and unhides products and offers. P0: the first imports must be moderated before approval (S9.4 depends on it).
15. S3.1 Admin manages networks, shops and feeds. P0: S9.4 enters the real shop and feed through it.
16. S3.6 Affiliate link pattern per shop. P0: S9.4 requires tracked outgoing links.
17. S3.2 Admin runs imports and reads their reports. P0: S9.4 reviews the import report before approving.
18. S3.4 Import XML and compressed feeds safely. P0: real feeds arrive as XML or gzip.
19. S3.5 Per-feed field mapping for network feed layouts. P0: real feeds arrive in network column layouts.
20. S4.1 Admin maintains the category tree. P0: unmapped products are not public.
21. S4.2 Admin maps feed categories and clears the unmapped queue. P0: no real product is public until its category is mapped.
22. S8.3 Price history chart. P0: history cannot be backfilled, so it starts before the first real feed.
23. S8.4 Product page stays when offers disappear. P0: indexed pages must not 404 after removal; needs OD4.
24. S3.3 Offers missing from the latest import are removed. P0: stale offers must disappear on real feeds; ships after S8.4 so removal never 404s a page.
25. S7.1 Match offers by brand and part number. P0: real feeds must not create duplicate products.
26. S7.2 Conflicting offers wait in an admin review queue. P0: conflicts must queue, not reject or merge, on real data.
27. S10.3 Feed URLs holding API keys are encrypted at rest. P0 (provisional on OD11): no plaintext key should ever reach production.
28. S9.4 First real affiliate feed goes live. Milestone M2. Blocked on network approval (O2, O12) and a real sample feed (O6).

Phase C, MVP completeness after the first real feed (P1, then P2):
29. S7.3 Admin maintains brand aliases. First after go-live; must precede approval of a second real feed.
30. S5.4 Visitor searches by text, EAN or part number.
31. S5.3 Visitor filters a category by brand, price and shop.
32. S10.1 Catalogue pages stay fast at 10,000 products (after search, filters and sitemap exist; dataset is generated).
33. S8.6 Product page shows feed attributes and supplier fitment text.
34. S8.1 Admin uploads product images; categories have placeholders.
35. S7.4 Admin merges two products.
36. S8.5 Admin ranks shops for product text.
37. S7.5 Admin splits offers off a product.
38. S8.2 Shop logos on offers.
39. S1.3 Admin sees click counts per shop and product.
Milestone M3 is owner-tracked: three feeds approved, 10k products indexed, first clicks, first commission.

Critical path to S9.4 (first real feed): every story in slices 1-28 is in S9.4's dependency closure, so none is off the path. The longest hard chain is S2.1, S2.2, S2.3, S3.2, S3.3 (with S8.3, S8.4 in front of S3.3) and then S9.4. External wait: network approval (O2, O12). Search (30) and filters (31) are not needed to be live with real feeds but are needed for the MVP done-definition.

Reasons for the edges:
- Slice 1 first: independent, small, and every later offer-facing slice then renders the link.
- Slices 2 and 3 before 9: networks only approve a site they can visit (0007); a visitor needs somewhere to go, and the sitemap needs category URLs.
- Slices 1, 3, 4, 5, 6, 7 and 8 before 9: S9.1 depends on each of them, so the go-live site is complete and reviewable.
- 10 straight after 9: it needs only a live server, and the owner's admin data entry (categories, mappings) is not reproducible from feeds.
- 11 before 12-15, 17, 20 and 26: every admin action needs the guard. 12 before any admin deploy.
- 13 and 15 before 17: Import now needs approved feeds that exist as rows. 15 before 16 and 27: both extend the feed form.
- 18 and 19 before 28: real feeds arrive as XML or gzip and in network column layouts.
- 20 and 21 before 28: real products arrive in feed categories nobody has mapped, and unmapped products are not public (D-1/OD3).
- 22 before 23 before 24 before 28: S8.4 reads its last known price from history (S8.3), and removal (S3.3) must not ship before the rule that keeps the page. S9.4 lists S8.3, S8.4 and S3.3 directly.
- 25 before 26: the queue and aliases refine the brand and part number step. 26 after 23: a queued offer must stay non-public on a kept page.
- 27 before 28 (provisional on OD11): real keys are first entered at S9.4.
- 29 after 28 and before a second feed: aliases are only needed once feeds disagree on brand spelling.
- 33 after 19: S8.6 extends the S3.5 mapping editor. 36 after 33: the ranking covers the S8.6 fields.
- 35 after 26 and 14: merge reuses the decision store and the hide controls. 37 after 35. 38 after 34 and 15.
- 39 after 1 and 12: it reads the click table behind the admin guard.

## Owner tasks

Owner work. Not code, not sized, never agent work. Each names the stories it blocks.

- O1 | owner work | blocks: S9.1 (T9.1.1, T9.1.5) | Choose a VPS provider and buy a domain; point DNS. Before slice 9. Recorded as a decision when done (decision 0004, OD6).
- O2 | owner work | blocks: S9.4 (external wait) | Register publisher accounts and apply to the five first shops (Awin: Leroy Merlin, ManoMano, Brico Depot; Kwanko: Oscaro; Effinity: Norauto) once the site is live. After slice 9. Approval time is unknown.
- O3 | owner work | blocks: S4.1 (real tree), S4.2, S9.4 | Write the list of about 30 categories (names and hierarchy, Spanish). Before slice 20.
- O4 | owner work | blocks: S9.3, and so S9.1 | Supply the Spanish legal text (legal notice, privacy policy, affiliate disclosure), and decide with a gestor when to register as autónomo or use a company; the legal notice may need the owner's identity before launch. Before slice 8 (D-1/OD5).
- O5 | owner work | blocks: S10.2 (T10.2.2), and so S9.1 | Review the Spanish copy in the message files. Before slice 9 (carried finding).
- O6 | owner work | blocks: S3.4 and S3.5 fixtures, S3.6 (tracked links?), S8.6 (attribute columns), S7.3 (brand spelling), S9.4 | Obtain a sample feed and format documentation from each network after the publisher account exists. Before slice 18 for realistic fixtures; slice 19 needs it.
- O7 | owner work | blocks: first use of any admin story on the live site (S2.3 onward) | Run the create-admin command for the three members and store their authenticator secrets safely. After slice 12.
- O8 | owner work | blocks: nothing in code; M3 | Verify the domain in Google Search Console after slice 9. Submit the sitemap after slice 28, since until then it holds no public product (demo products are excluded, D-1/OD2).
- O9 | owner work | blocks: nothing in code; first payout | Register as payee with a network when it asks (decision 0007).
- O10 | owner work | blocks: S1.2 (T1.2.4), S9.1 (T9.1.3) | Create the Umami website and change its default login. With slice 6 locally and slice 9 live.
- O11 | owner work | blocks: nothing in code; M3 | Track the done-definition: three approved feeds, 10k products indexed, first clicks, first commission.
- O12 | owner work | blocks: S9.4 (via O2); informs OD10 | Ask each network's publisher support what a site must show to be reviewed: demo content, legal pages, minimum traffic. Before O2. (New; the unverified claim in D-1/OD2.)
- O13 | owner work | blocks: S10.3, S9.2 | Choose where the feed-URL encryption key and the backup passphrase are kept, apart from the server and from the backups. Before slice 10. (New.)

## Open decisions

Rulings first, then the questions still open. Each open one has my recommendation and names the stories it blocks. None blocks the board update; D-2 requires the human to approve this brief before any board write.

Ruled by D-1 (2026-10-17), applied in this revision:
- OD2 ruled: the demo catalogue may be live during network review; demo products are noindex and out of the sitemap; demo `/go` clicks are not counted. Applied in S1.1, S6.2 (with T6.2.4), S8.4, S9.1, S9.4. Still unverified: whether networks accept it (O12).
- OD3 ruled: products from unmapped feed categories are not public until mapped. Applied in S5.1 (and T5.1.2), S4.2, S8.4, S9.4. mvp.md needs a matching edit (§ mvp.md amendment).
- OD5 ruled: legal notice, privacy and affiliate disclosure pages are in MVP scope (LSSI-CE); the owner supplies the text (O4). S9.3 is off HOLD, P0, slice 8; S9.1 depends on it.

Open:
- OD1. How should admin authentication be built? Options: a small purpose-built module (Node's built-in password hashing, one maintained TOTP library, server-stored opaque sessions in an HttpOnly cookie) or an off-the-shelf auth framework. Recommendation: the small purpose-built module, since there are three users and no OAuth, and record it as a decision. Needs a new dependency decision (TOTP library). Blocks S2.1 design (slice 11), and through it S2.2-S2.4, S3.x admin stories and S9.4.
- OD4. When a product loses all offers, does its page stay even if the cause was an admin disabling the feed? Today it returns 404 (TD-31), against mvp.md. Recommendation: keep the page in all cases except admin-hidden; price points are only recorded from visible offers, so what is shown was public when recorded. Alternative that avoids showing a price from a feed since disabled: keep the page but hide the last known price in that one case. Blocks S8.4 (slice 23), now on the critical path to S9.4, and so S3.3 and S7.2; decide before slice 21.
- OD6. VPS provider, domain and reverse proxy; who performs server work. Recommendation: the owner performs server tasks following the runbook, since no ops lane exists; use a reverse proxy with automatic TLS (Caddy), recorded as a decision. The proxy must be configured to log no client address (S9.1). Blocks S9.1 (slice 9) and S9.2 (backup destination).
- OD7. New runtime dependencies that each need a decision record: an XML parser (S3.4), a TOTP library (S2.1), image handling (S8.1), a chart approach (S8.3), a crawler-detection list (S1.1). Recommendation: one streaming XML parser; no chart library (server-drawn SVG); validate images but do not process them in the MVP; keep the crawler list as a short pattern list in our own code, no dependency. Each blocks only its own story's design (S3.4, S2.1, S8.1, S8.3, and S1.1 only if a dependency is chosen).
- OD8. Admin interface language. Recommendation: Spanish, in message files under a separate admin section, same rule as the public site. Blocks S2.1 design, trivially.
- OD9. Add a CI workflow so the gate runs on pull requests? There is no `.github`, and the gate needs Docker. Recommendation: defer; the orchestrator already runs the gate before each pull request. Blocks nothing.
- OD10 (new). Does the live demo catalogue carry a visible notice that it is a demonstration? The D-1 ruling on OD2 does not say. Demo product titles already start with "DEMO" and their descriptions say they are fictitious (demo/feeds CSVs, opened), so the open part is category and home pages and the legal text. Recommendation: yes, one short notice on pages that list only demo offers, plus a line in the legal text. Blocks S9.1 (slice 9); if yes it adds one frontend ticket, T9.3.3, to S9.3 (not created until decided).
- OD11 (new). Must feed-URL encryption (S10.3) land before the first real feed? Recommendation: yes. It costs one S story; it means no plaintext API key ever sits in production or in a backup and there is no live conversion. It protects against a leaked dump or an injection read, not a compromised host, since the key sits in server configuration. If the owner says no: S10.3 moves behind S9.4 as P1, S9.4 drops the dependency, and the runbook states that feed URLs are plaintext until then. Blocks the position of S10.3 (slice 27) and the dependency in S9.4 (slice 28).

## Board delta

For the orchestrator, after the human approves (D-2). Existing issues are updated in place; nothing is deleted. Issue numbers come from the prior run's tracker.md § issue-map.

(a) Issues to retitle or close as not planned: none. No story or ticket is removed, merged or renamed. S9.3 loses its HOLD text in the body only.

(b) New issues to create, with parent:
- Story S8.6 "Product page shows feed attributes and supplier fitment text", parent epic E8 (#16). Tickets T8.6.1, T8.6.2, T8.6.3, T8.6.4, T8.6.5, parent S8.6.
- T1.1.5, parent S1.1 (#19).
- T6.2.4, parent S6.2 (#39).
- T9.1.7, parent S9.1 (#50).
- T10.3.3, parent S10.3 (#56).
- Owner tasks O1-O13 (finding 14), each labelled as owner work, linked to the stories in § Owner tasks. O12 and O13 are new; O1-O11 carry changed "blocks" lists.
- Totals after creation: 39 stories, 140 tickets (131 plus 9 new), 10 epics plus E0.

(c) Story issues whose body changed in substance. Every story gets its Slice value (finding 12); the columns show what else changed. "Depends on" is now story IDs only; the orchestrator converts them to #issue references (finding 13).

| Story | Issue | Slice | Priority | Depends on changed | Outline changed |
|---|---|---|---|---|---|
| S1.1 | #19 | 1 | P0 | no | yes: counting rules, plain anchor, demo; T1.1.3, T1.1.4 reworded; T1.1.5 new |
| S5.1 | #34 | 2 | P0 | no (still none; the OD3 note is replaced by the ruling) | yes: ruling text; T5.1.2 reworded |
| S5.2 | #35 | 3 | P0 | no | no |
| S6.1 | #38 | 4 | P0 | no | yes: zero-offer rule; T6.1.1, T6.1.2 reworded |
| S6.2 | #39 | 5 | P0 | no | yes: demo noindex, /go disallowed; T6.2.4 new |
| S1.2 | #20 | 6 | P1 to P0 | no | no |
| S10.2 | #55 | 7 | P2 to P0 | no | yes: P0 reason line |
| S9.3 | #52 | 8 | P0 | no | yes: off HOLD, owner text, privacy content; T9.3.1 reworded |
| S9.1 | #50 | 9 | P0 | yes: adds S1.1, S1.2, S6.1, S10.2 | yes: logs rule, demo on; T9.1.2 reworded; T9.1.7 new |
| S9.2 | #51 | 10 | P1 to P0 | no (S9.1) | yes: before admin data entry |
| S2.1 | #22 | 11 | P0 | no | yes: OD1/OD8 line only |
| S2.2 | #23 | 12 | P0 | no | no |
| S2.3 | #24 | 13 | P0 | no | no |
| S2.4 | #25 | 14 | P0 | no | no |
| S3.1 | #26 | 15 | P0 | no | yes: encryption pointer |
| S3.6 | #31 | 16 | P1 to P0 | no (S1.1, S3.1); now ordered before S9.4 | yes: tracked-link rationale |
| S3.2 | #27 | 17 | P0 | yes: adds S3.1 (S2.3 kept) | no |
| S3.4 | #29 | 18 | P0 | no | no |
| S3.5 | #30 | 19 | P0 | no | yes: pointer to S8.6 |
| S4.1 | #32 | 20 | P0 | no | no |
| S4.2 | #33 | 21 | P0 | no | yes: ruling text |
| S8.3 | #47 | 22 | P1 to P0 | no | yes: gap rule, Madrid day, caption; T8.3.3, T8.3.4 reworded |
| S8.4 | #48 | 23 | P1 to P0 | yes: drops S3.3 | yes: demo exception, JSON-LD omitted, ordering; T8.4.1, T8.4.3, T8.4.4 reworded |
| S3.3 | #28 | 24 | P0 | yes: from none to S3.2, S8.4 | yes: page stays, stored report; T3.3.2 reworded |
| S7.1 | #40 | 25 | P1 to P0 | no | yes: sequencing, aliases note |
| S7.2 | #41 | 26 | P1 to P0 | yes: S2.2 (was S2.1), adds S8.4 | yes: queued offer on a kept page; T7.2.4 reworded |
| S10.3 | #56 | 27 | P2 to P0 | no (S3.1) | yes: key custody, provisional on OD11; T10.3.3 new |
| S9.4 | #53 | 28 | P0 | yes: adds S2.3, S3.2, S3.6, S7.1, S7.2, S8.3, S8.4, S10.3; keeps S2.4, S3.3, S3.5, S4.2, S9.1, S9.2 | yes: encrypted URL, queue, demo disable, history point, second feed gate |
| S7.3 | #42 | 29 | P1 | yes: S2.2 (was S2.1) | yes: gates the second feed |
| S5.4 | #37 | 30 | P0 to P1 | no | no |
| S5.3 | #36 | 31 | P0 to P1 | no | no |
| S10.1 | #54 | 32 | P1 | no | no |
| S8.6 | new | 33 | P1 | new | new |
| S8.1 | #45 | 34 | P1 | yes: S2.2 (was S2.1) | no |
| S7.4 | #43 | 35 | P1 | no | no |
| S8.5 | #49 | 36 | P1 | yes: S2.2 (was S2.1), adds S8.6 | yes: covers attributes and fitment text |
| S7.5 | #44 | 37 | P1 | no | no |
| S8.2 | #46 | 38 | P2 | no | no |
| S1.3 | #21 | 39 | P2 | yes: S2.2 (was S2.1); S1.1 unchanged | yes: click table holds no demo or bot rows |

Ticket body changes in substance: T1.1.3, T1.1.4, T3.3.2, T5.1.2, T6.1.1, T6.1.2, T6.2.4, T7.2.4, T8.3.3, T8.3.4, T8.4.1, T8.4.3, T8.4.4, T9.1.2, T9.3.1. All other tickets keep their text.

(d) Epics whose story list or priority changed:
- E8 (#16): story list gains S8.6; priority P1 to P0; outcome text adds attributes.
- E7 (#15): priority P1 to P0 (S7.1, S7.2 are P0); outcome text notes the split.
- E10 (#18): priority P2 to P0 (S10.2, S10.3 are P0).
- E1 (#9), E3 (#11), E4 (#12), E5 (#13), E6 (#14), E9 (#17): story list unchanged; outcome or covers text changed (counting rules, no-404 removal, unmapped not public, browsing P0 and search P1, demo noindex, legal pages and D-1). Priorities unchanged at P0.
- E2 (#10), E0 (#8): no change.

Finding 15 map (rulings to the issue bodies they block): OD3 into S5.1 (#34), S4.2 (#33), S8.4 (#48), S9.4 (#53). OD5 into S9.3 (#52), S9.1 (#50), E9 (#17). OD2 into S1.1 (#19), S6.2 (#39), S8.4 (#48), S9.1 (#50), S9.4 (#53). Open decisions OD1, OD4, OD6, OD7, OD8, OD10 and OD11 go on the issues they block, as listed in § Open decisions.

## mvp.md amendment

Yes, docs/product/mvp.md needs edits. Not applied; the owner decides. Proposed text per section:

- § Catalogue scope, bullet "Categories": append "Products from an unmapped feed category are not public until the admin maps the category (owner ruling, 2026-10-17)."
- § Visibility (guardrail 1): replace "Products from an approved feed publish automatically." with "Products from an approved feed publish automatically once their feed category is mapped; until then they wait in the admin queue and are not public." This removes the contradiction between § Visibility and § Catalogue scope.
- New section "Legal pages" after § Delivery: "The site carries a legal notice (aviso legal), a privacy policy and an affiliate disclosure, linked from the footer of every page (LSSI-CE). The owner supplies the Spanish text. There is still no cookie banner."
- § Delivery, append: "While the networks review the site it may show the demo catalogue. Demo products are noindex and left out of the sitemap, and clicks on demo offers are not counted. The demo feeds are disabled when the first real feed is approved. No visitor IP address or user agent appears in the proxy, app or container logs."
- § Outgoing clicks, append: "Prefetch and HEAD requests, known crawlers and demo offers are not counted. The count is best effort; the network's report is the authority for commission."
- § Product and offers, bullet "Price history": append "Imports are manual, so a day without an import has no point; the chart shows the gap and never invents a value."
- § Product and offers, bullet "When a product loses all its offers": append "Structured data is omitted while it has no offers."
- § Goal, optional: change the done-definition sentence "the site is live" to "the site is live with its legal pages".

No edit is needed for attributes and fitment text: § Product and offers and § Catalogue scope already say they come from feeds and are shown as text and nothing more; S8.6 is the missing story, not a missing scope line.

## Capability coverage

Changes to the prior coverage list (all other rows are as in runs/2026-10-17-mvp-backlog/02-product.md § Capability coverage):

- Product attributes and fitment text from feeds (not listed before; gap found by finding 6): S8.6, with S8.5 for precedence.
- Price history and chart (ABSENT): S8.3, now including the gap rule.
- No-offers state with last known price (ABSENT): S8.4 (OD4), before the first real feed.
- Matching by brand and part number, and conflict queue: S7.1 and S7.2, before the first real feed.
- Categories, unmapped queue (PARTIAL): S5.1, S4.1, S4.2, with unmapped products not public (D-1/OD3).
- `/go` redirect and click log (ABSENT): S1.1, including counting rules and demo exclusion.
- Delivery on a VPS with domain (ABSENT): S9.1 (logs rule, demo catalogue), S9.2, S9.3 (OD5 ruled; legal pages in scope).
- Affiliate link pattern: S3.6, now on the path to the first real feed.
- Feed URL protection: S3.1 (masking), S10.3 (encryption, OD11).

## Not in backlog

Out of MVP (mvp.md § Out of MVP), none planned: shops uploading their own feeds and per-click billing; ads and cookie banner; public accounts, alerts, reviews, ratings, favourites; shipping costs; fitment search and TecDoc; tyres, building materials, plumbing and electrical; Amazon; Open Icecat; scheduled imports; languages other than Spanish.

Newly noted as not planned:
- Carrying a price forward over days without an import, or interpolating: refused by S8.3; scheduled imports are out of MVP.
- Fitment as structured data, a vehicle filter or fitment search: out of MVP; S8.6 shows text only.
- A cookie, IP or user-agent store to detect bots: refused by guardrail 5; S1.1 reads the user agent in memory only.
- Demo categories on the home page after demo products stop being public: raised in risks, not scheduled.

Carried ledger rows (from the prior run, unchanged):
- Importer https redirect policy (F-1): ticket T3.4.3.
- e2e global-setup failure branches (F-3): ticket T10.2.1.
- Spanish copy is the lane's own wording: ticket T10.2.2 and owner task O5.
- CLAUDE.md § Stack lacks npm and Node 22: ticket T10.2.3, the owner's call.
- Umami default admin login: tickets T1.2.4 and T9.1.3.
- Feed URL may hold an API key: masking in S3.1, encryption in S10.3 (OD11).
- Dismissed, dev-only advisories via drizzle-kit: a check at deploy time is an acceptance bullet of S9.1.
- Dismissed, the pack style items and the CRLF tip disagreement: they concern the agentic network's own files; they stay in the run ledger for a protocol close-out.
- Dismissed, the missing decision numbers 0003 and 0005: a numbering gap with no consequence; no ticket.
