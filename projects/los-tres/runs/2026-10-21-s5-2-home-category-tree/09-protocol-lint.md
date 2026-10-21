REPORT 2026-10-21-s5-2-home-category-tree/09
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   claude plugin validate <agenticRoot>/plugins/agentic-core; git diff of the 5 packs; repo greps for premises
  result:    PASS
  detail:    1 BLOCKING (rule 9, frontend.md:36), 3 SHOULD_FIX (rule 8); 9 edits in 5 packs checked; plugin validate passed (license/icon notices only); anchor authoring.md; 11 premises confirmed in repo, 1 UNVERIFIED

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - BLOCKING rule 9 (Two instructions may not disagree) frontend.md:36 — for a non-muted <p> inside .page, sentence 1 says use a span or h2, sentence 2 says keep it and override with .panel .tagline; nothing says which wins. see § Finding F1
  - F1 satisfied by: one statement with precedence, e.g. "Text that must not be muted is a span or h2; where it must stay a <p> (the home tagline), override with a two-class selector under the container (.panel .tagline), never !important."
  - F1 owner: docs-engineer, scope fence capabilities/frontend.md § Layout only; delete the restated "A single-class module rule loses to .page p" clause, which repeats sentence 1.
  - SHOULD_FIX rule 8 testing.md:82 — bullet carries two facts (malformed slug insert; parent-cycle build); split into two bullets.
  - SHOULD_FIX rule 8 testing.md:37 — "the S5.2 testids" is provenance; name them as the home page's testids, the slice label changes no lane's action.
  - SHOULD_FIX rule 8 frontend.md:34 — the listing-components line now mixes listing, home and header components under "Listing components"; retitle as "Shared components" or split.

skill_calls:
  - none

risks:
  - UNVERIFIED: ux.md:112 claim that the empty home is producible only by wiping the demo database; I did not test a second database or another recipe.
  - ux.md:7-10 "no design system yet" is now further stale since docs/design/system.md was replaced this run; already carried in S5.1 Open (11-protocol-lint), not re-raised.
  - claude plugin validate reported LICENSE_MISSING and ICON_MISSING directory notices for plugins/agentic-core; outside scope and not authoring rules.

## Orchestrator brief

- Verdict FAIL on one rule-9 finding, § Finding F1; the other 8 edits conform on rules 1-7 and 9.
- Three rule-8 SHOULD_FIX items go to Open; none blocks.
- § Finding F1: the frontend.md § Layout contradiction, with evidence and the fix wording.

## Finding F1

- **Rule:** authoring.md § "Two instructions may not disagree" — "A rule and its exception are one fact"; "silence is not" a resolution.
- **File:line:** `C:\projects\investments\.agentic\projects\los-tres\capabilities\frontend.md:36` (§ Layout, always-read).
- **Sentence 1 (existing):** "use a `span` or `h2` for text that must not be muted, and `p` only for muted prose."
- **Sentence 2 (added this close-out):** "A single-class module rule loses to `.page p`; override it with a two-class selector under the container (`.panel .tagline`), never `!important`."
- **Same situation, two actions:** the home tagline is a `<p>` that must be white (`src/app/(public)/page.tsx:19`, `page.module.css:17-18`). Sentence 1 says change the element; sentence 2 says keep `<p>` and add a two-class selector. A frontend lane on the next non-muted `<p>` picks one, and nothing records which.
- **Satisfied by:** one statement giving precedence, per the handoff wording, and removing sentence 2's first clause, which restates sentence 1's specificity fact.
