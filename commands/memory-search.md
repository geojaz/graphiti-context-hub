---
description: Search Graphiti knowledge graph semantically
---

# Memory Search

Search the knowledge graph for relevant memories using Graphiti.

## Your Task

Search Graphiti for: **$ARGUMENTS**

## Implementation

**Step 1: Load config and detect group_id**

```python
import yaml
from pathlib import Path
import subprocess

# Load config
config_path = Path.cwd() / '.context-hub.yaml'
if config_path.exists():
    with open(config_path) as f:
        config = yaml.safe_load(f)
else:
    config = {'graphiti': {'group_id': 'auto'}}

group_id_setting = config.get('graphiti', {}).get('group_id', 'auto')

# Detect group_id if set to auto
if group_id_setting == 'auto':
    # Try to get from git repo name
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        if result.returncode == 0:
            remote = result.stdout.strip()
            # Extract repo name from URL
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

print(f"Using group_id: {group_id}\n")
```

**Step 2: Search Graphiti**

```python
query = "$ARGUMENTS"

# Call Graphiti MCP tool directly
result = mcp__graphiti__search_nodes({
    "query": query,
    "group_ids": [group_id],
    "max_nodes": 10
})

# Display results
nodes = result.get('nodes', [])
print(f"Found {len(nodes)} memories:\n")

for i, node in enumerate(nodes, 1):
    name = node.get('name', 'Untitled')
    summary = node.get('summary', '')
    created = node.get('created_at', '')[:10]

    print(f"{i}. {name}")
    if summary:
        print(f"   {summary[:150]}...")
    print(f"   Created: {created}")
    print()
```

## Response Format

Present results clearly with:
1. Group ID being searched
2. Number of results found
3. For each memory: title, summary snippet, creation date
4. Suggestions to refine search if needed
