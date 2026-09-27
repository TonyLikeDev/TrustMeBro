---
name: dedup-merge
description: Find copy-pasted code (components, pages, actions, queries), merge each duplicate group into one shared function or component with the differences passed as a variant, and report the before/after line counts. Use when the user runs /dedup-merge or asks to check for duplicated code, merge duplicates, or make copy-paste code share one function.
---

# Dedup merge

Purpose: copy-pasted code becomes one function, so there is less to read and change. "Merge" here means code merging, not git merging. Success is a smaller and simpler codebase, so measure it (step 5).

## 1. Find the duplicates

- Read `LAYOUT.md` if it exists, and look for sibling files with parallel names (`teachers/` vs `teachers/ta/`, `new-teacher` vs `new-ta`, `page.tsx` for two roles).
- Diff each pair (`diff a b | wc -l`, or compare line counts) and note how much of it is identical.
- List each group with its files, its size and its overlap, sorted by lines saved. Show the list to the user before merging anything, unless they already said "merge them".

## 2. Decide per group: merge, extract or leave

| Overlap | Action |
|---|---|
| About 70% identical or more | Merge into one file. The differences become a variant. |
| About 40 to 70% | Extract only the identical blocks as helpers. Leave the two callers in place. |
| Under about 40% | Leave as is. |

Also leave as is:
- Pairs that have a comment explaining why they are separate.
- Pairs whose shared part is under about 100 lines.
- Pairs where one side has a feature the other lacks (undo, extra step), unless it becomes a clean variant.

A merged pair that needs more adapter and type lines than it saves is the wrong call. Undo it and say so.

## 3. Merge with variants

- One shared file holds the common code. The differences come in as a `kind` prop (`"teacher" | "ta"`) or a small option (`noFuture`), not as copied branches.
- Put everything that differs in one place, a config object or one `loadView`-style function, so a reader sees the whole difference at once.
- Follow a pattern already in the repo (for example an existing `kind` prop) before inventing a new one.
- Delete the old files and any helper that only they used. Keep the old route or page files as thin wrappers when the framework needs them.
- Merge components first. Merge server actions and queries last: they are usually the least identical, so they save the least.

## 4. Verify

- Run typecheck, lint and tests. Fix failures before reporting.
- If the pages were not opened in a browser, say so.
- Write down every visible behaviour change (URL params, wording, control style). A merge should not change behaviour, and when it must, tell the user.
- Update `LAYOUT.md` in the same change (delete old entries, add the new files). Do not commit unless asked.

## 5. Report with numbers

Compare committed `HEAD` with the working tree per merged group:

```bash
# before: sum of the old files at HEAD; after: the new files
for f in old1 old2; do git show HEAD:"$f" | wc -l; done
wc -l new1 new2
git diff --shortstat HEAD -- src
```

Show one table (group, before, after, net, %) and one total. Then explain any gap between the expected saving (about half for exact copies) and the real one:

- **Similarity**: the fewer lines were really identical, the less the merge saves.
- **Adapter objects**: the per-caller config that re-states what the old code did inline.
- **Types**: the definitions the shared code needs to describe what each caller supplies.
- **Comments**: added explanations of why the variants differ.

Count "lines added" in the diff separately from net size. New shared files show up as all-new lines even when the total shrinks, and this is why a merge can look like growth in a diff.
