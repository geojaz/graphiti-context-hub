---
name: serena-code-architecture
description: Architectural analysis workflow using Serena symbols and Graphiti knowledge graph. Use when analyzing project structure, documenting architecture, or creating architectural memories from code.
allowed-tools: mcp__plugin_serena_serena__get_symbols_overview, mcp__plugin_serena_serena__find_symbol, mcp__plugin_serena_serena__find_referencing_symbols, mcp__plugin_serena_serena__list_dir, mcp__plugin_serena_serena__search_for_pattern, Read, Glob
---

# Architectural Analysis with Serena + Graphiti

This skill guides systematic architectural analysis using Serena's symbol-level understanding, with optional persistence to Graphiti knowledge graph.

## When to Use This Skill

- Analyzing a new codebase before implementing changes
- Documenting existing architecture for a project
- Persisting architectural insights to memory
- Understanding dependencies and call hierarchies
- Building a knowledge graph from code structure

## Analysis Workflow

### Phase 1: Project Structure Discovery

Understand the high-level layout:

```python
# Get directory structure
mcp__plugin_serena_serena__list_dir({
  "relative_path": ".",
  "recursive": false
})

# Identify key directories (src/, app/, lib/, etc.)
mcp__plugin_serena_serena__list_dir({
  "relative_path": "src",
  "recursive": true
})
```

**Goal**: Identify entry points, main modules, and organizational patterns.

### Phase 2: Entry Point Analysis

Find the application entry points:

```python
# Look for main/app files
mcp__plugin_serena_serena__search_for_pattern({
  "substring_pattern": "if __name__.*==.*__main__|def main\\(|app\\s*=\\s*FastAPI|createApp",
  "restrict_search_to_code_files": true
})

# Get symbols from entry file
mcp__plugin_serena_serena__get_symbols_overview({
  "relative_path": "src/main.py",
  "depth": 1
})
```

### Phase 3: Core Component Mapping

Identify and analyze major components:

```python
# Find all service/controller/model classes
mcp__plugin_serena_serena__find_symbol({
  "name_path_pattern": "Service",
  "substring_matching": true,
  "include_kinds": [5],  # Class only
  "depth": 1
})

# For each major component, get full structure
mcp__plugin_serena_serena__find_symbol({
  "name_path_pattern": "AuthService",
  "include_body": false,
  "depth": 1  # Get methods
})
```

### Phase 4: Dependency Tracing

Understand how components connect:

```python
# Find who uses AuthService
mcp__plugin_serena_serena__find_referencing_symbols({
  "name_path": "AuthService",
  "relative_path": "src/services/auth.py"
})

# Find what AuthService depends on
mcp__plugin_serena_serena__find_symbol({
  "name_path_pattern": "AuthService/__init__",
  "include_body": true
})
```

### Phase 5: Create Architectural Memories (Optional)

Store findings using Graphiti MCP:

```python
# Load config and detect group_id
import yaml
from pathlib import Path
import subprocess

config_path = Path.cwd() / '.context-hub.yaml'
if config_path.exists():
    with open(config_path) as f:
        config = yaml.safe_load(f)
else:
    config = {'graphiti': {'group_id': 'auto'}}

group_id_setting = config.get('graphiti', {}).get('group_id', 'auto')

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

# Save architectural finding to Graphiti
result = mcp__graphiti__add_memory({
    "name": "AuthService: Core authentication component",
    "episode_body": "AuthService handles JWT validation, user sessions, and OAuth flows. Dependencies: UserRepository, TokenService, CacheService. Used by: all API endpoints via middleware.",
    "group_id": group_id,
    "source": "serena-analysis",
    "source_description": "Code architecture analysis via Serena"
})
```

**Note**: Graphiti automatically extracts entities and relationships from the episode body.

### Phase 6: Exploring the Knowledge Graph (Optional)

Explore relationships between components:

```python
# Search for related entities
nodes_result = mcp__graphiti__search_nodes({
    "query": "AuthService",
    "group_ids": [group_id],
    "max_nodes": 10
})

# Get facts showing relationships
facts_result = mcp__graphiti__search_memory_facts({
    "query": "AuthService dependencies relationships",
    "group_ids": [group_id],
    "max_facts": 20
})
```

**Note**: Graphiti automatically creates entities and relationships from saved memories.

## Architectural Patterns

When saving architectural insights, include:

- **Component Purpose**: What the component does
- **Dependencies**: What it requires/uses
- **Dependents**: What uses it
- **Patterns**: Design patterns employed
- **External Connections**: APIs, databases, services

Graphiti will automatically extract:
- Entities (components, services, classes)
- Relationships (depends_on, uses, extends, implements)
- Temporal relationships (created_before, modified_after)

## Example: FastAPI Project Analysis

```python
# 1. Find routers
mcp__plugin_serena_serena__search_for_pattern({
  "substring_pattern": "APIRouter\\(\\)|router\\s*=",
  "restrict_search_to_code_files": true
})

# 2. Analyze router structure
mcp__plugin_serena_serena__get_symbols_overview({
  "relative_path": "src/routers/users.py",
  "depth": 1
})

# 3. Find dependency injection
mcp__plugin_serena_serena__search_for_pattern({
  "substring_pattern": "Depends\\(",
  "restrict_search_to_code_files": true,
  "context_lines_before": 1,
  "context_lines_after": 1
})

# 4. Trace service dependencies
mcp__plugin_serena_serena__find_referencing_symbols({
  "name_path": "get_current_user",
  "relative_path": "src/dependencies/auth.py"
})

# 5. Create architecture memory
result = mcp__graphiti__add_memory({
    "name": "FastAPI app structure: Routers + Dependencies",
    "episode_body": "App uses router-based organization with dependency injection. Routers: /users, /auth, /products. Dependencies: get_current_user, get_db. All routes require auth except /auth/login.",
    "group_id": group_id,
    "source": "serena-analysis",
    "source_description": "FastAPI architecture analysis"
})
```

## Analysis Checklist

- [ ] Directory structure mapped
- [ ] Entry points identified
- [ ] Major components catalogued
- [ ] Dependencies traced
- [ ] External connections documented
- [ ] Key patterns identified
- [ ] Architectural insights saved to memory
- [ ] Knowledge graph explored (if needed)

## Tips

1. **Work incrementally** - Don't try to analyze everything at once
2. **Focus on interfaces** - Public methods/APIs matter more than internals
3. **Document decisions** - Create memories for WHY, not just WHAT
4. **Include context** - Dependencies, dependents, patterns
5. **Rich episode content** - Include detailed descriptions for better entity extraction by Graphiti
