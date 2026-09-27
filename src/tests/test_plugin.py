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

BOB = ROOT.parent / ".bob" / "trustmebro"  # IBM Bob copy of the scripts and templates
MARK = "<!-- trustmebro -->\n"
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


def bob_hook(project, mode, payload=None):
    """Run the .bob/trustmebro copy the way IBM Bob does: from the workspace root, no CLAUDE_PROJECT_DIR."""
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
    cmd = [sys.executable, str(BOB / "hooks" / "roadmap_hook.py"), mode]
    return subprocess.run(cmd, input=json.dumps(payload or {}), capture_output=True, text=True, env=env, cwd=project).stdout


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


def test_prompt():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d).resolve()
        assert hook(p, "prompt") == ""  # no TrustMeBro files: silent
        (p / "LAYOUT.md").write_text("# Architecture\n")
        assert hook(p, "prompt") == ""  # a repo's own LAYOUT.md is not ours
        (p / "LAYOUT.md").write_text(MARK + "# Project layout\n")
        (p / "ROADMAP.md").write_text("# Our public roadmap\n")
        out = hook(p, "prompt")
        assert "belongs to the repo" in out and (p / "ROADMAP.md").read_text() == "# Our public roadmap\n", out
        (p / "ROADMAP.md").unlink()
        out = hook(p, "prompt", {"prompt": "add a login page"})
        assert "new task" in out and "just created" in out and "Maintenance" in out and "LAYOUT.md" in out, out
        made = (p / "ROADMAP.md").read_text()  # created by the hook, not the model
        assert made.startswith(MARK) and "<!-- progress:start -->" in made and "## Change log" in made, made
        assert "## Week" not in made and "<YYYY" not in made and "1. ..." not in made, made
        assert phases(made) == [], phases(made)
        out = hook(p, "prompt")
        assert "`ROADMAP.md`" in out and "just created" not in out, out  # created once, then just reminded
        if BOB.is_dir():  # Bob's payload has no cwd, and there is no CLAUDE_PROJECT_DIR
            out = bob_hook(p, "prompt", {"event": "UserPromptSubmit", "session_id": "s", "prompt": "fix the header"})
            assert "new task" in out and "`ROADMAP.md`" in out, out


def test_bob_copy():
    """The .bob/trustmebro files are copies of src/ so a copied .bob/ folder works in any project; they must not drift."""
    if not BOB.is_dir():
        return
    for src_file, bob_file in [("hooks/roadmap_hook.py", "hooks/roadmap_hook.py"),
                               ("scripts/roadmap_progress.py", "scripts/roadmap_progress.py"),
                               ("templates/ROADMAP.md", "templates/ROADMAP.md"),
                               ("templates/PLAN.md", "templates/PLAN.md"),
                               ("templates/LAYOUT.md", "templates/LAYOUT.md"),
                               ("rules/layout.md", "rules/layout.md")]:  # rules/roadmap.md is reworded for Bob on purpose
        assert (ROOT / src_file).read_bytes() == (BOB / bob_file).read_bytes(), f"copy src/{src_file} to .bob/trustmebro/{bob_file}"


if __name__ == "__main__":
    test_progress()
    test_start()
    test_stop()
    test_prompt()
    test_bob_copy()
    print("ok")
