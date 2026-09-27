---
name: dedup-merge
description: Find copy-pasted code (functions, classes, components, modules, queries), merge each duplicate group into one shared function or component with the differences passed as a variant, and report the before/after line counts. Use when the user runs /dedup-merge or asks to check for duplicated code, merge duplicates, or make copy-pasted code share one implementation.
---

# Dedup merge

Purpose: copy-pasted code becomes one implementation, so there is less to read and change. "Merge" here means code merging, not git merging. Success is a smaller and simpler codebase, so measure it (step 5).

## 1. Find the duplicates

- Read `LAYOUT.md` if it exists. Look for files or folders with parallel names (`admin/` vs `user/`, `create_order` vs `create_invoice`, `ProductCard` vs `ServiceCard`) and for functions with the same shape under different names.
- If the project already has a duplicate detector (`jscpd`, PMD CPD, pylint's `duplicate-code` check), run it instead of comparing by hand.
- Diff each candidate pair (`diff a b | wc -l`, or compare line counts) and note how much of it is identical.
- List each group with its files, its size and its overlap, sorted by lines saved. Show the list to the user before merging anything, unless they already said "merge them".

## 2. Decide per group: merge, extract or leave

| Overlap | Action |
|---|---|
| About 70% identical or more | Merge into one implementation. The differences become a variant. |
| About 40 to 70% | Extract only the identical blocks as helpers. Leave the callers in place. |
| Under about 40% | Leave as is. |

Also leave as is:
- Groups that have a comment explaining why they are separate.
- Groups whose shared part is only a few lines (under about 20): a helper that small costs more to follow than it saves.
- Groups where one side has a feature the other lacks (undo, an extra step), unless it becomes a clean variant.
- Code that is deliberately separate: generated files, vendored code, test fixtures, and copies kept apart on purpose (different release cycles, different owners).

A merge that needs more adapter and type lines than it saves is the wrong call. Undo it and say so.

## 3. Merge with variants

- One shared file holds the common code. The differences come in as a `kind` parameter (`kind: "admin" | "user"`) or a small option (`read_only=True`), not as copied branches.
- Put everything that differs in one place, a config object or one loader function, so a reader sees the whole difference at once.
- Follow a pattern already in the repo (an existing variant parameter, config object or base class) before inventing a new one.
- Delete the old files and any helper that only they used. Keep old entry points (routes, pages, public functions, exported names) as thin wrappers when something outside the group depends on them.
- Merge the most identical groups first (usually UI components and pure helpers). Merge data-access code (queries, API handlers, server actions) last: it is usually the least identical, so it saves the least.

## 4. Verify

- Run the project's checks (tests, type checker, linter), whichever exist. Fix failures before reporting.
- If a UI change was not checked in a browser or app, say so.
- Write down every visible behaviour change (URLs or parameters, wording, control style, error messages). A merge should not change behaviour, and when it must, tell the user.
- Update `LAYOUT.md` in the same change: the folder tree (delete old entries, add the new files) and the Logic list (point each merged piece of logic at the shared function). Do not commit unless asked.

## 5. Report with numbers

Compare committed `HEAD` with the working tree per merged group:

```bash
# before: sum of the old files at HEAD; after: the new files
for f in old1 old2; do git show HEAD:"$f" | wc -l; done
wc -l new1 new2
git diff --shortstat HEAD -- <files of the merged groups>
```

Show one table (group, before, after, net, %) and one total. Then explain any gap between the expected saving (about half for exact copies) and the real one:

- **Similarity**: the fewer lines were really identical, the less the merge saves.
- **Adapter objects**: the per-caller config that restates what the old code did inline.
- **Types**: the definitions the shared code needs to describe what each caller supplies.
- **Comments**: added explanations of why the variants differ.

Count "lines added" in the diff separately from net size. New shared files show up as all-new lines even when the total shrinks, which is why a merge can look like growth in a diff.
