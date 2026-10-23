"""Regression suite for ledger.py.

    python scripts/test_ledger.py

Covers the four things a scripted ledger write can get wrong in ways nobody
notices: the surgical edit that is not surgical (line endings, alignment, rows
other than the target), the derivation that drifts from what `check_budget`
requires, the ops that must refuse rather than invent, and the post-write
battery that is the whole reason this runs a validator instead of a `sed`.
Dependency-free, like the thing it tests."""
import io
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ledger as lg

results = []


def check(name, cond, extra=""):
    results.append((name, cond, extra))
    print(f"  {'PASS' if cond else 'FAIL'}  {name}"
          f"{'  ' + str(extra) if extra and not cond else ''}")


MID = [
    "# RUN 2026-09-14-demo",
    "request:      demo",
    "agentic_root: C:/projects/investments/.agentic",
    "project:      portfolio",
    "story:        NONE",
    "status:       DISPATCHING",
    "phase:        build",
    "plan:         v1",
    "budget:       4 - design, two build lanes, integration",
    "spent:        1",
    "next:         dispatch backend",
    "gates:        integration pending",
    "",
    "## Phases",
    "| phase | lane | fires when | state |",
    "|---|---|---|---|",
    "| design | design | contract boundary crossed | satisfied - 01 |",
    "| build | backend | anything that edits the repo | pending |",
    "| verify | integration | any build lane dispatched | pending |",
    "",
    "## Artifacts",
    "| # | lane | mode | agent | model | artifact | status | verdict |",
    "|---|------|------|-------|-------|----------|--------|---------|",
    "| 01 | design | DESIGN | tech-lead | opus | 01-design.md | DONE | - |",
    "",
]


def fixture(lines=None, nl="\r\n", **extra):
    """A run dir holding one ledger, written with the given line ending."""
    d = Path(tempfile.mkdtemp())
    body = nl.join(lines if lines is not None else MID)
    with io.open(d / "run.md", "w", encoding="utf-8", newline="") as fh:
        fh.write(body)
    for name, text in extra.items():
        (d / name).write_text(text, encoding="utf-8")
    return d


def run(d, *args):
    r = subprocess.run([sys.executable, str(Path(lg.__file__)), str(d), *args],
                       capture_output=True, text=True, encoding="utf-8")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def raw(d):
    with io.open(d / "run.md", encoding="utf-8", newline="") as fh:
        return fh.read()


print("A - the write is surgical: endings, alignment, and nothing else moves")
d = fixture()
before = raw(d)
code, out = run(d, "--next", "dispatch integration")
after = raw(d)
check("CRLF in, CRLF out", after.count("\r\n") == before.count("\r\n"),
      f"{before.count(chr(13))} -> {after.count(chr(13))}")
check("exactly one line differs",
      sum(1 for a, b in zip(before.split("\r\n"), after.split("\r\n"))
          if a != b) == 1)
check("and it is `next:`", "next:         dispatch integration" in after,
      [x for x in after.split("\r\n") if x.startswith("next:")])
check("the header column alignment survives",
      "status:       DISPATCHING" in after)
d = fixture(nl="\n")
run(d, "--next", "x")
check("an LF ledger is not converted to CRLF", "\r" not in raw(d))

print("B - `spent` is derived from the Artifacts rows, never typed")
d = fixture()
code, out = run(d, "--row",
                "02 | backend | - | backend-engineer | sonnet | "
                "02-backend.md | DONE | -")
after = raw(d)
check("a new row lands in the Artifacts table",
      "| 02 | backend |" in after)
check("and `spent` follows the count without being passed",
      "spent:        2" in after,
      [x for x in after.split("\r\n") if x.startswith("spent:")])
check("which is exactly what check_budget requires",
      not any("Artifacts row(s)" in p for p in
              lg.cr.check_budget(d / "run.md")),
      lg.cr.check_budget(d / "run.md"))
code, out = run(d, "--set", "spent=9")
check("passing it anyway is refused, and nothing is written", code == 2)
check("with the derivation named", "derived from the Artifacts rows" in out,
      out)
check("the refusal really did not write", "spent:        2" in raw(d))

print("C - a row already on a slot is corrected, not duplicated")
d = fixture()
run(d, "--row", "01 | design | DESIGN | tech-lead | opus | 01-design.md | "
                "PARTIAL | -")
after = raw(d)
check("the slot is rewritten in place", after.count("| 01 | design |") == 1)
check("with the new status", "| PARTIAL | - |" in after)
check("and `spent` still counts one dispatch", "spent:        1" in after)

print("D - ops that must refuse rather than invent")
d = fixture()
code, out = run(d, "--row", "02 | backend | sonnet | 02-backend.md | DONE")
check("a row with the wrong column count is refused", code == 2)
check("and the refusal prints the columns the table has",
      "# | lane | mode | agent | model | artifact | status | verdict" in out,
      out)
code, out = run(d, "--phase", "framing | product | not triggered (x)")
check("a `## Phases` row the profile never declared is refused", code == 2)
check("and the refusal lists the rows that exist", "design | design" in out,
      out)
