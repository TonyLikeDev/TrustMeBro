"""Checks for the progress script and the hooks. Run: python3 tests/test_plugin.py"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from roadmap_progress import phases, render  # noqa: E402

SAMPLE = """# Roadmap
## Progress
<!-- progress:start -->
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


def test_hooks():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d).resolve()
        assert hook(p, "start") == ""  # no plan, no roadmap: silent
        (p / "PLAN.md").write_text("# Plan\n")
        assert "draft plan" in hook(p, "start")

        git(p, "init", "-q")
        (p / "ROADMAP.md").write_text(SAMPLE)
        git(p, "add", ".")
        git(p, "commit", "-qm", "init")
        out = hook(p, "start")
        assert "Roadmap mode" in out and "not a phase item" in out, out

        assert hook(p, "stop") == ""  # clean tree
        (p / "code.py").write_text("x = 1\n")
        assert '"block"' in hook(p, "stop")  # code changed, roadmap untouched
        assert hook(p, "stop") == ""  # same state: asks only once
        (p / "code.py").write_text("x = 2\n")
        assert hook(p, "stop", {"stop_hook_active": True}) == ""  # never loops
        (p / "ROADMAP.md").write_text(SAMPLE + "- tick\n")
        assert hook(p, "stop") == ""  # roadmap already being updated

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
    test_hooks()
    print("ok")
