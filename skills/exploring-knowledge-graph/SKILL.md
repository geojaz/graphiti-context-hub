---
name: exploring-knowledge-graph
description: Use when user asks "what do you know about X", when planning complex work that spans multiple topics, when investigating how concepts connect across projects, or when simple memory queries don't provide enough context. Deep traversal of Forgetful MCP knowledge graph (mcp__forgetful__* tools).
---

# Exploring the Knowledge Graph

Use the memory adapter's `explore()` operation for deep traversal.

## How to Explore

```python
from bridge import memory_explore

graph = memory_explore("authentication", depth=2)

# Returns:
# {
#   'nodes': [{id, content, metadata}, ...],
#   'edges': [{source, target, type}, ...]
# }
```

## Backend Behavior

- **Graphiti**: Native graph traversal via search_facts
- **Forgetful**: Manual BFS via linked_memory_ids

Both return same structure for consistent exploration.
