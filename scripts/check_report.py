#!/usr/bin/env python3
"""Validate an agent report against PROTOCOL.md § 3, and its head against § 4.

    python scripts/check_report.py <run_dir>/01-scout.md [--lane recon]
    python scripts/check_report.py <run_dir>/               # every artifact
    python scripts/check_report.py <artifact> --emit-head   # print the head
    python scripts/check_report.py <artifact> --head head.txt
    python scripts/check_report.py <run_dir>/ --require-heads      # close-out

`<run_dir>` is `<agenticRoot>/projects/<project>/runs/<run-id>/`.

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
# The profile's `## Phases` table is the authority (`protocol/authoring.md`):
# its `verify` rows name the lanes that gate *this* project. This tuple is the
# fallback for a ledger whose profile cannot be resolved - a run dir copied
# elsewhere, a project.md not yet written - and it is this project's set, which
# is why resolving beats it wherever resolution is possible.
DEFAULT_LEDGER_GATES = ("quant-audit", "integration", "review")
LEDGER_GATES = DEFAULT_LEDGER_GATES
# Not in LEDGER_GATES - required only when the run produced pack
# corrections. See check_authoring_gate.
AUTHORING_GATE = "protocol-lint"

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


def _is_ledger(path: Path) -> bool:
    """The run ledger, by the two marks the protocol fixes: its name and its
    first line. Everything else in a run dir opens with `REPORT`."""
    if path.name.lower() == "run.md":
        return True
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                return line.strip().upper().startswith("# RUN ")
    except OSError:
        return False
    return False


def check_ledger(ledger: Path, closed_only: bool = False) -> list[str]:
    """Everything the ledger itself must satisfy, in one call.

    `check_gates` is the one member that cannot answer mid-run - a gate with no
    verdict row is a failure at close-out and simply the current state at
    dispatch three - so it joins only once the run says it is CLOSED.
    """
    problems = (check_header(ledger) + check_phases(ledger)
                + check_budget(ledger) + check_decisions(ledger)
                + check_open_table(ledger) + check_models(ledger)
                + check_authoring_gate(ledger.parent))
    status = (_ledger_field(ledger.read_text(encoding="utf-8"), "status")
              or "").strip().upper()
    if status == "CLOSED" or not closed_only:
        problems += check_gates(ledger)
    return problems


LEDGER_CHECKS = "header, phases, budget, decisions, gates, open, models, authoring"


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
                # So the author resolves the ambiguity, not the script.
                #
                # Blocking since v0.7.1, on the evidence of run 2026-09-12: the
                # docs lane wrote `pack_corrections: - none - verified both
                # packs, nothing to correct`, its head therefore advertised 1
                # correction, the orchestrator opened a pack-corrections.md for
                # it, and the ledger then recorded `protocol-lint skipped
                # (pack-corrections.md is empty)` about a file that was not.
                # One ambiguous bullet, three downstream records wrong. It is
                # also the cheapest violation in the set to fix - delete four
                # words - and blocking is what reaches the shell-less lanes,
                # since report_artifact_gate.py drops advisory notes and these
                # three lanes have no other check.
                bad.append(
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


def _gate_rows(arts: list[list[str]],
               gates: tuple[str, ...] = DEFAULT_LEDGER_GATES) -> dict[str, str]:
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
        if lane in gates and verdict and verdict not in {"—", "-"}:
            seen[lane] = verdict
    return seen


# `Open` holds what is still open (protocol/orchestrator.md § 1). A row that has
# been absorbed moves to `## Closed`; resolved is not a state a row sits in.
# Prose was not enough to hold that: the rule was superseded in v0.4.2 and two
# files went on instructing the old one, so a run could follow the documented
# procedure and still grow the table without bound - which is the cost the
# correction was made to stop, every row being re-read on every ledger update.
OPEN_STATES = {"OPEN", "CARRIED"}
RESOLVED_STATES = {"ABSORBED", "CLOSED"}


def check_open_table(ledger: Path) -> list[str]:
    """No row sits in `Open` in a state that means it should have left.

    Judged on the leading token, not the whole cell. Real ledgers qualify these
    - `ABSORBED by 06`, `CARRIED - deferred code nit` - and a `CARRIED` row is
    *supposed* to carry its reason to the human at close-out. Demanding a bare
    enum here would fail rows that are doing exactly what the protocol asks.
    """
    rows = _ledger_table(ledger.read_text(encoding="utf-8"), "Open")
    problems = []
    for row in rows:
        if len(row) < 5:
            continue
        cell = row[4].strip()
        if not cell:
            continue
        head = re.split(r"[^A-Za-z]", cell.upper(), 1)[0]
        if head in OPEN_STATES:
            continue
        ref = row[2].strip() or row[1].strip() or "?"
        if head in RESOLVED_STATES:
            problems.append(f"`Open` row {ref} is {head} - a resolved row moves "
                            f"to `## Closed` with the dispatch that absorbed "
                            f"it; leaving it here is what grows the table")
        else:
            problems.append(f"`Open` row {ref} has state {cell!r} - "
                            f"{sorted(OPEN_STATES)} are the states a row can "
                            f"still be open in")
    return problems


def check_authoring_gate(run_dir: Path) -> list[str]:
    """A run that rewrote the network's own files names the authoring gate.

    `protocol-lint` is deliberately outside `LEDGER_GATES`: it gates authoring
    orders, and a line reading `skipped (not an authoring order)` on every
    delivery run is a line nobody reads.

    But `pack-corrections.md` is an authoring order. It is the one dispatch
    that *always* writes inside `<agenticRoot>` - `packs.md` § 3 says so
    explicitly - and because it arrives at close-out inside a delivery run, the
    rule above excused the only gate that judges what it wrote.
    `2026-09-11-risk-summary-audit-foldable` is what that looks like: the docs
    lane rewrote 51 lines of `capabilities/product.md`, disclosed in `risks`
    that the edit went past what `packs.md` permits, and no gate saw it.

    So the trigger is the file, not the route: corrections exist, therefore the
    gate is accountable. `skipped` with a reason still satisfies this - the
    point is that a human decided, not that the gate ran.
    """
    corrections = run_dir / "pack-corrections.md"
    if not corrections.is_file() or not corrections.read_text(encoding="utf-8").strip():
        return []
    stated = _ledger_field((run_dir / "run.md").read_text(encoding="utf-8"), "gates")
    if stated and AUTHORING_GATE in stated.lower():
        return []
    return [f"pack-corrections.md is non-empty, so this run edited the "
            f"network's own files, but `gates:` does not account for "
            f"{AUTHORING_GATE} - name it with its verdict, or `skipped` and why"]


def check_gates(ledger: Path, gates: tuple[str, ...] | None = None) -> list[str]:
    """Every gate either ran and is recorded, or is accounted for as skipped.

    Two runs closed without an acceptance gate and without saying so anywhere
    that outlives the session. The skill already required the orchestrator to
    report "which gates did not run and why" - to the human, once, in prose
    that is gone by the next run. This puts the same disclosure in the ledger,
    where it survives and can be checked.
    """
    text = ledger.read_text(encoding="utf-8")
    gates = gates if gates is not None else profile_gates(ledger)
    stated = _ledger_field(text, "gates")
    ran = _gate_rows(_ledger_table(text, "Artifacts"), gates)
    if stated is None:
        return ["no `gates:` line - the ledger cannot say which gates ran and "
                "which were skipped on purpose"]
    low = stated.lower()
    problems = []
    for g in gates:
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


# The ledger header's own enum (protocol/orchestrator.md section 1). A run
# whose status is not one of these cannot be resumed by a fresh session, which
# is the only reason the field exists.
LEDGER_STATUS = {"PLANNING", "DISPATCHING", "GATING", "BLOCKED", "CLOSED"}

_SATISFIED = re.compile(r"^satisfied\b", re.I)
_NOT_TRIGGERED = re.compile(r"^not[ _-]triggered\b\s*(.*)$", re.I | re.S)
_PENDING = re.compile(r"^(pending|planned|queued)\b", re.I)


def _verify_lanes(profile: str) -> tuple[str, ...]:
    """Gate lanes a project profile declares, from its `## Phases` verify rows."""
    lanes: list[str] = []
    for row in _ledger_table(profile, "Phases"):
        if len(row) < 3 or row[0].strip().lower() != "verify":
            continue
        lane = row[2].strip().lower()
        if lane and lane not in lanes:
            lanes.append(lane)
    return tuple(lanes)


def _stop_lanes(profile: str) -> set[str]:
    """Lanes whose phase carries a human stop, from the profile's last column."""
    stops = set()
    for row in _ledger_table(profile, "Phases"):
        if len(row) < 5:
            continue
        if "yes" in row[4].strip().lower():
            stops.add(row[2].strip().lower())
    return stops


