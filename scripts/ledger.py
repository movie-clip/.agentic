#!/usr/bin/env python3
"""Apply one head's worth of run-ledger updates in a single call.

    python scripts/ledger.py <run_dir> --row "05 | quant-audit | AUDIT | quantitative-researcher | opus | 05-quant-audit.md | DONE | FAIL" --next "dispatch CR-1 to frontend"

Ops, applied together in one write. Each mirrors a table the ledger already
has, so there is no second vocabulary to learn - the cells are the cells.

    --row    "<nn> | lane | mode | agent | model | artifact | status | verdict"
    --next   "<the single next action>"
    --set    <field>=<value>   status phase plan budget story blocked_on gates
    --phase  "<phase> | <lane> | <state>"
    --open   "<kind> | <from> | <ref> | <one-line> | <state>"
    --close  "<ref> | <absorbed by>"

Exit 0 = written and the ledger is consistent. 1 = written, and the ledger now
says something inconsistent (the problems are printed; fix them on the next
call). 2 = nothing written, usage error.

Why this exists, measured rather than assumed. Across the four runs closed on
2026-09-12 the orchestrator made 107 separate edits to four `run.md` files -
61 of them to one ledger over 14 dispatches. By field, that run was: `spent` 18,
Artifacts row 16, Open/Closed 9, Phases 5, plan/status 4, Rounds 4, Replans 3.
Three of those classes fire on *every* head, which is the cost this collapses.

`spent:` is not an op. It is derived from the Artifacts rows on every write,
because `check_report.check_budget` already requires the two to be equal - so
typing it is copying a number the file can count, and the 18 edits above are
what copying it cost. This is the rule `--emit-head` follows for the head's
counts, one table over: derive it, do not write it.

Rounds and Replans are deliberately absent. They are prose rows written a
handful of times per run, and a flag for each would grow this surface past the
thing it replaces.

Nothing here re-states a ledger rule. After the write the file is handed to
`check_report.check_ledger(..., closed_only=True)` - the same battery close-out
runs, minus the gate check that cannot answer mid-run - so a malformed row, a
budget passed without a `## Replans` row, or a `CLOSED` run still naming a next
dispatch surfaces at the dispatch that caused it rather than at close-out.

Dependency-free, like the validator it calls.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_report as cr


class Usage(Exception):
    """A bad invocation. Nothing is written."""


# The ledger header, in the order `protocol/orchestrator.md` section 1 writes
# it. Used to place a field that is not in the file yet.
HEADER_ORDER = ["request", "agentic_root", "project", "story", "status",
                "phase", "plan", "budget", "spent", "blocked_on", "next",
                "gates"]
# `request` and `agentic_root` are written once at intake and never edited -
# `agentic_root` in particular is the string every later path is built from.
# `spent` is derived. Everything else is a field a dispatch can legitimately
# move.
SETTABLE = {"status", "phase", "plan", "budget", "story", "blocked_on",
            "next", "gates"}
DERIVED = {"spent"}
PAD = 14                       # `agentic_root:` plus one space, the widest key

TABLES = {
    "Phases":    ["phase", "lane", "fires when", "state"],
    "Artifacts": ["#", "lane", "mode", "agent", "model", "artifact", "status",
                  "verdict"],
    "Open":      ["kind", "from", "ref", "one-line", "state"],
    "Closed":    ["kind", "from", "absorbed by", "one-line"],
}
# Section order in the ledger, so a table this script has to create lands where
# a reader expects it rather than at the end of the file.
SECTIONS = ["Phases", "Artifacts", "Open", "Closed", "Rounds", "Replans"]


# --------------------------------------------------------------- primitives

def _table_of(what: str) -> str:
    return {"row": "Artifacts", "phase": "Phases", "open": "Open",
            "close": "Open"}[what]


def cells_of(value: str, n: int, what: str) -> list[str]:
    """Split a `|`-separated op value into exactly n cells."""
    parts = [p.strip() for p in value.split("|")]
    # A leading or trailing pipe is how the ledger writes a row; accept the
    # shape the orchestrator is looking at rather than making it strip them.
    if parts and not parts[0]:
        parts = parts[1:]
    if parts and not parts[-1]:
        parts = parts[:-1]
    if len(parts) != n:
        raise Usage(f"--{what} takes {n} cells separated by `|`, got "
                    f"{len(parts)}: {value!r}\n"
                    f"    columns: {' | '.join(TABLES[_table_of(what)])}")
    return parts


def render(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def bounds(lines: list[str], heading: str) -> tuple[int, int] | None:
    """(index of `## <heading>`, index one past its last line), or None."""
    for i, ln in enumerate(lines):
        if ln.strip() == f"## {heading}":
            end = len(lines)
            for j in range(i + 1, len(lines)):
                if lines[j].startswith("## "):
                    end = j
                    break
            return i, end
    return None


def rows(lines: list[str], heading: str) -> list[tuple[int, list[str]]]:
    """(line index, cells) for each data row, header and rule dropped.

    Same parse as `check_report._ledger_table`, kept row-addressable so a row
    can be rewritten in place instead of the table being regenerated.
    """
    b = bounds(lines, heading)
    if b is None:
        return []
    start, end = b
    found = []
    for i in range(start + 1, end):
        s = lines[i].strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(c and set(c) <= {"-", ":"} for c in cells):
            continue                       # the |---|---| rule
        found.append((i, cells))
    return found[1:] if found else []


def ensure_table(lines: list[str], heading: str) -> None:
    """Create `## <heading>` with its header row if the ledger has none."""
    if bounds(lines, heading) is not None:
        return
    cols = TABLES[heading]
    block = ["", f"## {heading}", render(cols),
             "|" + "|".join("---" for _ in cols) + "|"]
    # Before the first section that sorts after this one, so the file keeps the
    # order section 1 documents.
    for nxt in SECTIONS[SECTIONS.index(heading) + 1:]:
        b = bounds(lines, nxt)
        if b is not None:
            lines[b[0]:b[0]] = block + [""]
            return
    while lines and not lines[-1].strip():
        lines.pop()
    lines.extend(block)


def append_row(lines: list[str], heading: str, cells: list[str]) -> None:
    ensure_table(lines, heading)
    b = bounds(lines, heading)
    assert b is not None
    start, end = b
    last = max(i for i in range(start + 1, end)
               if lines[i].strip().startswith("|"))
    lines.insert(last + 1, render(cells))


# ---------------------------------------------------------------------- ops

def set_field(lines: list[str], name: str, value: str) -> None:
    """Write `name: value`, keeping the file's own column alignment."""
    pat = re.compile(rf"^({re.escape(name)}:[ \t]*)")
    for i, ln in enumerate(lines):
        m = pat.match(ln)
        if m:
            lines[i] = m.group(1) + value
            return
    new = f"{name}:".ljust(PAD) + value
    later = (HEADER_ORDER[HEADER_ORDER.index(name) + 1:]
             if name in HEADER_ORDER else [])
    for nxt in later:
        for i, ln in enumerate(lines):
            if re.match(rf"^{re.escape(nxt)}:", ln):
                lines.insert(i, new)
                return
    for i, ln in enumerate(lines):
        if ln.startswith("## "):
            lines.insert(i, new)
            return
    lines.append(new)


