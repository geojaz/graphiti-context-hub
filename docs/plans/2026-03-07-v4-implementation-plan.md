# v4.0 Simplification & Hooks Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Simplify the plugin by removing migration remnants, fixing tool names, adding advisory hooks, and streamlining the setup flow.

**Architecture:** Single global config file created by interactive setup. All hooks are command-type (zero token cost). MCP server ships with default endpoint in servers.json; commands/skills read config at runtime for group_id.

**Tech Stack:** Shell scripts (hooks), Markdown (commands/skills/agents), JSON (plugin config)

---

### Task 1: Delete Migration Remnants

**Files:**
- Delete: `.context-hub.conf`
- Delete: `.context-hub.conf.example`
- Delete: `.context-hub.yaml`
- Delete: `.context-hub.yaml.example`
- Delete: `requirements.txt`
- Delete: `lib/` directory (and `lib/backends/`)
- Delete: `graphiti-mcp.md`
- Delete: `.claude-plugin/README.md`
- Delete: `AGENTS.md`

**Step 1: Remove files**

```bash
rm -f .context-hub.conf .context-hub.conf.example
rm -f .context-hub.yaml .context-hub.yaml.example
rm -f requirements.txt
rm -rf lib/
rm -f graphiti-mcp.md
rm -f .claude-plugin/README.md
rm -f AGENTS.md
```

**Step 2: Update .gitignore if needed**

