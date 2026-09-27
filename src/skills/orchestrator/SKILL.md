---
name: orchestrator
description: Routes work between the TrustMeBro skills (layout-init, roadmap-planner, roadmap-sync, dedup-merge) and says which to run next. Use when the request is vague, spans several skills, or the user asks what to do next.
---

# Orchestrator

Pick the skill from project state, run it, then hand off. Suggest a skill; get the user's go-ahead before one that writes files.

## State to check (first lines only, no full reads)

`LAYOUT.md`, `PLAN.md` (or `RESEARCH_PLAN.md`) and `ROADMAP.md` in the project root, `docs/` and `research_docs/`, and whether there is code.

A file counts only if its first line is `<!-- trustmebro -->` (check with `head -n 1`). Without the marker it belongs to the repo, not to TrustMeBro: treat it as absent and never edit it. One exception: a `ROADMAP.md` that has `<!-- progress:start -->` but no marker is a TrustMeBro roadmap from before the marker existed; offer `roadmap-sync` to add it.

## Pick

| State / request | Run |
|---|---|
| Code, no `LAYOUT.md` | `layout-init` |
| New idea, spec or big feature, no approved plan | `roadmap-planner` (`layout-init` first if code exists) |
| `PLAN.md` but no `ROADMAP.md` | Ask for approval; stage 2 of `roadmap-planner` only after a yes |
| `ROADMAP.md` may be stale (break, other machine, "is it up to date") | `roadmap-sync` |
| Copy-pasted code, "merge duplicates" | `dedup-merge` |
| Small task, bug fix, question | None. Work from `ROADMAP.md` and `LAYOUT.md` directly |

## Hand-offs

- `layout-init` → nothing else needed; if a plan is open, offer `roadmap-planner`.
- `roadmap-planner` → stage 2 creates `ROADMAP.md`; then `LAYOUT.md` is kept current as code lands.
- `dedup-merge` → updates `LAYOUT.md` itself; then offer `roadmap-sync` if roadmap items were touched.
- `roadmap-sync` → if it finds unplanned work, ask before changing the plan (see roadmap rules).

## Rules

- One skill at a time. Say which and why in one line, then run it.
- `LAYOUT.md` before planning or dedup: both read it, so a stale map means wrong output.
- If two rows fit, take the higher one and mention the other.