def drop_field(lines: list[str], name: str) -> None:
    """`--set blocked_on=` removes the line.

    `check_header` reads a `blocked_on` left on a run that is no longer BLOCKED
    as a claim about a block that is over, so clearing one has to be sayable.
    """
    for i, ln in enumerate(lines):
        if re.match(rf"^{re.escape(name)}:", ln):
            lines.pop(i)
            return


def put_artifact(lines: list[str], cells: list[str]) -> None:
    """Write the Artifacts row for this slot, replacing any row already on it.

    Replacing rather than appending is what stops a correction to a slot from
    producing two accounts of it. A *retry* is a new slot, which section 1 is
    explicit about - so passing the same number twice is how a row gets
    corrected, never how a second attempt gets recorded.
    """
    num = cells[0]
    for i, existing in rows(lines, "Artifacts"):
        if existing and existing[0] == num:
            lines[i] = render(cells)
            return
    append_row(lines, "Artifacts", cells)


def put_phase(lines: list[str], phase: str, lane: str, state: str) -> None:
    """Set the `state` cell of one `## Phases` row.

    Never appends. The table is the project's, copied from `phases.md` at
    intake; a phase this script could invent is a phase no profile declared.
    """
    for i, cells in rows(lines, "Phases"):
        if len(cells) >= 4 and cells[0] == phase and cells[1] == lane:
            cells[3] = state
            lines[i] = render(cells)
            return
    have = ", ".join(f"{c[0]} | {c[1]}" for _, c in rows(lines, "Phases")
                     if len(c) >= 2) or "none"
    raise Usage(f"no `## Phases` row for {phase!r} | {lane!r}. The table is "
                f"copied from the project's phases.md at intake and this "
                f"script does not add to it.\n    rows: {have}")


def put_open(lines: list[str], cells: list[str]) -> None:
    """Append an `Open` row, or update the one already holding this fact.

    Section 1's `One fact, one row`: the same finding reaches the orchestrator
    from the lane that hit it and again from a later pass. Keyed on
    (`from`, `ref`), which is that rule's own test.
    """
    for i, existing in rows(lines, "Open"):
        if (len(existing) >= 3 and existing[1] == cells[1]
                and existing[2] == cells[2]):
            lines[i] = render(cells)
            return
    append_row(lines, "Open", cells)


