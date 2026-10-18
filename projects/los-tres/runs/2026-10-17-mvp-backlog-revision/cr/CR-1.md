CHANGE REQUEST CR-1 — 2026-10-17-mvp-backlog-revision
lane:        docs
severity:    BLOCKING
round:       1 of 2
raised by:   C:\projects\investments\.agentic\projects\los-tres\runs\2026-10-17-mvp-backlog-revision\03-integration.md § Findings
scope fence: C:\projects\investments\los-tres\docs\product\mvp.md (§ Product and offers, bullet "When a product loses all its offers" only)

Finding. In docs/product/mvp.md, § Product and offers, the bullet "When a
product loses all its offers" now reads: "its page stays exactly as it is
(text, image, price history, still indexed). Only the offer list changes: it
shows "No offers right now" ... Structured data is omitted while it has no
offers." The last sentence contradicts the two before it: "stays exactly as it
is" and "Only the offer list changes" are false once the schema.org
Product/AggregateOffer data (promised unconditionally in § Search and browsing)
disappears from the page.

Why it matters. This is the exact S6.1 versus S8.4 contradiction that finding 9
of the run request was raised to remove. A story author or engineer reading
only this bullet cannot tell whether S8.4 may keep or must drop the JSON-LD,
and the "only" sentence is the one a test would be written against.

What satisfies it. The bullet states one consistent rule. For example, change
"Only the offer list changes:" so it names both changes (the offer list shows
"No offers right now" with the last known lowest price and its date, and the
structured data is omitted), or move the structured-data sentence ahead of the
"stays exactly as it is" sentence as a stated exception. Keep the meaning of
the ruled text; do not edit any other section. The wording is the docs lane's.