check("nothing was written by either refusal", "| 02 |" not in raw(d), raw(d))
code, out = run(d, "--bogus", "x")
check("an unknown op is refused", code == 2, out)
code, out = run(d, "--set", "budget")
check("a --set with no `=` is refused", code == 2, out)
code, out = run(d, "--set", "agentic_root=D:/elsewhere")
check("`agentic_root` is not settable - it is written once at intake",
      code == 2 and "not a settable" in out, out)

print("E - Open rows: one fact one row, and absorbed rows leave")
d = fixture()
run(d, "--open", "should_fix | 02-backend | schemas/holding.py | "
                 "sector nullable, client type lags | OPEN")
check("the `## Open` table is created when the ledger has none",
      "## Open" in raw(d) and "| kind | from | ref | one-line | state |" in raw(d))
run(d, "--open", "should_fix | 02-backend | schemas/holding.py | "
                 "sector nullable, client type lags | CARRIED")
after = raw(d)
check("the same (from, ref) updates that row instead of adding a second",
      after.count("schemas/holding.py") == 1, after)
check("with the new state", "| CARRIED |" in after)
run(d, "--open", "should_fix | 03-frontend | cards/Foo.tsx | unwired | OPEN")
check("a different ref is a different row",
      raw(d).count("| should_fix |") == 2)
code, out = run(d, "--close", "schemas/holding.py | 04-frontend")
after = raw(d)
check("closing moves the row out of `## Open`",
      after.split("## Closed")[0].count("schemas/holding.py") == 0, after)
check("into `## Closed`", "schemas/holding.py" not in after.split("## Closed")[0]
      and "| 04-frontend |" in after.split("## Closed")[1], after)
check("dropping the `state` column, four cells not five",
      after.split("## Closed")[1].strip().splitlines()[2].count("|") == 5,
      after.split("## Closed")[1])
check("and check_open_table has nothing to say",
      lg.cr.check_open_table(d / "run.md") == [],
      lg.cr.check_open_table(d / "run.md"))
code, out = run(d, "--close", "nothing/here.py | x")
check("closing a ref no row holds is refused", code == 2)
check("and the refusal lists the refs that are open",
      "cards/Foo.tsx" in out, out)

d = fixture()
run(d, "--open", "risk | 03-design | src/auth.ts | origin check | OPEN")
run(d, "--open", "risk | 07-backend | src/auth.ts | sign-out swallow | OPEN")
check("two lanes on one path are two rows",
      raw(d).split("## Open")[1].count("src/auth.ts") == 2, raw(d))
before = raw(d)
code, out = run(d, "--next", "x", "--close", "src/auth.ts | 08-test")
check("closing a ref two rows share is refused", code == 2, out)
check("and the refusal names each row's `from`",
      "03-design" in out and "07-backend" in out, out)
check("and says how to pick one", "third cell" in out, out)
check("and that the other ops in the call were dropped too",
      "did not land either" in out and raw(d) == before, out)
code, out = run(d, "--close", "src/auth.ts | 08-test | 07-backend")
after = raw(d)
check("a third `from` cell picks the row", code == 0, out)
check("only that row moves",
      "sign-out swallow" in after.split("## Closed")[1]
      and "origin check" in after.split("## Closed")[0], after)
code, out = run(d, "--close", "src/auth.ts | 08-test | 99-nobody")
check("a `from` no open row has is refused",
      code == 2 and "from '99-nobody'" in out, out)

print("F - the post-write battery is check_report's, not a copy of it")
d = fixture()
code, out = run(d, "--set", "status=BLOCKED")
check("a BLOCKED run with no `blocked_on:` is reported", code == 1, out)
check("in check_header's own words", "blocked_on" in out, out)
code, out = run(d, "--set", "blocked_on=awaiting the epic decision")
check("supplying it clears the problem", code == 0, out)
check("and the ok line names the battery that ran",
      "header, phases, budget" in out, out)
code, out = run(d, "--set", "status=DISPATCHING", "--set", "blocked_on=")
check("an empty --set value removes the line, so a stale block can be cleared",
      code == 0 and "blocked_on" not in raw(d), out)

print("G - the budget trip-wire fires at the dispatch that spends it")
rows = ["| 0%d | backend | - | backend-engineer | sonnet | 0%d-backend.md | "
        "DONE | - |" % (n, n) for n in range(2, 5)]
d = fixture(MID[:-1] + rows + [""])
code, out = run(d, "--next", "decide whether to spend another")
check("at `spent == budget` the advisory names the hard stop",
      "hard stop is 8" in out, out)
check("and the ledger is still consistent, so it does not fail", code == 0, out)
d = fixture(MID[:-1] + rows + ["| 05 | test | - | test-engineer | sonnet | "
                               "05-test.md | DONE | - |", ""])
code, out = run(d, "--next", "x")
check("one dispatch past budget with no `## Replans` row fails",
      code == 1 and "no `## Replans` row" in out, out)

print("H - the ledger is found from the run dir or named directly")
d = fixture()
code, out = run(d / "run.md", "--next", "x")
check("pointing at run.md works", code == 0, out)
code, out = run(Path(tempfile.mkdtemp()), "--next", "x")
check("a directory with no ledger is refused", code == 2, out)
code, out = run(d)
check("no ops at all is refused rather than rewriting the file", code == 2, out)

n_fail = sum(1 for _, c, _ in results if not c)
print(f"\n{len(results) - n_fail}/{len(results)} passed")
sys.exit(1 if n_fail else 0)
