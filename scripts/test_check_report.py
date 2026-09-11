"""Regression suite for check_report.py.

    python scripts/test_check_report.py

Covers the six bugs found in the v0.4 review pass, plus the behaviour that
already worked and must not break. Dependency-free, like the thing it tests.
the behaviour that already worked and must not break."""
import sys, subprocess, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_report as cr

BLOCK = """REPORT test/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   pytest
  result:    PASS
  detail:    802 passed, 4 skipped, 1 xfail

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - one item

risks:
  - none
"""

HEAD = """REPORT HEAD test/01
artifact:        /x/01.md
status:          DONE
verdict:         NONE
verification:    PASS
detail:          802 passed, 4 skipped, 1 xfail
changed:         0
contract_notes:  0
pack_corrections: 0
handoff:         1
risks:           0
headline:        did the thing
"""

results = []
def check(name, cond, extra=""):
    results.append((name, cond, extra))
    print(f"  {'PASS' if cond else 'FAIL'}  {name}{'  ' + extra if extra and not cond else ''}")

print("F1 — markdown heading inside a code fence must not read as a section")
doc = BLOCK + "\n```markdown\n## Mechanical gates\ncontent\n```\n"
check("fenced ## ignored", cr._check_brief(doc) == [], str(cr._check_brief(doc)))

print("F2 — head detail may not stop short of the bad news")
h = HEAD.replace("detail:          802 passed, 4 skipped, 1 xfail",
                 "detail:          802 passed")
p = cr._check_head(h, BLOCK)
check("truncated detail rejected", any("verbatim" in x for x in p), str(p))
check("exact detail accepted", cr._check_head(HEAD, BLOCK) == [],
      str(cr._check_head(HEAD, BLOCK)))

print("F3 — an unedited --emit-head placeholder must not pass")
h = HEAD.replace("headline:        did the thing",
                 "headline:        <outcome in one sentence - replace this>")
p = cr._check_head(h, BLOCK)
check("placeholder headline rejected", any("placeholder" in x for x in p), str(p))

print("F5 — an ID must not match by substring")
check("US-36.10 does not satisfy US-36.1",
      cr._brief_covers("- only US-36.10 here", ["## US-36.1: other"]) != [])
check("US-36.1 does satisfy US-36.1",
      cr._brief_covers("- US-36.1 ships", ["## US-36.1: other"]) == [])
check("trailing period still matches",
      cr._brief_covers("- we ship US-36.1.", ["## US-36.1: other"]) == [])

print("F6 — a colon line inside a fence must not truncate its section")
doc = BLOCK.replace("handoff:\n  - one item",
                    "handoff:\n  - one item\n\n```yaml\nfixture: wired_repo\n```\n\n  - second item")
check("both bullets counted", cr.counts(doc)["handoff"] == 2,
      f"got {cr.counts(doc)['handoff']}")
doc2 = BLOCK.replace("handoff:\n  - one item",
                     "handoff:\n  - one item\n\n```yaml\n- not_a_bullet\n```")
check("fenced '- x' not counted as a bullet", cr.counts(doc2)["handoff"] == 1,
      f"got {cr.counts(doc2)['handoff']}")

print("F7 — lane inferred from filename")
for fn, want in [("04-backend.md", "backend"), ("06-backend-T36.1.1.md", "backend"),
                 ("14-integration.md", "integration"), ("15-review.md", "review"),
                 ("02-delivery-brief.md", None), ("run.md", None)]:
    got = cr.lane_from_name(Path(fn))
    check(f"{fn} -> {want}", got == want, f"got {got}")

print("still-working behaviour")
check("clean artifact passes", cr.check(Path(__file__), None) is not None)
d = Path(tempfile.mkdtemp())
(d / "01-backend.md").write_text(BLOCK, encoding="utf-8")
check("valid artifact has no violations", cr.check(d / "01-backend.md", "backend") == [],
      str(cr.check(d / "01-backend.md", "backend")))
bad = BLOCK.replace("verdict:     NONE", "verdict:     PASS")
(d / "02-backend.md").write_text(bad, encoding="utf-8")
check("non-gate lane verdict rejected",
      any("may judge" in x for x in cr.check(d / "02-backend.md", "backend")))
