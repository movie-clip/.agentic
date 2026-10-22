"""Regression suite for the three hooks.

    python scripts/hooks/test_hooks.py

Runs each hook the way Claude Code does -- a JSON payload on stdin, a decision
in the exit code -- because the only thing that matters about a hook is what it
does to exit 0/2, and nothing in-process proves that. Dependency-free, like the
validator it wraps.
"""
import json, os, subprocess, sys, tempfile
from pathlib import Path

HOOKS = Path(__file__).resolve().parent
sys.path.insert(0, str(HOOKS.parent))
import check_report as cr

ARTIFACT_GATE = HOOKS / "report_artifact_gate.py"
HEAD_GATE = HOOKS / "report_head_gate.py"
NETWORK_GATE = HOOKS / "network_edit_gate.py"

BLOCK = """REPORT test/06
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

skill_calls:
  - none

risks:
  - none
"""

results = []
def check(name, cond, extra=""):
    results.append((name, cond, extra))
    print(f"  {'PASS' if cond else 'FAIL'}  {name}{'  ' + extra if extra and not cond else ''}")

def run(script, payload):
    p = subprocess.run([sys.executable, str(script)], input=json.dumps(payload),
                       capture_output=True, text=True)
    return p.returncode, p.stderr

def run_dir():
    d = Path(tempfile.mkdtemp()) / "runs" / "2026-09-11-hooks"
    d.mkdir(parents=True)
    return d

def head_for_text(artifact):
    """The head a lane should return: derived, then its placeholders filled."""
    h = cr.head_for(artifact)
    return h.replace(
        f"<outcome in one sentence under {cr.MAX_HEADLINE} chars - replace this>",
        "did the thing")

# --------------------------------------------------------------- artifact gate

print("A — the write-time early warning")

d = run_dir()
good = d / "06-backend.md"
good.write_text(BLOCK, encoding="utf-8")
code, err = run(ARTIFACT_GATE, {"tool_input": {"file_path": str(good)}})
check("a valid artifact passes silently", (code, err) == (0, ""), f"{code} {err}")

bad = d / "07-frontend.md"
bad.write_text(BLOCK.replace("handoff:", "handsoff:"), encoding="utf-8")
code, err = run(ARTIFACT_GATE, {"tool_input": {"file_path": str(bad)}})
check("a missing section is reported back to the lane",
      code == 2 and "handoff" in err, f"{code} {err}")

# The filename is the only thing that says which lane this is, and the gate
# lanes are the ones whose bullets get routed one at a time.
gate = d / "09-quant-audit.md"
gate.write_text(BLOCK.replace("  - one item", "  - " + "x" * 500), encoding="utf-8")
code, err = run(ARTIFACT_GATE, {"tool_input": {"file_path": str(gate)}})
check("a gate lane's overlong bullet blocks", code == 2 and "max 400" in err,
      f"{code} {err}")

loose = d / "06-backend.md"
same = Path(tempfile.mkdtemp()) / "06-backend.md"
same.write_text(BLOCK.replace("handoff:", "handsoff:"), encoding="utf-8")
code, err = run(ARTIFACT_GATE, {"tool_input": {"file_path": str(same)}})
check("a report outside runs/ is not this hook's business",
      (code, err) == (0, ""), f"{code} {err}")

ledger = d / "run.md"
ledger.write_text("# Run\nstatus: open\n", encoding="utf-8")
code, err = run(ARTIFACT_GATE, {"tool_input": {"file_path": str(ledger)}})
check("the ledger is not a report and is left alone", (code, err) == (0, ""),
      f"{code} {err}")

above = d / "08-recon.md"
above.write_text("## Orchestrator brief\n\n- a finding\n\n" + BLOCK, encoding="utf-8")
code, err = run(ARTIFACT_GATE, {"tool_input": {"file_path": str(above)}})
check("a brief written above the block is caught at write time",
      code == 2 and "first non-blank line" in err, f"{code} {err}")

code, err = run(ARTIFACT_GATE, {"tool_input": {"file_path": str(d / "gone.md")}})
check("a path that does not exist is ignored", (code, err) == (0, ""),
      f"{code} {err}")

p = subprocess.run([sys.executable, str(ARTIFACT_GATE)], input="not json",
                   capture_output=True, text=True)
check("malformed stdin never breaks the lane", p.returncode == 0,
      f"{p.returncode} {p.stderr}")

