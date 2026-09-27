# tricklord

> A plan-first project workflow for Claude Code and IBM Bob: map the code in `LAYOUT.md`, plan the work in `PLAN.md`, track it in `ROADMAP.md`, and have your AI keep them current as work lands.

---

## Commands

- `/roadmap-planner`: an idea or source documents become `PLAN.md`. It stops for your review; once you approve, it creates `ROADMAP.md` and does the first action.
- `/layout-init`: an existing codebase becomes `LAYOUT.md`: folder tree with purposes, components and how they connect, database schema, and a list of the business logic with where each piece lives.
- `/roadmap-sync`: checks the roadmap against the code and git history and fixes the drift.
- `/dedup-merge`: finds copy-pasted code, merges each duplicate group into one shared implementation with the differences as a variant, and reports the before/after line counts.
- `/orchestrator`: looks at the project's state and tells you which of the other skills to run next, then hands off.

(Also reachable as `/tricklord:roadmap-planner` and so on. In Bob, skills activate automatically when a request matches their description.)

**Every new task goes on the roadmap** in a project with `LAYOUT.md`: just ask. Before doing the work, the AI records the task in `ROADMAP.md` (created automatically if missing) and tells you in one line: a feature becomes a new phase, a fix or small change an item under `## Maintenance: fixes and small changes`, and big work (new component, database change, several days) gets a plan that waits for your approval. Questions and follow-ups to the current task don't get an entry.

## What happens automatically

Only files whose first line is `<!-- tricklord -->` count (the templates add it), so a repo's own `PLAN.md` or `ROADMAP.md` is left alone.

- **Every prompt, `LAYOUT.md` or `ROADMAP.md` present** (Claude Code and Bob): the AI is reminded to put a new task on the roadmap before working on it. If there is a `LAYOUT.md` but no roadmap yet, the hook creates an empty `ROADMAP.md` from the template first.
- **Session start, `LAYOUT.md` present**: the AI gets the layout rules and the layout itself if everything fits in about 8,000 characters (otherwise a pointer to it).
- **Session start, `ROADMAP.md` present** (project root, `docs/` or `research_docs/`): the AI gets the roadmap rules, the progress headline, and the next actions, and reads the roadmap before the code.
- **Session start, plan but no roadmap**: the AI is told the plan is an unapproved draft and not to start building.
- **End of a reply in which the AI edited files but not the roadmap**, or created new files but not the layout: the AI is asked once to update them. Replies with no edits stay quiet. Claude Code only: Bob ignores the output of `Stop` and `PostToolUse` hooks, so in Bob the rules in `.bob/rules/tricklord.md` carry this instead.

The session-start items are Claude Code only; in Bob the same rules are always loaded from `.bob/rules/tricklord.md`.

Edit `src/rules/` to change how the AI maintains the layout and roadmap, and `src/templates/` to change the document format.

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
│   ├── roadmap-sync/SKILL.md    /roadmap-sync: fix drift between roadmap and code
│   ├── dedup-merge/SKILL.md     /dedup-merge: merge copy-pasted code into shared implementations
│   └── orchestrator/SKILL.md    /orchestrator: pick the next skill from the project's state
├── hooks/
│   ├── hooks.json               registers the SessionStart, UserPromptSubmit, PostToolUse and Stop hooks
│   └── roadmap_hook.py          start: rules and state; prompt: new-task reminder; edit: log edits; stop: reminder
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

.bob/                            IBM Bob integration (auto-discovered by Bob)
├── settings.json                hook: UserPromptSubmit (new-task reminder, creates ROADMAP.md if missing)
├── rules/
│   └── tricklord.md             layout + roadmap rules, always in context
├── tricklord/                   copies of src/hooks, src/scripts and src/templates, so .bob/ works in any project
└── skills/
    ├── roadmap-planner/SKILL.md Bob skill: plan a project or big feature
    ├── layout-init/SKILL.md     Bob skill: map an existing codebase
    └── roadmap-sync/SKILL.md    Bob skill: fix roadmap drift
```

---

## 🚀 Getting Started

### Prerequisites

```bash
# Claude Code and/or IBM Bob
# git
# python >= 3.8 (as python3 or python)
```

### Installation — Claude Code

```bash
# Try it without installing
claude --plugin-dir /path/to/tricklord/src

# Install for good (run inside Claude Code)
/plugin marketplace add TonyLikeDev/tricklord      # or a local path: /path/to/tricklord
/plugin install tricklord@tricklord
```

### Installation — IBM Bob

Copy the `.bob/` folder into your project and open it in Bob; everything it needs is inside it:

- Skills (`roadmap-planner`, `layout-init`, `roadmap-sync`) are discovered from `.bob/skills/`.
- The `UserPromptSubmit` hook in `.bob/settings.json` runs `.bob/tricklord/hooks/roadmap_hook.py` on every prompt (Bob adds its output to the context).
- Rules in `.bob/rules/tricklord.md` are always in context.

No install step beyond the copy. Bob only adds the output of `SessionStart` and `UserPromptSubmit` hooks to the context, so the end-of-reply reminders are Claude Code only. The files in `.bob/tricklord/` are copies of `src/`: after changing `src/`, copy them again (`tests/test_plugin.py` fails until you do).

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
| `.bob/skills/roadmap-planner/SKILL.md` | Designed and wrote the Bob skill from the Claude Code source | Skills |
| `.bob/skills/layout-init/SKILL.md` | Designed and wrote the Bob skill from the Claude Code source | Skills |
| `.bob/skills/roadmap-sync/SKILL.md` | Designed and wrote the Bob skill from the Claude Code source | Skills |
| `.bob/settings.json` | Translated hooks.json into Bob's hook format with correct tool matchers | Hooks |
| `.bob/rules/tricklord.md` | Wrote static layout + roadmap rules for Bob's rules system | Custom Rules |
| `src/hooks/roadmap_hook.py` | Patched to support Bob's `"path"` tool input field alongside Claude Code's `"file_path"` | Agent mode |

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
