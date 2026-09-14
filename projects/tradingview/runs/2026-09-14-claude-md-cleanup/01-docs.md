REPORT 2026-09-14-claude-md-cleanup/01
status:      DONE
verdict:     NONE

changed:
  - tradingview/CLAUDE.md — rewrote the "Layout" section's code block and surrounding prose to list what is actually on disk (three .pine files, the loose CSV, .agentic.json) instead of the never-built docs/ and fixtures/ directories, while keeping docs/<slug>.md and fixtures/*.csv named as the stated convention for future scripts

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    CLAUDE.md is prose; order named verification: NONE — no static/compile check applies

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - Kept docs/<slug>.md and fixtures/*.csv as a stated convention (option a in the order) rather than dropping it, per the order's stated preference: project.md's "Delivery model" and "The script header contract" sections, and the docs.md capability pack's § "docs/<slug>.md — the shape", all assume docs/<slug>.md is the target shape for a script doc, so dropping the convention from CLAUDE.md would put it at odds with those. I found no concrete reason the convention itself is wrong — only that it hasn't been used yet — so I left it in place, made explicit and non-misleading about current state.
  - project.md and docs.md's capability pack both already read consistently with the corrected CLAUDE.md (they describe docs/<slug>.md as a target/shape, not as something that currently exists for every script), so no pack_correction or project.md edit was needed — flagging this only because the order anticipated one might be, and I want the reasoning visible rather than silently concluding "nothing to do" with no trace.

## Orchestrator brief

- tradingview/CLAUDE.md § Layout rewritten to match the actual repo root listing confirmed by the 2026-09-14-audit-systemic-stress-dashboard recon run's § Repo listing notes: mm_cot_long_short_index.pine, strategy13_trend_carry.pine, systemic_stress_dashboard.pine, the one loose CSV (named and attributed to strategy13_trend_carry.pine), and .agentic.json — no docs/ or fixtures/ directories.
- Decision taken (see risks): kept docs/<slug>.md and fixtures/*.csv as an explicitly-labelled future convention rather than deleting it, because project.md and the docs capability pack both assume it as the target shape and removing it from CLAUDE.md alone would have created a contradiction between the two docs.
- No other section of CLAUDE.md touched — Stack, Commands, guardrails and "Working on a script" were already accurate per the prior audit and are left verbatim.
- No pack_correction or project.md change needed; reasoning is in risks, not silently omitted.
