# Run ledgers

One directory per slice: `<YYYY-MM-DD>-<slug>/`.

This is where a run's state actually lives — not in the orchestrator's context,
which compacts and restarts and loses things. `run.md` is the ledger; every
other file is an artifact written by the agent that produced it, so that
relaying a specialist's judgment is a filesystem operation rather than a
paraphrase.

Shape and rules: `../PROTOCOL.md` § "The run ledger".

Runs are committed. A closed run is the record of why the code looks the way it
does — which gates ran, what was requested and refused, which pack premises
turned out to be false. That is worth more than the disk it costs.