def _profile_text(ledger: Path) -> str | None:
    """This run's project profile, or None if it cannot be resolved."""
    text = ledger.read_text(encoding="utf-8")
    root = _ledger_field(text, "agentic_root")
    project = _ledger_field(text, "project")
    candidates = []
    if root and project:
        candidates.append(Path(root) / "projects" / project / "project.md")
    candidates.append(ledger.parent.parent.parent / "project.md")
    for cand in candidates:
        try:
            if cand.is_file():
                return cand.read_text(encoding="utf-8")
        except OSError:
            continue
    return None


def profile_gates(ledger: Path) -> tuple[str, ...]:
    """The gates this run's project declares, or the fallback set.

    Two ways to the profile, both cheap. The ledger names `project:` and
    `agentic_root:`, which is the explicit route; and a run dir living at
    `<agenticRoot>/projects/<project>/runs/<run-id>/` knows its own profile from
    its path, which is the route that survives a ledger missing the field.
    Neither existing is not an error - the fallback is a real set, and a script
    that refuses to run without a profile is a script the close-out skips.
    """
    profile = _profile_text(ledger)
    if profile:
        lanes = _verify_lanes(profile)
        if lanes:
            return lanes
    return DEFAULT_LEDGER_GATES


def check_header(ledger: Path) -> list[str]:
    """The header fields a resumed session reads before anything else.

    `status`, `blocked_on` and `next` are the three a fresh session acts on, and
    each has a failure that is silent at the moment it is written: a status
    outside the enum cannot be branched on, a `BLOCKED` with no `blocked_on`
    stops a run without saying what would restart it, and a `CLOSED` run whose
    `next:` still names a dispatch is how a resume re-runs a lane that already
    ran.
    """
    text = ledger.read_text(encoding="utf-8")
    status = _ledger_field(text, "status")
    blocked_on = _ledger_field(text, "blocked_on")
    nxt = _ledger_field(text, "next")
    problems = []
    if status is None:
        return ["no `status:` line - a run with no status cannot be resumed"]
    if status not in LEDGER_STATUS:
        problems.append(f"status {status!r} not in {sorted(LEDGER_STATUS)} - the "
                        f"field takes the bare enum; a reason goes on "
                        f"`blocked_on:`")
    if status == "BLOCKED" and not blocked_on:
        problems.append("status BLOCKED with no `blocked_on:` - the ledger says "
                        "the run stopped but not what would restart it")
    # `blocked_on: none` is an explicit "not blocked", which is a placeholder
    # and not a claim. A sentence there on a run that is not BLOCKED is a claim,
    # and it is one about a block that has ended.
    stale = blocked_on and blocked_on.strip().lower().strip(".") not in {
        "none", "-", "—", ""}
    if status != "BLOCKED" and stale:
        problems.append(f"`blocked_on: {blocked_on}` on a {status} run - it is "
                        f"written only while BLOCKED, or it describes a block "
                        f"that is over")
    if status == "CLOSED" and not (nxt or "").lower().startswith("none"):
        problems.append(f"status CLOSED with `next: {nxt}` - close-out sets "
                        f"`next: none - CLOSED`, or a resumed session "
                        f"re-dispatches a lane that already ran")
    return problems


