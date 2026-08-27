REPORT 2026-08-26-performance-benchmark-chart-audit/13
status:      DONE
verdict:     NONE

changed:
  - docs/contracts/dashboard-fields.md — updated the "Indexed chart" row (Performance & Benchmark card table) to name the new second arg to `buildIndexedSeries` and note both this-run fixes (portfolio leg re-based off `portfolio_return_pct` instead of raw `portfolio_value`; chart now filters/re-bases on `window_start_date` instead of ignoring the range selector)
  - docs/contracts/dashboard-fields.md — added a new `range_metrics[*].window_start_date` entry near the existing `portfolio_return_trust` entry (per 07-backend.md's suggested placement): type (`string | null`), semantics (window's own start date, null only for "All", YTD's own non-null special case), and why the field exists (it is what fixed CR-2 #1's range-ignoring bug)
  - docs/tech-debt-register.md — added new section "Deferred findings — 2026-08-26 Performance & Benchmark chart audit (not Epic 23/24)" with 4 entries: (a) CR-2 #2 financial-methodology.md §Indexed Return Series Implementation-list gap, (b) CR-2 #3 undocumented intentional-stub `/run` route, (c) 10-quant-audit.md FINDING 1 YTD-vs-sliding-window anchor convention doc gap, (d) 11-integration.md's optional-vs-strict `window_start_date` TS typing + the related `portfolioFixtures.ts` fixture-coverage footgun
  - docs/product/current-product-state.md — added a one-paragraph note under the Dashboard tab's Performance & Benchmark bullet list stating the chart's portfolio line and range-filtering are now both correct as of this run's fix, with pointers to the contract doc and tech-debt-register for detail

verification:
  command:   Grep tool (no Bash available to this lane): pattern `window_start_date` against docs/contracts/dashboard-fields.md (content mode, line numbers) — equivalent to the order's `grep -n`; pattern `^\|` against docs/tech-debt-register.md (count mode) — equivalent to the order's `grep -c "^|"`
  result:    PASS
  detail:    `window_start_date` matches on 2 lines in dashboard-fields.md (line 219, the field-table row; line 324, the new prose entry). `docs/tech-debt-register.md` has 105 lines starting with `|` (table rows across the whole file, including the 4 new rows this pass added under the new "Deferred findings" section's table). This lane has no Bash tool, so the two commands were run via the Grep tool rather than a literal shell `grep`; both checks confirm the definition_of_done's two file-level changes landed.

contract_notes:
  - none — this pass absorbed every open contract_note from 07-backend.md, 10-quant-audit.md and 11-integration.md (all three pointed at the same missing `range_metrics[*].window_start_date` entry in dashboard-fields.md); no new contract drift introduced by this pass, since it touched only docs, not schemas/types.

pack_corrections:
  - none

handoff:
  - The 4 tech-debt-register entries added this pass are all `owner-story: none (open)` — no ticket exists for them, per this order's non_goals (do not fix CR-2 #2/#3, do not touch stories). If/when a future docs-engineer or story-author picks one up, the register entry itself carries enough context (source report, exact expected fix) to act on directly.
  - The tech-debt-register's Entry schema (`category` enum) does not include a documentation-completeness or typing-precision value — I extended it locally with `doc-gap` and `typing-precision`, scoped to this new section only, with a one-line note explaining the extension. If this register ever gets a broader non-code-debt intake, that enum is worth revisiting formally rather than re-extending ad hoc per section.

risks:
  - `current-product-state.md`'s top-of-file `Updated: 2026-08-19 (after Epic 34...)` banner was left untouched. The doc does track individual card-level behavior at fine granularity (confirmed by reading its existing Dashboard-tab bullets, which is why I added the new note), but the banner date/parenthetical names Epic 34 specifically and this run is not an epic — bumping it felt like it would overstate this as an epic-level event rather than a defect-fix note. Flagging the inconsistency (content dated 2026-08-26, banner dated 2026-08-19) rather than silently deciding it myself.
  - The order's verification command (`grep -n` / `grep -c "^|"`) could not be run literally — this lane has no Bash tool (docs-engineer is one of the three deliberately shell-less lanes per PROTOCOL.md § 4/§7). Substituted the Grep tool for an equivalent check; see `verification.detail`. Not a gap in what I checked, only in which tool ran it.
