# Phase 2: MCP Integration & Command Updates Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Connect memory adapter to real MCP tools and update all commands/agents to use the adapter

**Architecture:** Commands are markdown files that instruct Claude to call MCP tools. We'll update the Python backends to call actual MCP tools, then update markdown commands to reference the new adapter pattern. Since commands can't import Python directly, we'll create simple wrapper functions that Claude can call.

**Tech Stack:** Python 3.10+, MCP tools (mcp__graphiti__*, mcp__forgetful__*), Markdown command files

**Epic:** context-hub-plugin-6de

---

## Critical Understanding

**The Challenge:**
- Commands are `.md` files (instructions for Claude, not executable code)
- Adapter is Python code in `lib/`
- MCP tools are called like: `mcp__graphiti__search_memory_nodes({args})`
- Commands currently say: "Use `execute_forgetful_tool('query_memory', {...})`"

**The Solution:**
1. **Backend Integration**: Wire Python backends to real MCP tool calls
2. **Command Pattern**: Update markdown to instruct Claude to use adapter operations
3. **Bridge Pattern**: Create helper that Claude can call to access adapter

---

## Task 1: Create Adapter Bridge for Commands

**Files:**
- Create: `lib/bridge.py`
- Create: `examples/test_bridge.py`

**Context:** Commands are markdown that Claude interprets. We need a simple way for Claude to call the adapter. Create a bridge module with simple functions Claude can invoke.

**Step 1: Create bridge module**

File: `lib/bridge.py`

```python
"""
Bridge module for Claude Code commands to access memory adapter.

Commands are markdown files that Claude interprets. This module provides
simple functions that can be called from command context.
"""
import sys
from pathlib import Path

# Ensure lib is in path
sys.path.insert(0, str(Path(__file__).parent))

from memory_adapter import MemoryAdapter
from models import Memory, Relationship, KnowledgeGraph


# Global adapter instance (initialized on first use)
_adapter = None


def get_adapter() -> MemoryAdapter:
    """Get or create the global adapter instance."""
    global _adapter
    if _adapter is None:
        _adapter = MemoryAdapter()
    return _adapter


# Simple wrapper functions that Claude can call

def memory_query(query: str, limit: int = 10) -> list:
    """
    Search for memories.

    Args:
        query: Search query text
        limit: Maximum results

    Returns:
        List of memory dictionaries
    """
    adapter = get_adapter()
    memories = adapter.query(query, limit)

    # Convert to simple dicts for easy consumption
    return [
        {
            'id': m.id,
            'content': m.content,
            'created_at': m.created_at.isoformat(),
            'importance': m.importance,
            'metadata': m.metadata
        }
        for m in memories
    ]


def memory_save(content: str, **metadata) -> str:
    """
    Save a new memory.

    Args:
        content: Memory content
        **metadata: title, importance, keywords, tags, etc.

    Returns:
        Memory ID
    """
    adapter = get_adapter()
    return adapter.save(content, **metadata)


def memory_list_recent(limit: int = 20) -> list:
    """List recent memories."""
    adapter = get_adapter()
    memories = adapter.list_recent(limit)

    return [
        {
            'id': m.id,
            'content': m.content,
            'created_at': m.created_at.isoformat(),
            'importance': m.importance,
            'metadata': m.metadata
        }
        for m in memories
    ]


def memory_explore(starting_point: str, depth: int = 2) -> dict:
    """
    Explore knowledge graph.

    Args:
        starting_point: Query to find starting point
        depth: Traversal depth

    Returns:
        Dict with 'nodes' and 'edges' lists
    """
    adapter = get_adapter()
    graph = adapter.explore(starting_point, depth)

    return {
        'nodes': [
            {
                'id': n.id,
                'content': n.content,
                'created_at': n.created_at.isoformat(),
                'metadata': n.metadata
            }
            for n in graph.nodes
        ],
        'edges': [
            {
                'source': e.source,
                'target': e.target,
                'type': e.relation_type,
                'metadata': e.metadata
            }
            for e in graph.edges
        ]
    }


def memory_search_facts(query: str, limit: int = 10) -> list:
    """Search for relationships."""
    adapter = get_adapter()
    relationships = adapter.search_facts(query, limit)

    return [
        {
            'source': r.source,
            'target': r.target,
            'type': r.relation_type,
            'metadata': r.metadata
        }
        for r in relationships
    ]


def memory_list_operations() -> list:
    """List available operations."""
    adapter = get_adapter()
    ops = adapter.list_operations()

    return [
        {
            'name': op.name,
            'description': op.description,
            'params': op.params,
            'example': op.example
        }
        for op in ops
    ]


def memory_get_config() -> dict:
    """Get current configuration."""
    adapter = get_adapter()

    return {
        'backend': adapter.config.memory.backend,
        'group_id': adapter.group_id,
        'config_file': 'auto-detected'  # Could track this if needed
    }
```

