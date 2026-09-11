#!/usr/bin/env python3
"""Validate an agent report against PROTOCOL.md § 3, and its head against § 4.

    python scripts/check_report.py runs/<run-id>/01-scout.md [--lane recon]
    python scripts/check_report.py runs/<run-id>/            # every artifact
    python scripts/check_report.py <artifact> --emit-head    # print the head
    python scripts/check_report.py <artifact> --head head.txt
    python scripts/check_report.py runs/<run-id>/ --require-heads   # close-out

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

`--require-heads` exists because deriving a head is worthless if nobody checks
it against the artifact. § 4 makes `--head` mandatory per dispatch, but a
mandate the close-out cannot see is a mandate that quietly lapses: across runs
2026-08-31 through 2026-09-03, not one head was saved and `--head` was never
run, so `rounds: 0` meant "nothing was sent back" and "nothing was checked"
indistinguishably. This flag makes the omission a failure the sweep reports,
for every numbered dispatch slot, in one command. It also checks the run
ledger's `gates:` line against its Artifacts rows, so a gate that quietly did
not run cannot pass close-out unnoticed.

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

# The three gates a delivery run can be asked for, checked against the ledger's
# `gates:` line by the close-out sweep. `quant-audit` is conditional on the
# substance being mathematical and `review` on there being a story to accept, so
# none of these is required by route alone - which is exactly why the ledger has
# to say what happened to each one rather than the sweep guessing.
#
# Deliberately three where GATE_LANES is four. The fourth, `protocol-lint`,
# gates authoring orders against the network's own files; it has nothing to say
# about a run that changes the bound repo, and requiring every delivery ledger
# to write `protocol-lint skipped (not an authoring order)` would be a line that
# is always the same and therefore never read.
LEDGER_GATES = ("quant-audit", "integration", "review")

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

# `recon` and `quant` RESEARCH are evidence lanes: a bullet carries a claim plus
# the file:line that proves it, and the citation is the point. Measured over the
# closed runs, recon's *median* bullet is 314 characters - a 200 target that
# half of all bullets miss is not a target, it is noise that teaches the reader
# to skip the `~` lines. Their ceiling is set above every quant bullet ever
# written (max 591) and above recon's p90 (634), which still leaves recon's real
# outliers - 923, 1000, 1517 - flagged as what they are.
WIDE_LANES = {"recon", "quant"}
WIDE_TARGET = 400
WIDE_MAX = 600


def _limits(lane: str | None) -> tuple[int, int]:
    """(target, max) for this lane's bullets."""
    if lane in WIDE_LANES:
        return WIDE_TARGET, WIDE_MAX
    return TARGET_BULLET, MAX_BULLET
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


def _is_report(path: Path) -> bool:
    """True when the file is an agent report rather than a ledger or a queue."""
    try:
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    return line.startswith("REPORT ")
    except (OSError, UnicodeDecodeError):
        return False
    return False


# Names filenames actually use that are not the lane's own name. Each entry is
# here because a real artifact carries it, not on speculation: `01-scout.md`
# (the agent, not the lane), `04-stories.md`, `AUDIT-quant.md` and
# `10-quant-reaudit.md` (a re-audit is an audit).
NAME_ALIASES = {
    "scout": "recon",
    "stories": "story",
    "audit-quant": "quant-audit",
    "quant-reaudit": "quant-audit",
}