def check_phases(ledger: Path) -> list[str]:
    """Every `## Phases` row is accounted for - the termination condition.

    `protocol/orchestrator.md` section 3 says a run may close when every row
    reads `satisfied` or `not triggered (<clause>)`. That was prose, and prose
    is what the route enum was replaced for: a `pending` row left in a CLOSED
    ledger is the run's own record that it stopped early, and nothing read it.

    The clause is required, not decorative. `not triggered` alone records that
    a question went unasked without recording which one, which is the single
    thing the phase model exists to give a later reader over a route name.
    """
    text = ledger.read_text(encoding="utf-8")
    rows = _ledger_table(text, "Phases")
    status = _ledger_field(text, "status")
    if not rows:
        if _ledger_field(text, "plan") or _ledger_field(text, "budget"):
            return ["no `## Phases` table - a phase-model ledger carries one, "
                    "and without it nothing can check that the run finished "
                    "what it planned"]
        return []
    problems = []
    if not _ledger_field(text, "project"):
        problems.append("no `project:` line - the ledger cannot say which "
                        "profile declared these phases, so the gates it owes "
                        "cannot be resolved")
    for row in rows:
        if len(row) < 4:
            problems.append(f"`Phases` row {row[0] if row else '?'!r} has "
                            f"{len(row)} columns - the table is "
                            f"phase | lane | fires when | state")
            continue
        phase, state = row[0].strip(), row[3].strip()
        if _SATISFIED.match(state):
            continue
        m = _NOT_TRIGGERED.match(state)
        if m:
            clause = m.group(1).strip().strip("()").strip()
            if not clause:
                problems.append(f"phase {phase!r} is `not triggered` with no "
                                f"clause - write the clause that was false, or "
                                f"the ledger records an omission where it "
                                f"means a decision")
            continue
        if _PENDING.match(state):
            if status == "CLOSED":
                problems.append(f"phase {phase!r} is still {state!r} in a "
                                f"CLOSED run - dispatch it, or write down the "
                                f"clause that stopped it firing")
            continue
        problems.append(f"phase {phase!r} has state {state!r} - a row reads "
                        f"`satisfied`, `pending`, or "
                        f"`not triggered (<clause>)`")
    return problems


