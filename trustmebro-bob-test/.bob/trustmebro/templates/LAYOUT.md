<!-- trustmebro -->
# Project layout

Map of the code: where things are, what they do, how they connect. **Rule: when a change adds, moves or removes a folder, component, table or piece of logic, update this file in the same commit.** One line per entry; point to files, don't paste code.

Last updated: <YYYY-MM-DD>.

## Overview

<2 to 3 sentences: what the project is, and the path a request or run takes through it.>

## Folder tree

```
<project>/
├── <folder>/            <purpose>
│   └── <file>           <purpose>
└── ...
```

## Components

| Component | Path | Does | Depends on |
| :--- | :--- | :--- | :--- |
| | | | |

**Flows**
- <name>: <A → B → C>

## Database

<!-- "No database." if there is none. -->

Defined in: `<schema, migrations or models path>`

| Table / collection | Key fields | Relations |
| :--- | :--- | :--- |
| | | |

## Logic

<!-- Each business rule or workflow, and where it lives. -->

- **<name>**: <what it does> → `path/to/file:function`
