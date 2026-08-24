// kind: "agent" | "skill" | "command"; each entry names the source basename → target plugin
export const AGENTS = {
  "documentation-writer": "aak-core", "product-manager": "aak-core", "product-owner": "aak-core",
  "backend-specialist": "aak-backend", "database-architect": "aak-backend", "devops-engineer": "aak-backend",
  "frontend-specialist": "aak-frontend", "mobile-developer": "aak-frontend",
  "security-auditor": "aak-security", "penetration-tester": "aak-security",
  "debugger": "aak-quality", "test-engineer": "aak-quality", "qa-automation-engineer": "aak-quality",
  "performance-optimizer": "aak-quality", "code-archaeologist": "aak-quality", "explorer-agent": "aak-quality",
  "seo-specialist": "aak-marketing",
  "game-developer": "aak-game",
  "project-planner": "aak-legacy",
  // orchestrator: NOT copied as an agent — merged into /orchestrate command in Task 5
};

export const SKILLS = {
  "architecture": "aak-core", "app-builder": "aak-core", "code-review-graph": "aak-core",
  "design-spec": "aak-core", "clean-code": "aak-core", "simplify-code": "aak-core",
  "i18n-localization": "aak-core", "batch-operations": "aak-core", "documentation-templates": "aak-core",
  "api-patterns": "aak-backend", "database-design": "aak-backend", "nodejs-best-practices": "aak-backend",
  "python-patterns": "aak-backend", "rust-pro": "aak-backend", "server-management": "aak-backend",
  "deployment-procedures": "aak-backend", "mcp-builder": "aak-backend",
  "bash-linux": "aak-backend", "powershell-windows": "aak-backend",
  "frontend-architecture": "aak-frontend", "frontend-design": "aak-frontend",
  "nextjs-react-expert": "aak-frontend", "tailwind-patterns": "aak-frontend",
  "web-design-guidelines": "aak-frontend", "mobile-design": "aak-frontend",
  "vulnerability-scanner": "aak-security", "red-team-tactics": "aak-security",
  "testing-patterns": "aak-quality", "webapp-testing": "aak-quality", "code-review-checklist": "aak-quality",
  "performance-profiling": "aak-quality", "lint-and-validate": "aak-quality",
  "seo-fundamentals": "aak-marketing", "geo-fundamentals": "aak-marketing",
  "game-development": "aak-game",
  "brainstorming": "aak-legacy", "systematic-debugging": "aak-legacy", "tdd-workflow": "aak-legacy",
  "plan-writing": "aak-legacy", "verify-changes": "aak-legacy", "parallel-agents": "aak-legacy",
  "coordinator-mode": "aak-legacy", "intelligent-routing": "aak-legacy", "behavioral-modes": "aak-legacy",
  "context-compression": "aak-legacy", "memory-system": "aak-legacy", "skillify": "aak-legacy",
};

export const COMMANDS = {
  "create": "aak-core", "enhance": "aak-core",
  "deploy": "aak-backend", "preview": "aak-backend",
  "brainstorm": "aak-legacy", "plan": "aak-legacy", "debug": "aak-legacy", "verify": "aak-legacy",
  "test": "aak-legacy", "status": "aak-legacy", "orchestrate": "aak-legacy", "coordinate": "aak-legacy",
  "remember": "aak-legacy",
};

// Frontmatter keys to delete outright (when_to_use is merged, not deleted).
export const DROP_KEYS = ["version","requires_agents","requires_skills","artifact_outputs","priority","effort","metadata","trigger","skills"];
