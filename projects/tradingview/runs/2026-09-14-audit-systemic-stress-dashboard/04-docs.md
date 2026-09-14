REPORT 2026-09-14-audit-systemic-stress-dashboard/04
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only close-out check, no command named by the order

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - CLAUDE.md documents a `docs/<slug>.md`-per-script convention and a `fixtures/` directory, but neither exists anywhere in the repo (confirmed: `tradingview/docs/**` glob returns no files, and 01-recon.md § Repo listing notes lists the actual `tradingview/*` root with no `docs` or `fixtures` entry). This predates this run. Backfilling either is new scope this order was not asked to do — flagging for the human to decide whether to open it as its own order.
  - 03-quant-audit.md § FINDING 1, § FINDING 2, § FINDING 4, § FINDING 5 and § FINDING 8 are candidates for new header admissions under project.md § "The script header contract" ("what was not verified," named in the header, on `tradingview/systemic_stress_dashboard.pine`). Recommending, not doing: writing them into the header is a build-phase edit to a `.pine` file, which would trigger this run's build/compile phase — an authorization the human has not given on an audit this run has not yet presented to them.
  - Specifically, per the audit: FINDING 4 (header's "if it stays blank, the symbol didn't resolve" diagnostic is false during warm-up and one-bar data gaps) and FINDING 8 (header never states whether TVC:VIX, CBOE:COR1M, AMEX:LQD, AMEX:HYG were confirmed against TradingView symbol search) are header-text gaps specifically; FINDING 1, FINDING 2 and FINDING 5 are undisclosed behaviours (degenerate-input percentile of 100 instead of n/a, impulse across a basis change, undisclosed last-bar repaint) that the header contract's "what was not verified" clause would also need to cover once a build lane resolves or discloses them.

risks:
  - none
