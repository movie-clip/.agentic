#!/usr/bin/env bash
# Builds a bound los-tres workspace in the current (empty) eval directory.
#   $1  los-tres commit the run started from
#   $2  past run whose input files the order cites (kept beside this script;
#       the run itself is pruned)
#   $3+ files from that run to copy into the workspace's run dir
#
# The repo is checked out as it was before the run. The profile and packs are
# taken from today's los-tres/agentic/, because those are what a merge changes:
# the lane table decides which agent fills each lane.
set -euo pipefail
INV=/c/projects/investments
commit=$1; run=$2; shift 2

git clone --quiet --no-checkout "$INV/los-tres/client" .
git checkout --quiet "$commit"
rm -rf agentic
cp -r "$INV/los-tres/client/agentic" agentic
rm -rf agentic/runs
mkdir -p "agentic/runs/eval-$run"
for f in "$@"; do
  cp "$(dirname "$0")/$run/$f" "agentic/runs/eval-$run/$f"
done
# Reading outside the workspace worked in one pilot run and was denied in
# another, so the network's own files come along. Agents and skills are
# loaded from the plugin, not from here.
mkdir -p .agentic-root
cp -r "$INV/.agentic/PROTOCOL.md" "$INV/.agentic/protocol" "$INV/.agentic/scripts" .agentic-root/
printf '{\n  "agenticRoot": ".agentic-root",\n  "project": "los-tres",\n  "projectDir": "agentic"\n}\n' > .agentic.json
