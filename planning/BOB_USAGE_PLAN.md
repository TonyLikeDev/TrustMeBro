# IBM Bob 2.0 Usage Plan

> This document describes exactly how IBM Bob 2.0 will be used in the project.
> The submission requires a **500-word IBM Bob Usage Statement** — use this file to draft it.

---

## 📋 Overview

IBM Bob 2.0 must be the **core component** of the solution, not just a helper.
The judges specifically evaluate **Application of Technology** — how completely and centrally Bob
was applied.

---

## 🤖 Bob 2.0 Features to Leverage

### 1. Agent Mode (Required — use extensively)
- Agent mode lets Bob autonomously execute multi-step tasks across the full codebase
- Bob reads files, edits code, runs commands, and iterates without manual prompting at every step
- **Plan**: Use Agent mode to _______________

### 2. Subagents (Required — use for parallel work)
- Subagents run isolated, focused tasks in their own context — perfect for parallel analysis
- Example: spin up 4 subagents simultaneously for security check, test coverage, style, logic
- **Plan**: Use subagents to _______________

### 3. Plan Mode → Agent Mode Workflow
- Use Plan mode to break down a complex feature end-to-end before Agent mode implements it
- **Plan**: Use Plan mode for _______________

### 4. Document Understanding
- Bob can read and reason over documents (specs, READMEs, API docs, test reports)
- **Plan**: Feed Bob the following documents: _______________

### 5. Custom Modes
- Create a custom mode with a specific role definition, rules, and tool access
- **Plan**: Create a custom mode called "_______________" that _______________

### 6. Custom Rules (.bob rules file)
- Rules files tell Bob how to behave consistently across sessions (coding style, decisions, etc.)
- **Plan**: Create rules for _______________

### 7. MCP Servers (Optional but powerful)
- Connect Bob to external tools — GitHub, databases, APIs, testing frameworks
- **Plan**: Connect Bob to _______________

### 8. Skills
- Reusable instruction sets for specialized, repeatable workflows
- **Plan**: Create a skill for _______________

### 9. Bob Shell (Optional — for automation/scripting)
- Use Bob from the command line for non-interactive automation pipelines
- **Plan**: Use Bob Shell to _______________

---

## 🗺️ Bob Usage by Project Phase

| Phase | Task | Bob Feature Used | Expected Output |
|-------|------|-----------------|-----------------|
| Analysis | Understand existing codebase | Ask mode + context mentions | Architecture summary |
| Planning | Break down solution into tasks | Plan mode | Detailed task plan |
| Implementation | Write core logic | Agent mode | Working code |
| Parallel work | Run multiple checks at once | Subagents | Concurrent analysis results |
| Testing | Generate tests | Agent mode | Test suite |
| Documentation | Generate docs and reports | Agent mode | README, reports |
| Review | Code review | Agent mode + review workflow | Review summary |
| Commit | Create commit + PR | Built-in Git integration | Commit + PR |

---

## 📊 Session Tracking

Every time you use Bob for a significant task, note it here so you don't miss screenshots.

| # | Date | Task Description | Bob Feature Used | Screenshot Saved? |
|---|------|-----------------|-----------------|-------------------|
| 1 | | | | [ ] |
| 2 | | | | [ ] |
| 3 | | | | [ ] |
| 4 | | | | [ ] |
| 5 | | | | [ ] |
| 6 | | | | [ ] |
| 7 | | | | [ ] |
| 8 | | | | [ ] |

> **Reminder**: After each session, go to Bob IDE → Tasks → select task → click header → screenshot
> the session consumption summary → save to `bob_sessions/` folder.

---

## 📝 IBM Bob Usage Statement Draft (500 words max)

> Use this section to write your final IBM Bob Usage Statement for the submission form.
> Be **specific** about how Bob contributed — vague statements score poorly.

### What to Include:
- Which Bob features were used and when
- How Agent mode orchestrated the workflow
- How subagents ran tasks in parallel
- Any custom modes, rules, or skills created
- How Bob helped with specific coding/testing/documentation tasks
- If applicable: how watsonx.ai or watsonx Orchestrate was also used

```
[DRAFT YOUR 500-WORD IBM BOB USAGE STATEMENT HERE]

Example structure:

"We used IBM Bob 2.0 as the central engine of our [solution name].

In the analysis phase, we used Ask mode with context mentions (@codebase, @README) to have Bob
produce a full architecture map of our target repository in under 5 minutes.

For implementation, we switched to Plan mode where Bob broke the 12-step workflow into discrete
subtasks. We then triggered Agent mode, which autonomously implemented 8 of the 12 steps across
14 files without manual intervention, using rollback to safely explore approaches.

We leveraged subagents for parallel execution: while one subagent analyzed test coverage gaps,
a second checked for OWASP security issues, and a third validated documentation drift. This
parallel execution compressed what would have been 3 hours of sequential manual work into 12 minutes.

We created a custom mode called 'ReviewAgent' with a specific role definition focused on code
quality, and a .bob rules file that enforced consistent output format across all sessions.

Bob also generated all unit tests, created commit messages, and opened the pull request directly
from the IDE.

Total Bobcoin usage: tracked in bob_sessions/ screenshots."
```

---

## 🔗 Key Bob 2.0 Documentation

| Feature | Link |
|---------|------|
| Getting Started | https://bob.ibm.com/docs/ide/getting-started/install |
| Best Practices | https://bob.ibm.com/docs/ide/getting-started/best-practices |
| Modes | https://bob.ibm.com/docs/ide/features/modes |
| Subagents | https://bob.ibm.com/docs/ide/features/subagents |
| Auto-approve | https://bob.ibm.com/docs/ide/features/auto-approving-actions |
| Custom Modes | https://bob.ibm.com/docs/ide/configuration/custom-modes |
| Custom Rules | https://bob.ibm.com/docs/ide/configuration/rules |
| MCP Servers | https://bob.ibm.com/docs/ide/configuration/mcp/mcp-in-bob |
| Skills | https://bob.ibm.com/docs/ide/features/skills |
| Rollback | https://bob.ibm.com/docs/ide/features/rollback |
| Code Reviews | https://bob.ibm.com/docs/ide/features/code-reviews |
| Bob Shell | https://bob.ibm.com/docs/shell/getting-started/install-and-setup |
| Quickstart Exercise | https://bob.ibm.com/docs/ide/getting-started/quickstart |
| Security Guidelines | https://bob.ibm.com/docs/ide/security/bob-security-guidance |
