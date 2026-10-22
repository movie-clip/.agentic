---
name: grill-plan
description: Use this at every human stop of an orchestrate-feature run that hands the human a planning artifact - the producer's delivery brief at framing, the story draft at specification, a UX spec whose direction is new or changed, and the design phase's plan at the build go when design fired. Maps the artifact's decisions as a tree, sends unsourced claims and silent assumptions back to the lane that made them, settles fact questions through the ground-truth phase, and only then puts the remaining decisions to the human in numbered rounds with a recommended answer each, writing every ruling to decisions.md.
argument-hint: the planning artifact to grill, by run-dir path
---

# Grill plan

You are the orchestrator, at a human stop. This skill is the **sequence** for
turning a planning artifact into rulings. It assumes `orchestrate-feature` is
loaded and `orchestrator.md` read; the rules it applies are cited, not
restated. Every `§` below without a file name is a section of this skill.

**Why the orchestrator does this and not the lane.** A dispatched lane runs to
completion and cannot wait for the human's answer, so a lane surfaces
questions and you ask them. The lane's judgment stays the lane's: you question
it by work order, never by rewriting it (`orchestrator.md` § 7).

## 1. Build the tree

Read the artifact the way `orchestrator.md` § 4 says: its
`## Orchestrator brief` and the sections it names, plus its decisions section
in full (`## Open decisions` in a brief or story draft, `decisions` in the
design plan, `Design system` in a UX spec whose `direction` is `new` or
`changed`). List every decision the artifact makes or depends on —
placement, scope, sequence, story split, contract shape, what is left out —
and for each, the decisions it hangs off. A node whose parent is unsettled is
not asked yet.

## 2. Sort every node

| The node is | Because | It goes to |
|---|---|---|
| **settled** | the artifact cites a path, a test result or a `decisions.md` entry for it | nowhere; leave it |
| **a fact** | the run needs a claim about the repo and nothing read this turn or named in `inputs` sources it | the `ground-truth` phase (`orchestrator.md` § 6), filled by the lane the profile's `phases.md` names |
| **a lane gap** | the artifact asserts it without a source, or chose silently where its own role says to escalate | the same lane, re-dispatched as the next slot, with the numbered questions in the order's request |
| **a human decision** | it is placement, priority, scope, a trade-off, or anything the lane escalated | the human, in § 4's rounds |

A fact node turns a `ground-truth` row recorded `not triggered` into a
triggered one, which is a re-plan (`orchestrator.md` § 3).

A node settled by an earlier `decisions.md` entry stays settled. If a lane's
answer contradicts it, that is a re-plan (`orchestrator.md` § 3), and the human
hears about it; you do not reopen the ruling yourself.

When you are unsure whether a node is a lane gap or a human decision, it is a
human decision.

## 3. Facts and lane gaps first

Dispatch the fact and lane-gap orders before the human round that depends on
them; `orchestrator.md` § 3, step 4, permits these at the stop. Each one is
dispatched and recorded as `orchestrator.md` § 1 and § 3 say.

A lane-gap order asks; it does not answer. Quote no preferred answer, and name
the artifact section each question came from in `inputs`. The lane returns a
revised artifact as a new slot. Build the tree again from it (§ 1): nodes the
revision settled drop out, nodes it raised join, and nodes a `decisions.md`
entry settled stay settled (§ 2). The revision gets no lane-gap round of its
own: a lane gap it leaves open or raises is handled as the gaps below are, and
a fact node it raises goes to `ground-truth` (§ 2).

One lane-gap round per human stop, however many slots the revisions take. Gaps
still open after it become human questions, each labelled with what the lane
said.

Do not hold the whole round for these dispatches: ask the human the questions
that do not depend on them now.

## 4. Human rounds

Ask the frontier, which is every human decision whose parents are settled, in
one message:

```
❓ **Q1** - **<title>**: <the question, with the options the artifact names>
   raised by: <artifact> § <section>

➡️ <recommended answer> — <whose: the lane's, or yours, with one line of why>
```

- Word each question so "yes" accepts the recommendation.
- Recommend the lane's answer when it gave one. If you recommend against it,
  say so and cite why.
- A question that depends on another one still open in this round waits for
  the next round.

After each round, write one `decisions.md` entry per decision the human
resolved, in their words, before anything else (`orchestrator.md` § 5).
Recompute the frontier and ask again.

## 5. Done

The grill is done when the frontier is empty: every node is settled, ruled, or
recorded by the human as left open on purpose. Then:

- If a ruling changes what the artifact says (placement, sequence, the stories,
  the contract), re-dispatch its lane as the next slot with the rulings in
  `inputs` before the next phase.
- Otherwise the stop's own go applies, and the next order names the
  `decisions.md` entries in `inputs`.

If § 1 finds nothing open, say so in one line and take the stop's go as
usual. A clean artifact needs no ceremony.
