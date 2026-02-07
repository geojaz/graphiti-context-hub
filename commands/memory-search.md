---
description: Search memories semantically using the memory adapter
---

# Memory Search

Search the knowledge base for relevant memories using the configured backend (Graphiti or Forgetful).

## Your Task

Use the memory adapter's `query` operation to search for memories.

**Query**: $ARGUMENTS

## Implementation

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'lib'))

from bridge import memory_query, memory_get_config

# Show current config
config = memory_get_config()
print(f"Using backend: {config['backend']}, group: {config['group_id']}\n")

# Search
query = "$ARGUMENTS"
results = memory_query(query, limit=10)

# Display results
print(f"Found {len(results)} memories:\n")
for i, memory in enumerate(results, 1):
    title = memory['metadata'].get('title', memory['content'][:50])
    print(f"{i}. {title}")
    print(f"   {memory['content'][:100]}...")
    print(f"   Created: {memory['created_at'][:10]}")
    if memory.get('importance'):
        print(f"   Importance: {memory['importance']}")
    print()
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
