# Long Description: RoadmapFlow

<!-- Problem & Solution Statement for the IBM Bob 2.0 hackathon submission form. Limit: 500 words. Paste everything below the line. -->

---

Every multi-session project built with an AI coding assistant hits the same two walls. The first is planning: turning a rough idea into phases, tasks, a definition of "done" and a list of risks often takes one to three days. The second is context: each new session either starts with the developer re-explaining where things stand, or with the whole plan and history dumped into the context window, where finished work costs tokens and pulls the assistant's attention away from the current task. We lived this ourselves: our first IBM Bob planning session used about 160,000 tokens without writing a line of code, about 80,000 of them from fetching the same page twice.

RoadmapFlow solves both with three composable IBM Bob 2.0 skills and a set of mode-specific rules.

/project-roadmap turns a brief into two documents. PLAN.md is a frozen master plan: phases, Build/Measure/Write tasks, binary exit criteria, a decisions log, and risks with fallbacks. ROADMAP.md is a live status board, ticked as work lands. The plan says what we intend; the roadmap says what is true. It also writes a short architecture snapshot of the project.

/roadmap-navigator runs at the start of each session. It finds the current phase and writes a snapshot of only its open tasks, capped at 200 tokens. On our demo, a real 10-week machine-learning research project, the plan and roadmap total about 8,500 tokens; each session now starts from at most about 700 (the 500-token architecture snapshot plus the phase snapshot). Full documents are only read by an explore subagent, so history never enters the main context window.

/dev-workflow executes the phase in Agent mode. Before any tool call, Bob declares a todo list; then it implements, tests, and ticks ROADMAP.md after each verified task. A phase closes only when every exit criterion passes. For risky work, an Actor-Critic pattern spawns a second Bob as a subagent to check the result against the criteria before the item is ticked, and a large context triggers an offer to continue in a fresh subtask.

Target users are solo developers and small teams running projects that span many sessions: research and course projects, hackathons, and feature builds. They work through three commands and two readable files that live in Git, so a teammate or a new session picks up exactly where the last one stopped.

What makes RoadmapFlow original is that it treats the context window as a budget to manage, not a bucket to fill: three tiers of context, subagents as the only readers of history, and mode rules that keep Ask mode from planning and Agent mode from acting before it plans. The structure comes from the plan-and-roadmap system of a real 10-week research project, not from a hackathon whiteboard.

The result: a structured plan in minutes instead of days, sessions that start focused instead of re-explained, and "done" that means verified, not guessed. No servers, no database, and no setup beyond copying the .bob folder into a project.
