# Long Description: TrustMeBro

<!-- Problem & Solution Statement for the IBM Bob 2.0 hackathon submission form. Limit: 500 words. Paste everything below the line. -->

---

AI coding agents are good at the task in front of them and bad at the project around it. Every new session starts from zero: the agent re-reads the code to work out what is done and what is next, or the developer re-explains it. Plans and roadmaps help only while they are true, and agents rarely update them, so within a few sessions the documents describe a project that no longer exists. A known bug written down in a tracker is invisible to an agent that only reads code.

TrustMeBro makes the agent keep the project's records itself. It is a plugin for IBM Bob and Claude Code built around three plain Markdown files that live in Git. LAYOUT.md maps the code: folders, components, database and where the business logic lives. PLAN.md holds the approved plan. ROADMAP.md is the live status board: phases, checkboxes, next actions and a change log.

Five skills maintain them; Bob ships the first three. /layout-init maps an existing codebase into LAYOUT.md. /roadmap-planner turns an idea or source documents into PLAN.md, then waits for approval before creating ROADMAP.md. /roadmap-sync fixes drift between the roadmap, the code and git history. /dedup-merge merges copy-pasted code into shared implementations. /orchestrator reads the project's state and picks the next skill.

Hooks make it automatic. At session start, Bob receives the layout, the roadmap rules, the progress headline and the next actions, so it reads the roadmap before the code. On every prompt, Bob is reminded that a new task goes on the roadmap before any work starts: a feature becomes a phase, a fix goes under Maintenance, and big work gets a plan that waits for approval. If there is no roadmap yet, the hook creates one. Always-loaded rules in .bob/rules tell Bob to tick each item with evidence, log the change, update the layout and refresh progress with a script.

In a live test in IBM Bob Shell 2.0.5, Bob put a new task on the roadmap first, wrote the code, updated the layout, ticked the item with evidence and reported back in one line: 35 seconds, 12 tool calls. In a 45-session benchmark on a half-finished 35-file shop backend (Claude Code, same plugin), resuming the project with TrustMeBro was 2× faster and 29% cheaper than the base agent, with half the tool calls. Answering "what is left?" took 46% fewer tokens and a single tool call, while the base agent never found the known shipping bug recorded only in the roadmap. Without the plugin, the same documents were updated in 0 of 5 change runs; with it, in every one. Implementation tasks cost about 20–30% more, the price of keeping records current, and every setup completed every task correctly.

TrustMeBro is for solo developers and small teams whose projects span many sessions. Setup in Bob is copying one .bob folder. No servers, no database: Python and files anyone can review in a pull request. The same skills also install in GitHub Copilot CLI, Antigravity CLI and Codex.
