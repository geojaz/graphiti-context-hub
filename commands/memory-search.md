---
description: Search Graphiti knowledge graph semantically
---

# Memory Search

Search the knowledge graph for relevant memories using Graphiti.

## Your Task

Search Graphiti for: **$ARGUMENTS**

## Implementation

**Step 1: Load config and detect repo**

```bash
# Load config
source "$HOME/.config/claude/graphiti-context-hub.conf" 2>/dev/null
GROUP_ID="${GRAPHITI_GROUP_ID:-main}"

# Detect repo name
if git remote get-url origin &>/dev/null; then
    REPO_NAME=$(git remote get-url origin | sed 's/.*\///' | sed 's/\.git$//')
else
    REPO_NAME=$(basename "$PWD")
fi

echo "Searching in group_id: $GROUP_ID"
echo "Current repo: $REPO_NAME"
echo ""
```

**Step 2: Search Graphiti**

Using the GROUP_ID from Step 1, search the knowledge graph:

```python
query = "$ARGUMENTS"

# GROUP_ID comes from Bash output above
result = mcp__graphiti__search_nodes({
    "query": query,
    "group_ids": [GROUP_ID],  # Now always "main"
    "max_nodes": 10
})

# Display results
nodes = result.get('nodes', [])
print(f"Found {len(nodes)} memories:\n")

for i, node in enumerate(nodes, 1):
    name = node.get('name', 'Untitled')
    summary = node.get('summary', '')
    created = node.get('created_at', '')[:10]

    print(f"{i}. {name}")
    if summary:
        print(f"   {summary[:150]}...")
    print(f"   Created: {created}")
    print()
```

## Response Format

Present results clearly with:
1. Group ID being searched
2. Number of results found
3. For each memory: title, summary snippet, creation date
4. Suggestions to refine search if needed