def check_decisions(ledger: Path) -> list[str]:
    """A human stop the run passed leaves the ruling on disk, in their words.

    The relay rule makes every judgment in a run a path, with one exception that
    the rule never named: the human's. A decision made in the chat reaches the
    next lane as the orchestrator's restatement of it, which is the exact shape
    the relay rule exists to forbid - and `2026-09-11`'s story lane said so in
    its own `risks`, having drafted against a paraphrase it could not check.

    The profile says which phases carry a stop (its `Human stop` column), so
    this needs no list of its own: a satisfied phase whose lane the profile
    marks as a stop owes an entry in `decisions.md`.
    """
    profile = _profile_text(ledger)
    if profile is None:
        return []
    stops = _stop_lanes(profile)
    if not stops:
        return []
    text = ledger.read_text(encoding="utf-8")
    passed = []
    for row in _ledger_table(text, "Phases"):
        if len(row) < 4:
            continue
        lane = row[1].strip().lower()
        if lane in stops and _SATISFIED.match(row[3].strip()):
            passed.append(lane)
    if not passed:
        return []
    decisions = ledger.parent / "decisions.md"
    try:
        written = decisions.is_file() and decisions.read_text(
            encoding="utf-8").strip()
    except OSError:
        written = False
    if written:
        return []
    return [f"{sorted(set(passed))} carried a human stop and the run passed it, "
            f"but there is no decisions.md - write what the human ruled, in "
            f"their words, or the next lane works from your restatement of it "
            f"and a resumed session has no record at all"]


AGENT_MODELS = {"opus", "sonnet", "haiku"}
AGENT_EFFORTS = {"low", "medium", "high", "xhigh", "max"}
AGENT_KEYS = ("name", "description", "tools", "model", "effort")


def _agents_dir() -> Path:
    """`<agenticRoot>/plugins/agentic-core/agents`, from this script's location.

    Not from the ledger's `agentic_root:`. A run whose ledger points at the
    wrong root is exactly the run whose agent files you most want checked, and
    this script already lives inside the tree it is checking.
    """
    return (Path(__file__).resolve().parent.parent
            / "plugins" / "agentic-core" / "agents")


