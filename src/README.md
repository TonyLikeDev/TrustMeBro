# tricklord

> A Claude Code plugin for plan-first projects: plan the work in `PLAN.md`, track it in `ROADMAP.md`, and have Claude keep the roadmap current as work lands.

---

## Commands

- `/roadmap-planner`: an idea or source documents become `PLAN.md`. It stops for your review; once you approve, it creates `ROADMAP.md` and does the first action.
- `/roadmap-init`: an existing codebase becomes `ROADMAP.md`, with done / unverified / open items and the evidence for each.
- `/roadmap-sync`: checks the roadmap against the code and git history and fixes the drift.

(Also reachable as `/tricklord:roadmap-planner` and so on.)

## What happens automatically

- **Session start, `ROADMAP.md` present** (project root, `docs/` or `research_docs/`): Claude gets the roadmap rules from `rules.md`, the progress block and the next actions, and reads the roadmap before the code.
- **Session start, plan but no roadmap**: Claude is told the plan is an unapproved draft and not to start building.
- **End of a reply that changed code but not the roadmap**: Claude is asked once whether an item should be ticked.

Edit `rules.md` to change how Claude maintains the roadmap, and `templates/` to change the document format.

---

## 📁 Layout

```
src/
├── .claude-plugin/
│   ├── plugin.json              plugin manifest (name, version, description)
│   └── marketplace.json         lets /plugin marketplace add install it
├── skills/
│   ├── roadmap-planner/SKILL.md /roadmap-planner: idea or documents → PLAN.md, approve → ROADMAP.md
│   ├── roadmap-init/SKILL.md    /roadmap-init: existing code → ROADMAP.md with evidence
│   └── roadmap-sync/SKILL.md    /roadmap-sync: fix drift between roadmap and code
├── hooks/
│   ├── hooks.json               registers the SessionStart and Stop hooks
│   └── roadmap_hook.py          start: load rules + progress + next actions; stop: tick reminder
├── rules.md                     the roadmap rules loaded into every session that has a ROADMAP.md
├── templates/
│   ├── PLAN.md                  plan format: decisions, objectives, design, schedule, risks, deviations
│   └── ROADMAP.md               status board format: progress block, phases, next actions, change log
├── scripts/
│   └── roadmap_progress.py      regenerates the progress block from the checkboxes
├── tests/
│   └── test_plugin.py           checks the progress math and both hooks
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
/plugin marketplace add /path/to/tricklord/src
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