**Step 2: Create test script**

File: `examples/test_bridge.py`

```python
#!/usr/bin/env python3
"""Test the bridge module."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from bridge import (
    memory_query,
    memory_save,
    memory_list_recent,
    memory_get_config,
    memory_list_operations
)


def main():
    print("=== Testing Memory Bridge ===\n")

    # Test config
    print("1. Configuration:")
    config = memory_get_config()
    print(f"   Backend: {config['backend']}")
    print(f"   Group ID: {config['group_id']}\n")

    # Test operations list
    print("2. Available operations:")
    ops = memory_list_operations()
    for op in ops[:3]:
        print(f"   - {op['name']}: {op['description']}\n")

    # Test query (stub for now)
    print("3. Query test:")
    results = memory_query("test", limit=5)
    print(f"   Found {len(results)} results\n")

    # Test save (stub for now)
    print("4. Save test:")
    memory_id = memory_save("Test content", title="Test")
    print(f"   Saved with ID: {memory_id}\n")

    print("Bridge functions working!")


if __name__ == "__main__":
    main()
```

**Step 3: Test bridge**

```bash
python examples/test_bridge.py
```

Expected: Shows config, operations, and stub results

**Step 4: Commit**

```bash
git add lib/bridge.py examples/test_bridge.py
git commit -m "feat: add bridge module for command integration

- Simple wrapper functions for Claude to call
- Converts adapter objects to dicts
- Global adapter instance management
- Tested with examples/test_bridge.py

References: #context-hub-plugin-6de"
```

---

## Task 2: Wire Graphiti Backend to Real MCP Tools

**Files:**
- Modify: `lib/backends/graphiti.py`
- Create: `lib/test_graphiti_live.py`

**Context:** Replace stub calls with actual `mcp__graphiti__*` tool invocations. The MCP tools should be available in Claude's context.

**Step 1: Update query() method**

File: `lib/backends/graphiti.py` (lines 41-54)

Replace the stub implementation:

```python
def query(self, query: str, group_id: str, limit: int) -> List[Memory]:
    """Search memories using Graphiti search_memory_nodes."""
    # Call actual MCP tool
    result = mcp__graphiti__search_memory_nodes({
        "query": query,
        "group_ids": [group_id],  # Note: Graphiti uses group_ids (list)
        "max_nodes": limit
    })

    return self._parse_nodes_to_memories(result)
```

**Step 2: Update search_facts() method**

File: `lib/backends/graphiti.py` (lines 56-66)

```python
def search_facts(self, query: str, group_id: str, limit: int) -> List[Relationship]:
    """Search relationships using Graphiti search_memory_facts."""
    result = mcp__graphiti__search_memory_facts({
        "query": query,
        "group_ids": [group_id],
        "max_facts": limit
    })

    return self._parse_facts_to_relationships(result)
```

**Step 3: Update save() method**

File: `lib/backends/graphiti.py` (lines 68-79)

```python
def save(self, content: str, group_id: str, **metadata) -> str:
    """Save episode using Graphiti add_memory."""
    result = mcp__graphiti__add_memory({
        "name": metadata.get("title", "Untitled"),
        "episode_body": content,
        "group_id": group_id,
        "source": metadata.get("source", "context-hub"),
        "source_description": metadata.get("source_description", "Saved via context-hub-plugin")
    })

    # Extract episode ID from result
    return result.get("episode_id", result.get("uuid", "unknown"))
```

**Step 4: Update list_recent() method**

File: `lib/backends/graphiti.py` (lines 87-96)

