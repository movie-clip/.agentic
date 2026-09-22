REPORT 2026-09-17-bind-datoro/02
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   claude plugin validate C:\projects\investments\.agentic\plugins\agentic-core
  result:    PASS
  detail:    Anchor: protocol/authoring.md (subject is a project profile, not authoring.md itself, so the rule text is the valid anchor). Manifest validation passed. Round-2 check of 4 files: FINDINGS 1-3 (all BLOCKING) satisfied, FINDING 4 (SHOULD_FIX) partially satisfied. No regression against round 1.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - FINDING 4 remains open as SHOULD_FIX — the retention rule now declares itself network-wide but its full statement still lives in `projects/portfolio/runs/README.md`, not in `protocol/`. See § FINDING 4.
  - Fixing it fully is an edit to `protocol/authoring.md` § "Adding a project" plus both run READMEs, which is outside this run's scope fence. It is a separate order, not a re-dispatch of this one.

risks:
  - `runs/README.md:17` cites `projects/portfolio/runs/README.md` as an agenticRoot-relative path while line 11 uses a file-relative one (`../../../protocol/...`). Both resolve for a reader; the mixed convention is style, not a rule, so not a finding.
  - I did not open `C:\projects\investments\datoro`. Every claim these files make about that repo's paths, scripts and CI remains unverified by me — authoring, not fact.
  - This was scoped as a round-2 check on four files. The five files round 1 passed (`product.md`, `testing.md`, `docs.md`, `architecture.md`, `phases.md`) were not reopened, per the order's `non_goals`.
  - The bullet-length observation from round 1 (13 of 79 bullets over authoring.md's 200-char instruction limit) is unchanged; none of the four edits added or lengthened a bullet. Still not raised as blocking, on round 1's reasoning.

## Orchestrator brief

- Verdict: PASS. All three BLOCKING findings from round 1 are satisfied by the exact edit each one proposed.
- FINDING 4 (SHOULD_FIX) is materially improved but not fully satisfied. It does not hold the slice — core § 5: only `BLOCKING` does — and it becomes an `Open` row at close-out.
- No regression: every row of round 1's "What passed" table that touches these four files was re-checked and still holds.
- Sections: § FINDING 1 — satisfied · § FINDING 2 — satisfied · § FINDING 3 — satisfied · § FINDING 4 — partially satisfied, stays SHOULD_FIX · § Regression check.

## FINDING 1 — satisfied

Round 1 asked: move `Guardrails, in code terms` out of the `## Index` table and
into the `Always read:` line at `frontend.md:17`.

The edit, `capabilities/frontend.md:17`:

```
**Always read:** **Component and composable conventions** · **Reuse — do not re-derive these** · **Guardrails, in code terms** · **Definition of done for this lane**
```

The table at :19-22 now carries only `Layout` and `Charts`. The section is in
exactly one of the two places, not both — which matters, because a name in both
lists is rule 2 ("every fact lives in exactly one section") reappearing in the
index itself.

`frontend.md` and `backend.md` now agree on this section name: both list
`Guardrails, in code terms` as always-read. The disagreement round 1 named is
gone.

Satisfied under `authoring.md` § "Indexing a pack or profile", rule 3.

## FINDING 2 — satisfied

Round 1 asked: move `Reuse — do not re-derive these` into the `Always read:`
line at `backend.md:19`.

The edit, `capabilities/backend.md:19`:

```
**Always read:** **Guardrails, in code terms** · **Reuse — do not re-derive these** · **Gotchas from `AGENTS.md`** · **Definition of done for this lane**
```

The table at :21-24 now carries only `Layout` and `Route conventions`. The
non-evaluable condition ("you are about to write a new service") is removed
rather than reworded, which is the right fix — `authoring.md` names that exact
condition shape as its own worked example, so no rewording of it would have
been evaluable either.

The consequence round 1 identified is closed: guardrails 1, 2 and 3 are bound
to `auth.ts`, `constructWebhookEvent` and `logger.ts` in this section, and a
backend order editing an existing route now reads that binding unconditionally.

Both packs now agree on this section name as well.

Satisfied under `authoring.md` § "Indexing a pack or profile", rule 3.

## FINDING 3 — satisfied

Round 1 asked for a row reading
`| Reference | you are a recon or product order checking whether something was already flagged |`.

The edit, `project.md:45`, is that row verbatim. `## Reference` now sits at
:150 (one line lower, consistent with a single added line and with nothing else
in the file having moved).

The index is now complete against the file: two always-read sections
(`Hard guardrails`, `Mechanical gates`) plus four table rows (`Delivery model`,
`Lane routing`, `Why quant is not bound`, `Reference`) against exactly six `##`
headings below the block. No section is unfindable and no section is named
twice.

The condition is evaluable from the order — a lane knows whether it is a recon
or product order — so a table row is correct here and always-read is not owed.

Satisfied under `authoring.md` § "Indexing a pack or profile", rule 1.

## FINDING 4 — partially satisfied, stays SHOULD_FIX

The edit, `runs/README.md:13-17`, replaced the twelve-line copy with:

```markdown
## Retention

Pruned at close-out once the lesson is in the protocol, and cited afterward by
run id, never by path — this is a network-wide policy, not a datoro-specific
one; see `projects/portfolio/runs/README.md` for the full statement of it.
```

**What this fixes.** The rationale is no longer duplicated, so the two copies
can no longer drift on reasoning — which was the concrete harm round 1 named,
and it is genuinely closed. The sentence about `CHANGELOG.md` that portfolio's
copy carries and datoro's dropped is now a difference between a statement and a
pointer to it, not a divergence between two statements.

**What it does not fix.** Round 1 offered two ways to satisfy the rule. Option
(b) — declare retention a deliberate per-project policy — is not what this edit
does: it says the opposite, explicitly, that the policy is network-wide. Option
(a) — state it once in `authoring.md` and reduce both READMEs to pointers — is
half done: datoro's is now a pointer, but the home it points at is
`projects/portfolio/runs/README.md:13-27`, another *project's* file.

`authoring.md` § "One rule, one home" places a rule by *who needs it*: "only a
human or an agent writing network files → `authoring.md`". A statement about how
any project's run directory is kept is needed by every project, so a home under
`projects/portfolio/` leaves a `datoro` lane reading a rule out of a directory
that is not its own and that nothing makes authoritative.

**Still SHOULD_FIX, and the verdict does not rest on it.** The remaining half of
the fix edits `protocol/authoring.md` and `projects/portfolio/runs/README.md`,
neither of which this order's `scope` names. That makes it a separate order
rather than a third round on this finding — and per core § 5 it reaches the
human through the ledger's `Open` table, not through a held slice.

## Regression check

Every row of round 1's "What passed" table that touches these four files,
re-checked against the current text.

| Check | Round 2 |
|---|---|
| `claude plugin validate plugins/agentic-core` | passes — manifest validation clean |
| Index present, all three indexed files | `project.md:32`, `frontend.md:11`, `backend.md:13` all carry `## Index` |
| Index complete | 6 sections / 6 headings in each of the three files; no name in both the always-read line and the table |
| Four-layer split | no message shape, report block or role definition introduced by any of the four edits |
| Tool premises | no command added or changed; the four edits are index rows, an always-read line and a README paragraph |
| MCP | `grep -rn "mcp__" projects/datoro` still returns one hit outside the run dir, `project.md:109`, which denies the grant |
| Lane routing table | unchanged at `project.md:94-106`; all eleven rows still resolve to `plugins/agentic-core/agents/` |
| Model / effort | not applicable — no agent file in scope, and none was touched |

The only line-number movement in scope is `project.md`, where everything below
:45 shifted by one. `frontend.md` and `backend.md` changed within their index
blocks only, with no net line change to the sections below. `runs/README.md`
lost nine lines, all inside `## Retention`.
