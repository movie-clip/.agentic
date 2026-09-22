REPORT 2026-09-22-bind-impact/02

status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   claude plugin validate C:\projects\investments\.agentic\plugins\agentic-core
  result:    PASS
  detail:    Anchor: protocol/authoring.md rule text (subject is a project profile and its packs, not authoring.md itself), plus the eleven `tools:` lines under plugins/agentic-core/agents/ for rule 7. Manifest validation passed. Round 2 over 4 files: 4/4 round-1 findings satisfied, 0 new findings, 0 regressions.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - I did not open `C:\projects\impact`. Every claim these four files make about that repo's paths, scripts and packages remains unverified by me — authoring, not fact, per the order's non_goals.
  - Round 1's `risks` 2-4 (triplicated package chain, `runs/README.md` retention pointer, `.\Tools\` vs `Tools/` path form) were not re-examined; none of the four edits touched them and they remain open as recorded.

## Orchestrator brief

- Verdict: PASS. All four round-1 findings are satisfied by the edits actually made, in the files round 1 named.
- FINDING 1 (BLOCKING) is closed: `product.md:3-4` now matches `producer.md:4`, and § Finding precedent names `git log -S`.
- SHOULD_FIX 1-3 are all closed by index moves; no `Open` row is carried forward from this report.
- Regression: all four `## Index` blocks still complete and non-duplicating after the three moves; no new tool-premise or layer violation introduced.
- Sections: § Finding-by-finding · § Regression check.

## Finding-by-finding

| Round-1 finding | Edit found | Verdict |
|---|---|---|
| FINDING 1 (BLOCKING) — `product.md:3-4` asserts `producer` has no `Bash` | `product.md:3-4` now reads "Read-only lane — `Read`/`Glob`/`Grep` over the repo, plus `Bash` for git history. You do not edit the repo; the only file you write is your report." — the proposed wording, verbatim. `product.md:33-36` adds "**and use `git`** — `git log -S<term>` / `git log --oneline -- <path>`" to the precedent check, with the reason `producer.md:50-52` gives. | satisfied |
| SHOULD_FIX 1 — `testing.md:11` files an always-true condition as conditional | "Running the suite" moved into the always-read line, `testing.md:7-8`; the row is gone. Two conditional rows remain, both evaluable from the order alone. | satisfied |
| SHOULD_FIX 2 — `project.md:141` "Any lane may reach for the `unity-cli` skill" | `project.md:140` now reads "Any lane with `Bash` may reach for the `unity-cli` skill". `scout`, `story-author` and `docs-engineer` are no longer addressed; the sentence no longer disagrees with `docs.md:5-7`. | satisfied |
| SHOULD_FIX 3 — Unity CLI sections gated on a condition only their own content answers | Both moved to always-read: `backend.md:13` ("Unity CLI for fast iteration") and `project.md:38` ("Unity CLI and the unity-agent-plugin skills"). Both conditional rows are gone. | satisfied |

FINDING 1's rule (`authoring.md` § "A pack may not instruct a tool the lane
does not have") is now satisfied in both directions for this pack: the tool
claimed is the tool granted, and the command written is one `producer` can run.

## Regression check

Nothing round 1 passed in these four files now fails.

| Check | Result after the edits |
|---|---|
| `claude plugin validate plugins/agentic-core` | passes — manifest validation clean |
| `## Index` present | `project.md:32`, `backend.md:8`, `testing.md:5`, `product.md:6` — all four intact |
| Index complete, no section named twice | `project.md` 6/6 (3 always-read + 3 rows), `backend.md` 7/7 (5 + 2), `testing.md` 5/5 (3 + 2), `product.md` 3/3 (2 + 1); every `##` heading appears exactly once |
| Always-read vs conditional | the six surviving conditional rows are all evaluable from the order before reading the section (crate pipeline, player/skin flow, single fixture, EditMode vs PlayMode, delivery model, lane routing, `frontend`/`quant`); gotchas, guardrails and weak spots remain always-read |
| Tool premises | re-derived from the agent files, not from round 1: `producer` has `Bash` (`producer.md:4`), `test-engineer` has `Bash` (`test-engineer.md:4`), `backend-engineer` has `Bash` (`backend-engineer.md:4`) — every `git`, `dotnet`, `powershell` and `unity` command in the four files belongs to a lane that can run it |
| Four-layer split | no message shape, report block or role definition added by any of the four edits; `product.md:3-4` states this lane's mutation boundary in this repo, the same shape as `docs.md:5-7`, not a copy of a protocol shape |
| Lane routing table | `project.md:92-103` unchanged — ten rows, nine agents, all resolving under `plugins/agentic-core/agents/` |
| MCP | `project.md:157-160` still denies the grant; no `mcp__project__*` tool is named anywhere in the four files |
| Written for a model | no provenance or change history introduced; the three index edits shortened two tables rather than adding prose |
| Bullet length | no bullet in the four files exceeds `authoring.md`'s 200-character instruction limit |