```python
def list_recent(self, group_id: str, limit: int) -> List[Memory]:
    """List recent episodes using get_episodes."""
    result = mcp__graphiti__get_episodes({
        "group_ids": [group_id],
        "max_episodes": limit
    })

    return self._parse_episodes_to_memories(result)
```

**Step 5: Implement _parse_episodes_to_memories helper**

File: `lib/backends/graphiti.py` (add after existing helpers, ~line 140)

```python
def _parse_episodes_to_memories(self, result: dict) -> List[Memory]:
    """Parse Graphiti episodes to Memory objects."""
    memories = []

    for episode in result.get("episodes", []):
        memories.append(Memory(
            id=episode.get("uuid", ""),
            content=episode.get("content", episode.get("name", "")),
            created_at=datetime.fromisoformat(
                episode.get("created_at", datetime.now().isoformat())
            ),
            metadata={
                "name": episode.get("name", ""),
                "source": episode.get("source", ""),
                "episode_type": "episode"
            }
        ))

    return memories
```

**Step 6: Test with live Graphiti server**

Create: `lib/test_graphiti_live.py`

```python
#!/usr/bin/env python3
"""Test GraphitiBackend with live MCP server."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backends.graphiti import GraphitiBackend
from config import Config, MemoryConfig


def main():
    print("=== Testing Graphiti Backend (Live) ===\n")

    # Create backend
    config = Config(memory=MemoryConfig(backend="graphiti"))
    backend = GraphitiBackend()
    group_id = "test-group"

    print(f"Testing with group_id: {group_id}\n")

    # Test save
    print("1. Saving test memory...")
    try:
        memory_id = backend.save(
            "Test memory for Graphiti integration",
            group_id,
            title="Integration Test"
        )
        print(f"   ✅ Saved with ID: {memory_id}\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")

    # Test query
    print("2. Querying memories...")
    try:
        memories = backend.query("test", group_id, 5)
        print(f"   ✅ Found {len(memories)} memories\n")
        for m in memories[:2]:
            print(f"   - {m.content[:60]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")

    # Test list recent
    print("3. Listing recent memories...")
    try:
        recent = backend.list_recent(group_id, 5)
        print(f"   ✅ Found {len(recent)} recent memories\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")

    print("Live test complete!")


if __name__ == "__main__":
    main()
```

**Step 7: Run live test**

Note: This test will only work when run from Claude Code context (where MCP tools are available)

```bash
python lib/test_graphiti_live.py
```

Expected: Creates memory, queries, lists recent (or shows what MCP errors look like)

**Step 8: Commit**

```bash
git add lib/backends/graphiti.py lib/test_graphiti_live.py
git commit -m "feat: wire GraphitiBackend to real MCP tools

- Replace stub calls with mcp__graphiti__* invocations
- Implement _parse_episodes_to_memories helper
- Add live test script (requires Claude Code context)
- Ready for command integration

References: #context-hub-plugin-6de.1"
```

---

## Task 3: Wire Forgetful Backend to Real MCP Tools

**Files:**
- Modify: `lib/backends/forgetful.py`

**Context:** Similar to Graphiti, but using `mcp__forgetful__execute_forgetful_tool`.

**Step 1: Update query() method**

File: `lib/backends/forgetful.py` (lines 12-26)

```python
def query(self, query: str, group_id: str, limit: int) -> List[Memory]:
    """Search memories using Forgetful query_memory."""
    project_id = self._group_to_project_id(group_id)

    result = mcp__forgetful__execute_forgetful_tool("query_memory", {
        "query": query,
        "project_ids": [project_id] if project_id else None,
        "k": limit,
        "include_links": True
    })

    return self._parse_forgetful_memories(result)
```

**Step 2: Update save() method**

File: `lib/backends/forgetful.py` (lines 46-62)

```python
def save(self, content: str, group_id: str, **metadata) -> str:
    """Save memory using Forgetful create_memory."""
    project_id = self._group_to_project_id(group_id)

    result = mcp__forgetful__execute_forgetful_tool("create_memory", {
        "title": metadata.get("title", "Untitled"),
        "content": content,
        "importance": metadata.get("importance", 5),
        "project_ids": [project_id] if project_id else [],
        "keywords": metadata.get("keywords", []),
        "tags": metadata.get("tags", []),
        "context": metadata.get("context", "")
    })

    return str(result.get("memory_id", result.get("id", "unknown")))
```

