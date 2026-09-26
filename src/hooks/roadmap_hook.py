#!/usr/bin/env python3
"""tricklord hooks.

start: with LAYOUT.md, load the layout rules and the layout itself. With ROADMAP.md, load the
       roadmap rules, progress and next actions. With only a plan file, flag it as an unapproved draft.
stop:  after code changes that left ROADMAP.md untouched, or files added/removed/renamed that left
       LAYOUT.md untouched, ask Claude once to update them.
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
LAYOUT_BUDGET = 6000  # characters of LAYOUT.md loaded into the session; longer ones are only pointed to

ROADMAP_REMINDER = (
    "Code changed but {roadmap} was not touched. If this work finished or advanced a roadmap item, "
    "tick it now ([x] with its evidence, [~] if written but not verified), add a dated Change log line, "
    "and refresh progress with: {cmd}."
)
LAYOUT_REMINDER = (
    "Files were added, removed or renamed but {layout} was not touched. If a folder, component, table "
    "or piece of logic changed, update {layout}."
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


def rules(name, values):
    text = (PLUGIN / "rules" / f"{name}.md").read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{" + key + "}", value)
    return text


def git(project, *args):
    r = subprocess.run(["git", *args], cwd=project, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout if r.returncode == 0 else None


def start(project, data):
    layout = find(project, "LAYOUT.md")
    roadmap = find(project, "ROADMAP.md")
    plan = find(project, "PLAN.md", "RESEARCH_PLAN.md")
    if layout:
        print(rules("layout", {
            "layout": rel(project, layout),
            "templates": (PLUGIN / "templates").as_posix(),
            "progress_cmd": progress_cmd(project, roadmap or project / "ROADMAP.md"),
        }))
        text = layout.read_text(encoding="utf-8")
        if len(text) <= LAYOUT_BUDGET:
            print(f"\n## Contents of {rel(project, layout)}\n\n{text}")
        else:
            print(f"\n`{rel(project, layout)}` is too long to load here; read it before searching the code.")
    if roadmap:
        print(rules("roadmap", {
            "roadmap": rel(project, roadmap),
            "plan": f"`{rel(project, plan)}`" if plan else "none (no plan file)",
            "progress_cmd": progress_cmd(project, roadmap),
        }))
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
    elif plan:
        print(f"tricklord: `{rel(project, plan)}` is a draft plan waiting for the user's approval (no ROADMAP.md yet). "
              "Read it before anything else. Don't start building; when the user approves, follow stage 2 of the "
              "roadmap-planner skill.")


def stop(project, data):
    if data.get("stop_hook_active"):
        return
    status = git(project, "status", "--porcelain", "--untracked-files=all")
    if not status:
        return  # clean tree or not a git repo

    def untouched(path):
        return path and not git(project, "status", "--porcelain", "--", str(path))

    notes = []
    roadmap, layout = find(project, "ROADMAP.md"), find(project, "LAYOUT.md")
    if untouched(roadmap):
        notes.append(ROADMAP_REMINDER.format(roadmap=rel(project, roadmap), cmd=progress_cmd(project, roadmap)))
    if untouched(layout) and re.search(r"^(\?\?|[ADR].|.[ADR]) ", status, re.M):
        notes.append(LAYOUT_REMINDER.format(layout=rel(project, layout)))
    if not notes:
        return
    # ponytail: can't tell this turn's edits from older uncommitted ones, so it asks once per new working-tree state
    fingerprint = hashlib.sha1((status + (git(project, "diff", "HEAD") or "")).encode()).hexdigest()
    mark = project / git(project, "rev-parse", "--git-path", "tricklord-stop").strip()
    if mark.is_file() and mark.read_text() == fingerprint:
        return
    mark.write_text(fingerprint)
    notes.append("If none of this applies to the change, say so in one line and stop.")
    print(json.dumps({"decision": "block", "reason": " ".join(notes)}))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # progress bars on a Windows console
    try:
        data = json.loads(sys.stdin.read() or "{}")
        project = Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ".").resolve()
        {"start": start, "stop": stop}[sys.argv[1]](project, data)
    except Exception as e:  # a broken hook must never break the session
        print(f"tricklord hook: {e}", file=sys.stderr)