Check `.gitignore` — remove any references to deleted files. Ensure `.context-hub.conf` is NOT in gitignore (it's gone now).

**Step 3: Commit**

```bash
git add -A
git commit -m "chore: remove migration remnants (YAML config, lib/, requirements.txt)"
```

---

### Task 2: Create Hook Scripts

**Files:**
- Create: `hooks/session-start.sh`
- Create: `hooks/context-reminder.sh`

**Step 1: Create hooks directory**

```bash
mkdir -p hooks
```

**Step 2: Write session-start.sh**

This script checks if config exists. If not, tells user to run `/context-hub-setup`.

```bash
#!/usr/bin/env bash
# Session start hook: check if graphiti-context-hub is configured
CONFIG_FILE="$HOME/.config/claude/graphiti-context-hub.conf"

if [ ! -f "$CONFIG_FILE" ]; then
    echo '{"additionalContext": "GRAPHITI NOT CONFIGURED: Run /context-hub-setup to configure your Graphiti endpoint and group_id. Memory features will not work until configured."}'
else
    source "$CONFIG_FILE"
    REPO_NAME=$(git remote get-url origin 2>/dev/null | sed 's/.*\///' | sed 's/\.git$//' || basename "$PWD")
    echo "{\"additionalContext\": \"Graphiti configured. group_id: ${GRAPHITI_GROUP_ID:-main}, repo: ${REPO_NAME}. Use mcp__graphiti__search_nodes and mcp__graphiti__search_memory_facts with group_ids: [\\\"${GRAPHITI_GROUP_ID:-main}\\\"] for all queries. Prefix episode_body with 'Repo: ${REPO_NAME}' when saving. Serena: ${SERENA_ENABLED:-false}.\"}"
fi
```

**Step 3: Write context-reminder.sh**

This script reads config and outputs appropriate additionalContext. Accepts a `$1` argument for the hook type (edit-write, plan, compact, subagent-start, subagent-stop).

```bash
#!/usr/bin/env bash
# Context reminder hook: reads config, outputs additionalContext JSON
CONFIG_FILE="$HOME/.config/claude/graphiti-context-hub.conf"
HOOK_TYPE="${1:-generic}"

# Load config
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
fi
GROUP_ID="${GRAPHITI_GROUP_ID:-main}"
SERENA="${SERENA_ENABLED:-false}"
REPO_NAME=$(git remote get-url origin 2>/dev/null | sed 's/.*\///' | sed 's/\.git$//' || basename "$PWD")

# Build Serena clause
SERENA_CLAUSE=""
if [ "$SERENA" = "true" ]; then
    SERENA_CLAUSE=" Also use Serena (get_symbols_overview, find_symbol with include_body on specific methods) to understand the structural context."
fi

case "$HOOK_TYPE" in
    edit-write)
        echo "{\"additionalContext\": \"Before modifying code: Have you queried Graphiti (search_memory_facts + search_nodes with group_ids: [\\\"${GROUP_ID}\\\"]) for prior decisions and patterns in this area?${SERENA_CLAUSE} If not, gather context first.\"}"
        ;;
    plan)
        echo "{\"additionalContext\": \"Before planning: Gather context first. (1) Query Graphiti (search_memory_facts + search_nodes with group_ids: [\\\"${GROUP_ID}\\\"]) for prior decisions and patterns. (2) Check docs/plans/ for prior design docs. (3) Check git history for recent changes.${SERENA_CLAUSE}\"}"
        ;;
    compact)
        echo "{\"additionalContext\": \"CONTEXT COMPACTION IMMINENT: Save any unsaved decisions, patterns, bug findings, or important context to Graphiti (add_memory with group_id \\\"${GROUP_ID}\\\", prefix episode_body with \\\"Repo: ${REPO_NAME}\\\"). Summarize the current task state so it survives compaction.\"}"
        ;;
    subagent-start)
        echo "{\"additionalContext\": \"SUBAGENT LAUNCHING: Save any important findings or decisions to Graphiti (add_memory with group_id \\\"${GROUP_ID}\\\", prefix episode_body with \\\"Repo: ${REPO_NAME}\\\") before handoff. The subagent will not have access to unsaved context.\"}"
        ;;
    subagent-stop)
        echo "{\"additionalContext\": \"SUBAGENT COMPLETED: Review its results. Did it discover architectural decisions, patterns, bugs, or reusable knowledge? If so, save to Graphiti (add_memory with group_id \\\"${GROUP_ID}\\\", prefix episode_body with \\\"Repo: ${REPO_NAME}\\\").\"}"
        ;;
    *)
        echo "{\"additionalContext\": \"Graphiti group_id: ${GROUP_ID}, repo: ${REPO_NAME}. Serena: ${SERENA}.\"}"
        ;;
esac
```

**Step 4: Make scripts executable**

```bash
chmod +x hooks/session-start.sh hooks/context-reminder.sh
```

**Step 5: Commit**

```bash
git add hooks/
git commit -m "feat: add hook scripts for session-start and context reminders"
```

---

### Task 3: Create hooks.json

**Files:**
- Create: `hooks/hooks.json`

**Step 1: Write hooks.json**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/session-start.sh",
            "statusMessage": "Checking Graphiti configuration..."
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/context-reminder.sh edit-write",
            "statusMessage": "Checking context gathering..."
          }
        ]
      },
      {
        "matcher": "EnterPlanMode",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/context-reminder.sh plan",
            "statusMessage": "Checking context before planning..."
          }
        ]
      }
    ],
    "PreCompact": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/context-reminder.sh compact",
            "statusMessage": "Preparing for context compaction..."
          }
        ]
      }
    ],
    "SubagentStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/context-reminder.sh subagent-start",
            "statusMessage": "Preserving context before subagent..."
          }
        ]
      }
    ],
    "SubagentStop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/context-reminder.sh subagent-stop",
            "statusMessage": "Capturing subagent findings..."
          }
        ]
      }
    ]
  }
}
```

**Step 2: Commit**

```bash
git add hooks/hooks.json
git commit -m "feat: add hooks.json for plugin hook registration"
```

---

### Task 4: Rewrite context-hub-setup.md

**Files:**
- Modify: `commands/context-hub-setup.md`

**Step 1: Rewrite the setup command**

Replace the entire file with an interactive setup flow that:
1. Asks user for Graphiti endpoint (default: `http://localhost:8000`)
2. Asks user for group_id (default: `main`)
3. Detects if Serena plugin is installed
4. Detects if Context7 plugin is installed
5. Writes `~/.config/claude/graphiti-context-hub.conf`
6. Tests Graphiti connection via `mcp__graphiti__get_status`
7. Reports status

