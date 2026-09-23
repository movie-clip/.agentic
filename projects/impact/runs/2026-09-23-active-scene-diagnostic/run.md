# RUN 2026-09-23-active-scene-diagnostic
request:      Add a small diagnostic ECS system that logs a one-line message once, on world
              initialization, with the name of the currently active scene (something like
              "[Impact] Active scene — <sceneName>"). Pick the package it belongs in
              yourself, using the dependency-chain guardrail in the project profile, and add
              an EditMode test that proves it fires exactly once. This should be a short
              run — no design phase, no story — since it adds no cross-package contract; if
              you find it needs one, say why instead of just proceeding.

              Before any implementation or test work, confirm the Unity CLI path is live:
              run `unity pipeline list` and report its exact output. If it confirms a
              connected Editor, both the backend and test lanes must do their iteration
              through the `unity-cli` skill (`unity command eval` against the open Editor)
              rather than a cold batchmode boot — that is the thing this run exists to
              prove out. If `unity pipeline list` does not confirm a connected Editor,
              stop pretending otherwise: state that plainly in the report, fall back to
              batchmode (`dotnet build` + `Run-UnityTests.ps1`) explicitly, and say why the
              CLI path wasn't available (Editor not open, Pipeline package not responding,
              etc.) rather than silently proceeding on batchmode alone.

              Either way, the final verification gate still runs `Run-UnityTests.ps1`
              normally per the testing pack — unity-cli is for iteration, not a substitute
              for that gate. Report, per lane: whether unity-cli was actually reachable,
              what commands were run through it if so, and the final batchmode
              verification result.
agentic_root: C:\projects\investments\.agentic
project:      impact
story:        NONE
status:       CLOSED
phase:        build
plan:         v2
budget:       5 — build(3: backend, test, test-rerun after the Editor-lock blocker) +
              verify/integration(1) + close/docs(1); ground-truth not triggered (prior recon
              covers the area, cited), framing/specification/design not triggered, review not
              triggered (no story)
spent:        5
next:         none -- CLOSED
gates:        integration PASS -- 04 . review skipped (no story) . protocol-lint skipped (no lane emitted a pack_correction this run, pack-corrections.md never created)

## Phases
| phase | lane | fires when | state |
|---|---|---|---|
| ground-truth | recon | the request names an existing system/behaviour, or rests on an unverified claim about current behaviour | not triggered (2026-09-22-session-start-diagnostic/01-recon.md already covers athena.core's dependency chain, ISystem pattern, and the Application-World-vs-Local-World split in WorldBootstrap.cs; that run's own SessionStartDiagnosticSystem.cs at Impact/Packages/athena.core/Runtime/Systems/ is now a direct precedent for a second one-shot world-init diagnostic ISystem in the same package) |
| framing | product | the request is a new gameplay system or feature surface, or changes what an existing one is for | not triggered (a one-off diagnostic log system is not a feature surface and changes no existing system's purpose — same reasoning as the prior run) |
| specification | story | framing produced scope no approved brief covers, and the slice crosses more than one lane's contract | not triggered (single lane — backend — no cross-package contract; the user's own request is the specification per delivery model) |
| design | tech-lead (DESIGN) | the change crosses a package-boundary contract — a shared singleton/component shape, the crate/content pipeline, a new cross-package .asmdef reference | not triggered (confirmed by 01-backend.md contract_notes: UnityEngine.SceneManagement needs no new .asmdef reference -- Athena.Core.Runtime.asmdef already grants the full engine core module set -- and athena.core remains correct per the dependency-chain guardrail, no shared singleton/component shape touched) |
| build | backend, test | anything that edits Impact/Packages/**, Impact/Assets/**, Impact/Tools/**, or Impact/*.md | satisfied -- 01, 02, 03 |
| verify | integration | any build lane was dispatched | satisfied -- 04, PASS (36/36 Core, corrected -CoreOnly flag) |
| verify | review | the run carries a story whose acceptance criteria someone must accept | not triggered (no story) |
| close | docs | always | satisfied -- 05 (PACKAGE_DOCUMENTATION.md + PACKAGE_ARCHITECTURE.md reconciled); no pack corrections emitted, pack-corrections.md not created |

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | backend | -- | backend-engineer | sonnet | 01-backend.md | DONE | -- |
| 02 | test | -- | test-engineer | sonnet | 02-test.md | PARTIAL | -- |
| 03 | test | -- | test-engineer | sonnet | 03-test.md | DONE | -- |
| 04 | integration | INTEGRATION | tech-lead | sonnet | 04-integration.md | DONE | PASS |
| 05 | docs | -- | docs-engineer | sonnet | 05-docs.md | DONE | -- |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| risk | 04-integration | 04-integration.md sect risks (bullet 1) | prior run dir 2026-09-22-session-start-diagnostic is gone from disk entirely -- cr/CR-1.md the order pointed at does not exist; verified independently via 2026-09-23-fix-cr1-cr2 instead, no verification gap, but the historical run record for a CLOSED run is lost | CARRIED |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|
| blocked | 02-test | 03-test | new EditMode test written and code-reviewed but unrun -- Editor PID 19804 open blocks batchmode, Pipeline server unreachable blocks unity-cli, both verification paths dead simultaneously |

## Rounds
| finding | lane | round | of | caused by |
|---|---|---|---|---|

## Replans
| plan | because | change |
|---|---|---|
| v2 | spent reached budget (4 of 4) with close/docs still pending -- the original build(2) estimate did not anticipate the Editor-lock/Pipeline-unreachable blocker forcing a third build-phase dispatch (03, verification rerun) between test (02) and integration | budget 4 -> 5 |
