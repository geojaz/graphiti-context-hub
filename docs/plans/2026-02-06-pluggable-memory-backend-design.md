# Pluggable Memory Backend Design

**Date:** 2026-02-06
**Status:** Approved
**Author:** Context Hub Plugin Team

## Overview

Refactor context-hub-plugin to support pluggable memory backends (Forgetful and Graphiti) with automatic project-based group detection, enabling users to switch backends via explicit configuration while maintaining a consistent API.

## Goals

1. **Backend Abstraction**: Create adapter layer that works with both Forgetful and Graphiti
2. **Automatic Scoping**: Detect project/group ID from git repository automatically
3. **Explicit Configuration**: Allow users to choose backend via config file
4. **Dynamic Discovery**: Preserve runtime tool discovery capabilities
5. **Minimal Context Usage**: Reduce agent context window usage with simplified API

## Architecture

### Core Components

```
Commands/Agents
      ↓
Memory Adapter (detect & route)
      ↓
Config Manager (hierarchical config + group detection)
      ↓
Backend Implementations
  ├── GraphitiBackend (mcp__graphiti__*)
  └── ForgetfulBackend (mcp__forgetful__*)
```

### Component Responsibilities

**1. Memory Adapter (`memory_adapter.py`)**
- Single entry point for all memory operations
- Detects backend from configuration
- Routes operations to appropriate MCP server
- Translates between unified API and backend-specific calls

**2. Config Manager (`config.py`)**
- Hierarchical config file discovery (cwd → project root → ~/.context-hub.yaml)
- Group ID detection (explicit > git repo > directory name)
- Default values: `backend=graphiti`, `group_id=auto`

**3. Backend Implementations**
- `GraphitiBackend`: Translates to `mcp__graphiti__*` tools
- `ForgetfulBackend`: Translates to `mcp__forgetful__*` tools
- Both implement common interface with dynamic discovery

## Configuration

### Config File Format

**`.context-hub.yaml`:**
```yaml
memory:
  # Backend selection
  backend: "graphiti"  # or "forgetful"

  # Group ID strategy
  group_id: "auto"  # or explicit value like "agent-context"

  # Future: Cross-project knowledge
  # global_group_id: "personal"

  # Optional: Backend-specific settings
  graphiti:
    endpoint: "http://localhost:8000/mcp"  # override default

  forgetful:
    # Future forgetful-specific settings
```

### Hierarchical Config Discovery

**Search order:**
1. Current directory: `./.context-hub.yaml`
2. Project root: `<project-root>/.context-hub.yaml` (searches for .git, pyproject.toml, package.json)
3. User home: `~/.context-hub.yaml`
4. Defaults: `backend=graphiti, group_id=auto`

### Group ID Detection

**Detection order:**
1. **Explicit config**: `group_id: "agent-context"` in config file
2. **Git repository**: Extract from `.git/config` remote or directory name
3. **Directory fallback**: Use basename of current working directory

**Example:**
- Path: `/Users/eric.hole/dev/geojaz/agent-context`
- Git remote: `git@github.com:user/agent-context.git`
- Detected group_id: `agent-context`

## Memory Adapter API

### Public Interface

```python
class MemoryAdapter:
    def __init__(self):
        self.config = load_config()
        self.backend = create_backend(self.config)

    # Core operations
    def query(self, query: str, limit: int = 10) -> List[Memory]:
        """Search for memories by semantic similarity"""

    def search_facts(self, query: str, limit: int = 10) -> List[Relationship]:
        """Search for relationships between entities"""

    def save(self, content: str, **metadata) -> str:
        """Save new memory/episode"""

    def explore(self, starting_point: str, depth: int = 2) -> KnowledgeGraph:
        """Deep traversal from a starting memory"""

    def list_recent(self, limit: int = 20) -> List[Memory]:
        """List recent memories"""

    # Dynamic discovery
    def list_operations(self) -> List[OperationInfo]:
        """Discover available operations for current backend"""

    def get_operation_schema(self, operation: str) -> Dict[str, Any]:
        """Get parameter schema for an operation"""

    def get_operation_examples(self, operation: str) -> List[str]:
        """Get usage examples for an operation"""
```

### Unified Data Models

```python
@dataclass
class Memory:
    id: str
    content: str
    created_at: datetime
    importance: Optional[int]  # Forgetful has this, Graphiti infers it
    metadata: Dict[str, Any]  # backend-specific extras

@dataclass
class Relationship:
    source: str
    target: str
    relation_type: str
    metadata: Dict[str, Any]

@dataclass
class OperationInfo:
    name: str
    description: str
    params: Dict[str, str]
    example: str
```