check("directory scan now applies gate rules via inferred lane",
      subprocess.run([sys.executable, str(Path(__file__).resolve().parent / "check_report.py"),
                      str(d)], capture_output=True).returncode == 1)
miss = BLOCK.replace("risks:\n  - none\n", "")
(d / "03-backend.md").write_text(miss, encoding="utf-8")
check("missing section still caught",
      any("missing section 'risks:'" in x for x in cr.check(d / "03-backend.md")))
empty = BLOCK.replace("handoff:\n  - one item", "handoff:")
(d / "04-backend.md").write_text(empty, encoding="utf-8")
check("empty section still caught",
      any("is empty" in x for x in cr.check(d / "04-backend.md")))
dn = BLOCK.replace("result:    PASS", "result:    NOT_RUN")
(d / "05-backend.md").write_text(dn, encoding="utf-8")
check("DONE + NOT_RUN still caught",
      any("must run it" in x for x in cr.check(d / "05-backend.md")))
check("bad path exits 2",
      subprocess.run([sys.executable, str(Path(__file__).resolve().parent / "check_report.py"),
                      "nope.md"], capture_output=True).returncode == 2)

print("R1 - a fence wrapping the whole document must not hide it")
wp = d / "10-backend.md"
wp.write_text("```\n" + BLOCK + "```\n", encoding="utf-8")
check("fence-wrapped report validates clean", cr.check(wp, "backend") == [],
      str(cr.check(wp, "backend")))
wh = "```\n" + HEAD + "```\n"
check("fence-wrapped head validates clean", cr._check_head(wh, BLOCK) == [],
      str(cr._check_head(wh, BLOCK)))

print("R2 - an unclosed fence must not report every later section as missing")
up = d / "11-backend.md"
up.write_text(BLOCK.replace("handoff:\n  - one item",
                            "handoff:\n  - one item\n\n```yaml\nunclosed: true"),
              encoding="utf-8")
check("no bogus 'missing section'",
      not any("missing section" in x for x in cr.check(up, "backend")))

print("R3 - the brief cap must never make completeness unsatisfiable")
secs = "\n".join(f"## Cross-cutting decision number {i}\ntext\n" for i in range(1, 21))
brief = "\n".join(f"- Cross-cutting decision number {i}" for i in range(1, 21))
check("20 sections named over 20 brief lines is allowed",
      cr._check_brief(BLOCK + f"\n## Orchestrator brief\n{brief}\n\n{secs}") == [])
check("a brief that omits sections still fails",
      len(cr._check_brief(BLOCK + "\n## Orchestrator brief\n- names three\n\n" + secs)) > 10)

print("R4 - '- none' with commentary is surfaced, never silently reinterpreted")
nd = BLOCK.replace("contract_notes:\n  - none",
                   "contract_notes:\n  - none - doc-only, no schema changed")
np_ = d / "12-backend.md"
np_.write_text(nd, encoding="utf-8")
w = []
cr.check(np_, "backend", None, w)
check("warns about none-with-commentary", any("trailing commentary" in x for x in w))
check("still counts it as an entry (never undercount)",
      cr.counts(nd)["contract_notes"] == 1)

print("R5 - a wrong --lane on a gate artifact suggests the right one")
gp = d / "13-quant-audit.md"
gp.write_text(BLOCK.replace("verdict:     NONE", "verdict:     FAIL"), encoding="utf-8")
probs = cr.check(gp, "quant")
check("suggests the filename lane", any("did you mean --lane quant-audit" in x for x in probs), str(probs))
check("correct lane passes", cr.check(gp, "quant-audit") == [], str(cr.check(gp, "quant-audit")))

print("R6 - protocol-lint is a gate lane and may judge")
pl = d / "14-protocol-lint.md"
pl.write_text(BLOCK.replace("verdict:     NONE", "verdict:     FAIL"), encoding="utf-8")
check("two-part lane parsed from the filename",
      cr.lane_from_name(pl) == "protocol-lint", str(cr.lane_from_name(pl)))
