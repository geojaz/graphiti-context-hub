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
