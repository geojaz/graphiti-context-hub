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

```python
import yaml
from pathlib import Path
import subprocess

# Load config and detect group_id
config_path = Path.cwd() / '.context-hub.yaml'
if config_path.exists():
    with open(config_path) as f:
        config = yaml.safe_load(f)
else:
    config = {'graphiti': {'group_id': 'auto'}}

group_id_setting = config.get('graphiti', {}).get('group_id', 'auto')

# Auto-detect group_id if needed
if group_id_setting == 'auto':
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        if result.returncode == 0:
            remote = result.stdout.strip()
            if '/' in remote:
                group_id = remote.split('/')[-1].replace('.git', '')
            else:
                group_id = Path.cwd().name
        else:
            group_id = Path.cwd().name
    except:
        group_id = Path.cwd().name
else:
    group_id = group_id_setting

# Search nodes (entities)
nodes_result = mcp__graphiti__search_nodes({
    "query": "authentication patterns",
    "group_ids": [group_id],
    "max_nodes": 10
})

# Search facts (relationships)
facts_result = mcp__graphiti__search_memory_facts({
    "query": "authentication flow",
    "group_ids": [group_id],
    "max_facts": 20
})
```

## How to Save

```python
# Save an episode (Graphiti automatically extracts entities)
result = mcp__graphiti__add_memory({
    "name": "Auth Decision: JWT with httponly cookies",
    "episode_body": """
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
    "group_id": group_id,
    "source": "context-hub",
    "source_description": "Architectural decision"
})

episode_id = result.get('episode_id', result.get('uuid'))
```

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

Set group_id in `.context-hub.yaml`:

```yaml
graphiti:
  group_id: "auto"  # or explicit: "my-project"
  endpoint: "http://localhost:8000"  # optional
```

Group ID is auto-detected from git repository name when set to "auto".

## Common Patterns

**Before implementing a feature:**
```python
# Search for related patterns
nodes = mcp__graphiti__search_nodes({
    "query": f"implementing {feature_name}",
    "group_ids": [group_id],
    "max_nodes": 10
})

# Check for architectural decisions
facts = mcp__graphiti__search_memory_facts({
    "query": f"{feature_name} architecture",
    "group_ids": [group_id],
    "max_facts": 20
})
```

**After making a decision:**
```python
mcp__graphiti__add_memory({
    "name": f"Decision: {decision_title}",
    "episode_body": f"""
    Decision: {what_you_decided}

    Context: {why_this_matters}

    Rationale: {reasoning}

    Trade-offs: {alternatives_considered}
    """,
    "group_id": group_id,
    "source": "context-hub"
})
```
