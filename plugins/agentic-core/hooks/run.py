#!/usr/bin/env python3
"""Launcher for the network's hooks, shipped in the plugin.

    python run.py <hook script name, without .py>

The hook scripts live in the network root (`<agenticRoot>/scripts/hooks/`),
not in the plugin: they import check_report.py and read the agents directory.
A plugin may be loaded from a cache copy, so this finds the root the way the
orchestrator does - from the bound repo's `.agentic.json`.

Silent, exit 0, in every case that is not "a bound repo, with that script
present, which does not already wire it itself":

- no `.agentic.json` at or above the project directory: the plugin is enabled
  in a repo the network does not drive;
- the repo's own `.claude/settings.json` or `settings.local.json` names the
  same script. Those entries predate this launcher; running both would check
  every report twice and spend the two-hold bound in one handback;
- the root or the script is missing, or anything here raises. A launcher that
  can fail is a launcher that can block every tool call in a session.

Otherwise the script's stderr and exit code are passed through unchanged.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def _binding(start: Path) -> Path | None:
    for folder in (start, *start.parents):
        if (folder / ".agentic.json").is_file():
            return folder
    return None


def _wired_by_repo(repo: Path, script: str) -> bool:
    for name in ("settings.json", "settings.local.json"):
        try:
            text = (repo / ".claude" / name).read_text(encoding="utf-8")
        except OSError:
            continue
        if script in text:
            return True
    return False


def main(argv: list[str]) -> int:
    if len(argv) != 1 or not argv[0].replace("_", "").isalnum():
        return 0
    script = argv[0] + ".py"
    raw = sys.stdin.buffer.read()
    try:
        payload = json.loads(raw.decode("utf-8", errors="replace"))
    except ValueError:
        payload = {}
    start = os.environ.get("CLAUDE_PROJECT_DIR") or (
        payload.get("cwd") if isinstance(payload, dict) else None)
    if not start:
        return 0
    repo = _binding(Path(start).resolve())
    if repo is None or _wired_by_repo(repo, script):
        return 0
    binding = json.loads((repo / ".agentic.json").read_text(encoding="utf-8"))
    root = (repo / str(binding.get("agenticRoot") or "")).resolve()
    target = root / "scripts" / "hooks" / script
    if not target.is_file():
        return 0
    done = subprocess.run([sys.executable, str(target)], input=raw,
                          stderr=subprocess.PIPE, check=False)
    sys.stderr.buffer.write(done.stderr)
    return done.returncode


if __name__ == "__main__":
    try:
        code = main(sys.argv[1:])
    except Exception:  # noqa: BLE001
        code = 0
    sys.exit(code)
