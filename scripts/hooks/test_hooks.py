"""Regression suite for the two report hooks.

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
      code == 2 and "not a report file" in err, f"{code} {err}")

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

n_fail = sum(1 for _, c, _ in results if not c)
print(f"\n{len(results) - n_fail}/{len(results)} passed")
sys.exit(1 if n_fail else 0)
