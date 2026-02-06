# Migration Guide: Pluggable Memory Backend

This guide helps existing users migrate to the new pluggable backend system.

## What Changed

**Before (Forgetful-only):**
- Commands called `execute_forgetful_tool()` directly
- Project ID discovery required for scoping
- Single backend (Forgetful)

**After (Pluggable):**
- Commands use memory adapter (Graphiti or Forgetful)
- Auto-detect group_id from git repo
- Config-based backend selection

## Migration Steps

### 1. Configuration

Create `.context-hub.yaml` in your project root:

```yaml
memory:
  backend: "graphiti"  # or "forgetful"
  group_id: "auto"     # auto-detect from git
```

For explicit group_id:

```yaml
memory:
  backend: "graphiti"
  group_id: "my-project"  # override auto-detection
```

### 2. Backend Setup

**For Graphiti:**
- Install and run Graphiti MCP server
- Configure in Claude Code: `claude mcp add --transport http graphiti http://localhost:8000/mcp`
- No migration needed - start fresh or sync manually

**For Forgetful:**
- Existing memories remain accessible
- Auto-creates project from group_id if needed
- No data migration required

### 3. Updated Commands

All commands now work the same way:

```
/memory-search <query>    # Uses configured backend
/memory-save              # Saves to configured backend
/memory-list [count]      # Lists from configured backend
```

### 4. Agents & Skills

- `context-retrieval` agent updated automatically
- Skills renamed: `using-forgetful-memory` → `using-memory-adapter`
- Use dynamic discovery to explore capabilities

## Backend Comparison

| Aspect | Graphiti | Forgetful |
|--------|----------|-----------|
| Setup | Docker + MCP | MCP only |
| Speed | Fast (graph DB) | Moderate (SQLite) |
| Entities | Auto-extracted | Manual |
| Search | Hybrid | Semantic |
| Best For | Large knowledge graphs | Simple memory |

## Troubleshooting

**"No backend configured"**
- Create `.context-hub.yaml` in project root
- Or set `CONTEXT_HUB_BACKEND=graphiti` env var

**"MCP tools not found"**
- Verify Graphiti/Forgetful MCP server is running
- Check `claude mcp list` shows your backend

**"Group ID detection failed"**
- Set explicit group_id in config
- Or run from git repository directory

## Rollback

To revert to Forgetful-only:

1. Set backend in config: `backend: "forgetful"`
2. Commands work as before (adapter routes to Forgetful)