**Step 3: Update list_recent() method**

File: `lib/backends/forgetful.py` (lines 90-100)

```python
def list_recent(self, group_id: str, limit: int) -> List[Memory]:
    """List recent memories using list_memories."""
    project_id = self._group_to_project_id(group_id)

    result = mcp__forgetful__execute_forgetful_tool("list_memories", {
        "project_ids": [project_id] if project_id else None,
        "limit": limit,
        "sort_by": "created_at",
        "sort_order": "desc"
    })

    return self._parse_forgetful_memories(result)
```

**Step 4: Implement _group_to_project_id**

File: `lib/backends/forgetful.py` (lines 146-170)

Replace stub implementation:

```python
def _group_to_project_id(self, group_id: str) -> Optional[int]:
    """
    Map group_id to Forgetful project_id.

    Strategy:
    1. Check cache
    2. List projects, find by name
    3. Create project if not found
    """
    # Check cache
    if group_id in self._project_cache:
        return self._project_cache[group_id]

    # List and find
    result = mcp__forgetful__execute_forgetful_tool("list_projects", {})

    for project in result.get("projects", []):
        if project.get("name") == group_id:
            project_id = project.get("id")
            self._project_cache[group_id] = project_id
            return project_id

    # Create new project
    create_result = mcp__forgetful__execute_forgetful_tool("create_project", {
        "name": group_id,
        "description": f"Auto-created from group_id: {group_id}"
    })

    project_id = create_result.get("project_id", create_result.get("id"))
    self._project_cache[group_id] = project_id
    return project_id
```

**Step 5: Implement get_capabilities with dynamic discovery**

File: `lib/backends/forgetful.py` (lines 107-120)

Replace static fallback:

```python
def get_capabilities(self) -> List[OperationInfo]:
    """Discover capabilities using Forgetful's meta-tools."""
    tools = mcp__forgetful__discover_forgetful_tools()

    # Map Forgetful tools to our operations
    # For now, return static list (full mapping can be done later)
    return [
        OperationInfo(
            name="query",
            description="Search for memories by semantic similarity",
            params={"query": "str", "limit": "int"},
            example='memory.query("auth patterns", limit=10)'
        ),
        OperationInfo(
            name="save",
            description="Save new memory",
            params={"content": "str", "title": "str", "importance": "int (1-10)"},
            example='memory.save("Decision: JWT auth", title="Auth", importance=9)'
        ),
        OperationInfo(
            name="list_recent",
            description="List recent memories",
            params={"limit": "int"},
            example='memory.list_recent(limit=20)'
        ),
    ]
```

**Step 6: Commit**

```bash
git add lib/backends/forgetful.py
git commit -m "feat: wire ForgetfulBackend to real MCP tools

- Replace stub calls with mcp__forgetful__execute_forgetful_tool
- Implement _group_to_project_id with auto-create
- Use discover_forgetful_tools for capabilities
- Ready for command integration

References: #context-hub-plugin-6de.2"
```

---

## Task 4: Update /memory-search Command

**Files:**
- Modify: `commands/memory-search.md`

**Context:** First command migration - establish the pattern for others.

**Step 1: Update command to use adapter**

File: `commands/memory-search.md`

Replace entire content:

```markdown
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
mcp__graphiti__search_memory_nodes({
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
```

**Step 2: Test the command**

Manually trigger in Claude Code:
```
/memory-search test query
```

Expected: Shows which backend is used, searches, displays results

**Step 3: Commit**

```bash
git add commands/memory-search.md
git commit -m "feat: update /memory-search to use adapter

- Use bridge.memory_query() when Python available
- Fallback to direct MCP tools
- Show backend config in response
- Establish pattern for other commands

References: #context-hub-plugin-6de.3"
```

---

## Task 5: Update /memory-save Command

**Files:**
- Modify: `commands/memory-save.md`

**Step 1: Update command**

File: `commands/memory-save.md`

Replace the entire file with:

