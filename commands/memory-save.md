---
description: Save current conversation context as a memory
---

# Memory Save

Save important context, decisions, or patterns to the Graphiti knowledge base.

## Your Task

Extract relevant context from the current conversation and save it using Graphiti.

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

**Step 2: Extract context and save to Graphiti**

```python
# Analyze the recent messages to determine:
# - What decision was made or pattern discovered
# - Why it matters (importance)
# - Relevant context

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

# Combine title and content for Graphiti
episode_body = f"{title}\n\n{content}"

# Call Graphiti MCP tool directly
result = mcp__graphiti__add_memory({
    "name": title,
    "episode_body": episode_body,
    "group_id": group_id,
    "source": "text",
    "source_description": "conversation context"
})

print(f"✅ Saved memory to Graphiti")
print(f"   Title: {title}")
print(f"   Group: {group_id}")
print(f"\nGraphiti will automatically extract entities and relationships from this memory.")
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

## Response Format

Clearly communicate what was saved:

```
✅ Saved: <title>

Content: <brief summary>
Group: <group-id>

Graphiti will automatically extract entities and relationships from this memory.
```

## Notes

- **No adapter layer**: Calls Graphiti MCP directly
- **Auto-extracts entities**: Graphiti automatically identifies concepts and relationships
- **Atomic memories**: Keep focused on one concept per save
- **Group isolation**: Memories are scoped by group_id (auto-detected from git repo)
