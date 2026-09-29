# Pack corrections — 2026-09-24-remove-multiplayer

- `architecture.md` — from `03-technical-plan.md`: requires calling `mattpocock-skills:codebase-design` on every DESIGN pass (§ Design pass checklist, § Technique skills); the Skill tool returned "Unknown skill: mattpocock-skills:codebase-design" in this session, so the call could not be made as written.
- `project.md` § Skills / `Impact/CLAUDE.md` — from `03-technical-plan.md`: both state `.claude/settings.json` enables `mattpocock-skills` for every dispatched lane; that premise did not hold in this session. Replace with: "confirm before relying on it; may be session-specific rather than a repo-wide drift."