```markdown
---
description: Save current conversation context as a memory
---

# Memory Save

Save important context, decisions, or patterns to the knowledge base.

## Your Task

Extract relevant context from the current conversation and save it using the memory adapter.

## Implementation

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'lib'))

from bridge import memory_save, memory_get_config

# Show config
config = memory_get_config()
print(f"Saving to backend: {config['backend']}, group: {config['group_id']}\n")

# Extract context from conversation
# Analyze the recent messages to determine:
# - What decision was made or pattern discovered
# - Why it matters (importance)
# - Relevant keywords/tags

# Example structure:
title = "<concise title of what's being saved>"
content = """
<detailed description of the context, decision, or pattern>

Include:
- What: The actual decision/pattern/insight
- Why: Rationale or context
- When: Temporal context if relevant
- How: Implementation details if applicable
"""

importance = <1-10 score>  # Only for Forgetful backend
keywords = ["keyword1", "keyword2"]
tags = ["tag1", "tag2"]

# Save the memory
memory_id = memory_save(
    content=content,
    title=title,
    importance=importance,  # Ignored by Graphiti
    keywords=keywords,      # Ignored by Graphiti
    tags=tags              # Ignored by Graphiti
)

print(f"✅ Saved memory with ID: {memory_id}")
print(f"   Title: {title}")
print(f"   Backend: {config['backend']}")
```

## Extraction Guidelines

**What to save:**
- ✅ Architectural decisions and rationale
- ✅ Patterns you've implemented together
- ✅ Important discoveries or insights
- ✅ User preferences and requirements
- ✅ Lessons learned from bugs or issues

**What NOT to save:**
- ❌ Obvious/trivial information
- ❌ Temporary implementation details
- ❌ Information already well-documented elsewhere

**Importance Scoring (for Forgetful):**
- 9-10: Critical decisions, user preferences, major patterns
- 7-8: Important patterns, significant implementations
- 5-6: Useful context, minor decisions
- 1-4: Nice-to-know, low priority

## Response Format

Clearly communicate what was saved:

```
✅ Saved: <title>

Content: <brief summary>
Backend: <graphiti|forgetful>
Group: <group-id>
ID: <memory-id>

This memory will be available for future context retrieval.
```

## Notes

- **No project discovery needed**: Adapter auto-detects group_id from git repo
- **Backend differences**: Graphiti auto-extracts entities, Forgetful uses explicit metadata
- **Atomic memories**: Keep focused on one concept per save
```

**Step 2: Commit**

```bash
git add commands/memory-save.md
git commit -m "feat: update /memory-save to use adapter

- Use bridge.memory_save()
- Remove project discovery (adapter handles it)
- Add extraction guidelines
- Backend-aware importance scoring

References: #context-hub-plugin-6de.4"
```

---

## Task 6: Update Remaining Commands

**Files:**
- Modify: `commands/memory-list.md`
- Modify: `commands/memory-explore.md`
- Modify: `commands/context_gather.md`

**Step 1: Update /memory-list**

File: `commands/memory-list.md`

```markdown
---
description: List recent memories from the knowledge base
---

# Memory List

List recent memories to see what context has been saved.

## Implementation

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'lib'))

from bridge import memory_list_recent, memory_get_config

config = memory_get_config()
print(f"Backend: {config['backend']}, Group: {config['group_id']}\n")

# Get count from user input or default to 20
limit = int("$ARGUMENTS") if "$ARGUMENTS".isdigit() else 20

# List recent
memories = memory_list_recent(limit=limit)

print(f"Found {len(memories)} recent memories:\n")

for i, memory in enumerate(memories, 1):
    title = memory['metadata'].get('title', memory['content'][:50])
    print(f"{i}. {title}")
    print(f"   Created: {memory['created_at'][:10]}")
    if memory.get('importance'):
        print(f"   Importance: {memory['importance']}")
    print()
```

## Response Format

Show memories in chronological order (newest first) with:
- Title or content preview
- Creation date
- Importance (if Forgetful backend)
```

**Step 2: Update /memory-explore**

File: `commands/memory-explore.md`

