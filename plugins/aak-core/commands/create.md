---
name: create
description: Create new application command. Triggers App Builder skill and starts interactive dialogue with user.
---

# /create - Create Application

$ARGUMENTS

---

## Task

This command starts a new application creation process. It is **self-contained**: it depends only on `aak-core`, and uses richer capabilities from other plugins **only when they are enabled** (never assume a cross-plugin agent or skill exists).

### Steps:

1. **Request Analysis (scoping gate)**
   - Understand what the user wants.
   - If a brainstorming skill is available (e.g. `superpowers:brainstorming` or `aak-legacy`'s `brainstorming`), defer to it for scoping.
   - Otherwise, ask 2–3 clarifying questions inline: What type of application? Core features? Who uses it? Use sensible defaults and refine later.

2. **Project Planning**
   - Plan inline: determine tech stack, file structure, and a short build sequence; write a `{task-slug}.md` plan file in the project root.
   - If `aak-legacy` is enabled, you may delegate the breakdown to its `project-planner` agent instead.

3. **Design Source-of-Truth (UI projects only)**
   - If the app has a UI, create `DESIGN.md` at the project root BEFORE building UI — follow the `design-spec` skill (in this plugin).
   - Skip only for headless/CLI/API-only projects.

4. **Application Building (after approval)**
   - Use the `app-builder` skill (this plugin) to drive scaffolding.
   - **Delegate expert work only to enabled plugins; otherwise scaffold inline:**
     - if `aak-backend` is enabled → `database-architect` (schema), `backend-specialist` (API);
     - if `aak-frontend` is enabled → `frontend-specialist` (UI, building against `DESIGN.md` tokens);
     - if a plugin is not enabled, perform that role yourself inline.

5. **Preview**
   - If `aak-backend` is enabled, start a preview with `/aak-backend:preview`.
   - Otherwise, tell the user the project's own run/dev command (e.g. `npm run dev`) and present the local URL.

---

## Usage Examples

```
/create blog site
/create e-commerce app with product listing and cart
/create todo app
/create Instagram clone
/create crm system with customer management
```

---

## Before Starting

If request is unclear, ask these questions:
- What type of application?
- What are the basic features?
- Who will use it?

Use defaults, add details later.
