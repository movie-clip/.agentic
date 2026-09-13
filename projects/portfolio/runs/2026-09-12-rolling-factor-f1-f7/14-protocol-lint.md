REPORT 2026-09-12-rolling-factor-f1-f7/14
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Read-only authoring lint. External anchor per gates.md sec 2 = protocol/authoring.md rule text (subject is a capability pack, not authoring.md itself, so anchor and subject are distinct files), plus pack-corrections.md as the independent statement of what the edit was meant to say. Rules 1, 2, 5, 6, 7, 8 checked against capabilities/frontend.md read end to end.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - Did not open `apps/desktop/src/.../TrustBadge.tsx:14`; it is outside this order's scope, so the union's truth against the code rests on 06-frontend.md and 13-docs.md, not on my reading.
  - Line 184 (Definition of done) still reads "`TrustBadge` for any synthetic/unavailable state" and now disagrees with the edited row at line 79, which includes `'degraded'`. Out of scope per non_goals, not part of the verdict — see § Out-of-scope observations.
  - Line 160 (Guardrails, in UI terms) requires a badge for `withheld`, a value the line 79 union does not carry. Pre-existing, out of scope, and a fact-about-the-code question rather than an authoring one — see § Out-of-scope observations.

## Orchestrator brief

PASS. Nothing to route. The docs lane's edit to `capabilities/frontend.md:79` matches
pack-corrections.md exactly and breaks no rule in `authoring.md`.

| Section | Contains |
|---|---|
| Findings | the rule-by-rule table (rules 1, 2, 5, 6, 7, 8) and the definition-of-done text match — all PASS |
| Out-of-scope observations | two consistency defects at lines 184 and 160, fenced off by `non_goals`, for a future frontend or docs dispatch |

No change request follows from this report. The two observations are `risks`, not
findings, and the verdict does not depend on them.

## Findings

None. The edit passes on every rule in scope.

| Rule (`authoring.md`) | Applied to | Result |
|---|---|---|
| 1 — four-layer split | line 79 | PASS. `{type: 'synthetic'\|'unavailable'\|'degraded', tooltip?}` is a repo component's prop shape — capability-layer content by that table's own "paths, frameworks, fixtures" column. It is not a protocol message shape and not a role definition, the two things this layer must not contain. |
| 2 — one rule, one home | line 79 vs rest of file | PASS within scope. The type union is stated once, in § The eight primitives. No protocol rule is restated. |
| 5 — index block | § Index, lines 15–28 | PASS. § The eight primitives is present in the index table under the name a lane would search for, and the edit added no new section needing an index entry. |
| 6 — always-read vs conditional | § Index line 26 | PASS. The condition "your order builds or changes any UI" is evaluable from the order text before the section is read, which is the test the rule states. Not the non-evaluable "read Reuse when you are about to write a helper" shape. |
| 7 — tool premises | § The eight primitives | PASS, vacuously. The edited section contains no command, so the edit introduces no tool premise. |
| 8 — written for a model | line 79 | PASS. The fact is a table row: one primitive per row, one fact per row. Notably, pack-corrections.md's provenance clause ("added by 03-frontend.md in this run") was **not** carried into the pack — provenance belongs in `CHANGELOG.md`, and copying it would itself have been a rule 8 violation. |

### Definition-of-done item 1 — does the table match the correction?

pack-corrections.md instructs: "Replace the table entry with `{type: 'synthetic'|'unavailable'|'degraded'}`."

`capabilities/frontend.md:79` now reads:

```
| `TrustBadge` `{type: 'synthetic'\|'unavailable'\|'degraded', tooltip?}` | the only legal way to render a trust badge |
```

Match. The three members are present in the instructed order; the pre-existing
`tooltip?` member was correctly retained, since the correction named only the `type`
union and a docs lane dropping `tooltip?` would have been an unscoped edit. The pipe
escapes are required by the surrounding Markdown table and are not a discrepancy.

## Out-of-scope observations

Recorded because the owning lane will want them, **not** as part of the verdict. Both
sit in sections this run did not touch, which `non_goals` fences off.

- **`capabilities/frontend.md:184`**, § Definition of done: `- [ ] TrustBadge for any synthetic/unavailable state; ...`. Consistent with line 79 before the edit, not consistent with it now. A lane reading only the checklist will not learn that `degraded` requires a badge. What would satisfy `authoring.md` § Indexing a pack, rule 2 ("every fact lives in exactly one section"): make the checklist cite the primitives table rather than re-list the states — e.g. `TrustBadge for any state in its type union (§ The eight primitives)`.
- **`capabilities/frontend.md:160`**, § Guardrails, in UI terms: "`withheld` and `degraded` always show their badge." `withheld` is not a member of the line 79 union. This may be correct about the product's trust vocabulary and wrong about the component, or the reverse; resolving it means opening `TrustBadge.tsx`, which this order does not permit. A candidate `pack_corrections` entry for a future frontend dispatch, not an authoring finding.