check("its FAIL verdict is allowed", cr.check(pl, "protocol-lint") == [],
      str(cr.check(pl, "protocol-lint")))
check("it still may not request changes",
      any("CHANGES_REQUESTED" in x for x in
          cr.check(pl, "protocol-lint")) is False)
cr2 = d / "15-protocol-lint.md"
cr2.write_text(BLOCK.replace("verdict:     NONE", "verdict:     CHANGES_REQUESTED"),
               encoding="utf-8")
check("CHANGES_REQUESTED from protocol-lint is rejected",
      any("may" in x and "CHANGES_REQUESTED" in x
          for x in cr.check(cr2, "protocol-lint")),
      str(cr.check(cr2, "protocol-lint")))

print("F3 - a directory sweep opens every report, not just numbered ones")
sweep = Path(tempfile.mkdtemp()) / "2026-01-01-a-run"
sweep.mkdir()
(sweep / "01-scout.md").write_text(BLOCK, encoding="utf-8")
(sweep / "AUDIT-quant.md").write_text(BLOCK, encoding="utf-8")
(sweep / "T-40.1.3-backend.md").write_text(BLOCK, encoding="utf-8")
(sweep / "run.md").write_text("# RUN 2026-01-01-a-run\nstatus: CLOSED\n",
                              encoding="utf-8")
(sweep / "pack-corrections.md").write_text("# Pack corrections\n- none\n",
                                           encoding="utf-8")
found = sorted(f.name for f in sweep.glob("*.md") if cr._is_report(f))
check("ticket-named artifacts are reports too",
      found == ["01-scout.md", "AUDIT-quant.md", "T-40.1.3-backend.md"], str(found))
check("the ledger is not a report", not cr._is_report(sweep / "run.md"))
check("the pack queue is not a report",
      not cr._is_report(sweep / "pack-corrections.md"))
check("the sweep exits 0 with every artifact clean",
      cr.main(["check_report.py", str(sweep)]) == 0)

print("F3 - the lane is read from anywhere in the name, once")
for _name, _want in [("T-40.1.3-T-40.2.2a-backend.md", "backend"),
                     ("INTEGRATION-tech-lead.md", "integration"),
                     ("CR-1-frontend.md", "frontend"),
                     ("01-scout.md", "recon"),
                     ("04-stories.md", "story")]:
    _got = cr.lane_from_name(Path(_name))
    check(f"{_name} -> {_want}", _got == _want, str(_got))

# `quant-audit` contains `quant`. Reading the shorter one would flag the audit's
# own verdict as coming from a lane that may not judge - a violation that is not
# there, which is worse than inferring nothing at all.
for _name in ("AUDIT-quant.md", "10-quant-reaudit.md", "13-quant-audit-recheck.md"):
    check(f"{_name} is the audit lane, not the research lane",
          cr.lane_from_name(Path(_name)) == "quant-audit",
          str(cr.lane_from_name(Path(_name))))
check("a name that says nothing infers nothing",
      cr.lane_from_name(Path("05-technical-plan.md")) is None,
      str(cr.lane_from_name(Path("05-technical-plan.md"))))
check("a name that says two lanes infers neither",
      cr.lane_from_name(Path("07-backend-and-frontend.md")) is None,
      str(cr.lane_from_name(Path("07-backend-and-frontend.md"))))

print("F3 - a character outside cp1252 does not abort the sweep")
wide = Path(tempfile.mkdtemp()) / "2026-01-01-wide"
wide.mkdir()
(wide / "01-scout.md").write_text(
    BLOCK.replace("  - one item", "  - a \u2192 b, and an em-dash \u2014 too"),
    encoding="utf-8")
(wide / "02-review.md").write_text(BLOCK, encoding="utf-8")
check("the run completes instead of raising UnicodeEncodeError",
      cr.main(["check_report.py", str(wide)]) == 0)

