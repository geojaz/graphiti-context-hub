---
description: Save current conversation context as a memory
---

# Memory Save

Save important context, decisions, or patterns to the Graphiti knowledge base.

## Your Task

Extract relevant context from the current conversation and save it using Graphiti.

## Implementation

**Step 1: Load config and detect repo**

```bash
# Load config
source "$HOME/.config/claude/graphiti-context-hub.conf" 2>/dev/null
GROUP_ID="${GRAPHITI_GROUP_ID:-main}"
REPO_NAME=$(git remote get-url origin 2>/dev/null | sed 's/.*\///' | sed 's/\.git$//' || basename "$PWD")

echo "group_id: $GROUP_ID"
echo "repo: $REPO_NAME"
```

**Step 2: Save to Graphiti with repo context**

Ask user what to save (title and content), then:

```python
# Format episode body with repo prefix
episode_body = f"""Repo: {REPO_NAME}

{content_from_user}
"""

# Save episode using GROUP_ID from Bash
result = mcp__graphiti__add_memory({
    "name": title_from_user,
    "episode_body": episode_body,
    "group_id": GROUP_ID,
    "source": "context-hub",
    "source_description": f"Manual save from {REPO_NAME}"
})

episode_id = result.get('episode_id', result.get('uuid', 'unknown'))
print(f"✓ Saved to group '{GROUP_ID}' with repo tag '{REPO_NAME}'")
print(f"  Episode ID: {episode_id}")
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
- **Group isolation**: Memories are scoped by group_id (configured in ~/.config/claude/graphiti-context-hub.conf)
