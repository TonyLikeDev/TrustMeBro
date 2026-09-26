# IBM Bob 2.0 Hackathon — Official Guide Summary

> Extracted and summarised from:
> https://lablab-ibm-bob-2-hackathon-guide.s3.us.cloud-object-storage.appdomain.cloud/index.html
>
> Read this before doing anything else.

---

## 1. The Hackathon Expectation

Build a **working prototype** using **IBM Bob IDE** aligned to:

> *"Build with purpose using IBM Bob 2.0 — Create a solution that improves a specific developer
> workflow such as onboarding, debugging, code review, testing, application maintenance, or release
> and deployment processes."*

Key requirements:
- Clearly define a problem where time/effort/errors are too high TODAY
- Build on a **real or sample project** (not a toy/hypothetical)
- Use **Agent mode, parallel tasks, subagents, and document understanding**
- Demonstrate **measurable impact**

---

## 2. Setting Up Your IBM Bob Account

### Step 1 — Get the Invite
- Check your hackathon registration email inbox (and Spam/Junk)
- Look for: *"You have been added as a team member to ibm-hackathon-xxxx"*
- Plan: **Enterprise plan**

### Step 2 — Install Bob IDE
- Install from: https://bob.ibm.com/docs/ide/getting-started/install
- **Minimum required version**: v2.0.2 (v1.0.3 and v2.0.0 stop working Sep 30, 2026)
- If on v1.0.3 → must upgrade to latest v2.0.x
- If on v2.0.0 → must upgrade to v2.0.2 or later

### Step 3 — Sign In
- Create an IBMid if needed: https://www.ibm.com/account/reg/us-en/signup?formid=urx-19776
- Open Bob IDE → click **Log in to Bob**
- Complete IBMid authentication in browser

### Step 4 — Switch to Hackathon Account (Critical!)
- Go to: **Settings** (gear icon) → **General** tab
- Switch Team to: **ibm-coding-challenge-uat (region: us-east)**
- This prevents spending Bobcoins from your personal account

---

## 3. Bobcoins (Usage Budget)

- You have a limited Bobcoin budget for the hackathon
- Monitor usage in Bob IDE Settings
- Don't waste Bobcoins on non-project exploration — use the official exercises to learn first
- Screenshots of the session summaries show your Bobcoin usage (required for submission)

---

## 4. Bob IDE — Key Features

| Feature | What It Does | Docs Link |
|---------|-------------|-----------|
| **Chat interface** | Primary workspace — natural language, slash commands, auto-approval | https://bob.ibm.com/docs/ide/features/chat-interface |
| **Modes** | Ask / Plan / Agent — specialized personas for different tasks | https://bob.ibm.com/docs/ide/features/modes |
| **Custom modes** | Create your own mode with a specific role, rules, tool access | https://bob.ibm.com/docs/ide/configuration/custom-modes |
| **Subagents** | Isolated focused tasks in their own context; enables parallelism | https://bob.ibm.com/docs/ide/features/subagents |
| **Auto-approve** | Eliminates repetitive approval prompts; configure carefully | https://bob.ibm.com/docs/ide/features/auto-approving-actions |
| **Custom rules** | Tell Bob how to behave consistently (.bob rules file) | https://bob.ibm.com/docs/ide/configuration/rules |
| **MCP servers** | Connect Bob to external tools and services | https://bob.ibm.com/docs/ide/configuration/mcp/mcp-in-bob |
| **Ignore files** | `.bobignore` — control which files Bob can access | https://bob.ibm.com/docs/ide/configuration/bobignore |
| **Context mentions** | @ symbol to reference files, folders, problems directly | https://bob.ibm.com/docs/ide/features/context-mentions |
| **Skills** | Reusable instruction sets for specialized workflows | https://bob.ibm.com/docs/ide/features/skills |
| **Rollback** | Auto-version files during AI tasks; recover from bad changes | https://bob.ibm.com/docs/ide/features/rollback |
| **Code reviews** | Built-in AI review workflow — flags issues before commit | https://bob.ibm.com/docs/ide/features/code-reviews |
| **Commit messages** | Auto-generate meaningful commit messages | https://bob.ibm.com/docs/ide/features/commit-messages |
| **Pull requests** | Generate PRs and PR descriptions from the IDE | https://bob.ibm.com/docs/ide/features/pull-requests |
| **Bob tips** | Real-time code quality issues + AI refactoring suggestions | https://bob.ibm.com/docs/ide/features/bob-tips |
| **Literate coding** | Write code by typing natural language comments inline | https://bob.ibm.com/docs/ide/features/literate-coding |
| **Enhance prompt** | Click sparkles icon to auto-improve your prompts | https://bob.ibm.com/docs/ide/features/enhance-prompt |
| **Code actions** | Quick fixes, refactorings, explanations via lightbulb icon | https://bob.ibm.com/docs/ide/features/code-actions |

---

## 5. Bob IDE — Hands-On Exercises (Run These First!)

