#!/usr/bin/env bash
# Builds a bound los-tres workspace in the current (empty) eval directory, with
# run artifacts taken from the local corpus.
#   $1   los-tres commit the workspace starts from
#   $2+  "<run-id>/<file>" paths under <agenticRoot>/corpus/los-tres/runs to
#        copy into the workspace's agentic/runs/, under the same run id
#
# The corpus is local and gitignored (scripts/replay_corpus.py), so a case
# built on this runs only where the corpus holds that run. Run ids are kept as
# they were, so a path one artifact cites in another still resolves.
#
# As los-tres.sh: the repo is checked out as it was, the profile and packs are
# today's (they are what a network change is measured against), and the
# network's own files come along because reading outside the workspace is not
# reliable in an eval.
set -euo pipefail
INV=/c/projects/investments
CORPUS=$INV/.agentic/corpus/los-tres/runs
commit=$1; shift

git clone --quiet --no-checkout "$INV/los-tres" .
git checkout --quiet "$commit"
rm -rf agentic
cp -r "$INV/los-tres/agentic" agentic
rm -rf agentic/runs
mkdir -p agentic/runs
for f in "$@"; do
  [ -f "$CORPUS/$f" ] || { echo "corpus has no $f - see scripts/replay_corpus.py --add" >&2; exit 1; }
  mkdir -p "agentic/runs/$(dirname "$f")"
  cp "$CORPUS/$f" "agentic/runs/$f"
done
mkdir -p .agentic-root/plugins/agentic-core/.claude-plugin
cp -r "$INV/.agentic/PROTOCOL.md" "$INV/.agentic/protocol" "$INV/.agentic/scripts" .agentic-root/
cp "$INV/.agentic/plugins/agentic-core/.claude-plugin/plugin.json" .agentic-root/plugins/agentic-core/.claude-plugin/
printf '{\n  "agenticRoot": ".agentic-root",\n  "project": "los-tres",\n  "projectDir": "agentic"\n}\n' > .agentic.json
