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
    prompt-submit)
        echo "{\"additionalContext\": \"REQUIRED: Before starting any task, you MUST run /context_gather with keywords from the user's request. Do this BEFORE reading files, running commands, or invoking other skills. This retrieves prior decisions, patterns, and relevant context from the knowledge graph and documentation sources. After completing work, use /memory-save to capture important decisions and findings. Repo: ${REPO_NAME}, group_id: ${GROUP_ID}.\"}"
        ;;
    edit-write)
        echo "{\"additionalContext\": \"Before modifying code: Have you queried Graphiti (search_memory_facts + search_nodes with group_ids: [\\\"${GROUP_ID}\\\"]) for prior decisions and patterns in this area?${SERENA_CLAUSE} If not, use /context_gather first.\"}"
        ;;
    plan)
        echo "{\"additionalContext\": \"Before planning: Gather context first. (1) Use /context_gather or query Graphiti (search_memory_facts + search_nodes with group_ids: [\\\"${GROUP_ID}\\\"]) for prior decisions and patterns. (2) Check docs/plans/ for prior design docs. (3) Check git history for recent changes.${SERENA_CLAUSE}\"}"
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
