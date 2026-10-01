# Pack corrections — 2026-09-24-remove-multiplayer

- `architecture.md` — from `03-technical-plan.md`: requires calling `mattpocock-skills:codebase-design` on every DESIGN pass (§ Design pass checklist, § Technique skills); the Skill tool returned "Unknown skill: mattpocock-skills:codebase-design" in this session, so the call could not be made as written.
- `project.md` § Skills / `Impact/CLAUDE.md` — from `03-technical-plan.md`: both state `.claude/settings.json` enables `mattpocock-skills` for every dispatched lane; that premise did not hold in this session. Replace with: "confirm before relying on it; may be session-specific rather than a repo-wide drift."

## Orchestrator check, 2026-10-01

Both entries above rest on the same premise, and it is false as a repo fact.
`C:\projects\impact\.claude\settings.json` `enabledPlugins` carries
`"mattpocock-skills@claude-plugins-official": true` alongside
`"agentic-core@agentic": true`, and `mattpocock-skills:codebase-design` resolves in
this session. So `project.md` § Skills and `Impact/CLAUDE.md` are correct and must not
be weakened to "confirm before relying on it" — what `03-technical-plan.md` hit was a
session-local marketplace failure, not drift.

What the close-out docs dispatch should do with them: **do not apply either as
written.** Record the session-local failure where it belongs instead — a lane that
cannot load a skill its pack mandates says so in `skill_calls:`, which is the field
PROTOCOL.md § 7 already names for exactly this. Neither pack file changes.
