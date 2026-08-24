# AI Agentic Kit

A broad Claude Code agent toolkit distributed as one marketplace of eight domain plugins (prefix `aak-`). Install the whole marketplace once, then **enable only the slices a given project needs** — breadth is the point; what you don't need, you simply don't enable.

Adapted from [ag-kit](https://github.com/vudovn/ag-kit) © vudovn (MIT): its domain knowledge (20 specialist agents, 47 skills, 13 workflows) is salvaged into native Claude Code plugins, with the Antigravity-specific plumbing rewritten or dropped.

## Install

```bash
# once per machine
/plugin marketplace add hoangdvh/ai-agentic-kit
# per project — enable only what you need
/plugin install aak-core@ai-agentic-kit
/plugin install aak-backend@ai-agentic-kit
```

`aak-legacy` stays uninstalled/disabled unless you want the ag-kit classic workflow bundle.

## Plugins

| Plugin | Covers |
|---|---|
| `aak-core` | Foundation: architecture, scaffolding, code-review, safety hook |
| `aak-backend` | Backend, data, API, devops, shell |
| `aak-frontend` | Frontend, design, mobile |
| `aak-security` | Offensive + defensive security |
| `aak-quality` | Test, debug, review, performance |
| `aak-marketing` | SEO, GEO, content |
| `aak-game` | Game development |
| `aak-legacy` | ag-kit classic workflow bundle (off by default) |

Commands and skills are namespaced per plugin (e.g. `/aak-core:create`).

## License

MIT. See [LICENSE](LICENSE). Adapted from [ag-kit](https://github.com/vudovn/ag-kit) © vudovn (MIT).