print("F1 - a derived head validates, and a hand-typed one names where it broke")
rt = Path(tempfile.mkdtemp()) / "2026-01-01-round-trip"
rt.mkdir()
art = rt / "01-scout.md"
long_detail = (
    "backend 905 passed, 4 skipped; frontend 331 passed (37 files); "
    "tsc clean; dead-code gate clean; goldens unchanged; "
    "and a good long tail running well past the two hundredth character, "
    "which is the part a hand-typed head keeps losing")
art.write_text(BLOCK.replace("802 passed, 4 skipped, 1 xfail", long_detail),
               encoding="utf-8")
check("the fixture detail is longer than the cap",
      len(long_detail) > cr.MAX_HEADLINE, str(len(long_detail)))

derived = cr.head_for(art)
filled = "\n".join(
    "headline:        one sentence of outcome" if ln.startswith("headline:") else ln
    for ln in derived.splitlines())
check("a derived head with only the headline filled in validates",
      [x for x in cr.check(art, "recon", filled, []) if x.startswith("head")] == [],
      str(cr.check(art, "recon", filled, [])))

# The three ways a hand-typed detail actually went wrong in the closed runs:
# one character too long, not truncated at all, and abridged in the middle.
for label, hd in [
        ("one char too long", long_detail[:cr.MAX_HEADLINE] + "."),
        ("never truncated", long_detail),
        ("abridged in the middle",
         long_detail[:60] + long_detail[120:cr.MAX_HEADLINE])]:
    typed = filled.replace("detail:", "detail:  @X@", 1).replace(
        "@X@" + filled.split("detail:")[1].split("\n")[0].strip(), hd)
    probs = [x for x in cr.check(art, "recon", typed, []) if "detail" in x]
    check(f"{label} is caught", bool(probs), str(probs))
    check(f"{label} says where they diverge",
          any("diverge at char" in x for x in probs), str(probs))

print("F4 - the bullet ceiling blocks on a gate lane and advises elsewhere")
def _bul(n):
    return BLOCK.replace("  - one item", "  - " + ("x" * n))

def _split(doc, lane):
    d = Path(tempfile.mkdtemp()) / "01-x.md"
    d.write_text(doc, encoding="utf-8")
    w = []
    return cr.check(d, lane, None, w), w

# Gate lanes have never exceeded 400 in a real run (longest: 310), so enforcing
# it there costs nothing - and it is the only place a bullet is routed onward.
for gate in ("integration", "review", "quant-audit", "protocol-lint"):
    b, w = _split(_bul(500), gate)
    check(f"{gate}: over the ceiling blocks",
          any("chars (max 400)" in x for x in b), str(b))
    b, w = _split(_bul(300), gate)
    check(f"{gate}: under the ceiling is advisory only",
          not b and any("target 200" in x for x in w), f"{b} {w}")

for lane in ("backend", "docs", "story", "test", "frontend"):
    b, w = _split(_bul(500), lane)
    check(f"{lane}: over the ceiling only advises",
          not b and any("chars (max 400)" in x for x in w), f"{b} {w}")

print("F4 - recon and quant carry citations, so they get more room")
for wide in ("recon", "quant"):
    b, w = _split(_bul(350), wide)
    check(f"{wide}: 350 chars is silent", not b and not w, f"{b} {w}")
    b, w = _split(_bul(500), wide)
    check(f"{wide}: 500 chars advises against the raised target",
          not b and any("target 400" in x for x in w), f"{b} {w}")
    b, w = _split(_bul(700), wide)
    check(f"{wide}: 700 chars advises against the raised ceiling",
          not b and any("chars (max 600)" in x for x in w), f"{b} {w}")
# recon and quant are not gate lanes, so nothing they write ever blocks on
# length; quant-audit is the gate and keeps the strict pair.
b, _ = _split(_bul(700), "quant-audit")
check("quant-audit keeps the strict ceiling, unlike quant",
      any("chars (max 400)" in x for x in b), str(b))

print("F8 - --require-heads: a dispatch with no saved head is a failure, not a note")


def _sweep(files: dict[str, str], *flags: str):
    """Run the real CLI over a temp run dir; returns (exit_code, stdout)."""
    with tempfile.TemporaryDirectory() as d:
        run = Path(d)
        for name, body in files.items():
            (run / name).write_text(body, encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(Path(cr.__file__)), str(run), *flags],
            capture_output=True, text=True)
        return proc.returncode, proc.stdout


