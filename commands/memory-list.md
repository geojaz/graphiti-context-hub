---
description: List recent memories from the knowledge base
---

# Memory List

List recent episodes from Graphiti to see what context has been saved.

## Your Task

List recent memories for the current project.

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

**Step 2: List recent episodes from Graphiti**

```python
# Get count from user input or default to 20
limit = int("$ARGUMENTS") if "$ARGUMENTS".strip().isdigit() else 20

# Call Graphiti MCP tool directly
result = mcp__graphiti__get_episodes({
    "group_ids": [group_id],
    "max_episodes": limit
})

# Display results
episodes = result.get('episodes', [])
print(f"Found {len(episodes)} recent episodes:\n")

for i, episode in enumerate(episodes, 1):
    name = episode.get('name', 'Untitled')
    content = episode.get('content', '')
    created = episode.get('created_at', '')[:19]  # YYYY-MM-DD HH:MM:SS

    print(f"{i}. {name}")
    # Show first 100 chars of content as preview
    preview = content[:100] + '...' if len(content) > 100 else content
    if preview:
        print(f"   {preview}")
    print(f"   Created: {created}")
    print()
```

## Response Format

Show episodes in chronological order (newest first) with:
- Episode name/title
- Content preview (first 100 chars)
- Creation timestamp

Example:
```
Using group_id: context-hub-plugin

Found 5 recent episodes:

1. Implemented Graphiti Backend
   Replaced Forgetful backend with Graphiti for graph-based memory storage...
   Created: 2024-03-15 14:30:22

2. Updated Memory Commands
   Refactored memory-search, memory-save, memory-list to use Graphiti MCP...
   Created: 2024-03-15 13:15:10
```

## Notes

- **No adapter layer**: Calls Graphiti MCP directly
- **Episodes vs Nodes**: This lists raw episodes (saved memories), not extracted entities
- **Group isolation**: Only shows episodes for the current project's group_id
- **Default limit**: Shows 20 most recent if no argument provided
