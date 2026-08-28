CHANGE REQUEST 2
lane:     docs
severity: SHOULD_FIX
round:    1
finding:  docs/product/stories/US-41.3-status-and-navigation-doc-reconciliation.md — line 8 still reads `**Status:** Next phase` and lines 11-16 still carry the `**Draft for human review.** ... Not yet approved.` banner, while the sibling story built in the same run (US-42.1) had its Status flipped to `Done` and a close-out block appended (by order 10). 06-docs-us41.3.md § risks records that Status was deliberately left alone because "the order did not instruct a status change".
why:      Two stories built and gated in the same run now report their completion state differently, so a reader of the story index cannot tell from the files whether US-41.3 landed. The inconsistency is between the two lanes' close-out handling, not a defect in either story's work.
expected: At close-out (order 13), align the two: flip US-41.3 to `Done` with an equivalent close-out block once AC7 (full suite) is confirmed green and the gates have passed, or record explicitly why the two are treated differently. Not a blocker for this slice.
