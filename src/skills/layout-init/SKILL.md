---
name: layout-init
description: Map an existing codebase into LAYOUT.md, covering the folder tree with the purpose of each part, the components and how they connect, the database schema, and a list of the business logic with where each piece lives. Use when the user runs /layout-init or asks to map, document or describe the layout or architecture of an existing project.
---

# Layout init

Write `LAYOUT.md` in the project root: a map that lets anyone, including Claude in a later session, find where things are and where a new addition fits without rereading the code. Every entry comes from the code and names its file.

Template: `../../templates/LAYOUT.md`, relative to this skill's base directory.

If `LAYOUT.md` already exists, update it in place instead of starting over, and report what changed.

## 1. Read

1. README, `CLAUDE.md` / `AGENTS.md`, package manifests (`package.json`, `pyproject.toml`, ...) and the directory tree. Skip generated and vendored folders (`node_modules`, `venv`, `dist`, `build`, caches, data dumps).
2. Entry points, then each top-level module: what it provides and what it uses from the others.
3. The database: schema files, migrations, ORM models. When they disagree, the migrations win.
4. The logic: routes and handlers, services, jobs, validators, anything that encodes a business rule or a workflow.

## 2. Write `LAYOUT.md` from the template

- **Folder tree**: every folder and every file that matters, each with a one-line purpose. Group trivial files ("assets/: images").
- **Components**: one row each with path, responsibility and dependencies, then the main flows as `A → B → C`.
- **Database**: every table or collection with its key fields and relations, plus the file that defines it. Write "No database." if there is none.
- **Logic**: one line per piece of business logic: what it does, and `file:function` where it lives.

It is a map, not documentation: one line per entry, no code. Session start loads it only while everything fits in about 8,000 characters (roughly 3,500 left for the layout when the project also has a roadmap); a longer layout is only pointed to. So keep it tight, and for a large project stay at module level. Check that every path you write exists.

## 3. Report

Summarize in a few lines: components, tables, and anything surprising (dead code, a README claim the code doesn't back). Tell the user that from now on, asking to add something plans it against this layout and records it in `ROADMAP.md`.