_HEAD_OK = HEAD.replace("artifact:        /x/01.md", "artifact:        01-lane.md")

code, out = _sweep({"01-lane.md": BLOCK})
check("without the flag, a missing head still passes", code == 0, out)

code, out = _sweep({"01-lane.md": BLOCK}, "--require-heads")
check("with the flag, a missing head fails", code == 1, out)
check("the failure names the file it wanted", "01-head.txt" in out, out)

code, out = _sweep({"01-lane.md": BLOCK, "01-head.txt": _HEAD_OK}, "--require-heads")
check("a saved, agreeing head passes", code == 0, out)

# The failure this whole flag exists to catch: a head that undercounts is
# routable-looking but silently drops work. It must fail even when saved.
under = _HEAD_OK.replace("handoff:         1", "handoff:         0")
code, out = _sweep({"01-lane.md": BLOCK, "01-head.txt": under}, "--require-heads")
check("a saved head that undercounts still fails", code == 1, out)
check("undercount is reported as such", "undercounts" in out, out)

# Ticket-named artifacts are not dispatch slots and have no head to demand.
code, out = _sweep({"T-43.1.5-note.md": BLOCK}, "--require-heads")
check("a non-numbered artifact needs no head", code == 0, out)
check("and says so as an advisory", "no head required" in out, out)

code, out = _sweep({"01-lane.md": BLOCK}, "--require-heads", "--head", "x.txt")
check("--require-heads and --head together are refused", code == 2, out)

check("head_path_for maps slot to head file",
      cr.head_path_for(Path("/r/07-review.md")).name == "07-head.txt")
check("head_path_for returns None off-slot",
      cr.head_path_for(Path("/r/pack-corrections.md")) is None)

print("the close-out sweep also checks the ledger's `gates:` line")

LEDGER = """# RUN test
status:       CLOSED
route:        full
gates:        quant-audit PASS · integration skipped (none) · review skipped (none)

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | recon | — | scout | sonnet | 01-lane.md | DONE | — |
| 02 | quant | AUDIT | quant-analyst | opus | 02-quant.md | DONE | PASS |
"""


def _gates(line):
    """Problems the sweep reports for a ledger whose `gates:` line is `line`."""
    d = Path(tempfile.mkdtemp())
    body = LEDGER if line is None else LEDGER.replace(
        "quant-audit PASS · integration skipped (none) · "
        "review skipped (none)", line)
    if line is None:
        body = "\n".join(l for l in LEDGER.splitlines()
                         if not l.startswith("gates:")) + "\n"
    (d / "run.md").write_text(body, encoding="utf-8")
    return cr.check_gates(d / "run.md")


check("all three named, verdicts matching the rows, is clean",
      _gates("quant-audit PASS · integration skipped (none) · "
             "review skipped (none)") == [], str(_gates(None)))
check("a ledger with no `gates:` line says so",
      any("no `gates:` line" in x for x in _gates(None)), str(_gates(None)))

# The failure this exists for: a run that closed with no acceptance gate and
# nothing anywhere saying so. Both spellings of that are caught.
_left_out = _gates("quant-audit PASS · integration skipped (none)")
check("a gate left out of the line is caught",
      any("does not account for review" in x for x in _left_out), str(_left_out))
_claimed = _gates("quant-audit PASS · integration skipped (none) · review PASS")
check("a gate claimed but never run is caught",
      any("no verdict row" in x and "review" in x for x in _claimed), str(_claimed))
_disagrees = _gates("quant-audit FAIL · integration skipped (none) · "
                    "review skipped (none)")
check("a verdict disagreeing with the rows is caught",
      any("disagrees with the rows on quant-audit" in x for x in _disagrees),
      str(_disagrees))
_ok = _gates("quant-audit PASS · integration skipped (express route) · "
             "review skipped (no story to accept)")
check("skipping a gate on purpose is clean", _ok == [], str(_ok))

