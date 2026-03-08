# Graphiti Context Hub Plugin v4.0 — Simplification & Hooks

## Problem

The plugin accumulated complexity from its Forgetful→Graphiti migration:
- Layered config system (global + local + deprecated YAML)
- Incorrect MCP tool names in some files
- Forgetful-era examples that don't match Graphiti's capabilities
- No automatic setup flow — users must know to run `/context-hub-setup`
- No hooks to encourage context gathering and memory saving
- Destructive MCP tools exposed unnecessarily

## Goals

1. Simplify configuration to a single global conf file
2. Add SessionStart hook for first-run setup detection
3. Add advisory hooks for context gathering and memory persistence
4. Fix all MCP tool names across the codebase
5. Audit and update examples for Graphiti (not Forgetful)
6. Deemphasize destructive MCP tools
7. Clean up migration remnants

## Design

### 1. Configuration System

**Single file:** `~/.config/claude/graphiti-context-hub.conf`

```bash
GRAPHITI_GROUP_ID=main
GRAPHITI_ENDPOINT=http://localhost:8000
SERENA_ENABLED=true
```

- Created interactively by `/context-hub-setup`
- No local overrides, no YAML layer, no precedence rules
- `SERENA_ENABLED` flag set during setup based on plugin detection

**Remove:**
- `.context-hub.conf` / `.context-hub.conf.example`
- `.context-hub.yaml` / `.context-hub.yaml.example`
- `requirements.txt` (PyYAML no longer needed)
- `lib/` directory (empty remnant)
- `graphiti-mcp.md` (reference absorbed into corrections)
- `.claude-plugin/README.md`

### 2. MCP Server Configuration

`servers.json` ships with default `http://localhost:8000/mcp`. Commands and skills
read the conf file for the actual endpoint and group_id at runtime.

### 3. Hooks

All hooks are `command` type (zero token cost, advisory reminders).
Bundled via plugin `hooks/hooks.json`.

| Hook Event | Matcher | Purpose |
|---|---|---|
| SessionStart | — | Check config exists; remind to run `/context-hub-setup` if missing |
| PreToolUse | `Edit\|Write` | Remind: query Graphiti (+ Serena if enabled) before modifying code |
| PreToolUse | `EnterPlanMode` | Remind: gather context from Graphiti before planning |
| PreCompact | — | Remind: save unsaved decisions/patterns to Graphiti |
| SubagentStart | — | Remind: save important context before subagent handoff |
| SubagentStop | — | Remind: capture valuable subagent findings to Graphiti |

Each hook script reads the conf file to inject correct `group_id` and conditionally
include Serena instructions based on `SERENA_ENABLED`.

### 4. MCP Tool Exposure

**Primary tools** (referenced in skills/commands):
- `mcp__graphiti__add_memory`
- `mcp__graphiti__search_nodes`
- `mcp__graphiti__search_memory_facts`
- `mcp__graphiti__get_episodes`
- `mcp__graphiti__get_entity_edge`

**Deemphasized** (not referenced, available if user explicitly needs them):
- `mcp__graphiti__delete_episode`
- `mcp__graphiti__delete_entity_edge`
- `mcp__graphiti__clear_graph`
- `mcp__graphiti__get_status`

### 5. Tool Name Audit

All commands, skills, and agents will be audited against actual Graphiti MCP tool
names. Known issues: some files reference old Forgetful-era tool names or
incorrect Graphiti tool signatures.

### 6. Example Audit

All examples will be reviewed for Graphiti compatibility:
- Remove Forgetful-specific patterns
- Update for Graphiti's automatic entity extraction (no manual entity creation)
- Ensure episode_body examples use proper repo tagging format
- Fix any examples showing manual relationship creation (Graphiti does this automatically)

### 7. Setup Flow

`/context-hub-setup` becomes the single entry point:
1. Detect if Serena plugin is installed → set `SERENA_ENABLED`
2. Ask user for Graphiti endpoint (default: `http://localhost:8000`)
3. Ask user for group_id (default: `main`)
4. Write `~/.config/claude/graphiti-context-hub.conf`
5. Test Graphiti connection via `mcp__graphiti__get_status`
6. Report setup status

### 8. Files Changed

**Create:**
- `hooks/hooks.json` — hook definitions
- `hooks/session-start.sh` — config check script
- `hooks/context-reminder.sh` — reads conf, outputs additionalContext JSON

**Modify:**
- All 7 commands — remove config boilerplate, fix tool names, update examples
- All 4 skills — fix tool names, simplify config references, update examples
- `agents/context-retrieval.md` — fix tool names
- `commands/context-hub-setup.md` — new interactive setup flow
- `.claude-plugin/plugin.json` — version bump to 4.0.0
- `.claude-plugin/servers.json` — keep default endpoint
- `README.md` — reflect simplified architecture

**Remove:**
- `.context-hub.conf`, `.context-hub.conf.example`
- `.context-hub.yaml`, `.context-hub.yaml.example`
- `requirements.txt`
- `lib/` directory
- `graphiti-mcp.md`
- `.claude-plugin/README.md`
