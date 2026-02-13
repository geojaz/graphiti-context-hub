# Graphiti Context Hub

Unified context retrieval for Claude Code - orchestrates **Graphiti knowledge graph**, **Context7 documentation**, and **Serena symbol analysis** into a single context-gathering workflow.

## Installation

```bash
claude plugins install graphiti-context-hub --marketplace geojaz
```

Or install from local path:
```bash
claude plugins install /path/to/graphiti-context-hub
```

## Configuration

Create `.context-hub.yaml`:

```yaml
graphiti:
  group_id: "auto"  # auto-detect from git repo, or set explicit name
  endpoint: "http://localhost:8000"  # optional, defaults to localhost:8000
```

**Group ID**: Isolates this project's knowledge graph. Set to `"auto"` to auto-detect from git repository name, or set explicit name like `"my-project"`.

## Prerequisites

### Required: Graphiti MCP Server

**Automatic Configuration**: This plugin automatically configures Claude Code to connect to Graphiti via HTTP at `http://localhost:8000/mcp`.

**You need to install and run Graphiti separately:**

1. Install the Graphiti MCP server (see [Graphiti documentation](https://github.com/getzep/graphiti))
2. Start the server:
   ```bash
   graphiti-server start --port 8000
   ```
3. Verify the connection:
   ```bash
   /context-hub-setup
   ```

**Custom endpoint**: If running on a different host/port, update `.context-hub.yaml`:
```yaml
graphiti:
  endpoint: "http://your-host:your-port"
```

### Required: Serena (for `/encode-repo-serena`)
```bash
claude plugins install serena
```

### Recommended: Context7 (for framework docs)
```bash
claude plugins install context7 --marketplace pleaseai/claude-code-plugins
```

## Setup

Run the setup command to configure and verify:

```bash
/context-hub-setup
```

This will:
1. Check if Serena and Context7 plugins are installed
2. Create `.context-hub.yaml` configuration file
3. Test Graphiti MCP connectivity
4. Verify group_id auto-detection

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

Graphiti Context Hub includes auto-discovered skills:

### Memory Skills
| Skill | Description |
|-------|-------------|
| `using-graphiti-memory` | When/how to query and save to Graphiti |
| `exploring-knowledge-graph` | Deep graph traversal and relationship discovery |

### Serena Skills
| Skill | Description |
|-------|-------------|
| `using-serena-symbols` | Symbol-level code analysis guidance |
| `serena-code-architecture` | Architectural analysis with Graphiti integration |

## How It Works

### /context_gather

Orchestrates multiple sources:

1. **Graphiti Knowledge Graph** - Semantic search across entities and relationships
2. **File System** - Read actual code files
3. **Context7** - Framework-specific documentation (if installed)
4. **Serena** - Symbol-level code analysis (if installed)
5. **WebSearch** - Fallback for recent information

Returns synthesized summary with:
- Relevant entities and relationships
- Code patterns and snippets
- Framework guidance
- Architectural decisions

### /encode-repo-serena

Uses Serena's LSP-powered analysis:
- **Symbol extraction** - Classes, functions, methods with locations
- **Relationship discovery** - Dependencies and references
- **Cross-file analysis** - Component connections

Stores findings as episodes in Graphiti for future retrieval.

## Example Usage

```bash
# Before implementing a feature
/context_gather implement OAuth2 authentication for the API

# Bootstrap a new project
/encode-repo-serena

# Quick memory search
/memory-search authentication patterns

# Save an important decision
/memory-save

# Explore the knowledge graph
/memory-explore authentication architecture
```

## Architecture

```
graphiti-context-hub
├── skills/
│   ├── using-graphiti-memory/      ─── Memory usage guide
│   ├── exploring-knowledge-graph/   ─── Graph traversal
│   ├── using-serena-symbols/        ─── Symbol analysis
│   └── serena-code-architecture/    ─── Architecture workflows
├── commands/
│   ├── context_gather.md            ─── Multi-source retrieval
│   ├── encode-repo-serena.md        ─── Repository encoding
│   └── memory-*.md                  ─── Memory management
└── agents/
    └── context-retrieval.md         ─── Context gathering agent
```

## Graphiti Features

**Automatic Entity Extraction:**
- Saves episodes and automatically extracts entities
- Creates relationships between entities
- No manual linking required

**Knowledge Graph:**
- Entities: Classes, functions, concepts, decisions
- Relationships: Dependencies, implementations, influences
- Temporal: Track evolution over time

**Search:**
- Semantic search across nodes (entities)
- Relationship search via facts
- Episode chronology for context

## License

MIT