# `Open` holds what is still open. The rule changed in v0.4.2 and two files went
# on instructing the superseded one, so prose alone did not hold it.
_OPEN_HEAD = "\n## Open\n| kind | from | ref | one-line | state |\n|---|---|---|---|---|\n"


def _open(rows):
    """Problems reported for an `## Open` table holding `rows`."""
    d = Path(tempfile.mkdtemp())
    (d / "run.md").write_text(LEDGER + _OPEN_HEAD + "".join(rows),
                              encoding="utf-8")
    return cr.check_open_table(d / "run.md")


_still = _open(["| contract_note | 04-backend | schemas/h.py | lags | OPEN |\n",
                "| should_fix | CR-2 | cr/CR-2.md | untested | CARRIED |\n"])
check("OPEN and CARRIED are the states `Open` is for", _still == [], str(_still))

_absorbed = _open(
    ["| contract_note | 04-backend | schemas/h.py | lags | ABSORBED |\n"])
check("an ABSORBED row left in `Open` is caught",
      any("moves to `## Closed`" in x for x in _absorbed), str(_absorbed))

# The states real ledgers actually write. Judged on the leading token, because
# a CARRIED row is supposed to carry its reason to the human at close-out.
_qualified = _open(
    ["| contract_note | 05-plan | 06-backend.md | landed | ABSORBED by 06 |\n",
     "| debt | 09 + 12 | risk.py:2120 | pre-existing | CARRIED - out of scope |\n"])
check("a qualified ABSORBED is caught and a qualified CARRIED is not",
      len(_qualified) == 1 and "ABSORBED" in _qualified[0], str(_qualified))

# The close-out checklist invented this one; no file ever defined it, and the
# one closed v0.5.x run used it for rows a gate had resolved.
_bogus = _open(["| risk | 06-backend | 10-integration.md | ok | CLOSED (noted) |\n"])
check("a resolved row written as CLOSED is caught too",
      any("is CLOSED" in x for x in _bogus), str(_bogus))

_unknown = _open(["| partial | 06-frontend | 06-frontend.md | unwired | PENDING |\n"])
check("a state no file defines is caught",
      any("'PENDING'" in x for x in _unknown), str(_unknown))

check("an empty `Open` table is clean", _open([]) == [], str(_open([])))

_d = Path(tempfile.mkdtemp())
(_d / "run.md").write_text(LEDGER, encoding="utf-8")
_no_table = cr.check_open_table(_d / "run.md")
check("a ledger with no `Open` table at all is clean",
      _no_table == [], str(_no_table))

# Wired into the sweep, not just importable: the close-out command is the only
# one anybody runs, so a check reachable only from Python is a check nobody runs.
_run = Path(tempfile.mkdtemp())
(_run / "01-lane.md").write_text(BLOCK, encoding="utf-8")
(_run / "01-head.txt").write_text(_HEAD_OK, encoding="utf-8")
(_run / "run.md").write_text(LEDGER, encoding="utf-8")
_proc = subprocess.run(
    [sys.executable, str(Path(cr.__file__)), str(_run), "--require-heads"],
    capture_output=True, text=True)
check("a clean run.md passes the close-out sweep", _proc.returncode == 0, _proc.stdout)
check("and the sweep says it checked the gates and the open table",
      "(gates, open)" in _proc.stdout, _proc.stdout)

(_run / "run.md").write_text(
    LEDGER.replace(" · review skipped (none)", ""), encoding="utf-8")
_proc = subprocess.run(
    [sys.executable, str(Path(cr.__file__)), str(_run), "--require-heads"],
    capture_output=True, text=True)
check("an unaccounted gate fails the close-out sweep", _proc.returncode == 1,
      _proc.stdout)

# Mid-flight sweeps have no verdicts yet, so the check belongs to close-out only.
_proc = subprocess.run(
    [sys.executable, str(Path(cr.__file__)), str(_run)],
    capture_output=True, text=True)
check("without --require-heads the ledger is not checked", _proc.returncode == 0,
      _proc.stdout)

n_fail = sum(1 for _, c, _ in results if not c)
print(f"\n{len(results) - n_fail}/{len(results)} passed")
sys.exit(1 if n_fail else 0)