def _frontmatter(text: str) -> tuple[dict[str, str], list[str]]:
    """Parse a `---` frontmatter block the way a YAML loader would, and say so.

    Deliberately not PyYAML - this script is dependency-free by design. It only
    needs to reproduce one failure, because that failure is the one that
    happened: a plain (unquoted) scalar containing a colon followed by a space
    is not a scalar to a YAML parser, it is a nested mapping, and the block
    raises. Claude Code then loads the agent with *no* frontmatter at all - no
    `tools:`, no `model:`, no `description:`.

    Silent in every direction. The lane still runs, so nothing fails; it simply
    runs unscoped, on the default model, with every MCP tool schema in the
    session loaded into its context.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, ["no `---` frontmatter block"]
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return {}, ["frontmatter block is never closed by a second `---`"]

    data: dict[str, str] = {}
    problems: list[str] = []
    key = None
    for raw in lines[1:end]:
        if not raw.strip():
            continue
        if raw[:1] in " \t" and key:       # folded continuation of the value
            data[key] += " " + raw.strip()
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", raw)
        if not m:
            problems.append(f"frontmatter line is not `key: value`: {raw[:60]!r}")
            continue
        key, value = m.group(1), m.group(2).strip()
        data[key] = value

    for k, v in data.items():
        if v[:1] in ("'", '"'):
            continue                       # quoted: a colon inside is fine
        hit = re.search(r".{0,30}\S: \S.{0,30}", v)
        if hit:
            problems.append(
                f"`{k}:` is an unquoted scalar containing a colon-space, so the "
                f"whole frontmatter block fails to parse and every field in it "
                f"is dropped - the lane then runs unscoped, on the default "
                f"model, with every tool schema in the session loaded. "
                f"Rewrite the colon or quote the value: ...{hit.group(0)}...")
    return data, problems


def check_agents(agents_dir: Path | None = None) -> list[str]:
    """Every agent definition parses, and declares what authoring.md requires.

    `protocol/authoring.md` already says all of this in prose - never
    `inherit`, never `fable`, `effort` is a separate dial, grant tools
    narrowly. A YAML typo defeats all four at once without failing anything,
    which is what `2026-09-12-composition-card-row-fold` ran on: `tech-lead`,
    `producer` and `quant-analyst` had unparseable frontmatter, so the
    integration gate arrived with a 49,341-token baseline against the frontend
    lane's 15,395 - roughly 34,000 tokens of tool schemas for tools its own
    file does not grant it - and had to call `ToolSearch` to find the two
    `mcp__project__` tools it was already supposed to be holding.
    """
    agents_dir = agents_dir or _agents_dir()
    if not agents_dir.is_dir():
        return []
    problems = []
    for path in sorted(agents_dir.glob("*.md")):
        data, bad = _frontmatter(path.read_text(encoding="utf-8"))
        for b in bad:
            problems.append(f"{path.name}: {b}")
        if bad:
            continue                       # every field below is unreliable
        for k in AGENT_KEYS:
            if not data.get(k):
                problems.append(f"{path.name}: missing `{k}:`")
        name, model = data.get("name", ""), data.get("model", "").lower()
        effort = data.get("effort", "").lower()
        if name and name != path.stem:
            problems.append(f"{path.name}: `name: {name}` does not match the "
                            f"filename - dispatch addresses the file")
        if model and model not in AGENT_MODELS:
            problems.append(f"{path.name}: `model: {model}` - authoring.md "
                            f"allows {sorted(AGENT_MODELS)}, and neither "
                            f"`inherit` nor `fable`")
        if effort and effort not in AGENT_EFFORTS:
            problems.append(f"{path.name}: `effort: {effort}` is not one of "
                            f"{sorted(AGENT_EFFORTS)}")
    return problems


def check_models(ledger: Path, agents_dir: Path | None = None) -> list[str]:
    """The ledger's `model` column says what actually ran, or it says nothing.

    It is written by hand, from the orchestrator's memory of the agent file, at
    the moment the head comes back - and nothing has ever compared the two.
    `2026-09-12-composition-card-row-fold` recorded `opus` against the
    integration gate. `tech-lead.md` declares `sonnet`; the transcript says
    `claude-sonnet-5`. The column was the only wrong thing in an otherwise
    clean ledger, and it is the column a cost review would trust.
    """
    agents_dir = agents_dir or _agents_dir()
    if not agents_dir.is_dir():
        return []
    problems = []
    for row in _ledger_table(ledger.read_text(encoding="utf-8"), "Artifacts"):
        if len(row) < 5:
            continue
        agent, claimed = row[3].strip(), row[4].strip().lower()
        if not agent or agent in ("-", "--", "\u2014") or not claimed:
            continue
        if claimed in ("-", "--", "\u2014"):
            continue
        path = agents_dir / f"{agent}.md"
        if not path.is_file():
            problems.append(f"Artifacts row {row[0].strip()} names agent "
                            f"{agent!r}, which has no definition in "
                            f"{agents_dir.name}/")
            continue
        data, bad = _frontmatter(path.read_text(encoding="utf-8"))
        if bad:
            continue                       # check_agents owns that failure
        declared = data.get("model", "").lower()
        if declared and claimed != declared:
            problems.append(
                f"Artifacts row {row[0].strip()} records `model: {claimed}` for "
                f"{agent}, whose definition declares `{declared}` - one of the "
                f"two is wrong, and the ledger is the copy nobody re-derives")
    return problems


def check_budget(ledger: Path) -> list[str]:
    """`spent` is the dispatches on disk, and `budget` is falsifiable.

    Three invariants, each one a failure the ledger was already supposed to
    prevent in prose:

    - `spent` equals the number of Artifacts rows. The one failure section 1
      spends three paragraphs on is a dispatch that happened and was never
      recorded; this is what notices. A dispatch that produced no artifact -
      a crashed subagent, a lost head - still owes a row, so the count holds.
    - over budget without a `## Replans` row is drift. The budget is only
      falsifiable if exceeding it costs a sentence.
    - twice the budget is the hard stop, wherever the run thinks it is.
    """
    text = ledger.read_text(encoding="utf-8")
    if not _ledger_table(text, "Phases"):
        return []
    problems = []
    budget_raw = _ledger_field(text, "budget")
    spent_raw = _ledger_field(text, "spent")
    budget = _leading_int(budget_raw)
    spent = _leading_int(spent_raw)
    if budget is None:
        problems.append("no readable `budget:` - a phase-model run derives one "
                        "at intake and it is the only number that measures the "
                        "plan rather than the work")
    if spent is None:
        problems.append("no readable `spent:` - it increments on every dispatch")
    if budget is None or spent is None:
        return problems
    rows = len(_ledger_table(text, "Artifacts"))
    if spent != rows:
        problems.append(f"`spent: {spent}` against {rows} Artifacts row(s) - "
                        f"every dispatch owes a row, including one that "
                        f"returned nothing; write it with `status: LOST` "
                        f"rather than leaving the count to disagree")
    if spent > budget and not _ledger_table(text, "Replans"):
        problems.append(f"`spent: {spent}` is past `budget: {budget}` with no "
                        f"`## Replans` row - say what the estimate missed and "
                        f"what the new budget is")
    if budget and spent > 2 * budget:
        problems.append(f"`spent: {spent}` is past twice `budget: {budget}` - "
                        f"that is the hard stop; hand back to the human")
    return problems


def _leading_int(value: str | None) -> int | None:
    """`7 - 5 triggered phases + 2 gates` -> 7. The derivation follows the number."""
    if not value:
        return None
    m = re.match(r"\s*(\d+)", value)
    return int(m.group(1)) if m else None


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

    if target.is_file() and _is_ledger(target):
        # Pointing the validator at the ledger used to produce nine failures
        # that were all the same failure: it was being asked the questions a
        # lane report answers. It is not a lane report.
        problems = check_ledger(target, closed_only=True)
        if problems:
            print(f"FAIL {target}")
            for g in problems:
                print(f"  - {g}")
            return 1
        print(f"ok   {target} ({LEDGER_CHECKS})")
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

    # Close-out also validates the ledger itself: the header a resumed session
    # reads, every `## Phases` row accounted for, `spent` against the dispatches
    # on disk, the `gates:` line against the gates the profile declares, and an
    # `Open` table holding only rows that are still open. Checked here rather
    # than in its own script because close-out is the only moment the answer is
    # knowable and the only moment anyone runs a sweep - a check with its own
    # command is a check that gets skipped.
    if target.is_dir():
        ledger = target / "run.md"
        if not ledger.is_file():
            print(f"  ~ no run.md in {target} - the ledger was not checked")
        elif require_heads:
            ledger_problems = check_ledger(ledger)
            if ledger_problems:
                failed = True
                print(f"FAIL {ledger}")
                for g in ledger_problems:
                    print(f"  - {g}")
            else:
                print(f"ok   {ledger} ({LEDGER_CHECKS})")
        else:
            # Silence here is the bug. A sweep that exits 0 without opening the
            # ledger looks identical to one that read it and found it clean.
            print(f"  ~ {ledger.name} not checked - this sweep validates "
                  f"artifacts only; add --require-heads for the ledger, or "
                  f"point the validator straight at run.md")

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
