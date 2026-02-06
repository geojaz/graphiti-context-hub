---
name: using-memory-adapter
description: When to query and save memories using the pluggable memory adapter (Graphiti or Forgetful). PROACTIVELY query before starting work. Save important decisions and patterns.
allowed-tools: Read, Glob, Grep
---

# Using the Memory Adapter

## When to Use

**Query PROACTIVELY:**
- ✅ Before implementing ANY feature
- ✅ When user mentions past work or patterns
- ✅ When architecting new components
- ✅ Before making technical decisions

**Save Immediately After:**
- ✅ Making architectural decisions
- ✅ Discovering reusable patterns
- ✅ Learning from bugs/issues
- ✅ Receiving user preferences

## How to Query

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'lib'))

from bridge import memory_query, memory_get_config

# Check backend
config = memory_get_config()
# Returns: {'backend': 'graphiti', 'group_id': 'agent-context'}

# Search
results = memory_query("authentication patterns", limit=10)
```

## How to Save

```python
from bridge import memory_save

memory_id = memory_save(
    content="Decision: Using JWT...",
    title="Auth Decision",
    importance=9,  # Forgetful only, ignored by Graphiti
    tags=["security", "decision"]
)
```

## Backend Differences

| Feature | Graphiti | Forgetful |
|---------|----------|-----------|
| Entity extraction | Automatic | Manual |
| Importance | Inferred | Explicit (1-10) |
| Linking | Auto via facts | Manual via IDs |
| Search | Hybrid (semantic + graph) | Semantic only |

## Configuration

Backend is selected via `.context-hub.yaml`:

```yaml
memory:
  backend: "graphiti"  # or "forgetful"
  group_id: "auto"     # or explicit name
```

Group ID is auto-detected from git repository name.
