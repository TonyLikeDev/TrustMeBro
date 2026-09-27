# IBM Bob Usage Statement: TrustMeBro

<!-- IBM Bob Usage Statement for the IBM Bob 2.0 hackathon submission form. Limit: 500 words. Paste everything below the line. -->

---

IBM Bob 2.0 both built TrustMeBro and runs it. We used Bob IDE and Bob Shell 2.0.5, in Ask mode and Agent mode.

Research (Ask mode, IBM docs search). Our first Bob session scanned our planning documents and searched IBM's documentation to map Bob's extension points: skills, custom modes, rules files and MCP servers. It measured the fixed cost of a Bob session at about 8,500 tokens before any work, and showed us the problem firsthand: the session used about 160,000 tokens without writing code, 80,000 of them from fetching the same page twice. That is why TrustMeBro starts each session with a progress headline and next actions, not whole documents. The same analysis led us to drop MCP as unneeded overhead.

Porting to Bob (Agent mode, skills, hooks, rules). TrustMeBro started as a Claude Code plugin. In an Agent mode session in Bob Shell, Bob read that source and wrote the Bob version: three skills in .bob/skills (roadmap-planner, layout-init, roadmap-sync), .bob/settings.json translating our hooks into Bob's format, and .bob/rules/trustmebro.md with the layout and roadmap rules. When our own edits left the port half-finished, Bob found three problems itself: the hook scripts its files pointed to did not exist, settings.json was missing three of four hooks, and the README tree was outdated. It built the self-contained .bob/trustmebro/ package (hook, progress script, rules, templates), restored the hooks, ran a Python check that every path resolved, and updated the README. It also patched roadmap_hook.py to read Bob's "path" tool field. That session used 93.9k of 270k context and 5.90 Bobcoins (screenshot in bob_sessions/).

Testing Bob as the runtime (Bob Shell headless). We ran TrustMeBro under `bob run` with --max-cost and --max-turns limits. We found that Bob ignores the output of PostToolUse and Stop hooks, so we moved those reminders into the always-loaded rules and added a UserPromptSubmit hook that creates ROADMAP.md when missing and reminds Bob to record each new task first. In the final test (task 22fdf4fa00395fcc3ecaf7472b82d4b9), asked to add a multiply function, Bob made the roadmap entry the first item of its todo list, recorded the task before touching code, implemented it, updated LAYOUT.md, ticked the item with evidence, ran the progress script and reported in one line: 12 tool calls, 35 seconds, every check passed.

What Bob does in the product. In a user's project, Bob is the engine. Its SessionStart hook injects the rules, progress and next actions; its UserPromptSubmit hook enforces roadmap-first work; its rules make it keep LAYOUT.md and ROADMAP.md current; its skills map the code, write the plan and fix drift; and Agent mode's todo list and command execution carry out the loop. Mode-specific rules from our first iteration (.bob/rules-ask, rules-plan, rules-agent) keep Ask mode from planning, Plan mode from executing, and Agent mode from calling tools before declaring a todo list.

Bob features used: Agent mode, Ask mode, skills, SessionStart and UserPromptSubmit hooks, always-loaded and mode-specific rules, the todo list, command execution, IBM docs search, and Bob Shell headless runs.
