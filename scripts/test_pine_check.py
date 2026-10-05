"""Regression suite for pine_check.py.

    python scripts/test_pine_check.py

Dependency-free, like the thing it tests and like `test_check_report.py`.

The argument for it is the same one: a checker nobody checks is a checker whose
findings are believed without evidence. It also pins the one bug this file was
written for -- an anchored `^\\s*` matching the newline, which dragged every
reported line number towards 1 and made the tool useless for the thing it is
most used for.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pine_check as pc

import tempfile

results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))


V6 = "//@version=6\n"
IND = 'indicator("t", overlay=true)\n'

_tmp = tempfile.TemporaryDirectory()
TMP = Path(_tmp.name)
_n = [0]


def run(src, version=6):
    """Findings for `src`, written to a fresh file each time."""
    _n[0] += 1
    f = TMP / f"t{_n[0]}.pine"
    f.write_text(src, encoding="utf-8")
    return pc.check(f, version)


def codes(findings):
    return [f[2] for f in findings]


def sev_of(findings, code):
    return next((f[1] for f in findings if f[2] == code), None)


def line_of(findings, code):
    return next((f[0] for f in findings if f[2] == code), None)


def path_for(src, name="x.pine"):
    _n[0] += 1
    f = TMP / f"{_n[0]}-{name}"
    f.write_text(src, encoding="utf-8")
    return f


# --- the happy path ------------------------------------------------------

check("a clean indicator has no findings", run(V6 + IND) == [])

check("a clean strategy with costs has no findings",
      run(V6 + 'strategy("t", commission_value=0.01, slippage=1)\n') == [])

# The arguments that matter are routinely on the last line of a six-line call.
# A regex that stops at the first newline misses every one of them.
check("a strategy wrapped across lines is read whole",
      run(V6 + 'strategy("t",\n    overlay=true,\n'
               "    commission_value=0.01,\n    slippage=1)\n") == [])

check("a library declaration is accepted", run(V6 + 'library("t")\n') == [])

# --- version -------------------------------------------------------------

_f = run(IND)
check("a missing //@version blocks", "P001" in codes(_f))
check("and it blocks rather than advises", sev_of(_f, "P001") == pc.BLOCKING)

check("a v5 file blocks against a v6 project", "P003" in codes(run("//@version=5\n" + IND)))
check("the expected version is configurable", run("//@version=5\n" + IND, version=5) == [])
check("a duplicate //@version blocks", "P002" in codes(run(V6 + V6 + IND)))

_f = run("// see //@version=5 for the old one\n" + V6 + IND)
check("a version mentioned in prose is not a second declaration",
      "P002" not in codes(_f) and "P003" not in codes(_f), codes(_f))

# --- declaration ---------------------------------------------------------

check("no declaration blocks", "P004" in codes(run(V6 + "x = close\n")))
check("two declarations block", "P005" in codes(run(V6 + IND + IND)))
check("the v4 study() declaration blocks", "P006" in codes(run(V6 + 'study("t")\n')))

# --- repaint -------------------------------------------------------------

_sec = 'x = request.security(syminfo.tickerid, "D", close'
_f = run(V6 + IND + _sec + ", lookahead=barmerge.lookahead_on)\n")
check("lookahead_on blocks", "P007" in codes(_f))
check("and it blocks rather than advises", sev_of(_f, "P007") == pc.BLOCKING)

check("lookahead_off is clean",
      run(V6 + IND + _sec + ", lookahead=barmerge.lookahead_off)\n") == [])

# The default is already lookahead_off, so this is a legibility finding, not a
# correctness one. Grading it BLOCKING would stop every script in the repo and
# teach people to never pass --strict.
_f = run(V6 + IND + _sec + ")\n")
check("security with no explicit lookahead advises", codes(_f) == ["P008"], codes(_f))
check("and it advises rather than blocks", sev_of(_f, "P008") == pc.SHOULD_FIX)

# request.security_lower_tf() has no `lookahead` parameter, so P008's fix cannot
# be applied to it. Flagging it made volume_profile.pine unpassable under --strict.
check("request.security_lower_tf is not asked for a lookahead it cannot take",
      "P008" not in codes(run(V6 + IND + 'x = request.security_lower_tf(t, "1", close)\n')))

check("bare v4 security() blocks",
      "P009" in codes(run(V6 + IND + 'x = security(syminfo.tickerid, "D", close)\n')))
check("request.security is not reported as bare security()",
      "P009" not in codes(run(V6 + IND + _sec + ", lookahead=barmerge.lookahead_off)\n")))

check("iff() blocks", "P010" in codes(run(V6 + IND + "x = iff(close > open, 1, 0)\n")))

# --- namespaces ----------------------------------------------------------

for _call in ("sma(close, 14)", "rsi(close, 14)", "abs(x)", "tostring(x)"):
    check(f"bare {_call.split('(')[0]}() blocks",
          "P011" in codes(run(V6 + IND + f"y = {_call}\n")))

for _call in ("ta.sma(close, 14)", "math.abs(x)", "str.tostring(x)"):
    check(f"{_call.split('(')[0]}() is clean", run(V6 + IND + f"y = {_call}\n") == [])

# `my_sma(...)` is not `sma(...)`. Without the lookbehind every wrapper
# function in the repo trips this rule and the tool becomes unusable.
check("a user function ending in a builtin name is not flagged",
      run(V6 + IND + "y = my_sma(close, 14)\n") == [])

# --- strategy costs ------------------------------------------------------

_f = run(V6 + 'strategy("t", slippage=1)\n')
check("a strategy with no commission blocks", "P012" in codes(_f))
check("and it blocks rather than advises", sev_of(_f, "P012") == pc.BLOCKING)

_f = run(V6 + 'strategy("t", commission_value=0.01)\n')
check("a strategy with no slippage advises", codes(_f) == ["P013"], codes(_f))
check("and it advises rather than blocks", sev_of(_f, "P013") == pc.SHOULD_FIX)

check("calc_on_every_tick advises",
      "P014" in codes(run(V6 + 'strategy("t", commission_value=0.01, '
                               "slippage=1, calc_on_every_tick=true)\n")))

_f = run(V6 + IND)
check("an indicator is not asked for costs",
      "P012" not in codes(_f) and "P013" not in codes(_f))

# --- balance -------------------------------------------------------------

check("an unclosed paren blocks", "P015" in codes(run(V6 + IND + "y = math.max(1, 2\n")))
check("an extra close paren blocks", "P015" in codes(run(V6 + IND + "y = 1)\n")))
check("an unclosed bracket blocks", "P016" in codes(run(V6 + IND + "y = close[1\n")))

# The rule that makes the balance check safe to run at all.
check("a paren inside a string does not count",
      run(V6 + 'indicator("t (unbalanced", overlay=true)\n') == [])
check("a paren inside a comment does not count",
      run(V6 + IND + "// a stray ( in prose\n") == [])
check("a double slash inside a string is not a comment",
      run(V6 + IND + 'x = str.replace(s, "//", "")\n') == [])

# --- ceilings ------------------------------------------------------------

check("exceeding the plot ceiling blocks",
      "P017" in codes(run(V6 + IND + "".join(
          f"plot(close + {i})\n" for i in range(pc.MAX_PLOTS + 1)))))
check("sitting exactly on the plot ceiling is clean",
      run(V6 + IND + "".join(
          f"plot(close + {i})\n" for i in range(pc.MAX_PLOTS))) == [])

# --- line numbers --------------------------------------------------------

# The regression this file was written for. `\s` matches the newline, so an
# anchored pattern starts its match on the last blank line above and every
# reported line number collapses towards 1.
_f = run(V6 + "\n\n\n" + 'strategy("t", commission_value=0.01)\n')
check("blank lines do not drag a line number to the top",
      line_of(_f, "P013") == 5, f"got {line_of(_f, 'P013')}, want 5")

_f = run(V6 + IND + "\n\n" + "y = sma(close, 14)\n")
check("a line number points at the offending call",
      line_of(_f, "P011") == 5, f"got {line_of(_f, 'P011')}, want 5")

# --- exit codes ----------------------------------------------------------

# `main` prints its findings, which is the point of it and is noise here - a
# suite whose own result scrolls off the top of its output is a suite nobody
# reads the last line of.
import contextlib
import io


def exit_code(argv):
    with contextlib.redirect_stdout(io.StringIO()):
        return pc.main(argv)


_p = path_for(V6 + 'strategy("t", commission_value=0.01)\n')
check("main exits 0 on advisories alone", exit_code([str(_p)]) == 0)
check("main exits 1 on advisories under --strict", exit_code([str(_p), "--strict"]) == 1)

check("main exits 1 on a blocking finding", exit_code([str(path_for(IND))]) == 1)
check("main exits 0 on a clean file", exit_code([str(path_for(V6 + IND))]) == 0)
check("a missing file is reported, not raised", exit_code([str(TMP / "nope.pine")]) == 1)

_p = path_for("//@version=5\n" + IND)
check("--version's argument does not become a filename",
      exit_code([str(_p), "--version", "5"]) == 0)

check("no arguments prints usage", exit_code([]) == 2)

# TradingView's copy button and Windows editors both produce a BOM.
_p = TMP / "bom.pine"
_p.write_bytes(("﻿" + V6 + IND).encode("utf-8"))
check("a BOM is tolerated", pc.check(_p) == [])

# --- the repo's own scripts ----------------------------------------------

# The checker has to be usable on what is actually here. If a rule fires
# BLOCKING on the existing three scripts, the rule is wrong, not the repo.
_repo = Path(__file__).resolve().parent.parent.parent / "tradingview"
_pines = sorted(_repo.glob("*.pine")) if _repo.is_dir() else []
if _pines:
    _blocking = [(p.name, f) for p in _pines for f in pc.check(p) if f[1] == pc.BLOCKING]
    check("no existing repo script has a blocking finding",
          not _blocking, str(_blocking[:3]))
else:
    check("the bound repo was found for the corpus check", False, str(_repo))

for name, ok, detail in results:
    if not ok:
        print(f"FAIL  {name}   {detail}")

n_fail = sum(1 for _, c, _ in results if not c)
print(f"\n{len(results) - n_fail}/{len(results)} passed")
_tmp.cleanup()
sys.exit(1 if n_fail else 0)
