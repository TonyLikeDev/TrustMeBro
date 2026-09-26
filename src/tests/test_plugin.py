"""Checks for the progress script and the layout and roadmap hooks. Run: python3 tests/test_plugin.py"""
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
        (p / "LAYOUT.md").write_text("# Project layout\n- **signup**: creates a user\n")
        git(p, "add", ".")
        git(p, "commit", "-qm", "init")
        out = hook(p, "start")
        assert "Layout mode" in out and "creates a user" in out, out
        assert "Roadmap mode" in out and "not a phase item" in out, out

        assert hook(p, "stop") == ""  # clean tree
        (p / "code.py").write_text("x = 1\n")
        out = hook(p, "stop")
        assert '"block"' in out and "ROADMAP.md" in out and "LAYOUT.md" in out, out  # new file, neither doc touched
        assert hook(p, "stop") == ""  # same state: asks only once
        (p / "code.py").write_text("x = 2\n")
        assert hook(p, "stop", {"stop_hook_active": True}) == ""  # never loops

        git(p, "add", ".")
        git(p, "commit", "-qm", "code")
        (p / "code.py").write_text("x = 3\n")
        out = hook(p, "stop")
        assert "ROADMAP.md" in out and "LAYOUT.md" not in out, out  # edit only: no structure change
        (p / "code.py").write_text("x = 4\n")
        (p / "ROADMAP.md").write_text(SAMPLE + "- tick\n")
        assert hook(p, "stop") == ""  # roadmap already being updated


if __name__ == "__main__":
    test_progress()
    test_hooks()
    print("ok")
