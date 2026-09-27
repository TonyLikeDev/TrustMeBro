---
name: roadmap-planner
description: Plan a new project, from an idea or from existing documents (proposal, spec, design notes, a PDF), or a big addition to an existing project, into PLAN.md. ROADMAP.md is not created until the user approves the plan; then the roadmap is generated and the first action runs. Use when the user runs /roadmap-planner or asks to plan a new project or a big feature, turn an idea or proposal into a plan, or write a project schedule.
---

# Roadmap planner

Two stages with a hard stop between them. Stage 1 writes `PLAN.md`; stage 2 runs only after the user approves it.

Plugin files, relative to this skill's base directory: templates at `../../templates/PLAN.md` and `../../templates/ROADMAP.md`, progress script at `../../scripts/roadmap_progress.py`.

**Planning an addition to an existing project** (a big feature): read `LAYOUT.md` first. The plan builds on the components, database and logic it describes, and names the ones it changes. If `PLAN.md` exists, append the new phases to its schedule and add a Deviations line `- YYYY-MM-DD: added <feature> (awaiting approval)`; otherwise write `PLAN.md` for this addition alone. Stage 1 runs as usual. In stage 2, add the phases to `ROADMAP.md` (creating it if needed) instead of starting a new roadmap, drop "(awaiting approval)", and update `LAYOUT.md` as the code lands.

## Stage 1: draft the plan

1. **Gather.** If the user named documents, read every one in full. Otherwise interview. Either way, ask in ONE batch only what you can't infer:
   - Goal and final deliverables (software, report, paper, demo, slides...).
   - Duration or deadline, and whether to schedule in **weeks** (fixed deadline) or **milestones** (open-ended).
   - Is it research? If yes: research questions, what gets measured, whether there is a paper. If no, drop the research sections.
   - Machines or environments it runs on, if that matters.
   - Constraints and decisions already made.
2. **Resolve conflicts.** When sources disagree (the proposal says X, the design doc says Y), don't pick silently: each conflict becomes a row in the Decisions table with the decision and the reason.
3. **Write `PLAN.md`** in the project root from the template. For the schedule:
   - Every phase has **Build**, **Measure**, **Write**, **Exit criteria**. Drop Measure or Write in a phase that has nothing real for them; never pad.
   - Items are concrete and checkable: a file, a command, a number, a document section. "Work on X" is not an item.
   - Exit criteria are observable ("tests pass", "table filled"), not feelings.
   - Front-load risk: what is most likely to fail goes early, with a row in Risks and fallbacks.
   - When there is a report or paper, map every section to the phases that produce it, so it is assembled from phase outputs.
4. **Stop.** Summarize in a few lines (phases, deliverables, biggest risk, open questions) and ask the user to review or edit `PLAN.md`. Do not create `ROADMAP.md` and do not start building. In later sessions the TrustMeBro hook treats a plan without a roadmap as an unapproved draft.

Iterate on the plan as long as the user wants.

## Stage 2: after the user approves

1. Create `ROADMAP.md` in the project root from the template, with one `## <Phase>: <title>` heading per phase in the plan. Expand only the first phase into checkboxes (its Build / Measure / Write / Exit criteria items); the others say "Not started. See the schedule in `PLAN.md`."
2. Fill "Next actions" with the first phase's items in order, **User action** items first.
3. Refresh progress: `python3 <base dir>/../../scripts/roadmap_progress.py ROADMAP.md` (`python` where `python3` is missing).
4. Do the first action, tick it with its evidence, add the Change log line, and rerun the progress script. From here the roadmap rules loaded by the hook apply.
