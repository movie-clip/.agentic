# Run ledgers

One directory per slice: `<YYYY-MM-DD>-<slug>/`.

This is where a run's state actually lives — not in the orchestrator's context,
which compacts and restarts and loses things. `run.md` is the ledger; every
other file is an artifact written by the agent that produced it, so that
relaying a specialist's judgment is a filesystem operation rather than a
paraphrase.

Shape and rules: `../../../protocol/orchestrator.md` § 1 "The run ledger".

## Retention

Pruned at close-out once the lesson is in the protocol, and cited afterward by
run id, never by path — this is a network-wide policy, not a datoro-specific
one; see `projects/portfolio/runs/README.md` for the full statement of it.
