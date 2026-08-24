---
name: enhance
description: Add or update features in existing application. Used for iterative development.
---

# /enhance - Update Application

$ARGUMENTS

---

## Task

This command adds features or makes updates to an existing application. It is **self-contained**: it depends only on `aak-core`, and uses other plugins only when enabled.

### Steps:

1. **Understand Current State**
   - Re-read project state inline: run `git status` and list the project tree to see existing files; inspect `package.json`/manifest and config to infer the tech stack and features.
   - If `aak-quality` is enabled, you may use its `code-archaeologist` agent for a deeper read of an unfamiliar codebase.

2. **Plan Changes**
   - Determine what will be added/changed; detect affected files; check dependencies.

3. **Present Plan to User** (for major changes)
   ```
   "To add admin panel:
   - New files: admin routes, components, and access control
   - Updates: navigation, auth middleware
   - Scope: moderate (touches auth + routing)

   Should I start?"
   ```

4. **Apply**
   - Make the changes (delegate to enabled-plugin specialists where useful; otherwise do it inline).
   - Test with the project's own test command.
   - If `aak-workflow` is enabled, you may use its `verify-changes` skill to prove the change works.

5. **Update Preview**
   - Hot reload / restart, or `/aak-backend:preview` if `aak-backend` is enabled.

---

## Usage Examples

```
/enhance add dark mode
/enhance build admin panel
/enhance integrate payment system
/enhance add search feature
/enhance edit profile page
/enhance make responsive
```

---

## Caution

- Get approval for major changes
- Warn on conflicting requests (e.g., "use Firebase" when project uses PostgreSQL)
- Commit each change with git
