# Decisions — 2026-09-17-fix-mm-cot-long-short-index

## D-1 · specification · 2026-09-17
open decision:  FINDING 3 — whether to rescale the COT index on net (long − short) position to match the cited Briese/Williams methodology, or keep the two independent gross long/gross short series and relabel the header to stop calling it "standard."
raised by:      ../2026-09-16-audit-mm-cot-long-short-index/02-quant-audit.md § FINDING 3 § expected
ruling:         "Switch to net position (recommended)" — rescale the index on net (long − short) to 0..100, matching the Briese/Williams methodology the header already cites. Keep raw gross long/short as table rows only, not as separate indices. This also resolves FINDING 4 (80/20 vs 90/10 guide lines) as part of the same change, and lets FINDING 5's citation be added honestly.
by:             the human, in session (AskUserQuestion)
