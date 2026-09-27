---
name: layout-init
description: Map an existing codebase into LAYOUT.md, covering the folder tree with the purpose of each part, the components and how they connect, the database schema, and a list of the business logic with where each piece lives. Use when the user runs /layout-init or asks to map, document or describe the layout or architecture of an existing project.
---

# Layout Init

Generates `LAYOUT.md` in the project root: a map documenting components, database, and logic so any session or agent can understand layout and component reuse without re-reading the full codebase.

## Workflow

1. Read README, package manifests, and project tree (excluding build artifacts).
2. Identify:
   - **Components**: Reusable UI and module components.
   - **Database**: Tables, schema, and models.
   - **Logic**: Key business rules and handlers.
3. Write `LAYOUT.md` conforming to standard template.
