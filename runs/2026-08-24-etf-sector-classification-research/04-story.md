REPORT 2026-08-24-etf-sector-classification-research/04
status:      DONE
verdict:     NONE

changed:
  - docs/product/stories/US-39.1-direct-held-etf-sector-classification.md — new story file, drafted from the delivery brief and quant research brief, not yet human-approved

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only drafting order; no verification command named

contract_notes:
  - Story requires a new ClassificationSource literal (schema addition) — the design pass (tech-lead DESIGN) settles the exact literal name, per T-39.1.1
  - Story requires a new MarketDataService/FmpClient method (get_etf_sector_weightings, name proposed not mandated) reading /stable/etf/sector-weightings — per T-39.1.3
  - Story requires a new SymbolResolutionRule for SBIO in app/core/symbols.py (SBIO.L candidate, no bare "SBIO") — per T-39.1.2

pack_corrections:
  - none

handoff:
  - story path: docs/product/stories/US-39.1-direct-held-etf-sector-classification.md — draft for human review, not approved
  - 2 open decisions block ticketing (both carried forward unresolved, per capability pack discipline): (1) exact DOMINANCE_THRESHOLD number within the data-backed 50-60% band; (2) whether/how the `category` field gets a dynamic tier, generic label, or stays out of scope
  - tickets drafted: T-39.1.1 (schema literal) -> T-39.1.2 (SBIO symbol rule) -> T-39.1.3 (FMP client method) -> T-39.1.4 (ETF resolution logic, depends on .1-.3) -> T-39.1.5 (docs) -> T-39.1.6 (tests)
  - epic title used verbatim per the work order: "Epic 39 — Direct-Held ETF Sector Classification" — PRD/roadmap/story-index entries not created by this draft, human's/docs-engineer's job at close-out
  - this is a draft for human review, not an approved, ticketed story ready to build

risks:
  - Assumed (not decided by this draft) that epic placement itself is settled, since the work order supplied the epic title as a given — the delivery brief's own Open decision #1 (placement) is not re-litigated here, only carried as a filing note
  - The classification_source literal name and the FMP client method name in the story are the research brief's proposals, explicitly flagged non-binding — the design pass may choose different names without contradicting this story
  - Assumed the `category` field's existing keyword-based derivation logic in registry.py's ETF branch stays untouched by this story (only `sector` derivation is replaced) — this follows from Open decision #2 being unresolved, not from an explicit instruction in either input brief

## Orchestrator brief
- Drafted 1 story: US-39.1, Epic 39 — Direct-Held ETF Sector Classification (title verbatim per order)
- Decision: story covers `sector` derivation only in registry.py's ETF branch; `category` derivation is explicitly untouched pending Open decision #2
- Decision: no frontend ticket (mirrors US-37.1/US-38.1 reasoning — rendering is already generic over bucket labels)
- Lane split: 6 tickets, backend-engineer x4 (schema, symbol rule, client method, resolution logic — in that dependency order), docs-engineer x1, test-engineer x1
- Blocks dispatch: 2 open decisions (dominance threshold exact number; category dynamic-tier treatment) — human/tech-lead must resolve before a design pass can proceed
- Sections in the story file: Open decisions · Story · Context (live evidence explained in full, no need to reopen 03-quant-research.md) · Acceptance criteria (AC1-AC12) · Test plan · Tickets (T-39.1.1-6) · Out of scope · Notes / decisions
- Status is Backlog; roadmap, story index, PRD, tech-debt-register.md untouched by this draft — human/docs-engineer close-out action