def lane_from_name(path: Path) -> str | None:
    """Infer the lane from an artifact filename, or None if unclear.

    Lets a whole-directory scan still apply the gate rules. Only returns a lane
    it actually recognises — guessing one would invent violations.

    The lane token used to be read from one fixed position, right after the
    `<nn>-` prefix. Ticket-named artifacts put it last instead
    (`INTEGRATION-tech-lead.md`, `T-40.1.3-T-40.2.2a-backend.md`), so every one
    of them inferred nothing and ran unchecked against the gate rules. Scan the
    whole name instead, and prefer a two-token match to a one-token match: a
    `quant-audit` that also contains `quant` is the more specific evidence, and
    reading it as the `quant` lane would flag its verdict as a lane that may not
    judge — inventing a violation, which is the one thing this must not do.
    """
    parts = [NAME_ALIASES.get(s, s) for s in path.stem.lower().split("-")]
    pairs = [f"{a}-{b}" for a, b in zip(parts, parts[1:])]
    for window in ([NAME_ALIASES.get(x, x) for x in pairs], parts):
        hits = {x for x in window if x in LANES}
        if len(hits) == 1:
            return hits.pop()
        if hits:
            return None  # two lanes named, no way to choose between them
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
            target, cap = _limits(lane)
            # Over the cap blocks on a gate lane and advises everywhere else.
            # The orchestrator *routes* off a gate's bullets - a finding becomes
            # a change request, a BLOCKING item becomes a dispatch - so one that
            # cannot be handed to a single lane is a structural problem there.
            # Elsewhere a long bullet is read by a human in context. The closed
            # runs say the same thing from the other side: gate lanes have never
            # once exceeded 400 (their longest is 310), so this costs them
            # nothing, while 97 blocking violations were overridden everywhere
            # else without one of them ever turning out to be a real defect.
            over = bad if lane in GATE_LANES else warn
            for b in _bullets(lines):
                if len(b) > cap:
                    over.append(
                        f"{name}: bullet is {len(b)} chars (max {cap}) - "
                        "it is carrying several facts; split it, or move the "
                        f"detail below the block and cite it: {b[:60]}...")
                elif len(b) > target:
                    warn.append(
                        f"{name}: bullet is {len(b)} chars (target "
                        f"{target}): {b[:60]}...")

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
            # Show where they part, not the first 60 characters of each. The
            # divergence is usually past that mark - an agent copies the detail
            # and stops one character late, or abridges the middle - so both
            # sides opened with an identical prefix and six ledger rows across
            # two runs wrote this off as a cosmetic encoding quirk. It was not
            # cosmetic: two of those were the lane editing its own evidence.
            i = next((k for k in range(min(len(hd), len(expect)))
                      if hd[k] != expect[k]), min(len(hd), len(expect)))
            bad.append(f"head detail must be verification.detail truncated at "
                       f"{MAX_HEADLINE} chars, verbatim - they diverge at char "
                       f"{i} of {len(hd)}/{len(expect)}: head has "
                       f"{hd[i:i + 40]!r}, artifact has {expect[i:i + 40]!r}")

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


def _ledger_field(text: str, name: str) -> str | None:
    """A `name:  value` line from the ledger header, or None."""
    m = re.search(rf"^{re.escape(name)}:[ 	]*(.*)$", text, re.M)
    return m.group(1).strip() if m else None


def _ledger_table(text: str, heading: str) -> list[list[str]]:
    """Rows of the markdown table under `## <heading>`, header/rule dropped."""
    m = re.search(rf"^## {re.escape(heading)}[ 	]*$", text, re.M)
    if not m:
        return []
    rows: list[list[str]] = []
    for ln in text[m.end():].splitlines():
        s = ln.strip()
        if s.startswith("## "):
            break
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(set(c) <= {"-", ":"} and c for c in cells):
            continue          # the |---|---| rule
        rows.append(cells)
    return rows[1:] if rows else []   # drop the header row


def _gate_rows(arts: list[list[str]]) -> dict[str, str]:
    """Gate lane -> the verdict its last Artifacts row recorded."""
    seen: dict[str, str] = {}
    for row in arts:
        if len(row) < 8:
            continue
        lane, verdict = row[1].strip().lower(), row[7].strip()
        # A gate can be written as its lane (`quant-audit`) or as a lane plus a
        # mode (`quant` + `AUDIT`), and both spellings are in the closed runs.
        mode = row[2].strip().lower()
        if lane == "quant" and mode.startswith("audit"):
            lane = "quant-audit"
        if lane in LEDGER_GATES and verdict and verdict not in {"—", "-"}:
            seen[lane] = verdict
    return seen


def check_gates(ledger: Path) -> list[str]:
    """Every gate either ran and is recorded, or is accounted for as skipped.

    Two runs closed without an acceptance gate and without saying so anywhere
    that outlives the session. The skill already required the orchestrator to
    report "which gates did not run and why" - to the human, once, in prose
    that is gone by the next run. This puts the same disclosure in the ledger,
    where it survives and can be checked.
    """
    text = ledger.read_text(encoding="utf-8")
    stated = _ledger_field(text, "gates")
    ran = _gate_rows(_ledger_table(text, "Artifacts"))
    if stated is None:
        return ["no `gates:` line - the ledger cannot say which gates ran and "
                "which were skipped on purpose"]
    low = stated.lower()
    problems = []
    for g in LEDGER_GATES:
        if g not in low:
            problems.append(f"`gates:` does not account for {g} - name it with "
                            f"its verdict, or `skipped` and why")
        elif g in ran and ran[g].lower() not in low:
            problems.append(f"`gates:` disagrees with the rows on {g}: rows "
                            f"recorded {ran[g]}")
        elif g not in ran and "skip" not in low.split(g, 1)[1][:40]:
            problems.append(f"{g} has no verdict row, and `gates:` does not "
                            f"mark it skipped - a gate that quietly did not "
                            f"run is the one failure close-out cannot see")
    return problems


