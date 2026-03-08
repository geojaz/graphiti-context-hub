---
description: Configure Graphiti MCP backend and plugin prerequisites
---

# Context Hub Setup

Configure Graphiti Context Hub with your endpoint and preferences.

## Step 1: Collect Configuration

Ask the user for the following (provide defaults):

1. **Graphiti endpoint** — Where is your Graphiti MCP server?
   - Default: `http://localhost:8000`
   - Examples: `http://localhost:8000`, `https://graphiti.example.com`

2. **Group ID** — Identifier for your knowledge graph
   - Default: `main`
   - All memories are stored under this group_id
   - Repo context is preserved via automatic `Repo: {name}` tagging in episodes

## Step 2: Detect Plugins

Check which companion plugins are available by attempting to use their tools:

**Serena check:** Try calling `mcp__plugin_serena_serena__get_current_config`. If it succeeds, Serena is available.

**Context7 check:** Try calling `mcp__plugin_context7_context7__resolve-library-id` with a test query. If it succeeds, Context7 is available.

Report findings to user.

## Step 3: Write Configuration

Create the global config file:

```bash
mkdir -p "$HOME/.config/claude"

cat > "$HOME/.config/claude/graphiti-context-hub.conf" << EOF
# Graphiti Context Hub Configuration
# Created by /context-hub-setup
GRAPHITI_GROUP_ID={user_group_id}
GRAPHITI_ENDPOINT={user_endpoint}
SERENA_ENABLED={true_or_false}
EOF

echo "Configuration saved to ~/.config/claude/graphiti-context-hub.conf"
```

## Step 4: Test Connection

Test Graphiti connectivity:

```
result = mcp__graphiti__get_status()
```

If successful, report:
```
Setup Complete

  Endpoint:  {endpoint}
  Group ID:  {group_id}
  Serena:    {enabled/not found}
  Context7:  {enabled/not found}
  Graphiti:  Connected

Available commands:
  /context_gather <task>  - Multi-source context retrieval
  /memory-search <query>  - Search knowledge graph
  /memory-list [count]    - List recent episodes
  /memory-save            - Save context as episode
  /memory-explore <query> - Deep graph traversal
  /encode-repo-serena     - Bootstrap repo (requires Serena)
```

If connection fails, provide troubleshooting:
```
Connection to Graphiti failed.

Troubleshooting:
1. Ensure Graphiti MCP server is running at {endpoint}
2. Test manually: curl {endpoint}/health
3. Check the Graphiti documentation: https://github.com/getzep/graphiti
4. Re-run /context-hub-setup with a different endpoint
```

## Troubleshooting

### Graphiti Connection Issues
- Verify server is running: `curl http://localhost:8000/health`
- Check that the Graphiti MCP server is properly started
- Review Claude Code logs for MCP errors

### Plugin Issues
- Serena not found: `claude plugins install serena`
- Context7 not found: `claude plugins install context7 --marketplace pleaseai/claude-code-plugins`

### Configuration Issues
- Config file location: `~/.config/claude/graphiti-context-hub.conf`
- Re-run `/context-hub-setup` to recreate
- Check file permissions
