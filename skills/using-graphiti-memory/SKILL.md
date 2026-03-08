---
name: using-graphiti-memory
description: When to query and save to Graphiti knowledge graph. PROACTIVELY query before starting work. Save important decisions and patterns.
allowed-tools: Read, Glob, Grep
---

# Using Graphiti Memory

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

**Step 1: Get config and repo context** (run once):

```bash
source "$HOME/.config/claude/graphiti-context-hub.conf" 2>/dev/null

GROUP_ID="${GRAPHITI_GROUP_ID:-main}"
REPO_NAME=$(git remote get-url origin 2>/dev/null | sed 's/.*\///' | sed 's/\.git$//' || basename "$PWD")
```

**Step 2: Search Graphiti** (use GROUP_ID from above):

```python
# Search nodes (entities)
nodes_result = mcp__graphiti__search_nodes({
    "query": "authentication patterns",
    "group_ids": [GROUP_ID],  # Always "main"
    "max_nodes": 10
})

# Search facts (relationships)
facts_result = mcp__graphiti__search_memory_facts({
    "query": "authentication flow",
    "group_ids": [GROUP_ID],
    "max_facts": 20
})
```

## How to Save

**Step 1: Get config** (if not already loaded):

```bash
source "$HOME/.config/claude/graphiti-context-hub.conf" 2>/dev/null

GROUP_ID="${GRAPHITI_GROUP_ID:-main}"
REPO_NAME=$(git remote get-url origin 2>/dev/null | sed 's/.*\///' | sed 's/\.git$//' || basename "$PWD")
```

**Step 2: Save episode with repo tagging**:

```python
# IMPORTANT: Prefix episode_body with "Repo: {REPO_NAME}\n\n"
result = mcp__graphiti__add_memory({
    "name": "Auth Decision: JWT with httponly cookies",
    "episode_body": f"""Repo: {REPO_NAME}

Decision: Using JWT tokens stored in httponly cookies.

Rationale:
- XSS protection via httponly flag
- CSRF protection via SameSite attribute
- Automatic token rotation on refresh

Implementation:
- Access token: 15 min expiry
- Refresh token: 7 day expiry
- Redis for token storage
""",
    "group_id": GROUP_ID,  # Always "main"
    "source": "context-hub",
    "source_description": "Architectural decision"
})

episode_id = result.get('episode_id', result.get('uuid'))
```

**Key Pattern**: Always prefix `episode_body` with `Repo: {REPO_NAME}\n\n` to tag which repository the memory belongs to.

## Graphiti Features

**Automatic Entity Extraction:**
- Graphiti extracts entities (JWT, Redis, tokens) automatically
- Creates relationships between entities
- No manual linking required

**Search Capabilities:**
- Semantic search across nodes (entities)
- Relationship search via facts
- Temporal queries (what changed when)

**Knowledge Graph Benefits:**
- See connections between decisions
- Trace architectural evolution
- Discover related patterns across projects

## Configuration

Config file: `~/.config/claude/graphiti-context-hub.conf`

```bash
GRAPHITI_GROUP_ID=main
GRAPHITI_ENDPOINT=http://localhost:8000
SERENA_ENABLED=true
```

Created by `/context-hub-setup`. Defaults: group_id=main, endpoint=localhost:8000.

## Common Patterns

**Before implementing a feature:**
```python
# Search for related patterns
nodes = mcp__graphiti__search_nodes({
    "query": f"implementing {feature_name}",
    "group_ids": [GROUP_ID],
    "max_nodes": 10
})

# Check for architectural decisions
facts = mcp__graphiti__search_memory_facts({
    "query": f"{feature_name} architecture",
    "group_ids": [GROUP_ID],
    "max_facts": 20
})
```

**After making a decision:**
```python
mcp__graphiti__add_memory({
    "name": f"Decision: {decision_title}",
    "episode_body": f"""Repo: {REPO_NAME}

Decision: {what_you_decided}

Context: {why_this_matters}

Rationale: {reasoning}

Trade-offs: {alternatives_considered}
""",
    "group_id": GROUP_ID,
    "source": "context-hub"
})
```
