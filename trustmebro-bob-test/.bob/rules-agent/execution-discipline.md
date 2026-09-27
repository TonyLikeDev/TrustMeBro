# Execution Discipline Rules (Agent Mode)

## Rule 1: Plan Before Act

Before calling ANY tool, always declare a todo list first:
```
update_todo_list:
[ ] What info is needed?
[ ] Is any of it already in this conversation? → audit Messages first
[ ] Fetch ONLY what is missing
[ ] Execute
[ ] Verify
```

## Rule 2: No Redundant Tool Calls

Never call the same tool with the same parameters more than once per session.

Before calling `read_file`, `web_fetch`, `search_ibm_docs`, or any MCP tool:
- Scan the current conversation for the data
- If already present → mark step done, skip the tool call
- Only call if the data is genuinely absent from context

## Rule 3: Token Budget Awareness

Monitor context usage:
- If Messages category > 50,000 tokens → STOP current work
- Report to user: "Context at ~Xk tokens. Recommend starting a subtask to preserve quality."
- Offer: `start_subtask` with only the next step's context

## Rule 4: Codebase Exploration via Subagent

Never read multiple files directly into main context for exploration.
Use `spawn_subagent(type: "explore")` for:
- Understanding unfamiliar code sections
- Finding which files are affected by a change
- Scanning directory structures

The subagent returns a summary only → main context stays lean.

## Rule 5: One Resource, One Read

Read each file once per task. If you need to refer back to file content,
use the already-loaded content from Messages — do not re-read.
