#!/usr/bin/env python3
"""tricklord hooks. Only files carrying the `<!-- tricklord -->` marker count.

start: load the layout and roadmap rules, the progress headline, the next actions and, if it
       fits the budget, LAYOUT.md itself. With only a plan, flag it as an unapproved draft.
prompt: (UserPromptSubmit, Claude Code and IBM Bob) with every prompt, remind the AI to put a new task
       on the roadmap before working on it. With LAYOUT.md but no roadmap, create an empty ROADMAP.md first.
edit:  (PostToolUse on Edit/Write) record the edited file for this session.
stop:  if files were edited this turn without touching ROADMAP.md, or new files were created
       without touching LAYOUT.md, ask Claude once to update them.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
DIRS = ["", "docs", "research_docs"]
MARKER = "<!-- tricklord -->"
BUDGET = 8000  # characters printed at session start; Claude Code shortens long hook output

ROADMAP_REMINDER = (
    "Files were edited this turn but {roadmap} was not. If this work finished or advanced a roadmap item, "
    "tick it now ([x] with its evidence, [~] if written but not verified), add a dated Change log line, "
    "and refresh progress with: {cmd}."
)
PROMPT_REMINDER = (
    "tricklord: if this message starts a new task that will change the project, add it to {roadmap} before doing "
    "the work, then tell the user in one line what you added. A feature gets a new phase `## Feature <n>: <title>` "
    "with Build and Exit criteria items{layout_hint}; a fix or small change becomes an item under "
    "`## Maintenance: fixes and small changes`; big work (a new component, a database change, several days) gets a "
    "phase with `[ ] Plan approved by the user`, a plan from the roadmap-planner skill, and no code until the user "
    "approves.{create} If the task is already on the roadmap, work from that item. Questions, and follow-ups that "
    "continue the current task, need no new entry."
)
LAYOUT_REMINDER = (
    "New files were created this turn but {layout} was not updated. If a folder, component, table "
    "or piece of logic changed, update {layout}."
)


def find(project, *names):
    for d in DIRS:
        for name in names:
            p = project / d / name
            if p.is_file() and MARKER in p.read_text(encoding="utf-8", errors="ignore"):
                return p
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


def edit_log(data):
    return Path(tempfile.gettempdir()) / f"tricklord-{data.get('session_id', 'default')}.log"


def start(project, data):
    layout = find(project, "LAYOUT.md")
    roadmap = find(project, "ROADMAP.md")
    plan = find(project, "PLAN.md", "RESEARCH_PLAN.md")
    parts = []
    if layout:
        parts.append(rules("layout", {
            "layout": rel(project, layout),
            "templates": (PLUGIN / "templates").as_posix(),
            "progress_cmd": progress_cmd(project, roadmap or project / "ROADMAP.md"),
        }))
    if roadmap:
        parts.append(rules("roadmap", {
            "roadmap": rel(project, roadmap),
            "plan": f"`{rel(project, plan)}`" if plan else "none (no plan file)",
            "progress_cmd": progress_cmd(project, roadmap),
        }))
        text = roadmap.read_text(encoding="utf-8")
        headline = re.search(r"<!-- progress:start -->\s*(\*\*Progress[^\n]*)", text)
        actions = re.search(r"^## [^\n]*next actions[^\n]*\n(.*?)(?=^## |\Z)", text, re.S | re.M | re.I)
        if headline:
            parts.append("## Current progress\n\n" + headline.group(1).strip())
        if actions:
            parts.append("## Next actions\n\n" + actions.group(1).strip())
    elif plan:
        parts.append(f"tricklord: `{rel(project, plan)}` is a draft plan waiting for the user's approval (no ROADMAP.md "
                     "yet). Read it before anything else. Don't start building; when the user approves, follow stage 2 "
                     "of the roadmap-planner skill.")
    if layout:
        # rules, progress and next actions always load; the layout itself only if it still fits
        block = f"## Contents of {rel(project, layout)}\n\n{layout.read_text(encoding='utf-8')}"
        room = BUDGET - len("\n\n".join(parts)) - 2
        parts.append(block if len(block) <= room else
                     f"`{rel(project, layout)}` is too long to load here; read it before searching the code.")
    if parts:
        print("\n\n".join(parts))


def new_roadmap():
    """The ROADMAP.md template with its placeholder phases removed and today's date filled in."""
    text = (PLUGIN / "templates" / "ROADMAP.md").read_text(encoding="utf-8")
    text = re.sub(r"^## [^\n]*:[^\n]*\n.*?(?=^## )", "", text, flags=re.S | re.M)
    return text.replace("<YYYY-MM-DD>", date.today().isoformat()).replace("1. ...\n", "")


def prompt(project, data):
    layout, roadmap = find(project, "LAYOUT.md"), find(project, "ROADMAP.md")
    if not (layout or roadmap):
        return
    note = ""
    if not roadmap:
        path = layout.parent / "ROADMAP.md"
        if path.exists():  # the repo's own ROADMAP.md: never touch it
            note = f" `{rel(project, path)}` belongs to the repo, not tricklord: ask the user where the tricklord roadmap should go."
        else:
            path.write_text(new_roadmap(), encoding="utf-8")
            roadmap = path
            note = f" tricklord just created an empty `{rel(project, path)}` for this project; add entries under its Progress section."
    print(PROMPT_REMINDER.format(
        roadmap=f"`{rel(project, roadmap)}`" if roadmap else "the roadmap",
        layout_hint=f" (use `{rel(project, layout)}` to see where it fits)" if layout else "",
        create=note,
    ))


def edit(project, data):
    tool_input = data.get("tool_input") or {}
    # Bob uses "path"; Claude Code uses "file_path" / "notebook_path"
    path = tool_input.get("path") or tool_input.get("file_path") or tool_input.get("notebook_path")
    if path:
        with edit_log(data).open("a", encoding="utf-8") as f:
            f.write(path + "\n")


def stop(project, data):
    log = edit_log(data)
    if not log.is_file():
        return
    # ponytail: only Edit/Write tools are recorded; files changed through shell commands are missed (BUG-012)
    edited = {Path(p).resolve() for p in log.read_text(encoding="utf-8").splitlines() if p}
    log.unlink()
    if data.get("stop_hook_active"):
        return
    roadmap, layout = find(project, "ROADMAP.md"), find(project, "LAYOUT.md")
    docs = {p for p in (roadmap, layout, find(project, "PLAN.md", "RESEARCH_PLAN.md")) if p}
    code = [p for p in edited if project in p.parents and p not in docs]
    if not code:
        return
    notes = []
    if roadmap and roadmap not in edited:
        notes.append(ROADMAP_REMINDER.format(roadmap=rel(project, roadmap), cmd=progress_cmd(project, roadmap)))
    if layout and layout not in edited and git(project, "rev-parse", "--is-inside-work-tree"):
        if any(p.exists() and git(project, "ls-files", "--error-unmatch", "--", str(p)) is None for p in code):
            notes.append(LAYOUT_REMINDER.format(layout=rel(project, layout)))
    if notes:
        notes.append("If none of this applies to the change, say so in one line and stop.")
        print(json.dumps({"decision": "block", "reason": " ".join(notes)}))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # progress bars on a Windows console
    try:
        data = json.loads(sys.stdin.read() or "{}")
        project = Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ".").resolve()
        {"start": start, "prompt": prompt, "edit": edit, "stop": stop}[sys.argv[1]](project, data)
    except Exception as e:  # a broken hook must never break the session
        print(f"tricklord hook: {e}", file=sys.stderr)