## Backend Implementations

### Backend Interface

```python
class Backend(ABC):
    @abstractmethod
    def query(self, query: str, group_id: str, limit: int) -> List[Memory]:
        pass

    @abstractmethod
    def search_facts(self, query: str, group_id: str, limit: int) -> List[Relationship]:
        pass

    @abstractmethod
    def save(self, content: str, group_id: str, **metadata) -> str:
        pass

    @abstractmethod
    def explore(self, starting_point: str, group_id: str, depth: int) -> KnowledgeGraph:
        pass

    @abstractmethod
    def list_recent(self, group_id: str, limit: int) -> List[Memory]:
        pass

    # Dynamic discovery
    @abstractmethod
    def get_capabilities(self) -> List[OperationInfo]:
        pass

    @abstractmethod
    def get_schema(self, operation: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_examples(self, operation: str) -> List[str]:
        pass
```

### GraphitiBackend Translation

**Key Mappings:**
- `query()` → `mcp__graphiti__search_memory_nodes`
- `search_facts()` → `mcp__graphiti__search_memory_facts`
- `save()` → `mcp__graphiti__add_memory` (episode-based)
- `list_recent()` → `mcp__graphiti__get_episodes`

**Dynamic Discovery:**
- Uses standard MCP `tools/list` to discover available tools
- Maps MCP tools to adapter operations
- Returns schemas from MCP tool definitions

**Example Implementation:**
```python
class GraphitiBackend(Backend):
    def query(self, query: str, group_id: str, limit: int) -> List[Memory]:
        result = mcp__graphiti__search_memory_nodes({
            "query": query,
            "group_id": group_id,
            "limit": limit
        })
        return self._parse_nodes_to_memories(result)

    def save(self, content: str, group_id: str, **metadata) -> str:
        result = mcp__graphiti__add_memory({
            "episode_body": content,
            "group_id": group_id,
            "name": metadata.get("title", "Untitled"),
            "source": "context-hub",
        })
        return result.episode_id

    def get_capabilities(self) -> List[OperationInfo]:
        # Query MCP server for available tools
        mcp_tools = self._list_mcp_tools()
        return self._map_mcp_tools_to_operations(mcp_tools)
```

### ForgetfulBackend Translation

**Key Mappings:**
- `query()` → `execute_forgetful_tool("query_memory", {project_ids: [...]})`
- `save()` → `execute_forgetful_tool("create_memory", {...})`
- `explore()` → Follow `linked_memory_ids` manually
- `group_id` → `project_id` mapping (discover or create project)

**Dynamic Discovery:**
- Uses Forgetful's native `discover_forgetful_tools()`
- Uses `how_to_use_forgetful_tool()` for schemas
- Maps Forgetful tools to adapter operations

**Project ID Mapping:**
```python
def _group_to_project_id(self, group_id: str) -> Optional[int]:
    # Discover or create project based on group_id
    projects = execute_forgetful_tool("list_projects", {})

    for project in projects:
        if project.name == group_id:
            return project.id

    # Create new project if doesn't exist
    result = execute_forgetful_tool("create_project", {
        "name": group_id,
        "description": f"Auto-created from group_id: {group_id}"
    })
    return result.project_id
```

## Command Updates

### Migration Pattern

**Before (Forgetful-specific):**
```markdown
# /memory-search command
Call: execute_forgetful_tool("query_memory", {
  "query": "{QUERY}",
  "project_ids": [discovered_id],
  "k": 10
})
```

**After (Adapter-based):**
```markdown
# /memory-search command
Call: memory.query(
  query="{QUERY}",
  limit=10
)
# Adapter handles group_id detection and backend routing
```

### Commands to Update

1. **`/context_gather`** - Use `memory.query()` instead of Forgetful
2. **`/memory-save`** - Use `memory.save()`, remove project discovery logic
3. **`/memory-search`** - Use `memory.query()`
4. **`/memory-list`** - Use `memory.list_recent()`
5. **`/memory-explore`** - Use `memory.explore()`
6. **`/encode-repo-serena`** - Use `memory.save()` for each entity
7. **`/context-hub-setup`** - Create/validate `.context-hub.yaml`, test connection

## Agent Updates

### Tool List Changes

