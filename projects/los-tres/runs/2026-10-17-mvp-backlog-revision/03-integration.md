REPORT 2026-10-17-mvp-backlog-revision/03
status:      DONE
verdict:     CHANGES_REQUESTED

changed:
  - none

verification:
  command:   cd C:\projects\investments\los-tres && npm run gate
  result:    PASS
  detail:    npm run gate exit 0 on 188-mvp-amendment (cca91f4): lint, typecheck, db:up, Vitest 30 files / 396 tests passed, stack:up healthy, Playwright 23 passed. Docs-only diff; gate shows no regression. Anchor: consistency check against D-1, D-3 and 01-product § mvp.md amendment, not independent.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - C:\projects\investments\.agentic\projects\los-tres\runs\2026-10-17-mvp-backlog-revision\cr\CR-1.md — docs lane: mvp.md bullet "When a product loses all its offers" contradicts itself on structured data

skill_calls:
  - none

risks:
  - mvp.md § Outgoing clicks says "It logs the click" then "not counted" for HEAD, prefetch, bots and demo, never saying they still redirect (01-product S1.1 does); decision 0009 says /go writes one click row. Owner may want a line in 0009
  - Header gains "the owner approved the amendment" and OD10/OD11 sentences, outside the proposed text; D-3 covers both, so not a finding. The owner should read those two passages, as 02-docs risks say
  - Goal first line and the Visibility line "then they wait ... hide any product or offer," now run past the 80-column wrap the rest of mvp.md keeps; no tool enforces it, so not a change request
  - The OD11 sentence (masked, never logged until encrypted) restates S3.1 acceptance; shipped code was not inspected here, since the diff is docs only
  - project.md guardrail 1 still lacks the unmapped state; it stays true as a necessary condition and is the owner's call, carried from 01-product

## Orchestrator brief
Verdict CHANGES_REQUESTED: one BLOCKING finding, everything else clean. Route CR-1 to the docs lane by path.
- Diff touches only docs/product/mvp.md (35 insertions, 8 deletions); no other file changed, tree clean after the gate.
- Gate: npm run gate exit 0 (396 unit/integration, 23 e2e). Docs-only, so it proves no regression, not doc correctness.
- Every proposed edit in 01-product § mvp.md amendment is present, plus OD10, OD11 and the header line; D-1 and D-3 rulings are all in.
- No contradiction with the five guardrails, CLAUDE.md § Stack, or decisions 0007-0009.
- CR-1 (docs, BLOCKING): "Only the offer list changes" contradicts "Structured data is omitted" in the same bullet.
- After CR-1 is fixed, re-run only this gate; a quick diff read suffices, the gate need not change.
- Sections below: Findings (CR-1), Checked clean (per-passage check against the ruling).

## Findings
- CR-1, BLOCKING, docs lane, mvp.md § Product and offers: see cr/CR-1.md. Cause: the proposed text in 01-product was applied verbatim, and the proposal itself carried the contradiction.

## Checked clean
- Header: provenance line added, supported by D-3.
- Goal: "live with its legal pages" is the optional change in 01-product, applied.
- Catalogue scope, Visibility: unmapped products not public, dated 2026-10-17 (D-1/OD3); the two sections agree and guardrail 1 still holds as a necessary condition.
- Price history gap rule: verbatim, no value invented, consistent with guardrail 4.
- Shops and feeds: OD11 sentence matches D-3 ("before") and S3.1 acceptance.
- Outgoing clicks: counting rules verbatim; user agent is never stored, so guardrail 5 and decision 0009 hold.
- Delivery: demo catalogue, noindex, sitemap, uncounted clicks (D-1/OD2), OD10 notice and legal line (D-3), logs without IP or user agent (guardrail 5).
- Legal pages: new section as proposed, OD5 ruled; "no cookie banner" agrees with decision 0009.
- Out of MVP: untouched, no conflict with the additions.
