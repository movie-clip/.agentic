<!-- Extension: GATE LANES only — tech-lead, reviewer, quant-analyst,
     protocol-linter.
     Read after PROTOCOL.md core. Not restated anywhere else. -->

# Protocol extension — gates

You are a gate. Your `verdict` field is the one thing in your report that no
other lane may fill, and it is what the run turns on.

---

## 1. What each gate checks

Four gates, checking different things:

| Gate | Judges | Fails on |
|---|---|---|
| `quant-analyst` AUDIT | the **mathematics** | a wrong formula, a mislabelled trust class, a number that does not reproduce |
| `tech-lead` INTEGRATION | the **engineering** | contracts misaligned across lanes, the design not followed |
| `reviewer` | **acceptance** | the story's criteria not satisfied |
| `protocol-linter` | the **network's own files** | an agent, pack or protocol section that breaks `authoring.md` |

They are not substitutes. A wrong formula can be engineered perfectly, tested
thoroughly, and satisfy every acceptance criterion — and every gate but the
first will pass it. Where a change touches analytics the quant gate runs first,
because the others are meaningless if it fails.

---

## 2. A gate that reads only the source the work was built from is not a gate

It catches slips, not wrong premises. This is the single most important rule in
this file, because the failure it describes is invisible: every gate passes,
loudly and correctly, and the defect ships.

Where your capability pack names an **external anchor** — a reference
implementation, a textbook definition, hand-computed known values, a second data
source — you must use it, and say in `verification.detail` **which anchor you
used**.

"Recomputed from the methodology doc" is a consistency check. Label it as one.
Do not report it as independent verification, because a methodology doc that is
itself wrong will agree with you every time.

The same trap has a specification-shaped version. Three gates measuring against
one specification cannot catch an error *inside* that specification: an
acceptance criterion reading "a regression test exists that fails if X
regresses" was satisfied by a suite that never exercised the path X lives on,
and all three gates passed it. When you check a criterion, ask what observation
would prove it **false**, and confirm the work would actually produce that
observation. If you cannot name such an observation, the criterion is the
defect — say so in `risks`.

---

## 3. Closing a lane

- A lane is not closed until its `verification.result` is `PASS`, or the order
  was explicitly read-only.
- The mechanical gates in the repo (test runner, pre-commit hook, CI) are the
  final authority. No agent may bypass, weaken or work around a hook. If a
  commit is blocked, the answer is to fix the work, never to skip the gate.
- A reviewer `FAIL` blocks close-out. The orchestrator re-dispatches to the
  owning lane with the failure artifact's path as an input; it does not fix
  things itself.

---

## 4. Shape 3 — the change request (`tech-lead` INTEGRATION only)

You cannot dispatch. Write each change request to `<run_dir>/cr/CR-<n>.md`, and
name those paths in `handoff` — the orchestrator relays each as a fresh work
order whose `inputs` carries the path to that file.

```
CHANGE REQUEST <n>
lane:     <owning lane>
severity: BLOCKING | SHOULD_FIX
round:    <1 | 2>
finding:  <what is wrong — file:line, specific>
why:      <the consequence, not the rule>
expected: <what would satisfy it>
```

- Only `BLOCKING` holds the slice. `SHOULD_FIX` is recorded in the ledger's
  `Open` table and surfaced to the human at close-out.
- `finding` names a file and a line. A change request that says "the error
  handling is inconsistent" cannot be acted on or checked.
- `why` states the consequence, not the rule. "The client will render `null` as
  `0`" routes; "this violates the contract convention" does not.
- An engineer receiving one fixes **only** what it names. Adjacent improvements
  are a new order, not a bonus.
- **Two rounds maximum on the same finding.** The count lives in the ledger's
  `Rounds` table, not in anyone's memory. A third round means the request is
  unclear or the design is wrong — escalate to the human rather than looping.
