# Memory Adapter Bridge Reference

Complete reference for memory operations using the Context Hub bridge. Works with **both Graphiti and Forgetful backends**.

**Use this for:** All standard memory operations (query, save, list, explore)
**Use FORGETFUL_TOOLS.md for:** Advanced Forgetful-only features (entities, relationships, projects, curation)

---

## Getting Started

All bridge functions are imported from the `bridge` module:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'lib'))

from bridge import (
    memory_query,
    memory_save,
    memory_list_recent,
    memory_explore,
    memory_search_facts,
    memory_get_config,
    memory_list_operations
)
```

---

## Configuration

### memory_get_config()

Get current backend and group_id.

**Returns:** `{'backend': 'graphiti'|'forgetful', 'group_id': 'project-name'}`

```python
config = memory_get_config()
print(f"Backend: {config['backend']}, Group: {config['group_id']}")
```

---

## Core Operations

### memory_query(query, limit=10)

Semantic search across memories.

**Parameters:**
- `query` (str): Natural language search query
- `limit` (int): Maximum results to return (default 10)

**Returns:** List of memory dictionaries with `id`, `content`, `created_at`, `importance`, `metadata`

```python
results = memory_query("authentication patterns", limit=5)

for memory in results:
    print(f"{memory['id']}: {memory['content'][:100]}")
    print(f"Created: {memory['created_at']}")
    if memory.get('importance'):
        print(f"Importance: {memory['importance']}")
```

---

### memory_save(content, **metadata)

Save new memory/episode to knowledge base.

**Parameters:**
- `content` (str): Memory content (main text)
- `**metadata`: Backend-specific metadata
  - `title` (str): Memory title (both backends)
  - `importance` (int): 1-10 importance (Forgetful only, ignored by Graphiti)
  - `keywords` (list): Search keywords (Forgetful only)
  - `tags` (list): Categorization tags (Forgetful only)
  - `source` (str): Content source (Graphiti only)
  - `source_description` (str): Source description (Graphiti only)

**Returns:** Memory/episode ID (str)

**Graphiti example:**
```python
memory_id = memory_save(
    content="Decision: Using JWT tokens for authentication with httponly cookies...",
    title="Auth Decision - JWT",
    source="architectural-decision",
    source_description="Security architecture discussion"
)
```

**Forgetful example:**
```python
memory_id = memory_save(
    content="Decision: Using JWT tokens for authentication with httponly cookies...",
    title="Auth Decision - JWT",
    importance=9,
    keywords=["auth", "jwt", "security"],
    tags=["decision", "security"]
)
```

---

### memory_list_recent(limit=20)

List recent memories in chronological order.

**Parameters:**
- `limit` (int): Maximum results to return (default 20)

**Returns:** List of memory dictionaries (same format as `memory_query`)

```python
recent = memory_list_recent(limit=10)

print(f"Found {len(recent)} recent memories:\n")
for i, memory in enumerate(recent, 1):
    title = memory['metadata'].get('title', memory['content'][:50])
    print(f"{i}. {title}")
    print(f"   Created: {memory['created_at'][:10]}")
```

---

### memory_explore(starting_point, depth=2)

Deep knowledge graph traversal from a starting query.

**Parameters:**
- `starting_point` (str): Query to find initial nodes
- `depth` (int): How many relationship hops to traverse (default 2)

**Returns:** Dictionary with `nodes` and `edges` lists

```python
graph = memory_explore("authentication", depth=2)

print(f"Found {len(graph['nodes'])} connected memories")
print(f"Found {len(graph['edges'])} relationships\n")

# Display nodes
for node in graph['nodes']:
    print(f"- {node['content'][:60]}...")

# Display relationships
for edge in graph['edges']:
    print(f"{edge['source']} --[{edge['type']}]--> {edge['target']}")
```

---

### memory_search_facts(query, limit=10)

Search for relationships between entities (Graphiti-optimized, basic support in Forgetful).

**Parameters:**
- `query` (str): Search query for relationships
- `limit` (int): Maximum results to return (default 10)

**Returns:** List of relationship dictionaries with `source`, `target`, `type`, `metadata`

```python
relationships = memory_search_facts("authentication flow", limit=20)

for rel in relationships:
    print(f"{rel['source']} → {rel['target']}")
    print(f"   Type: {rel['type']}")
```

---

### memory_list_operations()

Discover available operations for the current backend.

**Returns:** List of operation info dictionaries with `name`, `description`, `params`, `example`

```python
ops = memory_list_operations()

print("Available operations:")
for op in ops:
    print(f"- {op['name']}: {op['description']}")
    print(f"  Example: {op['example']}")
```

---

## Backend Differences

| Feature | Graphiti | Forgetful |
|---------|----------|-----------|
| **Entity extraction** | Automatic from content | Manual via separate tools |
| **Relationship discovery** | Auto via facts | Manual linking required |
| **Importance scoring** | Inferred automatically | Explicit 1-10 scale |
| **Tags/Keywords** | Not used | Used for categorization |
| **Graph traversal** | Native graph operations | BFS via linked_memory_ids |
| **Search** | Hybrid (semantic + graph) | Pure semantic |

---

## Error Handling

All bridge functions require MCP tools to be available. If called from outside Claude Code's execution context (e.g., via Bash subprocess), you'll get:

```
RuntimeError: Graphiti MCP tools are not available in this execution context.

The memory adapter can only be used when Python code is executed by Claude Code
directly (e.g., via commands or skills).
```

**Solution:** Use these functions only in:
- Command files (e.g., `commands/memory-search.md`)
- Skill implementations
- Python blocks executed by Claude Code

**Do NOT use in:**
- Bash subprocess Python scripts
- External Python scripts

---

## Advanced: Backend-Specific Features

For advanced features only available in Forgetful:
- Entity management
- Project organization
- Document storage
- Code artifacts
- Memory curation (mark obsolete, explicit linking)
- Entity relationships

See **FORGETFUL_TOOLS.md** for the complete Forgetful-specific API.