Key changes from current:
- Remove all references to local `.context-hub.conf` override
- Remove YAML config references
- Remove `claude plugins list` / `claude mcp list` bash commands (these don't work in MCP context)
- Add interactive prompts for endpoint and group_id
- Add `SERENA_ENABLED` flag to config
- Simplify to one clear flow

New content:

```markdown
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
```

**Step 2: Commit**

```bash
git add commands/context-hub-setup.md
git commit -m "feat: rewrite context-hub-setup with interactive config flow"
```

---

### Task 5: Fix agent context-retrieval.md

**Files:**
- Modify: `agents/context-retrieval.md`

**Step 1: Fix tool name in frontmatter**

Line 4: Change `mcp__graphiti__search_facts` → `mcp__graphiti__search_memory_facts`

**Step 2: Remove config boilerplate**

Remove the bash config-loading block (lines 20-24) and the `os.environ.get` pattern. Replace with a simple note that group_id comes from the SessionStart hook context.

Replace config loading with:
```
**Configuration**: The SessionStart hook provides group_id and repo context. Use group_ids: ["main"] (or the value from hook context) for all Graphiti queries. Prefix episode_body with "Repo: {repo_name}" when saving.
```

**Step 3: Remove Forgetful-era references**

Lines 77-84: Remove references to `linked_memory_ids`, `code_artifact_ids`, `document_ids`. Replace with Graphiti-appropriate guidance:
```
**Explore the Knowledge Graph:**
- When you find a relevant node, use search_memory_facts with center_node_uuid to find connected facts
- Get episodes chronologically with get_episodes to understand evolution
- Use get_entity_edge for specific relationship details
- Don't artificially limit exploration if the connections are valuable
```

**Step 4: Fix example code blocks**

Replace `os.environ.get('GRAPHITI_GROUP_ID', 'main')` with just `"main"` (or note it comes from hook context). The examples should show direct MCP tool calls without env var wrapping.

**Step 5: Commit**

```bash
git add agents/context-retrieval.md
git commit -m "fix: update context-retrieval agent tool names and remove Forgetful references"
```

---

### Task 6: Fix using-serena-symbols skill

**Files:**
- Modify: `skills/using-serena-symbols/SKILL.md`

**Step 1: Fix Forgetful reference**

Line 194: Change `**Combine with Forgetful** - create memories for important architectural findings` to `**Combine with Graphiti** - save important architectural findings as episodes`

**Step 2: Commit**

```bash
git add skills/using-serena-symbols/SKILL.md
git commit -m "fix: replace Forgetful reference with Graphiti in using-serena-symbols"
```

---

### Task 7: Simplify config loading in commands

**Files:**
- Modify: `commands/memory-search.md`
- Modify: `commands/memory-save.md`
- Modify: `commands/memory-list.md`
- Modify: `commands/memory-explore.md`

For each file:

**Step 1: Replace config boilerplate**

Remove the multi-line bash config loading block. Replace with a simpler version that only reads the global config:

```bash
# Load config
source "$HOME/.config/claude/graphiti-context-hub.conf" 2>/dev/null
GROUP_ID="${GRAPHITI_GROUP_ID:-main}"
REPO_NAME=$(git remote get-url origin 2>/dev/null | sed 's/.*\///' | sed 's/\.git$//' || basename "$PWD")
```

This removes:
- The local `.context-hub.conf` sourcing (file no longer exists)
- Any YAML config references

**Step 2: Remove stale notes**

In memory-save.md line 85: Change `Group isolation: Memories are scoped by group_id (auto-detected from git repo)` to `Group isolation: Memories are scoped by group_id (configured in ~/.config/claude/graphiti-context-hub.conf)`

In memory-list.md line 83: Same — remove `(auto-detected from git repo)` references.

**Step 3: Commit**

```bash
git add commands/memory-search.md commands/memory-save.md commands/memory-list.md commands/memory-explore.md
git commit -m "fix: simplify config loading in memory commands, remove local config references"
```

---

### Task 8: Simplify config in skills

**Files:**
- Modify: `skills/using-graphiti-memory/SKILL.md`
- Modify: `skills/exploring-knowledge-graph/SKILL.md`
- Modify: `skills/serena-code-architecture/SKILL.md`

For each file:

**Step 1: Replace config boilerplate**

Same as Task 7 — remove local `.context-hub.conf` sourcing. Use single-line global config source.

**Step 2: In using-graphiti-memory/SKILL.md**

- Remove the "Configuration" section (lines 112-127) which documents both global and repo-level config. Replace with:
```
## Configuration

Config file: `~/.config/claude/graphiti-context-hub.conf`

```bash
GRAPHITI_GROUP_ID=main
GRAPHITI_ENDPOINT=http://localhost:8000
SERENA_ENABLED=true
```

Created by `/context-hub-setup`. Defaults: group_id=main, endpoint=localhost:8000.
```

**Step 3: Commit**

```bash
git add skills/
git commit -m "fix: simplify config references in skills, remove local config override docs"
```

---

### Task 9: Fix encode-repo-serena.md

**Files:**
- Modify: `commands/encode-repo-serena.md`

**Step 1: Fix Python import remnant**

Lines 143-149 (Phase 0, Step 3): Remove the `sys.path.insert` / `lib.config` import block. Replace with:

```bash
# Load config
source "$HOME/.config/claude/graphiti-context-hub.conf" 2>/dev/null
GROUP_ID="${GRAPHITI_GROUP_ID:-main}"
REPO_NAME=$(git remote get-url origin 2>/dev/null | sed 's/.*\///' | sed 's/\.git$//' || basename "$PWD")
```

Then the Graphiti query uses `GROUP_ID` directly.

**Step 2: Fix validation section**

Lines 1139-1176: Same fix — remove `lib.config` imports in the validation Python blocks. Replace with direct GROUP_ID usage.

**Step 3: Remove local config sourcing**

Lines 186-188: Remove `.context-hub.conf` local override sourcing.

**Step 4: Commit**

```bash
git add commands/encode-repo-serena.md
git commit -m "fix: remove lib.config imports and local config refs from encode-repo-serena"
```

---

### Task 10: Update plugin.json and servers.json

**Files:**
- Modify: `.claude-plugin/plugin.json`
- Verify: `.claude-plugin/servers.json` (may already exist from exploration, or create it)

**Step 1: Bump version**

In plugin.json, change `"version": "3.2.0"` → `"version": "4.0.0"`

**Step 2: Verify servers.json**

Ensure `.claude-plugin/servers.json` exists with:

```json
{
  "mcpServers": {
    "graphiti": {
      "url": "http://localhost:8000/mcp",
      "transport": "http"
    }
  }
}
```

This is the default — users who configure a different endpoint will still need to update this or the setup command should handle it.

**Step 3: Commit**

```bash
git add .claude-plugin/
git commit -m "chore: bump version to 4.0.0"
```

---

### Task 11: Rewrite README.md

**Files:**
- Modify: `README.md`

**Step 1: Rewrite to reflect v4.0 state**

Key changes:
- Remove all YAML config references
- Remove local `.context-hub.conf` override documentation
- Add hooks documentation section
- Update setup flow to mention interactive prompts
- Remove `.context-hub.yaml` reference in "Custom endpoint" section
- Update architecture diagram to include `hooks/` directory
- Fix any Forgetful references
- Mention that hooks are bundled and automatic

New structure:
1. Title + description
2. Installation
3. Setup (just run `/context-hub-setup`)
4. Configuration (single file at `~/.config/claude/...`)
5. Commands table
6. Skills table
7. Hooks (new section — explain what they do)
8. How It Works (streamlined)
9. Architecture diagram (add hooks/)
10. License

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: rewrite README for v4.0 simplified architecture"
```

---

### Task 12: Verify and Test

**Step 1: Check for any remaining references to removed files**

```bash
grep -r "context-hub.conf.example\|context-hub.yaml\|requirements.txt\|lib/config\|lib\.config\|lib/backends\|AGENTS.md\|forgetful\|Forgetful" --include="*.md" --include="*.json" .
```

Fix any remaining references found.

**Step 2: Check for wrong tool names**

```bash
grep -r "search_facts\b" --include="*.md" .
```

Should find zero results (all should be `search_memory_facts`).

```bash
grep -r "mcp__graphiti__" --include="*.md" . | grep -v "add_memory\|search_nodes\|search_memory_facts\|get_episodes\|get_entity_edge\|get_status\|delete_episode\|delete_entity_edge\|clear_graph"
```

Should find zero results (no invented tool names).

**Step 3: Commit any fixes**

```bash
git add -A
git commit -m "fix: clean up remaining stale references"
```

---

## Execution Notes

- Tasks 1-3 are independent foundation work (cleanup + hooks)
- Tasks 4-9 are the content updates (can be parallelized)
- Task 10-11 are packaging (depend on content being stable)
- Task 12 is final verification (must run last)

## Post-Implementation

After all tasks complete:
- Test `/context-hub-setup` flow end-to-end
- Verify hooks fire correctly (SessionStart, PreToolUse, etc.)
- Run `/memory-search` to verify Graphiti integration still works
- Consider running `/encode-repo-serena` on this repo to update its own knowledge graph entry