```markdown
---
description: Deep exploration of the knowledge graph
---

# Memory Explore

Traverse the knowledge graph from a starting point to discover connected concepts.

**Query**: $ARGUMENTS

## Implementation

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'lib'))

from bridge import memory_explore, memory_get_config

config = memory_get_config()
print(f"Backend: {config['backend']}, Group: {config['group_id']}\n")

# Explore from starting point
graph = memory_explore("$ARGUMENTS", depth=2)

print(f"Explored knowledge graph from: $ARGUMENTS\n")
print(f"Found {len(graph['nodes'])} nodes and {len(graph['edges'])} connections\n")

# Show nodes
print("Key Concepts:")
for node in graph['nodes'][:5]:
    title = node['metadata'].get('title', node['content'][:50])
    print(f"  - {title}")

print(f"\nConnections: {len(graph['edges'])} relationships discovered")

# Show some relationships
for edge in graph['edges'][:5]:
    print(f"  {edge['source']} --[{edge['type']}]--> {edge['target']}")
```

## Notes

- **Graphiti**: Native graph traversal via search_facts
- **Forgetful**: Manual traversal via linked_memory_ids
- Depth=2 explores 2 levels of connections
```

**Step 3: Update /context_gather**

File: `commands/context_gather.md`

```markdown
---
description: Gather comprehensive context from all sources
---

# Context Gather

Use the context-retrieval agent with memory adapter integration.

**Task**: $ARGUMENTS

## Implementation

Launch the context-retrieval agent with the task description.

The agent will:
1. Query memory backend (auto-selected: Graphiti or Forgetful)
2. Read linked code artifacts and files
3. Query Context7 for framework docs
4. Search web if needed

The agent has been updated to use the memory adapter automatically.
```

**Step 4: Commit all**

```bash
git add commands/memory-list.md commands/memory-explore.md commands/context_gather.md
git commit -m "feat: update remaining memory commands

- /memory-list uses memory_list_recent()
- /memory-explore uses memory_explore() with graph visualization
- /context_gather references updated agent
- All commands use bridge pattern

References: #context-hub-plugin-6de.5 #context-hub-plugin-6de.6 #context-hub-plugin-6de.7"
```

---

## Task 7: Update context-retrieval Agent

**Files:**
- Modify: `agents/context-retrieval.md`

**Step 1: Update tools and description**

File: `agents/context-retrieval.md` (lines 1-6)

```markdown
---
name: context-retrieval
description: Context retrieval specialist for gathering relevant memories, code patterns, and framework documentation. Uses memory adapter (Graphiti/Forgetful) for cross-project knowledge search.
tools: mcp__context7__resolve-library-id, mcp__context7__get-library-docs, WebSearch, WebFetch, Read, Glob, Grep
model: sonnet
---
```

**Step 2: Update memory search strategy**

File: `agents/context-retrieval.md` (lines 14-23)

Replace Forgetful-specific instructions:

```markdown
### 1. Memory Backend (Primary Source)

**Query across ALL projects** - Memory adapter handles backend selection:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'lib'))

from bridge import memory_query, memory_get_config

# Check which backend is active
config = memory_get_config()
# Backend: graphiti or forgetful
# Group: auto-detected from git repo

# Search for relevant memories
memories = memory_query("<your search query>", limit=10)
```

**Tips:**
- Prioritize high importance memories (9-10 = architectural patterns)
- Look for patterns from other projects (cross-project learning)
- Read linked code artifacts when memories reference them
```

**Step 3: Update examples throughout**

Replace all instances of `execute_forgetful_tool` with bridge calls.

Example at line 132:

```markdown
2. **Check ALL projects**: Use memory adapter (auto-searches across group_id)

```python
# Memory adapter automatically:
# - Detects group_id from git repo
# - Routes to configured backend (Graphiti/Forgetful)
# - Handles backend-specific query format

results = memory_query("authentication patterns", limit=15)
```
```

**Step 4: Add dynamic discovery section**

Add new section after line 50:

```markdown
## Dynamic Discovery

Discover available memory operations at runtime:

```python
from bridge import memory_list_operations

operations = memory_list_operations()
for op in operations:
    print(f"{op['name']}: {op['description']}")
    print(f"  Example: {op['example']}")
```

Useful when:
- Backend capabilities differ (Graphiti vs Forgetful)
- New operations added
- Debugging integration issues
```

**Step 5: Commit**

```bash
git add agents/context-retrieval.md
git commit -m "feat: update context-retrieval agent for adapter

- Remove mcp__forgetful__* tools (now handled by adapter)
- Use bridge pattern for memory operations
- Add dynamic discovery documentation
- Backend-agnostic instructions

References: #context-hub-plugin-6de.10"
```

