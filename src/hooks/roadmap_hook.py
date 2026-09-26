#!/usr/bin/env python3
"""tricklord hooks.

start: in a project with ROADMAP.md, load the roadmap rules, progress and next actions into
       the session. With only a plan file, flag the plan as an unapproved draft.
stop:  after code changes that left ROADMAP.md untouched, ask Claude once to tick the roadmap.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
DIRS = ["", "teamsource", "docs", "research_docs"]

REMINDER = (
    "Code changed but {roadmap} was not touched. If this work finished or advanced a roadmap item, "
    "tick it now ([x] with its evidence, [~] if written but not verified), add a dated Change log line, "
    "and refresh progress with: {cmd}. If the change doesn't belong to any roadmap item, say so in one line and stop."
)


def find(project, *names):
    for d in DIRS:
        for name in names:
            if (project / d / name).is_file():
                return project / d / name
    return None


def rel(project, path):
    return path.relative_to(project).as_posix()


def progress_cmd(project, roadmap):
    script = PLUGIN / "scripts" / "roadmap_progress.py"
    return f'"{sys.executable}" "{script}" "{rel(project, roadmap)}"'


def git(project, *args):
    r = subprocess.run(["git", *args], cwd=project, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout if r.returncode == 0 else None


def start(project, data):
    roadmap = find(project, "ROADMAP.md")
    plan = find(project, "PLAN.md", "RESEARCH_PLAN.md")
    if not roadmap:
        if plan:
            print(f"tricklord: `{rel(project, plan)}` is a draft plan waiting for the user's approval (no ROADMAP.md yet). "
                  "Read it before anything else. Don't start building; when the user approves, follow stage 2 of the "
                  "roadmap-planner skill.")
        return
    rules = (PLUGIN / "rules.md").read_text(encoding="utf-8")
    for key, value in {
        "{roadmap}": rel(project, roadmap),
        "{plan}": f"`{rel(project, plan)}`" if plan else "none (this roadmap was built from the code)",
        "{progress_cmd}": progress_cmd(project, roadmap),
    }.items():
        rules = rules.replace(key, value)
    print(rules)
    text = roadmap.read_text(encoding="utf-8")
    progress = re.search(r"<!-- progress:start -->(.*?)<!-- progress:end -->", text, re.S)
    actions = re.search(r"^## [^\n]*next actions[^\n]*\n(.*?)(?=^## |\Z)", text, re.S | re.M | re.I)
    if progress:
        print("\n## Current progress\n\n" + progress.group(1).strip())
    tier2 = project / ".bob/context/current-phase.md"
    if tier2.is_file():
        print("\n## Active Phase Snapshot (Tier 2 Context)\n\n" + tier2.read_text(encoding="utf-8").strip())
    if actions:
        print("\n## Next actions\n\n" + actions.group(1).strip())


def stop(project, data):
    roadmap = find(project, "ROADMAP.md")
    if data.get("stop_hook_active") or not roadmap:
        return
    status = git(project, "status", "--porcelain", "--untracked-files=all")
    if not status or git(project, "status", "--porcelain", "--", str(roadmap)):
        return  # clean, not a git repo, or the roadmap is already being updated
    # ponytail: can't tell this turn's edits from older uncommitted ones, so it asks once per new working-tree state
    fingerprint = hashlib.sha1((status + (git(project, "diff", "HEAD") or "")).encode()).hexdigest()
    mark = project / git(project, "rev-parse", "--git-path", "tricklord-stop").strip()
    if mark.is_file() and mark.read_text() == fingerprint:
        return
    mark.write_text(fingerprint)
    reason = REMINDER.format(roadmap=rel(project, roadmap), cmd=progress_cmd(project, roadmap))
    print(json.dumps({"decision": "block", "reason": reason}))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # progress bars on a Windows console
    try:
        data = json.loads(sys.stdin.read() or "{}")
        project = Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ".").resolve()
        {"start": start, "stop": stop}[sys.argv[1]](project, data)
    except Exception as e:  # a broken hook must never break the session
        print(f"tricklord hook: {e}", file=sys.stderr)