# -------------------------------------------------------------------- head gate

print("B — the stop-time gate")

def payload(msg, lane="backend-engineer", agent_id=None):
    return {"agent_type": lane, "agent_id": agent_id or f"t{os.getpid()}-{os.urandom(4).hex()}",
            "last_assistant_message": msg}

d = run_dir()
art = d / "06-backend.md"
art.write_text(BLOCK, encoding="utf-8")
HEAD = head_for_text(art)

code, err = run(HEAD_GATE, payload(HEAD))
check("a valid head lets the lane stop", (code, err) == (0, ""), f"{code} {err}")
check("and the head file is saved beside the artifact",
      (d / "06-head.txt").read_text(encoding="utf-8").strip() == HEAD.strip(),
      "not written")

code, err = run(HEAD_GATE, {"agent_type": "Explore", "agent_id": "x",
                            "last_assistant_message": "no head here"})
check("a subagent that is not a network lane is untouched",
      (code, err) == (0, ""), f"{code} {err}")

code, err = run(HEAD_GATE, payload("I finished the work, all good."))
check("a lane that returns no head is held", code == 2 and "NO REPORT HEAD" in err,
      f"{code} {err}")

code, err = run(HEAD_GATE, payload(HEAD.replace("handoff:         1",
                                                "handoff:         0")))
check("a head that undercounts is held",
      code == 2 and "silently drops work" in err, f"{code} {err}")

code, err = run(HEAD_GATE, payload(HEAD.replace("status:          DONE",
                                                "status:          PARTIAL")))
check("a head that disagrees on status is held",
      code == 2 and "disagrees" in err, f"{code} {err}")

# The head carries the resolved path, which on Windows is not the string the
# artifact was built from - replace what the head actually says.
_named = cr._scalar(HEAD, "artifact")
code, err = run(HEAD_GATE, payload(HEAD.replace(_named, str(d / "nope.md"))))
check("a head naming an artifact that is not there is held",
      code == 2 and "does not exist" in err, f"{code} {err}")

# Run 2026-09-27-sort-potential-rules-by-frequency: the recon wrote its brief
# above the block. The gate must say what is wrong with the file, not imply
# the path is.
top = d / "08-recon.md"
top.write_text("## Orchestrator brief\n\n- a finding\n\n" + BLOCK, encoding="utf-8")
code, err = run(HEAD_GATE, payload(HEAD.replace(_named, str(top)), lane="scout"))
check("a brief above the block is held and named as the reason",
      code == 2 and "first non-blank line" in err, f"{code} {err}")

prose = d / "10-recon.md"
prose.write_text("## Orchestrator brief\n\n- a finding\n", encoding="utf-8")
code, err = run(HEAD_GATE, payload(HEAD.replace(_named, str(prose)), lane="scout"))
check("a file with no REPORT line is held with what to put first",
      code == 2 and "has no 'REPORT <id>' line" in err, f"{code} {err}")

code, err = run(HEAD_GATE, payload(head_for_text(art)))
check("an unedited --emit-head placeholder is held",
      run(HEAD_GATE, payload(cr.head_for(art)))[0] == 2, f"{code} {err}")

# PROTOCOL says nothing after the block; a lane that fences it is still legible.
code, err = run(HEAD_GATE, payload("Done.\n\n```\n" + HEAD + "\n```"))
check("a fenced head is read, not rejected", (code, err) == (0, ""),
      f"{code} {err}")

# A ticket-named artifact is not a dispatch slot, so it has no head file.
tk = d / "T-40.1.3-backend.md"
tk.write_text(BLOCK, encoding="utf-8")
code, err = run(HEAD_GATE, payload(head_for_text(tk)))
check("a ticket-named artifact passes with no head file written",
      (code, err) == (0, "") and not list(d.glob("T-40*head*")), f"{code} {err}")

# A hook that can refuse forever can hang a run.
stuck = f"loop{os.getpid()}-{os.urandom(4).hex()}"
codes = [run(HEAD_GATE, payload("no head", agent_id=stuck))[0] for _ in range(3)]
check("the gate gives up after two holds", codes == [2, 2, 0], str(codes))

# A rejected head is answered with the right one, because the three Bash-less
# lanes have no other way to obtain it.
_wrong = HEAD.replace("handoff:         1", "handoff:         0")
code, err = run(HEAD_GATE, payload(_wrong))
check("a rejected head is answered with the derived one",
      code == 2 and "Return this head instead" in err
      and "REPORT HEAD test/06" in err, f"{code} {err}")

