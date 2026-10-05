#!/usr/bin/env python3
"""Static checks for Pine Script v6 source.

Pine has no local compiler. TradingView's editor is the only thing that can say
"this compiles", and that check runs in the main session against a live chart
(`projects/tradingview/project.md` § "Mechanical gates"). This script is the
part that *can* run inside a lane: the class of defect that is visible in the
text, cheap to check, and expensive to find on a chart.

It is deliberately not a parser. Every rule below was written down after being
bitten, and fires on a pattern rather than on a parse tree. That means it can be
fooled; it also means it never blocks a lane over a construct it failed to
model. The compile check is the authority. This is the fast filter in front of
it, and it exists so that a build lane's `verification` is a command it actually
ran rather than a promise.

Usage:
    python pine_check.py <file.pine> [...]         exit 1 on any BLOCKING finding
    python pine_check.py <file.pine> --strict      exit 1 on SHOULD_FIX too
    python pine_check.py <file.pine> --version 5   expect //@version=5

A finding prints as:
    <path>:<line>: <BLOCKING|SHOULD_FIX> <code> <message>
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

BLOCKING = "BLOCKING"
SHOULD_FIX = "SHOULD_FIX"

DEFAULT_VERSION = 6

QUOTES = ('"', "'")

# v6 moved most built-ins behind namespaces. A bare call to one of these in a
# file declaring //@version=6 does not compile, and the editor's error names the
# line but not the rename - so the fix is a lookup every time.
NAMESPACED = {
    "ta": (
        "sma ema rma wma vwma hma swma alma linreg rsi stoch cci mfi cmo cog "
        "atr tr stdev dev variance correlation median mode percentrank "
        "percentile_linear_interpolation percentile_nearest_rank "
        "highest lowest highestbars lowestbars crossover crossunder cross "
        "change mom roc valuewhen barssince falling rising pivothigh pivotlow "
        "supertrend macd bb bbw kc kcw dmi sar wpr tsi accdist cum"
    ),
    "math": (
        "abs sign round floor ceil sqrt pow exp log log10 random "
        "todegrees toradians sin cos tan asin acos atan"
    ),
    "str": (
        "tostring tonumber substring replace replace_all split contains "
        "startswith endswith upper lower format"
    ),
}

# v4 and earlier. Present in a v5/v6 file, these are a copy-paste from an old
# script and it will not compile.
# Horizontal whitespace only. `\s` would match the newline too, so an anchored
# `^\s*` pattern silently starts its match on an earlier blank line and every
# line number it reports is wrong - which is exactly what this script's first
# run against the repo did, reporting a line 14 finding as line 1.
H = r"[^\S\n]"

LEGACY_DECL = re.compile(rf"^{H}*study{H}*\(", re.M)
LEGACY_SECURITY = re.compile(r"(?<![.\w])security\s*\(")
LEGACY_IFF = re.compile(r"(?<![.\w])iff\s*\(")

DECL = re.compile(rf"^{H}*(indicator|strategy|library){H}*\(", re.M)
VERSION = re.compile(rf"^{H}*//@version{H}*={H}*(\d+){H}*$", re.M)
# Not `_lower_tf`: that call takes no `lookahead` argument, so P007/P008 cannot apply.
SECURITY_CALL = re.compile(r"request\.security\s*\(")
PLOT_CALL = re.compile(rf"^{H}*plot(?:candle|bar|char|shape|arrow)?{H}*\(", re.M)

# TradingView's published ceiling. Exceeding it is a compile error whose message
# points at the declaration rather than at the 65th plot.
MAX_PLOTS = 64


def strip_noise(src: str) -> str:
    """Blank out string literals and line comments, preserving line structure.

    Every rule below scans code, not prose. A `//` inside a string is not a
    comment and a `(` inside one is not a paren - getting that wrong is how a
    linter starts reporting balance errors on a correct file.
    """
    out: list[str] = []
    for line in src.split("\n"):
        buf: list[str] = []
        i, n, quote = 0, len(line), ""
        while i < n:
            ch = line[i]
            if quote:
                buf.append(" ")
                if ch == "\\" and i + 1 < n:
                    buf.append(" ")
                    i += 2
                    continue
                if ch == quote:
                    quote = ""
                i += 1
                continue
            if ch in QUOTES:
                quote = ch
                buf.append(" ")
                i += 1
                continue
            if ch == "/" and i + 1 < n and line[i + 1] == "/":
                break
            buf.append(ch)
            i += 1
        out.append("".join(buf))
    return "\n".join(out)


def _line_of(src: str, pos: int) -> int:
    return src.count("\n", 0, pos) + 1


def _call_args(code: str, open_pos: int) -> str:
    """The text between `code[open_pos]` and its matching close paren."""
    depth, i, n = 0, open_pos, len(code)
    while i < n:
        if code[i] == "(":
            depth += 1
        elif code[i] == ")":
            depth -= 1
            if depth == 0:
                return code[open_pos + 1 : i]
        i += 1
    return code[open_pos + 1 :]


def _decl_call(code: str) -> tuple[str, str, int] | None:
    """The declaration statement's kind, argument text, and line.

    Read by walking parens rather than by regex: a `strategy(...)` call is
    routinely wrapped across six lines, and the arguments this script cares
    about tend to be on the last one.
    """
    m = DECL.search(code)
    if not m:
        return None
    start = code.index("(", m.start())
    return m.group(1), _call_args(code, start), _line_of(code, m.start())


def check(path: Path, expect_version: int = DEFAULT_VERSION) -> list[tuple[int, str, str, str]]:
    """Return findings as (line, severity, code, message), in source order."""
    src = path.read_text(encoding="utf-8-sig")
    code = strip_noise(src)
    found: list[tuple[int, str, str, str]] = []

    def add(line: int, sev: str, rule: str, msg: str) -> None:
        found.append((line, sev, rule, msg))

    # --- version -----------------------------------------------------------
    versions = list(VERSION.finditer(src))
    if not versions:
        add(1, BLOCKING, "P001",
            "no //@version annotation - TradingView compiles this as v1")
    else:
        if len(versions) > 1:
            add(_line_of(src, versions[1].start()), BLOCKING, "P002",
                f"{len(versions)} //@version annotations - only the first is read")
        declared = int(versions[0].group(1))
        if declared != expect_version:
            add(_line_of(src, versions[0].start()), BLOCKING, "P003",
                f"//@version={declared}, project expects v{expect_version}")

    # --- declaration -------------------------------------------------------
    decls = list(DECL.finditer(code))
    if not decls:
        add(1, BLOCKING, "P004",
            "no indicator(), strategy() or library() declaration")
    elif len(decls) > 1:
        add(_line_of(code, decls[1].start()), BLOCKING, "P005",
            f"{len(decls)} declaration statements - a script declares exactly one")

    for m in LEGACY_DECL.finditer(code):
        add(_line_of(code, m.start()), BLOCKING, "P006",
            "study() is the v4 declaration - v5+ uses indicator()")

    # --- repaint -----------------------------------------------------------
    # Guardrail 1. `lookahead_on` reads bars that had not closed when the signal
    # was drawn, so the backtest sees the future and the live chart does not.
    # Silent, and the most expensive defect in this repo's subject matter.
    for m in SECURITY_CALL.finditer(code):
        args = _call_args(code, code.index("(", m.start()))
        line = _line_of(code, m.start())
        if "lookahead_on" in args:
            add(line, BLOCKING, "P007",
                "request.security(..., lookahead=barmerge.lookahead_on) repaints - "
                "the backtest reads bars that had not closed")
        elif "lookahead" not in args:
            add(line, SHOULD_FIX, "P008",
                "request.security() without an explicit lookahead - pass "
                "barmerge.lookahead_off so the intent is on the page")

    for m in LEGACY_SECURITY.finditer(code):
        add(_line_of(code, m.start()), BLOCKING, "P009",
            "bare security() is v4 - v5+ uses request.security()")

    for m in LEGACY_IFF.finditer(code):
        add(_line_of(code, m.start()), BLOCKING, "P010",
            "iff() was removed in v5 - use the ternary operator")

    # --- namespaces --------------------------------------------------------
    for ns, names in NAMESPACED.items():
        for name in names.split():
            for m in re.finditer(rf"(?<![.\w]){re.escape(name)}\s*\(", code):
                add(_line_of(code, m.start()), BLOCKING, "P011",
                    f"bare {name}() - v6 requires {ns}.{name}()")

    # --- strategy costs ----------------------------------------------------
    # Guardrail 4. A strategy with no costs backtests a market that does not
    # exist, and the equity curve is wrong in the flattering direction.
    decl = _decl_call(code)
    if decl and decl[0] == "strategy":
        _, args, line = decl
        if "commission_value" not in args:
            add(line, BLOCKING, "P012",
                "strategy() declares no commission_value - an uncosted backtest "
                "overstates every result")
        if "slippage" not in args:
            add(line, SHOULD_FIX, "P013",
                "strategy() declares no slippage - state it, even as 0, so the "
                "assumption is visible")
        if re.search(r"calc_on_every_tick\s*=\s*true", args):
            add(line, SHOULD_FIX, "P014",
                "calc_on_every_tick=true makes the backtest and the live chart "
                "disagree - justify it or drop it")

    # --- balance -----------------------------------------------------------
    for open_ch, close_ch, rule in (("(", ")", "P015"), ("[", "]", "P016")):
        depth, where = 0, 0
        for i, ch in enumerate(code):
            if ch == open_ch:
                if depth == 0:
                    where = i
                depth += 1
            elif ch == close_ch:
                depth -= 1
                if depth < 0:
                    add(_line_of(code, i), BLOCKING, rule,
                        f"unbalanced '{close_ch}' - closes nothing")
                    depth = 0
        if depth > 0:
            add(_line_of(code, where), BLOCKING, rule,
                f"unbalanced '{open_ch}' - {depth} never closed")

    # --- ceilings ----------------------------------------------------------
    plots = len(PLOT_CALL.findall(code))
    if plots > MAX_PLOTS:
        add(1, BLOCKING, "P017",
            f"{plots} plot calls - TradingView's ceiling is {MAX_PLOTS}")

    return sorted(found, key=lambda f: (f[0], f[2]))


def main(argv: list[str]) -> int:
    strict = "--strict" in argv
    version = DEFAULT_VERSION
    skip: set[str] = set()
    for i, a in enumerate(argv):
        if a == "--version" and i + 1 < len(argv):
            version = int(argv[i + 1])
            skip.add(argv[i + 1])
    args = [a for a in argv if not a.startswith("--") and a not in skip]
    if not args:
        print(__doc__)
        return 2

    saw_blocking = False
    saw_should = False
    for name in args:
        path = Path(name)
        if not path.is_file():
            print(f"{name}: BLOCKING P000 no such file")
            saw_blocking = True
            continue
        findings = check(path, version)
        for line, sev, rule, msg in findings:
            print(f"{path}:{line}: {sev} {rule} {msg}")
            if sev == BLOCKING:
                saw_blocking = True
            else:
                saw_should = True
        if not findings:
            print(f"{path}: PASS 0 findings")

    if saw_blocking or (strict and saw_should):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
