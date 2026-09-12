# Run ledgers

One directory per slice: `<YYYY-MM-DD>-<slug>/`.

This is where a run's state actually lives — not in the orchestrator's context,
which compacts and restarts and loses things. `run.md` is the ledger; every
other file is an artifact written by the agent that produced it, so that
relaying a specialist's judgment is a filesystem operation rather than a
paraphrase.

Shape and rules: `../../../protocol/orchestrator.md` § 1 "The run ledger".

## Retention

Runs are committed, and **closed runs are pruned once what they taught is in the
protocol.** A run earns its disk while it is open, while its work is
uncommitted, or while it is the evidence for a change not yet made. After that
it is a transcript of a decision already encoded in `PROTOCOL.md`,
`protocol/`, the profile or a capability pack — and a reader who needs it can
get it from git history.

So: **cite a pruned run by its id, never by a path.** `CHANGELOG.md` names
run ids as provenance for every version entry and opens none of them; that is
the durable form. A capability pack or a protocol file that tells a lane to
*read* a run artifact has a dangling reference the moment that run is pruned,
and the claim it was supporting has to stand on its own instead.
