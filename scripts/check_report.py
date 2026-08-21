#!/usr/bin/env python3
"""Validate an agent report against PROTOCOL.md § 3, and its head against § 4.

    python scripts/check_report.py runs/<run-id>/01-scout.md [--lane recon]
    python scripts/check_report.py runs/<run-id>/            # every artifact
    python scripts/check_report.py <artifact> --emit-head    # print the head
    python scripts/check_report.py <artifact> --head head.txt

Exit 0 = valid. Exit 1 = violations, printed one per line. Lines prefixed `~`
are advisory and do not fail the run.

This exists because "reports are structured" was, until v0.3.2, enforced by
asking agents nicely. A format nothing checks is a format that drifts, and the
orchestrator routes from these fields — an unparseable contract_notes block is
a downstream order that never gets written.

`--emit-head` exists because the head's counts must match the artifact, and a
count typed by hand is a count that can be wrong in the one direction that
matters: too low, silently dropping work the orchestrator would have routed.
Derive it, don't write it.

Dependency-free by design: it runs anywhere the network runs.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

STATUS = {"DONE", "PARTIAL", "BLOCKED", "REFUSED"}
VERDICT = {"PASS", "FAIL", "CHANGES_REQUESTED", "NONE"}
RESULT = {"PASS", "FAIL", "NOT_RUN"}

SECTIONS = ["changed", "verification", "contract_notes",
            "pack_corrections", "handoff", "risks"]
# Sections the head reports a count for. `verification` is a scalar, not a list.
COUNTED = ["changed", "contract_notes", "pack_corrections", "handoff", "risks"]

LANES = {"product", "quant", "recon", "story", "design", "backend", "frontend",
         "test", "docs", "quant-audit", "integration", "review",
         "protocol-lint"}
# Lanes permitted to render a judgment. Everyone else writes verdict: NONE.
GATE_LANES = {"integration", "review", "quant-audit", "protocol-lint"}
# Only the tech lead's integration pass may request changes.
CR_LANES = {"integration"}

# PROTOCOL.md § 3 "Bullet discipline". One fact per bullet, short enough that
# the orchestrator can route it without re-reading the artifact.
#
# Two thresholds, because the two failures are different sizes. Over TARGET is
# a bullet carrying its fact plus commentary — worth saying, not worth blocking.
# Over MAX it is carrying several facts, and cannot be routed to several lanes;
# that is structural. Measured against the first full run: 186 bullets, median
# 336 chars, longest 1517. The median is the habit this cap is changing.
TARGET_BULLET = 200
MAX_BULLET = 400
# PROTOCOL.md § 4. An index with verdicts, not a summary of the reasoning.
MAX_HEADLINE = 200
MAX_BRIEF = 15
BRIEF_HEADING = "## Orchestrator brief"

_SECTION_STOP = re.compile(r"^(?:\S+:|## )")
# A value that is nothing but a placeholder: `<one sentence ...>`. --emit-head
# writes these for the two fields it cannot derive, and an agent that ran the
# command but did none of the thinking returns them unedited.
_PLACEHOLDER = re.compile(r"^<[^>]*>$")


def _unwrap(text: str) -> str:
    """Drop a fence that wraps the ENTIRE document, if there is one.

    PROTOCOL.md shows the report block and the head inside ``` fences, so an
    agent reproducing that format wraps its whole artifact. Fence-awareness
    would then hide every field, and a perfectly good report reads as ten
    violations. Only an outer fence is removed, and only when the fences inside
    it balance — otherwise the leading ``` is a real, unclosed fence and the
    caller should see it as one.
    """
    lines = text.splitlines()
    live = [i for i, ln in enumerate(lines) if ln.strip()]
    if len(live) < 2:
        return text
    first, last = live[0], live[-1]
    if not (lines[first].strip().startswith("```")
            and lines[last].strip() == "```"):
        return text
    inner = sum(1 for i in range(first + 1, last)
                if lines[i].strip().startswith("```"))
    if inner % 2:
        return text
    return "\n".join(lines[first + 1:last])


def _fenced(text: str) -> set[int]:
    """Line indices inside a ``` fenced block, fence lines included.

    Reports quote markdown and YAML — the docs lane reports the headings it
    wrote, the tech lead pastes a config. Without this, a `## Mechanical gates`
    inside a fence reads as a document section, and a `key: value` inside one
    truncates the section it sits in, which makes the head's counts wrong while
    every other check still passes.
    """
    lines = text.splitlines()
    inside: set[int] = set()
    open_fence = False
    for i, ln in enumerate(lines):
        if re.match(r"^\s*```", ln):
            inside.add(i)
            open_fence = not open_fence
        elif open_fence:
            inside.add(i)
    if open_fence:
        # An unclosed fence would swallow every later section and report each
        # as "missing", which sends the author hunting for something they did
        # write. Treat the stray marker as text and let the real checks run.
        return set()
    return inside


def _scalar(text: str, key: str) -> str | None:
    """First value for `key:`, ignoring anything inside a code fence.

    command/result/detail are indented under `verification:`, so leading
    whitespace is expected — matching at column 0 only was the first bug this
    script found, in itself.
    """
    fenced = _fenced(text)
    pat = re.compile(rf"^[ \t]*{re.escape(key)}:[ \t]*(.*)$")
    for i, ln in enumerate(text.splitlines()):
        if i in fenced:
            continue
        m = pat.match(ln)
        if m:
            return m.group(1).strip()
    return None


def _section(text: str, name: str) -> list[str] | None:
    """Body lines of a top-level section, or None if the heading is absent.

    Fenced lines are excluded from the body: a `- item` inside a YAML example
    is not a bullet the orchestrator can route.
    """
    lines = text.splitlines()
    fenced = _fenced(text)
    head = re.compile(rf"^{re.escape(name)}:[ \t]*$")

    start = next((i for i, ln in enumerate(lines)
                  if i not in fenced and head.match(ln)), None)
    if start is None:
        return None

    body: list[str] = []
    for i in range(start + 1, len(lines)):
        if i in fenced:
            continue
        if _SECTION_STOP.match(lines[i]):
            break
        body.append(lines[i])
    return [ln.strip() for ln in body if ln.strip()]


def _bullets(lines: list[str]) -> list[str]:
    """Real entries in a section — `- none` is a filled-in empty, not an entry."""
    if len(lines) == 1 and lines[0].lower().lstrip("- ").strip() == "none":
        return []
    return [ln for ln in lines if ln.startswith("- ")]


def counts(text: str) -> dict[str, int]:
    return {n: len(_bullets(_section(text, n) or [])) for n in COUNTED}


def lane_from_name(path: Path) -> str | None:
    """Infer the lane from `<nn>-<lane>[-<ticket>].md`, or None if unclear.

    Lets a whole-directory scan still apply the gate rules. Only returns a lane
    it actually recognises — guessing one would invent violations.
    """
    parts = path.stem.split("-")
    if len(parts) >= 3 and f"{parts[1]}-{parts[2]}" in LANES:
        return f"{parts[1]}-{parts[2]}"
    if len(parts) >= 2 and parts[1] in LANES:
        return parts[1]
    return None


def head_for(path: Path) -> str:
    """Derive the § 4 head from the artifact, so the counts cannot disagree."""
    text = _unwrap(path.read_text(encoding="utf-8"))
    first = next((ln for ln in text.splitlines() if ln.strip()), "")
    run_id = first[len("REPORT "):].strip() if first.startswith("REPORT ") else "?"
    c = counts(text)
    status = _scalar(text, "status") or "?"

    out = [
        f"REPORT HEAD {run_id}",
        f"{'artifact:':16s} {path.resolve()}",
        f"{'status:':16s} {status}",
        f"{'verdict:':16s} {_scalar(text, 'verdict') or '?'}",
        f"{'verification:':16s} {_scalar(text, 'result') or '?'}",
        f"{'detail:':16s} {(_scalar(text, 'detail') or '?')[:MAX_HEADLINE]}",
    ]
    out += [f"{n + ':':16s} {c[n]}" for n in COUNTED]
    if status in {"BLOCKED", "REFUSED"}:
        out.append(f"{'blocked_on:':16s} <why, in one line - replace this>")
    out.append(f"{'headline:':16s} "
               f"<outcome in one sentence under {MAX_HEADLINE} chars - replace this>")
    return "\n".join(out)


def check(path: Path, lane: str | None = None, head: str | None = None,
          warn: list[str] | None = None) -> list[str]:
    """Return blocking violations; append advisory notes to `warn` if given."""
    text = _unwrap(path.read_text(encoding="utf-8"))
    bad: list[str] = []
    warn = warn if warn is not None else []

    first = next((ln for ln in text.splitlines() if ln.strip()), "")
    if not first.startswith("REPORT "):
        bad.append(f"first non-blank line must be 'REPORT <id>', got {first!r}")

    status = _scalar(text, "status")
    if status is None:
        bad.append("missing 'status:'")
    elif status not in STATUS:
        bad.append(f"status {status!r} not in {sorted(STATUS)}"
                   + (" - CHANGES_REQUESTED is a verdict, not a status"
                      if status == "CHANGES_REQUESTED" else ""))

    verdict = _scalar(text, "verdict")
    if verdict is None:
        bad.append("missing 'verdict:' (write NONE if this lane is not a gate)")
    elif verdict not in VERDICT:
        bad.append(f"verdict {verdict!r} not in {sorted(VERDICT)}")

    for name in SECTIONS:
        lines = _section(text, name)
        if lines is None:
            bad.append(f"missing section '{name}:'")
        elif not lines:
            bad.append(f"section '{name}:' is empty - write '- none', "
                       "silence is ambiguous")
        elif name in COUNTED:
            if len(lines) == 1 and re.match(r"^-\s*none\b.", lines[0], re.I):
                # Counted as an entry, deliberately: reinterpreting it as empty
                # could drop a real note hiding behind "none of X, but Y lags".
                # Say so instead, so the author resolves the ambiguity.
                warn.append(
                    f"{name}: '- none' carries trailing commentary, so it counts "
                    "as 1 entry - write bare '- none', or make it a real bullet")
            for b in _bullets(lines):
                if len(b) > MAX_BULLET:
                    bad.append(
                        f"{name}: bullet is {len(b)} chars (max {MAX_BULLET}) - "
                        "it is carrying several facts; split it, or move the "
                        f"detail below the block and cite it: {b[:60]}...")
                elif len(b) > TARGET_BULLET:
                    warn.append(
                        f"{name}: bullet is {len(b)} chars (target "
                        f"{TARGET_BULLET}): {b[:60]}...")

    result = _scalar(text, "result")
    command = _scalar(text, "command")
    if result is None:
        bad.append("missing 'result:' under verification")
    elif result not in RESULT:
        bad.append(f"verification.result {result!r} not in {sorted(RESULT)}")

    # The rule that catches the expensive failure: claiming DONE on unverified
    # work. A read-only order (command NONE) is exempt.
    read_only = command is None or command.strip().upper() in {"NONE", "-"}
    if status == "DONE" and result == "NOT_RUN" and not read_only:
        bad.append(f"status DONE with result NOT_RUN and command {command!r} - "
                   "an order that named a command must run it")

    bad += _check_brief(text)

    if lane:
        # `quant` and `quant-audit` are different lanes and the filename knows
        # which one this is. Without the hint the message reads as "this report
        # is wrong" when the real fault is the --lane argument, which cost a
        # wasted round-trip on the first real run.
        inferred = lane_from_name(path)
        hint = (f" — the filename says lane {inferred!r}; did you mean "
                f"--lane {inferred}?") if inferred and inferred != lane else ""
        if verdict and verdict != "NONE" and lane not in GATE_LANES:
            bad.append(f"lane {lane!r} emitted verdict {verdict!r}; only "
                       f"{sorted(GATE_LANES)} may judge{hint}")
        if verdict == "CHANGES_REQUESTED" and lane not in CR_LANES:
            bad.append(f"lane {lane!r} emitted CHANGES_REQUESTED; only "
                       f"{sorted(CR_LANES)} may{hint}")

    if head is not None:
        bad += _check_head(head, text)

    return bad


def _check_brief(text: str) -> list[str]:
    """An artifact with a body beyond the block must open that body with a brief.

    The orchestrator reads the brief instead of the document. Without one it
    reads the document — which is how two planning artifacts came to be half of
    a run's entire artifact volume, read end to end for thirty lines of routing.
    """
    lines = text.splitlines()
    fenced = _fenced(text)
    headings = [(i, ln.strip()) for i, ln in enumerate(lines)
                if i not in fenced and ln.startswith("## ")]
    if not headings:
        return []
    if headings[0][1] != BRIEF_HEADING:
        return [f"artifact has sections but the first is {headings[0][1]!r}; "
                f"a body beyond the report block must open with {BRIEF_HEADING!r}"]

    start = headings[0][0]
    end = headings[1][0] if len(headings) > 1 else len(lines)
    body = "\n".join(lines[start + 1:end])
    n = len([ln for ln in body.splitlines() if ln.strip()])

    # The brief must also NAME every section below it. With more sections than
    # MAX_BRIEF those two rules would be mutually unsatisfiable, and the only
    # escape an agent has is deleting real sections — so the cap grows with the
    # document it indexes. One line per section is still an index, not prose.
    cap = max(MAX_BRIEF, len(headings) - 1 + 3)

    bad: list[str] = []
    if n > cap:
        bad.append(f"{BRIEF_HEADING} is {n} lines (max {cap} for "
                   f"{len(headings) - 1} sections) - it is an index with "
                   "verdicts, not a summary of the reasoning")
    bad += _brief_covers(body, [h for _, h in headings[1:]])
    return bad


# Identifiers are how sections get referred to downstream: US-36.1, T-36.1.1,
# CR-2, AC7, F-R4.
ID_RE = re.compile(r"\b(?:[A-Z]{1,3}-)?[A-Z]{1,3}-?\d+(?:\.\d+)*[a-z]?\b")


def _brief_covers(brief: str, sections: list[str]) -> list[str]:
    """Every section below the brief must be findable *from* the brief.

    This is what keeps the brief from becoming a lossy summary. The orchestrator
    routes from these 15 lines and never reads the document, so a story the
    brief forgets to name is a story that never gets dispatched — and reading
    all 546 lines is precisely what used to prevent that. Making the read
    shorter is only safe if the short part is provably complete.
    """
    flat = " ".join(brief.split()).lower()
    bad: list[str] = []
    for title in (h[3:].strip() for h in sections):
        ids = ID_RE.findall(title)
        if ids:
            # `(?!\d)` so naming US-36.10 does not satisfy a US-36.1 section.
            if not any(re.search(rf"{re.escape(i.lower())}(?!\d)", flat)
                       for i in ids):
                bad.append(f"{BRIEF_HEADING} does not name {ids[0]!r} "
                           f"(section {title[:50]!r}) - a section the brief "
                           "omits is one the orchestrator never routes")
            continue
        if " ".join(title.split()).lower() not in flat:
            bad.append(f"{BRIEF_HEADING} does not name section {title[:50]!r} - "
                       "the brief must name every section below it")
    return bad


def _check_head(head: str, text: str) -> list[str]:
    head = _unwrap(head)
    bad: list[str] = []
    first = next((ln for ln in head.splitlines() if ln.strip()), "")
    if not first.startswith("REPORT HEAD "):
        bad.append(f"head must start 'REPORT HEAD <id>', got {first!r}")

    for key in ("artifact", "status", "verdict", "verification", "detail",
                "headline"):
        v = _scalar(head, key)
        if v is None:
            bad.append(f"head missing {key!r}")
        elif _PLACEHOLDER.match(v):
            bad.append(f"head {key} is still the --emit-head placeholder "
                       f"{v!r} - fill it in")

    for key in ("status", "verdict"):
        h, a = _scalar(head, key), _scalar(text, key)
        if h is not None and a is not None and h != a:
            bad.append(f"head {key} {h!r} disagrees with artifact {a!r}")

    hv, av = _scalar(head, "verification"), _scalar(text, "result")
    if hv is not None and av is not None and hv != av:
        bad.append(f"head verification {hv!r} disagrees with "
                   f"artifact verification.result {av!r}")

    # `detail` is the orchestrator's only window onto whether a PASS is real —
    # "802 passed" vs "802 passed, 4 skipped". It must be the artifact's detail
    # truncated at MAX_HEADLINE, *verbatim*, not merely a prefix of it: an agent
    # free to stop early can stop just before the bad news, which is exactly the
    # failure putting `detail` in the head was meant to close.
    hd, ad = _scalar(head, "detail"), _scalar(text, "detail")
    if hd is not None and ad is not None and not _PLACEHOLDER.match(hd):
        expect = ad[:MAX_HEADLINE].strip()
        if hd != expect:
            bad.append(f"head detail must be verification.detail truncated at "
                       f"{MAX_HEADLINE} chars, verbatim - expected "
                       f"{expect[:60]!r}..., got {hd[:60]!r}...")

    for name, n in counts(text).items():
        raw = _scalar(head, name)
        if raw is None:
            bad.append(f"head missing count {name!r}")
        elif not raw.isdigit():
            bad.append(f"head {name} {raw!r} is not an integer")
        elif int(raw) != n:
            bad.append(f"head {name} says {raw} but artifact has {n} - a head "
                       "that undercounts silently drops work")

    status = _scalar(text, "status")
    if status in {"BLOCKED", "REFUSED"} and _scalar(head, "blocked_on") is None:
        bad.append(f"status {status} requires 'blocked_on:' in the head")

    headline = _scalar(head, "headline") or ""
    if len(headline) > MAX_HEADLINE:
        bad.append(f"head headline is {len(headline)} chars (max {MAX_HEADLINE})")
    return bad


def _flag_value(argv: list[str], flag: str) -> str | None:
    """Value after `flag`, or None. A following flag is not a value."""
    if flag not in argv:
        return None
    i = argv.index(flag)
    if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
        return None
    return argv[i + 1]


def main(argv: list[str]) -> int:
    lane = _flag_value(argv, "--lane")
    head_path = _flag_value(argv, "--head")
    emit = "--emit-head" in argv

    # Drop flags and the values they consume *by position*, so an artifact whose
    # name happens to match a lane is not silently swallowed.
    skip: set[int] = set()
    for j, a in enumerate(argv):
        if a in ("--lane", "--head"):
            skip.update({j, j + 1})
        elif a.startswith("--"):
            skip.add(j)
    args = [a for j, a in enumerate(argv) if j > 0 and j not in skip]

    if not args:
        print(__doc__)
        return 2

    target = Path(args[0])
    if not target.exists():
        print(f"no such path: {target}")
        return 2

    if emit:
        if target.is_dir():
            print("--emit-head takes one artifact, not a directory")
            return 2
        print(head_for(target))
        return 0

    if target.is_dir():
        # Report artifacts are numbered: 01-scout.md, 02-delivery-brief.md.
        # run.md is the ledger and pack-corrections.md is a queue; neither is
        # a report and neither should be validated as one.
        files = sorted(p for p in target.glob("*.md")
                       if re.match(r"^\d{2}-", p.name))
    else:
        files = [target]
    if not files:
        print(f"no report artifacts found in {target}")
        return 2

    head = None
    if head_path:
        if len(files) > 1:
            print("--head checks one artifact, not a directory")
            return 2
        head = (sys.stdin.read() if head_path == "-"
                else Path(head_path).read_text(encoding="utf-8"))

    failed = False
    for f in files:
        notes: list[str] = []
        problems = check(f, lane or lane_from_name(f), head, notes)
        if problems:
            failed = True
            print(f"FAIL {f}")
            for p in problems:
                print(f"  - {p}")
        else:
            print(f"ok   {f}")
        for w in notes:
            print(f"  ~ {w}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