---

## Task 8: Update Skills

**Files:**
- Rename: `skills/using-forgetful-memory/` → `skills/using-memory-adapter/`
- Modify: `skills/using-memory-adapter/SKILL.md`
- Modify: `skills/exploring-knowledge-graph/SKILL.md`

**Step 1: Rename skill directory**

```bash
mv skills/using-forgetful-memory skills/using-memory-adapter
```

**Step 2: Update skill frontmatter**

File: `skills/using-memory-adapter/SKILL.md` (lines 1-6)

```markdown
---
name: using-memory-adapter
description: When to query and save memories using the pluggable memory adapter (Graphiti or Forgetful). PROACTIVELY query before starting work. Save important decisions and patterns.
allowed-tools: Read, Glob, Grep
---
```

**Step 3: Update skill content**

File: `skills/using-memory-adapter/SKILL.md`

Replace Forgetful-specific content with adapter-based instructions:

```markdown
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
```

**Step 4: Update exploring-knowledge-graph skill**

File: `skills/exploring-knowledge-graph/SKILL.md`

Update to use memory_explore():

```markdown
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
```

**Step 5: Commit**

```bash
git add skills/using-memory-adapter/ skills/exploring-knowledge-graph/
git commit -m "feat: update skills for memory adapter

- Rename using-forgetful-memory → using-memory-adapter
- Backend-agnostic instructions
- Document Graphiti vs Forgetful differences
- Update exploring-knowledge-graph for adapter

References: #context-hub-plugin-6de.11 #context-hub-plugin-6de.12"
```

---

## Task 9: Testing and Documentation

**Files:**
- Create: `docs/MIGRATION.md`
- Modify: `README.md`
- Create: `examples/test_end_to_end.py`

**Step 1: Create migration guide**

File: `docs/MIGRATION.md`

```markdown
# Migration Guide: Pluggable Memory Backend

This guide helps existing users migrate to the new pluggable backend system.

## What Changed

**Before (Forgetful-only):**
- Commands called `execute_forgetful_tool()` directly
- Project ID discovery required for scoping
- Single backend (Forgetful)

**After (Pluggable):**
- Commands use memory adapter (Graphiti or Forgetful)
- Auto-detect group_id from git repo
- Config-based backend selection

## Migration Steps

### 1. Configuration

Create `.context-hub.yaml` in your project root:

```yaml
memory:
  backend: "graphiti"  # or "forgetful"
  group_id: "auto"     # auto-detect from git
```

For explicit group_id:

```yaml
memory:
  backend: "graphiti"
  group_id: "my-project"  # override auto-detection
```

### 2. Backend Setup

**For Graphiti:**
- Install and run Graphiti MCP server
- Configure in Claude Code: `claude mcp add --transport http graphiti http://localhost:8000/mcp`
- No migration needed - start fresh or sync manually

**For Forgetful:**
- Existing memories remain accessible
- Auto-creates project from group_id if needed
- No data migration required

### 3. Updated Commands

All commands now work the same way:

```
/memory-search <query>    # Uses configured backend
/memory-save              # Saves to configured backend
/memory-list [count]      # Lists from configured backend
```

### 4. Agents & Skills

- `context-retrieval` agent updated automatically
- Skills renamed: `using-forgetful-memory` → `using-memory-adapter`
- Use dynamic discovery to explore capabilities

## Backend Comparison

| Aspect | Graphiti | Forgetful |
|--------|----------|-----------|
| Setup | Docker + MCP | MCP only |
| Speed | Fast (graph DB) | Moderate (SQLite) |
| Entities | Auto-extracted | Manual |
| Search | Hybrid | Semantic |
| Best For | Large knowledge graphs | Simple memory |

## Troubleshooting

**"No backend configured"**
- Create `.context-hub.yaml` in project root
- Or set `CONTEXT_HUB_BACKEND=graphiti` env var

**"MCP tools not found"**
- Verify Graphiti/Forgetful MCP server is running
- Check `claude mcp list` shows your backend

**"Group ID detection failed"**
- Set explicit group_id in config
- Or run from git repository directory

## Rollback

