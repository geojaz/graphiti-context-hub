# Graphiti Context Hub

Unified context retrieval for Claude Code — orchestrates **Graphiti knowledge graph**, **Context7 documentation**, and **Serena symbol analysis** into a single context-gathering workflow.

## Installation

```bash
claude plugins install graphiti-context-hub --marketplace geojaz
```

Or install from local path:
```bash
claude plugins install /path/to/graphiti-context-hub
```

## Setup

Run the setup command to configure:

```
/context-hub-setup
```

This will:
1. Ask for your Graphiti endpoint (default: `http://localhost:8000`)
2. Ask for your group_id (default: `main`)
3. Detect companion plugins (Serena, Context7)
4. Write configuration to `~/.config/claude/graphiti-context-hub.conf`
5. Test Graphiti connectivity

### Prerequisites

**Required: Graphiti MCP Server**

Install and run the Graphiti MCP server (see [Graphiti documentation](https://github.com/getzep/graphiti)):

```bash
graphiti-server start --port 8000
```

**Recommended: Serena** (for `/encode-repo-serena`)
```bash
claude plugins install serena
```

**Recommended: Context7** (for framework docs)
```bash
claude plugins install context7 --marketplace pleaseai/claude-code-plugins
```

## Configuration

Single config file: `~/.config/claude/graphiti-context-hub.conf`

```bash
GRAPHITI_GROUP_ID=main
GRAPHITI_ENDPOINT=http://localhost:8000
SERENA_ENABLED=true
```

Created automatically by `/context-hub-setup`.

**Group ID**: Uses a single unified knowledge graph. All memories include repo context via automatic `Repo: {name}` tagging for flexible cross-repo querying.

## Commands

### Context Retrieval

| Command | Description |
|---------|-------------|
| `/context_gather <task>` | Gather context from Graphiti, code, and docs |
| `/encode-repo-serena` | Bootstrap repository into Graphiti using Serena |

### Memory Management

| Command | Description |
|---------|-------------|
| `/memory-search <query>` | Search knowledge graph semantically |
| `/memory-list [count]` | List recent episodes |
| `/memory-save` | Save current context as episode |
| `/memory-explore <query>` | Deep knowledge graph traversal |

### Setup

| Command | Description |
|---------|-------------|
| `/context-hub-setup` | Configure and verify setup |

## Skills

| Skill | Description |
|-------|-------------|
| `using-graphiti-memory` | When/how to query and save to Graphiti |
| `exploring-knowledge-graph` | Deep graph traversal and relationship discovery |
| `using-serena-symbols` | Symbol-level code analysis guidance |
| `serena-code-architecture` | Architectural analysis with Graphiti integration |

## Hooks

This plugin automatically registers advisory hooks that encourage context-aware development:

| Hook | Trigger | Purpose |
|------|---------|---------|
| SessionStart | Every session | Check config, provide Graphiti context |
| PreToolUse (Edit/Write) | Before code changes | Remind to query Graphiti for prior decisions |
| PreToolUse (EnterPlanMode) | Before planning | Remind to gather context first |
| PreCompact | Before compaction | Remind to save unsaved context to Graphiti |
| SubagentStart | Before subagent | Remind to persist context before handoff |
| SubagentStop | After subagent | Remind to capture subagent findings |

All hooks are zero-token-cost (`command` type) — they add context reminders without consuming LLM tokens.

Hooks are conditional on configuration:
- Serena reminders only appear when `SERENA_ENABLED=true` in config
- Group ID and repo name are automatically injected from config

## How It Works

### /context_gather

Orchestrates multiple sources:

1. **Graphiti Knowledge Graph** — Semantic search across entities and relationships
2. **File System** — Read actual code files
3. **Context7** — Framework-specific documentation (if installed)
4. **Serena** — Symbol-level code analysis (if installed)
5. **WebSearch** — Fallback for recent information

### Repository Tagging

All memories automatically include repository context:

```
Repo: my-project

Decision: Implemented user-level group_id
Rationale: Enables cross-repo pattern discovery
```

This enables both repo-specific and cross-repo queries.

## Architecture

```
graphiti-context-hub/
├── hooks/
│   ├── hooks.json                 ─── Hook registration
│   ├── session-start.sh           ─── Config check on session start
│   └── context-reminder.sh        ─── Advisory context reminders
├── skills/
│   ├── using-graphiti-memory/     ─── Memory usage guide
│   ├── exploring-knowledge-graph/ ─── Graph traversal
│   ├── using-serena-symbols/      ─── Symbol analysis
│   └── serena-code-architecture/  ─── Architecture workflows
├── commands/
│   ├── context_gather.md          ─── Multi-source retrieval
│   ├── context-hub-setup.md       ─── Interactive setup
│   ├── encode-repo-serena.md      ─── Repository encoding
│   └── memory-*.md                ─── Memory management
├── agents/
│   └── context-retrieval.md       ─── Context gathering agent
└── .claude-plugin/
    ├── plugin.json                ─── Plugin metadata
    └── servers.json               ─── Graphiti MCP default config
```

## Graphiti MCP Tools

**Primary tools used by this plugin:**
- `mcp__graphiti__add_memory` — Save episodes to knowledge graph
- `mcp__graphiti__search_nodes` — Search for entities
- `mcp__graphiti__search_memory_facts` — Search for relationships between entities
- `mcp__graphiti__get_episodes` — List episodes chronologically
- `mcp__graphiti__get_entity_edge` — Get specific relationship details

Graphiti automatically extracts entities and relationships from episode content — no manual linking required.

## License

MIT
