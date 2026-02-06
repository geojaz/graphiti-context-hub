---
description: Search memories semantically using the memory adapter
---

# Memory Search

Search the knowledge base for relevant memories using the configured backend (Graphiti or Forgetful).

## Your Task

Use the memory adapter's `query` operation to search for memories.

**Query**: $ARGUMENTS

## Implementation

You have two options for searching:

### Option A: Direct Python (if available)
If you can execute Python in this context:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'lib'))

from bridge import memory_query, memory_get_config

# Show current config
config = memory_get_config()
print(f"Using backend: {config['backend']}, group: {config['group_id']}")

# Search
results = memory_query("$ARGUMENTS", limit=10)

# Display results
print(f"\nFound {len(results)} memories:\n")
for i, memory in enumerate(results, 1):
    print(f"{i}. {memory['metadata'].get('title', 'Untitled')}")
    print(f"   {memory['content'][:100]}...")
    if memory.get('importance'):
        print(f"   Importance: {memory['importance']}")
    print()
```

### Option B: MCP Tool Pattern (fallback)
If Python execution isn't available, use the backend MCP tools directly based on config:

**For Graphiti backend:**
```
mcp__graphiti__search_nodes({
  "query": "$ARGUMENTS",
  "group_ids": ["<detected-group-id>"],
  "max_nodes": 10
})
```

**For Forgetful backend:**
```
mcp__forgetful__execute_forgetful_tool("query_memory", {
  "query": "$ARGUMENTS",
  "k": 10,
  "include_links": true
})
```

## Response Format

Present results clearly:

1. **Summary**: Brief overview of what was found
2. **Memories**: For each result:
   - Title/summary
   - Content snippet (100 chars)
   - Relevance indicators (importance, tags, dates)
3. **Suggestions**: Help refine search if needed

## Example

User: `/memory-search authentication patterns`

You respond:
```
Using backend: graphiti, group: agent-context

Found 3 memories:

1. FastAPI JWT Authentication
   JWT middleware using httponly cookies for security...
   Created: 2026-01-15

2. OAuth2 Decision
   Chose OAuth2 over API keys for user-facing auth...
   Created: 2026-01-10

3. Session Management
   Redis-based session store with 24h expiration...
   Created: 2026-01-08
```
