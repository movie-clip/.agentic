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

n_fail = sum(1 for _, c, _ in results if not c)
print(f"\n{len(results) - n_fail}/{len(results)} passed")
sys.exit(1 if n_fail else 0)