**Before:**
```yaml
tools: mcp__forgetful__discover_forgetful_tools, mcp__forgetful__execute_forgetful_tool, ...
```

**After:**
```yaml
tools: memory_query, memory_save, memory_explore, memory_search_facts, memory_list_recent, memory_list_operations, memory_get_operation_schema, ...
# Plus: Read, Glob, Grep, Context7, WebSearch (unchanged)
```

### Prompt Updates

**Context-retrieval agent:**
- Replace `execute_forgetful_tool()` examples with `memory.query()`
- Update "Four-Source Strategy" to mention "Memory Backend (Graphiti/Forgetful)"
- Add dynamic discovery usage:
  ```
  # Discover available operations
  operations = memory.list_operations()

  # Learn how to use an operation
  schema = memory.get_operation_schema("query")
  examples = memory.get_operation_examples("query")
  ```

## Skills Updates

### Rename and Refactor

1. **`using-forgetful-memory`** → **`using-memory-adapter`**
   - Generic memory operations
   - Remove Forgetful-specific tool references
   - Add dynamic discovery examples
   - Document both Graphiti and Forgetful backends

2. **`exploring-knowledge-graph`**
   - Update to use `memory.explore()`
   - Remove manual link following (adapter handles it)

3. **`serena-code-architecture`**
   - Update memory saves to use `memory.save()`
   - Remove project_id discovery

## Context Window Benefits

**Traditional Approach:**
- Forgetful: Agent sees 3 meta-tools + needs to discover 38 tools
- Graphiti: Agent sees 8 tools directly

**Adapter Approach:**
- Agent sees: 5-7 operations (`memory.query`, `memory.save`, etc.)
- Uses LEAST context: Simple, high-level API
- Backend complexity completely hidden
- Dynamic discovery available when needed

**Result:** Significant context window savings while maintaining full functionality.

## Future Enhancements

### Cross-Project Knowledge

Support global knowledge that spans all projects:

```yaml
memory:
  backend: "graphiti"
  group_id: "agent-context"  # project-specific
  global_group_id: "personal"  # cross-project knowledge
```

**Query strategy:**
1. Search project-scoped first (`group_id="agent-context"`)
2. Also search global scope (`group_id="personal"`)
3. Merge and rank results

**Save strategy:**
- `/memory-save --scope project` → uses "agent-context"
- `/memory-save --scope global` → uses "personal"

### Backend Comparison Mode

Enable side-by-side testing:

```yaml
memory:
  backend: "both"  # Save to both, query both
  primary: "graphiti"  # Use for conflicts
```

Use cases:
- Data migration validation
- A/B testing backends
- Gradual migration confidence building

## Implementation Plan

### Phase 1: Core Adapter (Week 1)
1. Create `memory_adapter.py` with unified interface
2. Implement `config.py` with hierarchical discovery
3. Build `GraphitiBackend` with MCP tool mapping
4. Build `ForgetfulBackend` with project_id mapping
5. Add dynamic discovery to both backends

### Phase 2: Command Migration (Week 1-2)
1. Update `/memory-save` command
2. Update `/memory-search` command
3. Update `/memory-list` command
4. Update `/context_gather` command
5. Update `/memory-explore` command
6. Update `/encode-repo-serena` command
7. Update `/context-hub-setup` command

### Phase 3: Agent & Skills (Week 2)
1. Update context-retrieval agent
2. Rename and update `using-forgetful-memory` skill
3. Update `exploring-knowledge-graph` skill
4. Update `serena-code-architecture` skill

### Phase 4: Testing & Documentation (Week 2)
1. Test with Graphiti backend
2. Test with Forgetful backend
3. Test backend switching
4. Update README with new configuration
5. Create migration guide for existing users

## Success Criteria

- ✅ Can switch between Graphiti and Forgetful via config file
- ✅ Group ID auto-detected from git repository
- ✅ All commands work with both backends
- ✅ Dynamic tool discovery functional
- ✅ Context window usage reduced vs direct MCP calls
- ✅ No breaking changes to command UX

## Trade-offs

**Pros:**
- Future-proof for additional backends
- Cleaner abstraction
- Better context window usage
- Gradual migration path
- Side-by-side comparison possible

**Cons:**
- Additional indirection layer (minimal overhead)
- Need to maintain backend mappings
- Initial implementation time (~2-3 hours)

**Decision:** Benefits outweigh costs - proceed with pluggable backend design.
