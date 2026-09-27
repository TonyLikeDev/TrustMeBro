# tricklord

> A Claude Code plugin for plan-first projects: map the code in `LAYOUT.md`, plan the work in `PLAN.md`, track it in `ROADMAP.md`, and have Claude keep them current as work lands.

---

## Commands

- `/roadmap-planner`: an idea or source documents become `PLAN.md`. It stops for your review; once you approve, it creates `ROADMAP.md` and does the first action.
- `/layout-init`: an existing codebase becomes `LAYOUT.md`: folder tree with purposes, components and how they connect, database schema, and a list of the business logic with where each piece lives.
- `/roadmap-sync`: checks the roadmap against the code and git history and fixes the drift.

(Also reachable as `/tricklord:roadmap-planner` and so on.)

**Adding something** to a project with `LAYOUT.md`: just ask. Claude finds where it fits in the layout, then sizes it. A small addition becomes a new phase in `ROADMAP.md` and work starts; a big one (new component, database change, several days) is planned first and waits for your approval.

## What happens automatically

- **Session start, `LAYOUT.md` present**: Claude gets the layout rules from `rules/layout.md` and the layout itself (or a pointer to it if it's over 6,000 characters).
- **Session start, `ROADMAP.md` present** (project root, `docs/` or `research_docs/`): Claude gets the roadmap rules from `rules/roadmap.md`, the progress block and the next actions, and reads the roadmap before the code.
- **Session start, plan but no roadmap**: Claude is told the plan is an unapproved draft and not to start building.
- **End of a reply that changed code but not the roadmap**, or added / removed / renamed files but not the layout: Claude is asked once to update them.

Edit `rules/` to change how Claude maintains the layout and roadmap, and `templates/` to change the document format.

---

## 📁 Layout

```
src/
├── .claude-plugin/
│   ├── plugin.json              plugin manifest (name, version, description)
│   └── marketplace.json         lets /plugin marketplace add install it
├── skills/
│   ├── roadmap-planner/SKILL.md /roadmap-planner: idea or documents → PLAN.md, approve → ROADMAP.md
│   ├── layout-init/SKILL.md     /layout-init: existing code → LAYOUT.md (tree, components, database, logic)
│   └── roadmap-sync/SKILL.md    /roadmap-sync: fix drift between roadmap and code
├── hooks/
│   ├── hooks.json               registers the SessionStart and Stop hooks
│   └── roadmap_hook.py          start: load layout + roadmap rules and state; stop: update reminder
├── rules/
│   ├── layout.md                loaded when LAYOUT.md exists: keep it current, how to add something
│   └── roadmap.md               loaded when ROADMAP.md exists: tick, log, progress, deviations
├── templates/
│   ├── LAYOUT.md                layout format: overview, folder tree, components, database, logic
│   ├── PLAN.md                  plan format: decisions, objectives, design, schedule, risks, deviations
│   └── ROADMAP.md               status board format: progress block, phases, next actions, change log
├── scripts/
│   └── roadmap_progress.py      regenerates the progress block from the checkboxes
├── tests/
│   └── test_plugin.py           checks the progress math and both hooks
├── BUG_LOGS.md                  known flaws, their status and fix ideas
└── research_docs/               example plan and roadmap from a real project
```

---

## 🚀 Getting Started

### Prerequisites

```bash
# Claude Code
# git
# python >= 3.8 (as python3 or python)
```

### Installation

```bash
# Try it without installing
claude --plugin-dir /path/to/tricklord/src

# Install for good (run inside Claude Code)
/plugin marketplace add TonyLikeDev/tricklord      # or a local path: /path/to/tricklord
/plugin install tricklord@tricklord
```

### Running Tests

```bash
cd src
python3 tests/test_plugin.py
```

---

## 🤖 IBM Bob 2.0 Usage in This Code

> Document how Bob contributed to building this code.
> This feeds into your IBM Bob Usage Statement for submission.

| File/Module | How Bob Helped | Bob Feature Used |
| ----------- | -------------- | ---------------- |
|             |                |                  |
|             |                |                  |

---

## ⚠️ Credential Safety

- **Never hardcode API keys, passwords, or secrets** in any file in this directory
- Use environment variables: `process.env.API_KEY` or `os.environ['API_KEY']`
- All secrets belong in `.env` (which is in `.gitignore` and `.bobignore`)
- IBM Cloud credential exposure = account suspension

### Required `.gitignore` entries:

```
.env
.env.*
credentials.json
ibm-credentials.env
*.key
*.pem
```

### Required `.bobignore` entries:

```
.env
.env.*
credentials.json
ibm-credentials.env
```