def close_open(lines: list[str], ref: str, absorbed: str) -> None:
    """Move an `Open` row to `## Closed`, dropping its `state` column.

    Section 1: a row leaves `Open` by being absorbed or dismissed, and being in
    `Closed` *is* the state - so the column does not travel with it.
    """
    found = [(i, c) for i, c in rows(lines, "Open")
             if len(c) >= 4 and c[2] == ref]
    if not found:
        found = [(i, c) for i, c in rows(lines, "Open")
                 if len(c) >= 4 and ref in c[2]]
    if not found:
        have = "; ".join(c[2] for _, c in rows(lines, "Open") if len(c) >= 3)
        raise Usage(f"no `Open` row whose ref is or contains {ref!r}\n"
                    f"    refs: {have or 'the table is empty'}")
    if len(found) > 1:
        raise Usage(f"{ref!r} matches {len(found)} `Open` rows - name the ref "
                    f"exactly:\n    "
                    + "\n    ".join(c[2] for _, c in found))
    i, cells = found[0]
    lines.pop(i)
    append_row(lines, "Closed", [cells[0], cells[1], absorbed, cells[3]])


def derive_spent(lines: list[str]) -> int:
    n = len(rows(lines, "Artifacts"))
    set_field(lines, "spent", str(n))
    return n


# -------------------------------------------------------------------- shell

KNOWN = ("--row", "--next", "--set", "--phase", "--open", "--close")


def parse(argv: list[str]) -> tuple[Path, list[tuple[str, str]]]:
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        raise Usage(__doc__ or "")
    target = Path(argv[1])
    ledger = target / "run.md" if target.is_dir() else target
    if not ledger.is_file():
        raise Usage(f"no ledger at {ledger}")
    ops: list[tuple[str, str]] = []
    i = 2
    while i < len(argv):
        flag = argv[i]
        if flag not in KNOWN:
            raise Usage(f"unknown op {flag!r} - one of {', '.join(KNOWN)}")
        if i + 1 >= len(argv):
            raise Usage(f"{flag} takes a value")
        ops.append((flag[2:], argv[i + 1]))
        i += 2
    if not ops:
        raise Usage("no ops given - nothing to write")
    return ledger, ops


def apply(lines: list[str], ops: list[tuple[str, str]]) -> None:
    """Rows first, then the derived count, then the header fields.

    Order matters exactly once: `spent` is counted after `--row` has landed.
    """
    for op, value in ops:
        if op == "row":
            put_artifact(lines, cells_of(value, 8, "row"))
        elif op == "phase":
            put_phase(lines, *cells_of(value, 3, "phase"))
        elif op == "open":
            put_open(lines, cells_of(value, 5, "open"))
        elif op == "close":
            close_open(lines, *cells_of(value, 2, "close"))
    derive_spent(lines)
    for op, value in ops:
        if op == "next":
            set_field(lines, "next", value)
        elif op == "set":
            if "=" not in value:
                raise Usage(f"--set takes <field>=<value>, got {value!r}")
            name, _, val = value.partition("=")
            name, val = name.strip(), val.strip()
            if name in DERIVED:
                raise Usage(f"`{name}` is derived from the Artifacts rows on "
                            f"every write, not set - pass `--row` and it "
                            f"follows")
            if name not in SETTABLE:
                raise Usage(f"`{name}` is not a settable header field - one "
                            f"of {', '.join(sorted(SETTABLE))}")
            if val:
                set_field(lines, name, val)
            else:
                drop_field(lines, name)


def advisories(ledger: Path) -> list[str]:
    """The one thing `check_budget` cannot say: how close the hard stop is.

    It speaks at `spent > budget` and again at twice the original. Between
    those two is the whole of a run's late middle, where the orchestrator is
    deciding whether to spend another dispatch and the ledger it is writing
    already knows the answer.
    """
    text = ledger.read_text(encoding="utf-8")
    budget = cr._leading_int(cr._ledger_field(text, "budget"))
    spent = cr._leading_int(cr._ledger_field(text, "spent"))
    if budget is None or spent is None:
        return []
    original, _ = cr._budget_chain(cr._ledger_table(text, "Replans"))
    original = original or budget
    if spent < budget:
        return []
    return [f"spent {spent} of budget {budget}; the hard stop is "
            f"{2 * original} (twice the original {original})"]


def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    try:
        ledger, ops = parse(argv)
    except Usage as e:
        print(e)
        return 2

    # `newline=""` on both ends, so the ledger keeps the line endings it had
    # rather than whatever this platform defaults to. The four closed runs are
    # LF in the working tree while the checked-out `.md` beside them are CRLF,
    # so neither can be assumed: converting one would show the whole file as
    # changed and bury the row that actually moved.
    with open(ledger, encoding="utf-8", newline="") as fh:
        raw = fh.read()
    crlf = raw.count("\r\n")
    nl = "\r\n" if crlf > (raw.count("\n") - crlf) else "\n"
    lines = raw.replace("\r\n", "\n").split("\n")
    try:
        apply(lines, ops)
    except Usage as e:
        print(e)
        return 2
    with open(ledger, "w", encoding="utf-8", newline="") as fh:
        fh.write(nl.join(lines))

    print(f"wrote {ledger}")
    problems = cr.check_ledger(ledger, closed_only=True)
    for a in advisories(ledger):
        print(f"  ~ {a}")
    if problems:
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"  ok ({cr.LEDGER_CHECKS})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
