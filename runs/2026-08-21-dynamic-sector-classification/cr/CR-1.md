CHANGE REQUEST 1
lane:     backend
severity: BLOCKING (MATERIAL finding from quant-audit — FAIL verdict)
source:   10-quant-audit.md, FINDING 1

finding:  services/quant-engine/app/instruments/registry.py:337-346 —
          attach_snapshot_metadata's pre-existing, untouched no-imported-instrument
          catch-all constructs Instrument(..., sector="Other", ...). Because "Other"
          is a truthy string, overview.py's new line
          `sector = instrument.sector or UNCLASSIFIED_SECTOR_LABEL` never reaches
          the UNCLASSIFIED_SECTOR_LABEL branch for this instrument. Independently
          reproduced: a one-position snapshot with no matching ImportedInstrument
          record yields `sector_allocation == [{'sector': 'Other', ...}]` through
          build_portfolio_overview().

why:      Violates AC9 ("never the string 'Other'") and the new methodology
          section's own stated contract rule ("no fourth outcome ... never
          silently folded into any named sector including 'Other'"). This path
          is reachable in practice — the project's own "Importer resilience
          rule" (financial-methodology.md) documents that a malformed/dropped
          statement record yields a position with no corresponding instrument
          record, which is exactly the condition this catch-all handles. A
          researcher would see a real position folded into a bucket literally
          named "Other" in a codebase whose own story report claims to have
          eliminated exactly that fabrication.

expected: Route this catch-all's sector through the same unresolved-outcome
          path as every other case this story defined: construct the catch-all
          Instrument with sector=None (classification_source stays None,
          consistent with 05-technical-plan.md's own stated intent for this
          branch — it was never meant to originate a real classification) and
          let overview.py's existing `instrument.sector or UNCLASSIFIED_SECTOR_LABEL`
          handle it, OR special-case it explicitly in overview.py if changing
          the catch-all's constructor is undesirable for another reason — your
          call which, but the observable outcome must be: a position with no
          matching ImportedInstrument record lands in the "Unclassified" bucket,
          never the literal string "Other".

non_goals:
  - do not touch anything else in registry.py or overview.py beyond what this
    fix requires — Finding 2 (MINOR, taxonomy-lookup case/whitespace
    normalization) is explicitly NOT part of this change request; it is
    carried separately as a should-fix, not blocking
  - do not re-litigate any other part of the merged T-37.1.1/T-37.1.2 diff —
    the audit confirmed the taxonomy map, identity gate, and trust-labeling
    are all correct