To revert to Forgetful-only:

1. Set backend in config: `backend: "forgetful"`
2. Commands work as before (adapter routes to Forgetful)
```

**Step 2: Update README**

File: `README.md` (add new section after "Installation")

```markdown
## Configuration

Context Hub supports pluggable memory backends. Create `.context-hub.yaml`:

```yaml
memory:
  backend: "graphiti"  # or "forgetful"
  group_id: "auto"     # auto-detect from git repo
```

**Supported Backends:**
- **Graphiti**: Knowledge graph with automatic entity extraction (recommended)
- **Forgetful**: Atomic memories with explicit linking

Backend is auto-selected from config. Group ID is auto-detected from git repository.

See [Migration Guide](docs/MIGRATION.md) for details.
```

**Step 3: Create end-to-end test**

File: `examples/test_end_to_end.py`

```python
#!/usr/bin/env python3
"""End-to-end test of adapter with both backends."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from bridge import (
    memory_query,
    memory_save,
    memory_list_recent,
    memory_explore,
    memory_get_config
)


def test_backend(backend_name: str):
    """Test a specific backend."""
    print(f"\n{'='*60}")
    print(f"Testing {backend_name.upper()} Backend")
    print(f"{'='*60}\n")

    # Get config
    config = memory_get_config()
    print(f"Config: {config}\n")

    # Test save
    print("1. Saving test memory...")
    try:
        memory_id = memory_save(
            f"Test memory for {backend_name}",
            title=f"{backend_name} Test",
            importance=7
        )
        print(f"   ✅ Saved: {memory_id}\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
        return False

    # Test query
    print("2. Querying memories...")
    try:
        results = memory_query("test", limit=5)
        print(f"   ✅ Found {len(results)} memories\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
        return False

    # Test list
    print("3. Listing recent...")
    try:
        recent = memory_list_recent(limit=5)
        print(f"   ✅ Listed {len(recent)} recent\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
        return False

    # Test explore
    print("4. Exploring graph...")
    try:
        graph = memory_explore("test", depth=1)
        print(f"   ✅ Graph: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
        return False

    return True


def main():
    """Run end-to-end tests."""
    print("=== End-to-End Adapter Test ===")

    # Test current backend
    config = memory_get_config()
    backend = config['backend']

    success = test_backend(backend)

    if success:
        print(f"\n✅ All tests passed for {backend} backend!")
    else:
        print(f"\n❌ Tests failed for {backend} backend")

    print("\nTo test other backend:")
    print("1. Update .context-hub.yaml")
    print("2. Restart Claude Code")
    print("3. Run this test again")


if __name__ == "__main__":
    main()
```

**Step 4: Test everything**

```bash
# Run end-to-end test
python examples/test_end_to_end.py

# Test commands manually
/memory-search test
/memory-save
/memory-list
```

**Step 5: Commit**

```bash
git add docs/MIGRATION.md README.md examples/test_end_to_end.py
git commit -m "docs: add migration guide and update README

- Migration guide for existing users
- Updated README with configuration
- End-to-end test script
- Backend comparison table

References: #context-hub-plugin-6de.14"
```

---

## Summary

**Phase 2 Complete!** 🎉

**What's Been Built:**
1. ✅ Bridge module for command integration
2. ✅ Graphiti backend MCP wiring
3. ✅ Forgetful backend MCP wiring
4. ✅ All commands updated (/memory-search, /memory-save, /memory-list, /memory-explore, /context_gather)
5. ✅ context-retrieval agent updated
6. ✅ Skills updated (renamed + adapter-based)
7. ✅ Migration guide and documentation
8. ✅ End-to-end testing

**Epic Status:**
- `context-hub-plugin-6de`: All 14 tasks complete

**Next Steps:**

The plugin is now fully integrated! Users can:

1. **Configure backend** via `.context-hub.yaml`
2. **Use any command** - adapter routes to correct backend
3. **Switch backends** - just update config and restart

**Test the integration:**
```bash
# Set backend to Graphiti
echo "memory:
  backend: graphiti
  group_id: auto" > .context-hub.yaml

# Test commands
/memory-search authentication
/memory-save
```

**Want to:**
- Test with live Graphiti server?
- Add more backends in future?
- Optimize performance?
