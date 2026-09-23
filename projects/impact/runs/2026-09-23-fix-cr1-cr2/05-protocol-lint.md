REPORT 2026-09-23-fix-cr1-cr2/05
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   claude plugin validate C:\projects\investments\.agentic\plugins\agentic-core
  result:    PASS
  detail:    Validation passed, 0 errors across plugin.json and all agent frontmatter. Anchors beyond the rule text: 02-test.md and 03-integration.md (independent 35/35 re-run) for PC-1's factual claim, and test-engineer.md's `tools:` line for rule 7. 8 pack bullets measured mechanically, max 182 chars vs the 200 ceiling.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - testing.md:36-37 calls 35 "the full Core suite"; 35 is the verified EditMode count and no report states the PlayMode Core count. A fact about the repo I did not open, not an authoring finding.
  - testing.md:69-71 restates this lane's verification bar, adjacent to PROTOCOL.md § 7. Pre-existing, untouched by PC-1, phrased as a lane bar not a shape, so not failed under "One rule, one home".
  - No `.agentic.json` at or above cwd; cwd is itself `<agenticRoot>`, so binding resolved by identity rather than the core § 1 walk. Not treated as BLOCKED because the root was unambiguous.

## Orchestrator brief

PASS. PC-1 applied verbatim and accurate to what CR-1's fix did; no authoring
regression elsewhere in the file. Nothing to route.

| Section | Contains |
|---|---|
| Findings by rule | the eight `authoring.md` rules, each with its result |
| PC-1 application | verbatim-match check, and the cross-check against 02-test.md / 03-integration.md |
| Gotchas bullet lengths | measured proof the prior run's round-2 fix still holds |

## Findings by rule

| # | Rule (`protocol/authoring.md`) | Result |
|---|---|---|
| 1 | The four-layer split | PASS — paths, commands and gotchas only; no message shape, no role definition. |
| 2 | One rule, one home | PASS — `-CoreOnly` behaviour stated once (lines 36-37); `-Filter`/`-testFilter` at 48-58 is the distinct raw-batchmode sense. One borderline in `risks`. |
| 3 | Model declared | N/A — capability pack, no frontmatter. Plugin validate passed for the agent files. |
| 4 | Effort declared | N/A — same. |
| 5 | Index block | PASS — `## Index` present; all five sections findable under the name a lane would search; no fact in two sections. |
| 6 | Always-read vs conditional | PASS — Gotchas, Running the suite and Definition of done are always-read; the two conditional sections ("only needs to prove one behaviour", "adding a new test and choosing which platform") are both evaluable from the order before reading. |
| 7 | Tool premises | PASS — every command is `powershell` or `dotnet`; `test-engineer.md` declares `tools: Read, Write, Edit, Glob, Grep, Bash, mcp__project__*`, so `Bash` covers all of them. |
| 8 | Written for a model | PASS — no provenance or change history; mapping content is tabular; all 8 bullets carry one fact each and measure 89-182 chars. |

## PC-1 application

pack-corrections.md's `replacement` string, unescaped, is present verbatim at
testing.md:36-37. The stale text it replaced (`-CoreOnly` mapping to
`-testFilter "Core"`) no longer appears anywhere in the file.

The replacement is accurate to what CR-1's fix actually did: 02-test.md
§ changed records `Run-UnityTests.ps1` switching `-CoreOnly` to
`-testCategory "Core"` with `-Filter` still mapping to `-testFilter`, and
03-integration.md re-ran `-CoreOnly` itself rather than trusting that report,
getting `testcasecount="35" total="35" passed="35"`. Both halves of the pack
sentence — the mechanism and the 35 — therefore rest on an observation that
would have contradicted them had the fix not landed.

## Gotchas bullet lengths

Measured by joining each bullet's continuation lines and collapsing whitespace,
against the 200-character instruction-file ceiling in "Writing for the reader
you actually have":

| Line | Chars |
|---|---|
| 17 | 182 |
| 20 | 136 |
| 22 | 147 |
| 24 | 165 |
| 27 | 141 |

The three previously over-length Gotchas bullets remain split and within the
ceiling. PC-1's text is prose in **Running the suite**, not a bullet, and at
~140 characters would clear the ceiling regardless; it reintroduces nothing.