def _flag_value(argv: list[str], flag: str) -> str | None:
    """Value after `flag`, or None. A following flag is not a value."""
    if flag not in argv:
        return None
    i = argv.index(flag)
    if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
        return None
    return argv[i + 1]


HEAD_SLOT = re.compile(r"^(\d+)-")


def head_path_for(artifact: Path) -> Path | None:
    """The head file a numbered dispatch slot must have saved beside it.

    `01-recon.md` -> `01-head.txt`, the name SKILL.md § "Validate the artifact
    against its head" tells the orchestrator to write. Returns None for an
    artifact that is not a numbered slot -- ticket-named artifacts are not
    dispatches and have no head to check.
    """
    m = HEAD_SLOT.match(artifact.name)
    return artifact.with_name(f"{m.group(1)}-head.txt") if m else None


def main(argv: list[str]) -> int:
    # Reports quote file paths, arrows and dashes; Python on Windows encodes
    # stdout as cp1252 and raises on the first character outside it. That
    # aborted the whole sweep mid-directory with a traceback, so the artifacts
    # after the offending one were never checked and the run still looked like
    # a tooling glitch rather than a gap in coverage.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    lane = _flag_value(argv, "--lane")
    head_path = _flag_value(argv, "--head")
    emit = "--emit-head" in argv
    require_heads = "--require-heads" in argv

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
        # A report is a file whose first line says so — PROTOCOL.md § 3's own
        # definition. The rule used to be the filename regex `^\d{2}-`, which
        # silently skipped every ticket-named artifact once runs started using
        # them: a sweep of a 10-artifact run reported "ok" having opened 3,
        # including neither the AUDIT nor the INTEGRATION gate. run.md is the
        # ledger and pack-corrections.md is a queue; neither opens with REPORT,
        # so neither needs naming here.
        files = sorted(p for p in target.glob("*.md") if _is_report(p))
    else:
        files = [target]
    if not files:
        print(f"no report artifacts found in {target}")
        return 2

    if require_heads and head_path:
        print("--require-heads finds each head by name; do not also pass --head")
        return 2

    head = None
    if head_path:
        if len(files) > 1:
            print("--head checks one artifact, not a directory")
            return 2
        head = (sys.stdin.read() if head_path == "-"
                else Path(head_path).read_text(encoding="utf-8"))

    failed = False

    # Close-out also validates the ledger itself: the `gates:` line has to
    # account for all three delivery gates. It is checked here rather than in
    # its own script because close-out is the only moment the answer is knowable
    # and the only moment anyone runs a sweep - a check with its own command is
    # a check that gets skipped.
    if require_heads and target.is_dir():
        ledger = target / "run.md"
        if not ledger.is_file():
            print(f"  ~ no run.md in {target} - `gates:` not checked")
        else:
            gate_problems = check_gates(ledger)
            if gate_problems:
                failed = True
                print(f"FAIL {ledger}")
                for g in gate_problems:
                    print(f"  - {g}")
            else:
                print(f"ok   {ledger} (gates)")

    for f in files:
        notes: list[str] = []
        f_head = head
        if require_heads:
            hp = head_path_for(f)
            if hp is None:
                notes.append(f"{f.name} is not a numbered dispatch slot - "
                             "no head required")
            elif not hp.is_file():
                # Not an advisory. A dispatch whose head was never saved was
                # never validated against its artifact, and an unvalidated
                # head is the one failure that does not announce itself.
                failed = True
                print(f"FAIL {f}")
                print(f"  - no head saved at {hp.name} - PROTOCOL.md " "§ 4 "
                      "requires one per dispatch, and without it nothing "
                      "checked this artifact against its own summary")
                continue
            else:
                f_head = hp.read_text(encoding="utf-8")
        problems = check(f, lane or lane_from_name(f), f_head, notes)
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
