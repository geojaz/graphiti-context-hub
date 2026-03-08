---
description: Configure Graphiti MCP backend and plugin prerequisites
---

# Context Hub Setup

You MUST follow these steps in order. Do NOT summarize — execute each step interactively.

## Step 1: Collect Configuration

You MUST ask the user this question before proceeding. Wait for their answer.

**Question:** "What group_id should I use for your knowledge graph? (default: `main`)"

Note: The Graphiti MCP endpoint is configured in the plugin's `.mcp.json` file, not here.
Store the group_id for use in later steps.

## Step 2: Detect Companion Plugins

Run these checks NOW and report what you find:

1. **Serena:** Call `mcp__plugin_serena_serena__get_current_config`. Report whether it succeeded.
2. **Context7:** Call `mcp__plugin_context7_context7__resolve-library-id` with query "test". Report whether it succeeded.

Tell the user which companions were detected.

## Step 3: Test Graphiti Connection

Call `mcp__graphiti__get_status()` to verify the Graphiti MCP server is reachable.

If it fails, show this and STOP:
```
Connection to Graphiti failed.

Troubleshooting:
1. Ensure Graphiti MCP server is running (check the URL in plugin .mcp.json)
2. Test manually: curl http://localhost:8000/health
3. Check the Graphiti documentation: https://github.com/getzep/graphiti
4. Update the endpoint in the plugin's .mcp.json if needed
```

## Step 4: Write Configuration

This conf file is sourced by the plugin's hooks to inject group_id and companion status into prompts.

Run this bash command (substitute the user's values):

```bash
mkdir -p "$HOME/.config/claude"

cat > "$HOME/.config/claude/graphiti-context-hub.conf" << EOF
# Graphiti Context Hub Configuration
# Created by /context-hub-setup
# Sourced by plugin hooks (session-start.sh, context-reminder.sh)
GRAPHITI_GROUP_ID={user_group_id}
SERENA_ENABLED={true_or_false}
EOF

echo "Configuration saved to ~/.config/claude/graphiti-context-hub.conf"
```

## Step 5: Report Results

Show this summary with the actual values filled in:

```
✓ Setup Complete

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