# An unusable artifact is named as the cause instead, so the lane fixes the
# file rather than retyping a head that could never have been right.
_broken = d / "08-test.md"
_broken.write_text(BLOCK.replace("risks:", "risk:"), encoding="utf-8")
code, err = run(HEAD_GATE, payload(head_for_text(_broken)))
check("an unusable artifact is reported ahead of its head",
      code == 2 and "section 3" in err and "Return this head" not in err,
      f"{code} {err}")

# The advisory half of check_report.py reaches the Bash-less lanes here and
# nowhere else - and it rides along with a hold rather than causing one.
_long = "- " + "x" * 350
_adv = d / "09-docs.md"
_adv.write_text(BLOCK.replace("  - one item", "  " + _long), encoding="utf-8")
code, err = run(HEAD_GATE, payload(head_for_text(_adv), lane="docs-engineer"))
check("a long bullet alone does not hold the lane", code == 0, f"{code} {err}")
_adv.write_text(BLOCK.replace("  - one item", "  " + _long)
                .replace("risks:", "risk:"), encoding="utf-8")
code, err = run(HEAD_GATE, payload(head_for_text(_adv), lane="docs-engineer"))
check("but a real violation carries the advisories with it",
      code == 2 and "do not block" in err and "target 300" in err,
      f"{code} {err}")

print("C — bounding, which is what keeps a hook from hanging a session")

# `stop_hook_active` arrives on exactly the attempt after a hold, so the head
# gate must still check that attempt: the counter bounds it, and the flag bounds
# only a payload with no agent_id to count.
_p = payload(HEAD)
_p["last_assistant_message"] = "no head at all"
code, err = run(HEAD_GATE, _p)
check("the head gate holds a lane with no head", code == 2, f"{code} {err}")
_p["stop_hook_active"] = True
code, err = run(HEAD_GATE, _p)
check("and holds it a second time with stop_hook_active set", code == 2,
      f"{code} {err}")
code, err = run(HEAD_GATE, _p)
check("then releases it, by the counter", code == 0 and "two attempts" in err,
      f"{code} {err}")

(d / "06-head.txt").unlink()
_p = payload(HEAD)
_p["stop_hook_active"] = True
code, err = run(HEAD_GATE, _p)
check("a corrected head on the retry is checked and saved",
      (code, err) == (0, "") and (d / "06-head.txt").is_file(), f"{code} {err}")

_p = {"agent_type": "backend-engineer", "last_assistant_message": "no head",
      "stop_hook_active": True}
code, err = run(HEAD_GATE, _p)
check("with no agent_id, stop_hook_active still releases", code == 0,
      f"{code} {err}")

# The network gate needs a real unlinted file to have anything to hold on, so it
# plants one and removes it either way. `protocol/**` is in scope and a `zz-`
# name sorts clear of anything the network ships.
_probe = HOOKS.parent.parent / "protocol" / "zz-test-hooks-probe.md"
try:
    _probe.parent.mkdir(parents=True, exist_ok=True)
    _probe.write_text("# probe" + chr(10), encoding="utf-8")
    _sid = f"test-hooks-{os.getpid()}"
    code, err = run(NETWORK_GATE, {"session_id": _sid})
    check("the network gate holds on an unlinted protocol file",
          code == 2 and _probe.name in err, f"{code} {err}")
    code, err = run(NETWORK_GATE, {"session_id": _sid})
    check("one hold per session, then it releases and says so",
          code == 0 and "letting this session stop" in err, f"{code} {err}")
    code, err = run(NETWORK_GATE, {"session_id": f"{_sid}-b", "stop_hook_active": True})
    check("and stop_hook_active releases it outright", (code, err) == (0, ""),
          f"{code} {err}")
    # With no session to key on there is no marker to write, and writing one
    # under a shared name would let a single hold exempt every later session.
    code, _ = run(NETWORK_GATE, {})
    code2, _ = run(NETWORK_GATE, {})
    check("with no session_id it still holds every time, not once",
          (code, code2) == (2, 2), f"{code} {code2}")
finally:
    _probe.unlink(missing_ok=True)

n_fail = sum(1 for _, c, _ in results if not c)
print(f"\n{len(results) - n_fail}/{len(results)} passed")
sys.exit(1 if n_fail else 0)
