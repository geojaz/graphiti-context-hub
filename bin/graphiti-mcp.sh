#!/bin/bash
# Graphiti MCP stdio wrapper
# Handles auth and proxies to the remote Graphiti MCP endpoint via mcp-remote
# Updated by /context-hub-setup

GRAPHITI_MCP_URL="${GRAPHITI_MCP_URL:-http://localhost:8000/mcp/}"

exec npx mcp-remote "$GRAPHITI_MCP_URL"
