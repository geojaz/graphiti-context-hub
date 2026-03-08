---
description: List recent memories from the knowledge base
---

# Memory List

List recent episodes from Graphiti to see what context has been saved.

## Your Task

List recent memories for the current project.

## Implementation

**Step 1: Load config**

```bash
# Load config
source "$HOME/.config/claude/graphiti-context-hub.conf" 2>/dev/null
GROUP_ID="${GRAPHITI_GROUP_ID:-main}"
echo "Listing episodes from group: $GROUP_ID"
```

**Step 2: List recent episodes from Graphiti**

```python
# Get count from user input or default to 20
limit = int("$ARGUMENTS") if "$ARGUMENTS".strip().isdigit() else 20

# Call Graphiti MCP tool directly
result = mcp__graphiti__get_episodes({
    "group_ids": [GROUP_ID],
    "max_episodes": limit
})

# Display results
episodes = result.get('episodes', [])
print(f"Found {len(episodes)} recent episodes:\n")

for i, episode in enumerate(episodes, 1):
    name = episode.get('name', 'Untitled')
    content = episode.get('content', '')
    created = episode.get('created_at', '')[:19]  # YYYY-MM-DD HH:MM:SS

    print(f"{i}. {name}")
    # Show first 100 chars of content as preview
    preview = content[:100] + '...' if len(content) > 100 else content
    if preview:
        print(f"   {preview}")
    print(f"   Created: {created}")
    print()
```

## Response Format

Show episodes in chronological order (newest first) with:
- Episode name/title
- Content preview (first 100 chars)
- Creation timestamp

Example:
```
Using group_id: context-hub-plugin

Found 5 recent episodes:

1. Implemented Graphiti Backend
   Replaced Forgetful backend with Graphiti for graph-based memory storage...
   Created: 2024-03-15 14:30:22

2. Updated Memory Commands
   Refactored memory-search, memory-save, memory-list to use Graphiti MCP...
   Created: 2024-03-15 13:15:10
```

## Notes

- **No adapter layer**: Calls Graphiti MCP directly
- **Episodes vs Nodes**: This lists raw episodes (saved memories), not extracted entities
- **Group isolation**: Memories are scoped by group_id (configured in ~/.config/claude/graphiti-context-hub.conf)
- **Default limit**: Shows 20 most recent if no argument provided
