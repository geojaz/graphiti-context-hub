---
description: Configure Graphiti MCP backend and plugin prerequisites
---

# Context Hub Setup

You MUST follow these steps in order. Do NOT summarize — execute each step interactively.

## Step 1: Collect Configuration

You MUST ask the user these questions before proceeding. Wait for their answers.

**Question 1:** "What is your Graphiti MCP endpoint URL? (default: `http://localhost:8000/mcp/`)"
- Examples: `http://localhost:8000/mcp/`, `https://graphiti-mcp-xyz.a.run.app/mcp/`

**Question 2:** "Does your endpoint require authentication? If so, what kind?"
- None (default for local)
- GCP Identity Token (`gcloud auth print-identity-token`)
- Bearer token (static)
- Other

**Question 3:** "What group_id should I use for your knowledge graph? (default: `main`)"

Store their answers for use in later steps.

## Step 2: Detect Companion Plugins

Run these checks NOW and report what you find:

1. **Serena:** Call `mcp__plugin_serena_serena__get_current_config`. Report whether it succeeded.
2. **Context7:** Call `mcp__plugin_context7_context7__resolve-library-id` with query "test". Report whether it succeeded.

Tell the user which companions were detected.

## Step 3: Write MCP Wrapper Script

The plugin ships with `bin/graphiti-mcp.sh` which is a stdio wrapper that proxies to the remote endpoint via `npx mcp-remote`. Update it NOW based on the user's answers from Step 1.

Find the plugin root path:
```bash
# The script lives at ${CLAUDE_PLUGIN_ROOT}/bin/graphiti-mcp.sh
# Find actual path by checking where the plugin is installed
PLUGIN_ROOT=$(dirname "$(dirname "$(readlink -f "$(which graphiti-mcp.sh 2>/dev/null)" 2>/dev/null)")" 2>/dev/null)
```

If you cannot determine the plugin root, search for it:
```bash
find ~/.claude/plugins/cache -path "*/graphiti-context-hub/*/bin/graphiti-mcp.sh" 2>/dev/null | sort -V | tail -1
```

Write the script content based on auth type:

**No auth (local):**
```bash
#!/bin/bash
exec npx mcp-remote "{endpoint_url}"
```

**GCP Identity Token:**
```bash
#!/bin/bash
TOKEN=$(gcloud auth print-identity-token)
exec npx mcp-remote "{endpoint_url}" \
  --header "Authorization:Bearer ${TOKEN}"
```

**Static Bearer token:**
```bash
#!/bin/bash
exec npx mcp-remote "{endpoint_url}" \
  --header "Authorization:Bearer {token}"
```

Make sure the script is executable: `chmod +x <path>`

After writing, tell the user: "Updated MCP wrapper script. You'll need to `/reload-plugins` for the new endpoint to take effect."

## Step 4: Write Hook Configuration

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

## Step 5: Test Connection

Tell the user to run `/reload-plugins` to pick up the new MCP script.

Then call `mcp__graphiti__get_status()` to verify connectivity.

If it fails, show this and STOP:
```
Connection to Graphiti failed.

Troubleshooting:
1. Ensure Graphiti MCP server is running at {endpoint}
2. Test manually: curl {endpoint}/health
3. Check the wrapper script: find ~/.claude/plugins/cache -path "*/graphiti-context-hub/*/bin/graphiti-mcp.sh" | tail -1
4. Re-run /context-hub-setup to reconfigure
```

## Step 6: Report Results

Show this summary with the actual values filled in:

```
✓ Setup Complete

  Endpoint:  {endpoint}
  Auth:      {auth_type}
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
