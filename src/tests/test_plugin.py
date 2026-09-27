"""Checks for the progress script and the layout and roadmap hooks. Run: python3 tests/test_plugin.py"""
import json
import os
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from roadmap_progress import phases, render  # noqa: E402

MARK = "<!-- tricklord -->\n"
SAMPLE = MARK + """# Roadmap
## Progress
<!-- progress:start -->
**Progress: 25% of the 2-week plan**

| Week 1 | 3 | 1.5 |
<!-- progress:end -->
## Week 1: Build it
### Build
- [x] a
- [~] b
- [ ] c
## Week 2: Ship it
Not started.
## Next actions (in order)
- [ ] not a phase item
"""


def hook(project, mode, payload=None):
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(project)}
    cmd = [sys.executable, str(ROOT / "hooks" / "roadmap_hook.py"), mode]
    return subprocess.run(cmd, input=json.dumps(payload or {}), capture_output=True, text=True, env=env).stdout


def git(project, *args):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=project, check=True, capture_output=True)


def test_progress():
    ph = phases(SAMPLE)
    assert ph == [["Week 1", 3, 1.5], ["Week 2", 0, 0.0]], ph
    out = render(ph)
    assert out[0].startswith("**Progress: 25% of the 2-week plan**"), out[0]
    assert out[4].startswith("| Week 1 | 3 | 1.5 |") and out[4].endswith("| 50% |"), out[4]
    assert out[5].endswith("| not started |"), out[5]


def test_start():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d).resolve()
        (p / "PLAN.md").write_text("# Migration plan\n")
        assert hook(p, "start") == ""  # a PLAN.md without the marker is not ours
        (p / "PLAN.md").write_text(MARK + "# Plan\n")
        assert "draft plan" in hook(p, "start")

        (p / "ROADMAP.md").write_text(SAMPLE)
        (p / "LAYOUT.md").write_text(MARK + "# Project layout\n- **signup**: creates a user\n")
        out = hook(p, "start")
        assert "Layout mode" in out and "creates a user" in out, out
        assert "Roadmap mode" in out and "**Progress: 25%" in out and "not a phase item" in out, out
        assert "| Week 1 |" not in out, out  # the progress table stays in the file

        (p / "LAYOUT.md").write_text(MARK + "x" * 9000)
        out = hook(p, "start")
        assert "too long to load" in out and len(out) <= 8000, len(out)  # one budget for everything


def test_stop():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d).resolve()
        git(p, "init", "-q")
        (p / "ROADMAP.md").write_text(SAMPLE)
        (p / "LAYOUT.md").write_text(MARK + "# Project layout\n")
        git(p, "add", ".")
        git(p, "commit", "-qm", "init")
        s = {"session_id": uuid.uuid4().hex}

        def edit(name):
            hook(p, "edit", {**s, "tool_input": {"file_path": str(p / name)}})

        (p / "notes.txt").write_text("dirty tree\n")
        assert hook(p, "stop", s) == ""  # nothing edited this turn: quiet even on a dirty tree

        (p / "code.py").write_text("x = 1\n")
        edit("code.py")
        out = hook(p, "stop", s)
        assert '"block"' in out and "ROADMAP.md" in out and "LAYOUT.md" in out, out  # new file, no doc touched
        assert hook(p, "stop", s) == ""  # log cleared: asks once per turn

        git(p, "add", "code.py")
        git(p, "commit", "-qm", "code")
        edit("code.py")
        out = hook(p, "stop", s)
        assert "ROADMAP.md" in out and "LAYOUT.md" not in out, out  # tracked file: no layout reminder

        edit("code.py")
        edit("ROADMAP.md")
        assert hook(p, "stop", s) == ""  # roadmap updated in the same turn

        edit("code.py")
        assert hook(p, "stop", {**s, "stop_hook_active": True}) == ""  # never loops
        assert hook(p, "stop", s) == ""  # and the log was still cleared

        hook(p, "edit", {**s, "tool_input": {"file_path": str(Path(d).parent / "memory.md")}})
        assert hook(p, "stop", s) == ""  # edits outside the project don't count

        # Test Tier 2 snapshot loading
        context_dir = p / ".bob/context"
        context_dir.mkdir(parents=True, exist_ok=True)
        (context_dir / "current-phase.md").write_text("# Phase 1 snapshot\n")
        out2 = hook(p, "start")
        assert "Active Phase Snapshot" in out2 and "Phase 1 snapshot" in out2, out2

        # Test teamsource roadmap discovery
        with tempfile.TemporaryDirectory() as d2:
            p2 = Path(d2).resolve()
            (p2 / "teamsource").mkdir(parents=True)
            (p2 / "teamsource/ROADMAP.md").write_text(SAMPLE)
            out_ts = hook(p2, "start")
            assert "Roadmap mode" in out_ts, out_ts


if __name__ == "__main__":
    test_progress()
    test_start()
    test_stop()
    print("ok")
