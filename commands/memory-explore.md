---
description: Deep exploration of the knowledge graph
---

# Memory Explore

Traverse the Graphiti knowledge graph from a starting point to discover connected concepts.

## Your Task

Explore the knowledge graph starting from: **$ARGUMENTS**

## Implementation

**Step 1: Load config**

```bash
# Load config
source "$HOME/.config/claude/graphiti-context-hub.conf" 2>/dev/null
GROUP_ID="${GRAPHITI_GROUP_ID:-main}"
REPO_NAME=$(git remote get-url origin 2>/dev/null | sed 's/.*\///' | sed 's/\.git$//' || basename "$PWD")

echo "Exploring group: $GROUP_ID"
echo "Current repo: $REPO_NAME"
```

**Step 2: Explore graph from starting point**

```python
query = "$ARGUMENTS"

# First, find the starting node
node_result = mcp__graphiti__search_nodes({
    "query": query,
    "group_ids": [GROUP_ID],
    "max_nodes": 1
})

nodes = node_result.get('nodes', [])
if not nodes:
    print(f"No starting node found for: {query}")
    print("Try a different search term or use /memory-search to find concepts first.")
    exit(0)

starting_node = nodes[0]
center_node_uuid = starting_node.get('uuid')

print(f"Starting from: {starting_node.get('name', 'Unknown')}")
print(f"Summary: {starting_node.get('summary', '')[:150]}...\n")

# Now explore facts around this node
facts_result = mcp__graphiti__search_memory_facts({
    "query": query,
    "group_ids": [GROUP_ID],
    "center_node_uuid": center_node_uuid,
    "max_facts": 20
})

# Display discovered relationships
facts = facts_result.get('facts', [])
print(f"Discovered {len(facts)} related facts:\n")

for i, fact in enumerate(facts, 1):
    fact_text = fact.get('fact', '')
    # Extract relationship info if available
    source = fact.get('source_node', {}).get('name', '')
    target = fact.get('target_node', {}).get('name', '')

    print(f"{i}. {fact_text}")
    if source and target:
        print(f"   {source} → {target}")
    print()

# Also show connected nodes
connected_nodes = set()
for fact in facts:
    if 'source_node' in fact:
        connected_nodes.add(fact['source_node'].get('name', ''))
    if 'target_node' in fact:
        connected_nodes.add(fact['target_node'].get('name', ''))

connected_nodes.discard('')  # Remove empty names
connected_nodes.discard(starting_node.get('name', ''))  # Remove starting node

if connected_nodes:
    print(f"\nConnected concepts ({len(connected_nodes)}):")
    for node_name in sorted(connected_nodes)[:10]:
        print(f"  - {node_name}")
```

## Response Format

Present exploration results with:
1. Starting node (name and summary)
2. Number of facts discovered
3. List of facts/relationships
4. Connected concepts discovered

Example:
```
Using group_id: context-hub-plugin

Starting from: Authentication Service
Summary: Handles JWT validation, user sessions, and OAuth flows for the API...

Discovered 8 related facts:

1. AuthService depends on Redis for session storage
   AuthService → Redis

2. All API endpoints require authentication via middleware
   API Endpoints → AuthService

3. JWT tokens use httponly cookies for XSS protection
   AuthService → JWT Configuration

Connected concepts (5):
  - Redis
  - JWT Configuration
  - API Endpoints
  - User Sessions
  - OAuth Provider
```

## Notes

- **No adapter layer**: Calls Graphiti MCP directly
- **Two-step process**: First find starting node, then explore facts around it
- **Center node search**: Uses center_node_uuid to focus exploration
- **Graph traversal**: Graphiti's search_memory_facts does native graph traversal
- **Relationship discovery**: Automatically finds connections between concepts