### Bob Exercises
| Exercise | What You Learn | Link |
|----------|---------------|------|
| Quickstart | Build a web UI for Node.js Express API using modes + approval workflow | https://bob.ibm.com/docs/ide/getting-started/quickstart |
| Travel demo app | Understand the tutorial flow, setup, architecture | https://bob.ibm.com/docs/ide/getting-started/tutorials/introduction |
| Build agents with /init | Persistent project context across conversations | https://bob.ibm.com/docs/ide/getting-started/tutorials/start-a-project |
| Create commit + PR | Branch → stage → commit message → push → PR | https://bob.ibm.com/docs/ide/tutorials/create-commit-and-pr |
| Generate code from comments | Literate coding in practice | https://bob.ibm.com/docs/ide/getting-started/tutorials/generate-code-from-comments |
| Plan + implement complex features | Plan mode → Agent mode workflow | https://bob.ibm.com/docs/ide/getting-started/tutorials/partner-with-a-coding-agent |
| Standardize Bob's behavior | Project-level rules files | https://bob.ibm.com/docs/ide/getting-started/tutorials/standardize-bobs-behavior |
| Add a custom mode | Custom product-manager mode creation | https://bob.ibm.com/docs/ide/getting-started/tutorials/add-bob-capabilities |
| Create a new context window | Manage memory, control cost | https://bob.ibm.com/docs/ide/getting-started/tutorials/context-window |
| Modernize a Node.js app | Upgrade Express API from v16 to v22 | https://bob.ibm.com/docs/ide/tutorials/modernize-nodejs-express-api |
| Inspect an unfamiliar codebase | Understand purpose, architecture, tech stack | https://bob.ibm.com/docs/ide/tutorials/inspect-a-codebase |
| Generate architecture diagrams | Mermaid UML, sequence, use-case diagrams | https://bob.ibm.com/docs/ide/tutorials/generate-architecture-diagrams |
| Audit code + generate reports | OWASP ASVS, SARIF, OSCAL reports | https://bob.ibm.com/docs/ide/tutorials/audit-code |
| Secure code with actor-critic workflow | Security rules + actor-critic pattern | https://bob.ibm.com/docs/ide/tutorials/generate-secure-code |

### Bob + watsonx Orchestrate Exercises
| Exercise | Link |
|----------|------|
| Build watsonx Orchestrate agents + MCP tools using Bob | https://developer.ibm.com/tutorials/build-agents-mcp-tools-watsonx-orchestrate-using-bob/ |
| Build programmatic agentic workflows on watsonx Orchestrate | https://developer.ibm.com/tutorials/build-programmatic-agentic-workflows-watsonx-orchestrate-bob/ |
| BPMN to production-ready agents with Bob skills + watsonx Orchestrate | https://developer.ibm.com/tutorials/bpmn-to-agents-bob-skills-watsonx-orchestrate/ |

---

## 6. Bob Shell (Optional)

- Brings IBM Bob's AI to the command line
- Good for automation, scripting, batch processing
- Requires a fresh install (no upgrade path from 1.0.x)
- Authentication: same IBMid login at bob.ibm.com/login
- Install: https://bob.ibm.com/docs/shell/getting-started/install-and-setup

---

## 7. Uploading Bob Task Session Summary (Required for Submission)

### Steps:
1. In Bob IDE chat → click **Tasks** tab
2. Select a task related to your project
3. Click the **task header** to see the session consumption summary
4. Screenshot it (PNG preferred)
5. Name it: `teamname_task##_short_description_summary.png`
6. Create folder `bob_sessions/` in your repo
7. Upload all screenshots there
8. Repeat for ALL relevant tasks, for ALL team members

---

## 8. Optional: IBM watsonx

| Product | What It Does | Guide |
|---------|-------------|-------|
| **watsonx Orchestrate** | No-code/low-code platform for orchestrating AI agents across workflows | https://lablab-ibm-bob-2-hackathon-guide.s3.us.cloud-object-storage.appdomain.cloud/watsonx-guide.html |
| **watsonx.ai** | AI studio with foundation models (Granite + others); can serve as inference provider | Same link above |

---

## 9. Example Use Cases

| Idea | Description |
|------|-------------|
| Smart onboarding assistant | Analyze repos, explain architecture, generate setup guidance, suggest starter tasks |
| Intelligent code review & quality coach | Analyze code changes, identify risks, explain findings, recommend fixes |
| Automated testing & validation hub | Generate unit tests, identify coverage gaps, validate changes |
| Release readiness & deployment assistant | Analyze changes, review dependencies, summarize risks, generate release notes |
| Legacy app modernization accelerator | Explain existing code, identify modernization opportunities, generate updated components |

---

## 10. Data Rules

- Bring your own datasets
- No company confidential data, client data, PI, or social media data
- Public website data OK if terms allow commercial use — keep a source list
- See `planning/DATASET_GUIDELINES.md` for full details
