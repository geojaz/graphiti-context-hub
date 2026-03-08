---
name: exploring-knowledge-graph
description: Deep exploration of Graphiti knowledge graph. Use when investigating connections, tracing decisions, or understanding architectural evolution.
allowed-tools: Read, Glob, Grep
---

# Exploring the Knowledge Graph

## When to Use

**Deep graph exploration:**
- ✅ Tracing how a decision evolved over time
- ✅ Understanding connections between components
- ✅ Finding related architectural patterns
- ✅ Investigating why something was built a certain way

## Exploration Strategy

**Step 1: Find starting point**

```bash
source "$HOME/.config/claude/graphiti-context-hub.conf" 2>/dev/null

GROUP_ID="${GRAPHITI_GROUP_ID:-main}"
REPO_NAME=$(git remote get-url origin 2>/dev/null | sed 's/.*\///' | sed 's/\.git$//' || basename "$PWD")
```

```python
# Find starting nodes
starting_nodes = mcp__graphiti__search_nodes({
    "query": "authentication architecture",
    "group_ids": [GROUP_ID],
    "max_nodes": 5
})
```

**Step 2: Explore relationships**

```python
# Get facts related to the topic
facts = mcp__graphiti__search_memory_facts({
    "query": "authentication dependencies relationships",
    "group_ids": [GROUP_ID],
    "max_facts": 30
})

# Analyze fact patterns
for fact in facts.get('facts', []):
    print(f"Relationship: {fact.get('fact')}")
    print(f"  From: {fact.get('source_node_uuid')}")
    print(f"  To: {fact.get('target_node_uuid')}")
```

**Step 3: Get episode context**

```python
# Get episodes (chronological context)
episodes = mcp__graphiti__get_episodes({
    "group_ids": [GROUP_ID],
    "max_episodes": 20
})

# Look for evolution over time
for ep in episodes.get('episodes', []):
    if 'authentication' in ep.get('name', '').lower():
        print(f"{ep.get('created_at')}: {ep.get('name')}")
```

## Exploration Patterns

**Pattern 1: Trace a decision's evolution**

1. Search nodes for the concept
2. Get facts showing relationships
3. Get episodes chronologically
4. Identify what changed and why

**Pattern 2: Understand component dependencies**

1. Search for component name
2. Get facts showing dependencies
3. Map the dependency graph
4. Identify potential issues

**Pattern 3: Find reusable patterns**

1. Search broadly (e.g., "API design patterns")
2. Group nodes by similarity
3. Extract common patterns from facts
4. Synthesize reusable approach

## Response Format

Present findings as:

```markdown
## Exploration: [Topic]

### Central Entities
- Entity 1: Description
- Entity 2: Description

### Key Relationships
- Entity A → Entity B: Relationship type
- Entity B → Entity C: Relationship type

### Evolution Timeline
- [Date]: Initial decision
- [Date]: Refinement
- [Date]: Current state

### Insights
- Pattern discovered
- Dependency identified
- Trade-off understood
```

## Anti-Patterns

❌ Exploring without a clear starting query
❌ Looking only at nodes without checking facts
❌ Ignoring temporal context (episode chronology)
❌ Not synthesizing findings into actionable insights
