# Pluggable Memory Backend Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refactor context-hub-plugin to support switchable memory backends (Forgetful/Graphiti) with auto-detected project scoping

**Architecture:** Memory adapter layer that discovers config, detects group_id from git, and routes operations to backend-specific MCP tool implementations

**Tech Stack:** Python 3.10+, YAML config, Git integration, MCP tools (Forgetful/Graphiti)

---

## Task 1: Project Structure Setup

**Files:**
- Create: `lib/__init__.py`
- Create: `lib/models.py`
- Create: `lib/config.py`
- Create: `lib/backends/__init__.py`
- Create: `lib/backends/base.py`
- Create: `.context-hub.yaml` (example config)

**Step 1: Create library directory structure**

```bash
mkdir -p lib/backends
touch lib/__init__.py
touch lib/backends/__init__.py
```

**Step 2: Create data models**

File: `lib/models.py`

```python
"""Unified data models for memory operations."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Memory:
    """Unified memory representation across backends."""
    id: str
    content: str
    created_at: datetime
    importance: Optional[int] = None  # Forgetful has this, Graphiti infers it
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Relationship:
    """Relationship between entities in knowledge graph."""
    source: str
    target: str
    relation_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeGraph:
    """Graph of memories and their relationships."""
    nodes: List[Memory]
    edges: List[Relationship]


@dataclass
class OperationInfo:
    """Information about available memory operations."""
    name: str
    description: str
    params: Dict[str, str]
    example: str
```

**Step 3: Create example config file**

File: `.context-hub.yaml`

```yaml
memory:
  # Backend selection
  backend: "graphiti"  # or "forgetful"

  # Group ID strategy
  group_id: "auto"  # or explicit value like "my-project"

  # Optional: Backend-specific settings
  graphiti:
    endpoint: "http://localhost:8000/mcp"

  forgetful:
    # Future settings
```

**Step 4: Commit structure**

```bash
git add lib/ .context-hub.yaml
git commit -m "feat: add library structure and data models

- Create lib/ directory for Python adapter code
- Add unified data models (Memory, Relationship, KnowledgeGraph)
- Add example .context-hub.yaml configuration"
```

---

## Task 2: Configuration Manager

**Files:**
- Create: `lib/config.py`
- Modify: `lib/__init__.py` (add exports)

**Step 1: Implement config loading**

File: `lib/config.py`

```python
"""Configuration management with hierarchical discovery."""
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

import yaml


@dataclass
class MemoryConfig:
    """Memory backend configuration."""
    backend: str = "graphiti"
    group_id: str = "auto"
    graphiti: Dict[str, str] = field(default_factory=lambda: {
        "endpoint": "http://localhost:8000/mcp"
    })
    forgetful: Dict[str, str] = field(default_factory=dict)


@dataclass
class Config:
    """Root configuration."""
    memory: MemoryConfig = field(default_factory=MemoryConfig)


def find_project_root() -> Optional[Path]:
    """Find project root by looking for markers."""
    cwd = Path.cwd()

    # Walk up directory tree
    for parent in [cwd] + list(cwd.parents):
        # Check for project markers
        markers = ['.git', 'pyproject.toml', 'package.json', 'pom.xml']
        if any((parent / marker).exists() for marker in markers):
            return parent

    return None


def find_config_file() -> Optional[Path]:
    """
    Find config file using hierarchical search.

    Search order:
    1. Current directory: ./.context-hub.yaml
    2. Project root: <root>/.context-hub.yaml
    3. User home: ~/.context-hub.yaml
    4. None (use defaults)
    """
    # 1. Current directory
    cwd_config = Path.cwd() / '.context-hub.yaml'
    if cwd_config.exists():
        return cwd_config

    # 2. Project root
    project_root = find_project_root()
    if project_root:
        root_config = project_root / '.context-hub.yaml'
        if root_config.exists():
            return root_config

    # 3. User home
    home_config = Path.home() / '.context-hub.yaml'
    if home_config.exists():
        return home_config

    # 4. No config found
    return None


def load_config() -> Config:
    """Load configuration from file or use defaults."""
    config_file = find_config_file()

    if not config_file:
        # Use defaults
        return Config()

    with open(config_file, 'r') as f:
        data = yaml.safe_load(f) or {}

    # Parse memory config
    memory_data = data.get('memory', {})
    memory_config = MemoryConfig(
        backend=memory_data.get('backend', 'graphiti'),
        group_id=memory_data.get('group_id', 'auto'),
        graphiti=memory_data.get('graphiti', {'endpoint': 'http://localhost:8000/mcp'}),
        forgetful=memory_data.get('forgetful', {})
    )

    return Config(memory=memory_config)


def get_git_repo_name() -> Optional[str]:
    """Extract repository name from git remote or directory."""
    try:
        # Try git remote
        result = subprocess.run(
            ['git', 'config', '--get', 'remote.origin.url'],
            capture_output=True,
            text=True,
            check=True
        )

        # Parse repo name from URL
        # Examples:
        #   git@github.com:user/repo.git -> repo
        #   https://github.com/user/repo.git -> repo
        url = result.stdout.strip()
        if url:
            # Extract last part before .git
            parts = url.rstrip('/').replace('.git', '').split('/')
            if parts:
                return parts[-1]

    except (subprocess.CalledProcessError, FileNotFoundError):
        # Git command failed, try .git directory name
        project_root = find_project_root()
        if project_root and (project_root / '.git').exists():
            return project_root.name

    return None


def detect_group_id(config: Config) -> str:
    """
    Detect group_id using strategy from config.

    Detection order:
    1. Explicit config value (if not "auto")
    2. Git repository name
    3. Current directory name (fallback)
    """
    # 1. Explicit override
    if config.memory.group_id != "auto":
        return config.memory.group_id

    # 2. Git repository name
    git_name = get_git_repo_name()
    if git_name:
        return git_name

    # 3. Directory fallback
    return Path.cwd().name
```

**Step 2: Update lib/__init__.py**

File: `lib/__init__.py`

```python
"""Context Hub memory adapter library."""
from .config import Config, MemoryConfig, load_config, detect_group_id
from .models import Memory, Relationship, KnowledgeGraph, OperationInfo

__all__ = [
    'Config',
    'MemoryConfig',
    'load_config',
    'detect_group_id',
    'Memory',
    'Relationship',
    'KnowledgeGraph',
    'OperationInfo',
]
```

**Step 3: Test config loading**

Create test file: `lib/test_config.py` (temporary, delete after testing)

```python
"""Quick test of config loading."""
from config import load_config, detect_group_id

config = load_config()
print(f"Backend: {config.memory.backend}")
print(f"Config group_id: {config.memory.group_id}")

group_id = detect_group_id(config)
print(f"Detected group_id: {group_id}")
```

Run: `cd lib && python test_config.py`
Expected: Prints backend, config group_id, and detected group_id

**Step 4: Clean up and commit**

```bash
rm lib/test_config.py
git add lib/config.py lib/__init__.py
git commit -m "feat: add configuration manager

- Hierarchical config discovery (cwd → project root → home)
- Auto-detect group_id from git repo or directory
- YAML-based configuration with defaults"
```

---

## Task 3: Backend Base Interface

**Files:**
- Create: `lib/backends/base.py`
- Modify: `lib/backends/__init__.py`

**Step 1: Create abstract backend interface**

File: `lib/backends/base.py`

```python
"""Abstract base class for memory backends."""
from abc import ABC, abstractmethod
from typing import List

from ..models import Memory, Relationship, KnowledgeGraph, OperationInfo


class Backend(ABC):
    """Abstract interface that all backends must implement."""

    @abstractmethod
    def query(self, query: str, group_id: str, limit: int) -> List[Memory]:
        """Search for memories by semantic similarity."""
        pass

    @abstractmethod
    def search_facts(self, query: str, group_id: str, limit: int) -> List[Relationship]:
        """Search for relationships between entities."""
        pass

    @abstractmethod
    def save(self, content: str, group_id: str, **metadata) -> str:
        """Save new memory/episode."""
        pass

    @abstractmethod
    def explore(self, starting_point: str, group_id: str, depth: int) -> KnowledgeGraph:
        """Deep traversal from a starting memory."""
        pass

    @abstractmethod
    def list_recent(self, group_id: str, limit: int) -> List[Memory]:
        """List recent memories."""
        pass

    # Dynamic discovery methods

    @abstractmethod
    def get_capabilities(self) -> List[OperationInfo]:
        """Discover available operations for this backend."""
        pass

    @abstractmethod
    def get_schema(self, operation: str) -> dict:
        """Get parameter schema for an operation."""
        pass

    @abstractmethod
    def get_examples(self, operation: str) -> List[str]:
        """Get usage examples for an operation."""
        pass
```

**Step 2: Update backends/__init__.py**

File: `lib/backends/__init__.py`

```python
"""Memory backend implementations."""
from .base import Backend

__all__ = ['Backend']
```

**Step 3: Commit interface**

```bash
git add lib/backends/base.py lib/backends/__init__.py
git commit -m "feat: add backend abstract interface

- Define Backend ABC with all required methods
- Core operations: query, save, explore, search_facts, list_recent
- Dynamic discovery: get_capabilities, get_schema, get_examples"
```

---

## Task 4: Graphiti Backend Implementation

**Files:**
- Create: `lib/backends/graphiti.py`
- Modify: `lib/backends/__init__.py`

**Step 1: Implement GraphitiBackend**

File: `lib/backends/graphiti.py`

```python
"""Graphiti backend implementation."""
from datetime import datetime
from typing import List

from ..models import Memory, Relationship, KnowledgeGraph, OperationInfo
from .base import Backend


class GraphitiBackend(Backend):
    """Backend implementation for Graphiti MCP server."""

    # Static operation definitions
    OPERATIONS = {
        "query": {
            "description": "Search for memories by semantic similarity",
            "params": {"query": "str", "limit": "int"},
            "example": 'memory.query("auth patterns", limit=10)'
        },
        "search_facts": {
            "description": "Search for relationships between entities",
            "params": {"query": "str", "limit": "int"},
            "example": 'memory.search_facts("authentication flow", limit=20)'
        },
        "save": {
            "description": "Save new episode to knowledge graph",
            "params": {"content": "str", "title": "str (optional)"},
            "example": 'memory.save("Decision: Using JWT for auth", title="Auth Decision")'
        },
        "explore": {
            "description": "Deep traversal from a starting memory",
            "params": {"starting_point": "str", "depth": "int"},
            "example": 'memory.explore("authentication", depth=2)'
        },
        "list_recent": {
            "description": "List recent memories",
            "params": {"limit": "int"},
            "example": 'memory.list_recent(limit=20)'
        }
    }

    def query(self, query: str, group_id: str, limit: int) -> List[Memory]:
        """Search memories using Graphiti search_memory_nodes."""
        # NOTE: Actual MCP call will be added when integrating with commands
        # For now, this is a stub that returns the expected structure

        # Future implementation:
        # result = mcp__graphiti__search_memory_nodes({
        #     "query": query,
        #     "group_id": group_id,
        #     "limit": limit
        # })
        # return self._parse_nodes_to_memories(result)

        return []

    def search_facts(self, query: str, group_id: str, limit: int) -> List[Relationship]:
        """Search relationships using Graphiti search_memory_facts."""
        # Future implementation:
        # result = mcp__graphiti__search_memory_facts({
        #     "query": query,
        #     "group_id": group_id,
        #     "limit": limit
        # })
        # return self._parse_facts_to_relationships(result)

        return []

    def save(self, content: str, group_id: str, **metadata) -> str:
        """Save episode using Graphiti add_memory."""
        # Future implementation:
        # result = mcp__graphiti__add_memory({
        #     "episode_body": content,
        #     "group_id": group_id,
        #     "name": metadata.get("title", "Untitled"),
        #     "source": "context-hub",
        # })
        # return result.get("episode_id", "")

        return "stub-episode-id"

    def explore(self, starting_point: str, group_id: str, depth: int) -> KnowledgeGraph:
        """Explore knowledge graph from starting point."""
        # Combine nodes + facts to build graph
        nodes = self.query(starting_point, group_id, 10)
        edges = self.search_facts(starting_point, group_id, 20)

        return KnowledgeGraph(nodes=nodes, edges=edges)

    def list_recent(self, group_id: str, limit: int) -> List[Memory]:
        """List recent episodes using get_episodes."""
        # Future implementation:
        # result = mcp__graphiti__get_episodes({
        #     "group_id": group_id,
        #     "limit": limit
        # })
        # return self._parse_episodes_to_memories(result)

        return []

    # Dynamic discovery

    def get_capabilities(self) -> List[OperationInfo]:
        """Return available operations."""
        return [
            OperationInfo(name=op, **details)
            for op, details in self.OPERATIONS.items()
        ]

    def get_schema(self, operation: str) -> dict:
        """Get schema for operation."""
        if operation not in self.OPERATIONS:
            raise ValueError(f"Unknown operation: {operation}")

        op_info = self.OPERATIONS[operation]
        return {
            "description": op_info["description"],
            "params": op_info["params"]
        }

    def get_examples(self, operation: str) -> List[str]:
        """Get usage examples."""
        if operation not in self.OPERATIONS:
            raise ValueError(f"Unknown operation: {operation}")

        return [self.OPERATIONS[operation]["example"]]

    # Helper methods (future implementation)

    def _parse_nodes_to_memories(self, result: dict) -> List[Memory]:
        """Parse Graphiti nodes to Memory objects."""
        memories = []

        for node in result.get("nodes", []):
            memories.append(Memory(
                id=node.get("uuid", ""),
                content=node.get("name", ""),
                created_at=datetime.fromisoformat(node.get("created_at", datetime.now().isoformat())),
                metadata={"summary": node.get("summary", "")}
            ))

        return memories

    def _parse_facts_to_relationships(self, result: dict) -> List[Relationship]:
        """Parse Graphiti facts to Relationship objects."""
        relationships = []

        for fact in result.get("facts", []):
            relationships.append(Relationship(
                source=fact.get("source_node_uuid", ""),
                target=fact.get("target_node_uuid", ""),
                relation_type=fact.get("fact", ""),
                metadata={"created_at": fact.get("created_at", "")}
            ))

        return relationships
```

**Step 2: Update backends/__init__.py**

File: `lib/backends/__init__.py`

```python
"""Memory backend implementations."""
from .base import Backend
from .graphiti import GraphitiBackend

__all__ = ['Backend', 'GraphitiBackend']
```

**Step 3: Test GraphitiBackend instantiation**

Create test: `lib/test_graphiti.py` (temporary)

```python
"""Quick test of GraphitiBackend."""
from backends.graphiti import GraphitiBackend

backend = GraphitiBackend()

# Test capabilities discovery
caps = backend.get_capabilities()
print(f"Found {len(caps)} operations:")
for cap in caps:
    print(f"  - {cap.name}: {cap.description}")

# Test schema retrieval
schema = backend.get_schema("query")
print(f"\nquery schema: {schema}")

# Test examples
examples = backend.get_examples("save")
print(f"\nsave examples: {examples}")
```

Run: `cd lib && python test_graphiti.py`
Expected: Lists 5 operations, shows query schema, shows save example

**Step 4: Clean up and commit**

```bash
rm lib/test_graphiti.py
git add lib/backends/graphiti.py lib/backends/__init__.py
git commit -m "feat: add Graphiti backend implementation

- Implement all Backend interface methods
- Static operation definitions with examples
- Stub MCP calls (to be connected later)
- Helper methods for parsing Graphiti responses"
```

---

## Task 5: Forgetful Backend Implementation

**Files:**
- Create: `lib/backends/forgetful.py`
- Modify: `lib/backends/__init__.py`

**Step 1: Implement ForgetfulBackend**

File: `lib/backends/forgetful.py`

```python
"""Forgetful backend implementation."""
from datetime import datetime
from typing import List, Optional

from ..models import Memory, Relationship, KnowledgeGraph, OperationInfo
from .base import Backend


class ForgetfulBackend(Backend):
    """Backend implementation for Forgetful MCP server."""

    def __init__(self):
        self._project_cache = {}  # Cache group_id -> project_id mapping

    def query(self, query: str, group_id: str, limit: int) -> List[Memory]:
        """Search memories using Forgetful query_memory."""
        project_id = self._group_to_project_id(group_id)

        # Future implementation:
        # result = mcp__forgetful__execute_forgetful_tool("query_memory", {
        #     "query": query,
        #     "project_ids": [project_id] if project_id else None,
        #     "k": limit
        # })
        # return self._parse_forgetful_memories(result)

        return []

    def search_facts(self, query: str, group_id: str, limit: int) -> List[Relationship]:
        """
        Search for relationships.

        Note: Forgetful doesn't have direct fact search, so we:
        1. Query memories
        2. Extract linked_memory_ids as relationships
        """
        memories = self.query(query, group_id, limit)
        relationships = []

        for memory in memories:
            linked_ids = memory.metadata.get("linked_memory_ids", [])
            for linked_id in linked_ids:
                relationships.append(Relationship(
                    source=memory.id,
                    target=str(linked_id),
                    relation_type="linked_to",
                    metadata={}
                ))

        return relationships

    def save(self, content: str, group_id: str, **metadata) -> str:
        """Save memory using Forgetful create_memory."""
        project_id = self._group_to_project_id(group_id)

        # Future implementation:
        # result = mcp__forgetful__execute_forgetful_tool("create_memory", {
        #     "title": metadata.get("title", "Untitled"),
        #     "content": content,
        #     "importance": metadata.get("importance", 5),
        #     "project_ids": [project_id] if project_id else [],
        #     "keywords": metadata.get("keywords", []),
        #     "tags": metadata.get("tags", []),
        # })
        # return str(result.get("memory_id", ""))

        return "stub-memory-id"

    def explore(self, starting_point: str, group_id: str, depth: int) -> KnowledgeGraph:
        """Explore by following linked_memory_ids."""
        visited = set()
        nodes = []
        edges = []

        # BFS traversal
        queue = [(starting_point, 0)]

        while queue:
            query_text, current_depth = queue.pop(0)

            if current_depth > depth:
                break

            # Query for memories
            memories = self.query(query_text, group_id, 5)

            for memory in memories:
                if memory.id in visited:
                    continue

                visited.add(memory.id)
                nodes.append(memory)

                # Extract relationships
                linked_ids = memory.metadata.get("linked_memory_ids", [])
                for linked_id in linked_ids:
                    edges.append(Relationship(
                        source=memory.id,
                        target=str(linked_id),
                        relation_type="linked_to",
                        metadata={}
                    ))

                    # Queue linked memories for next level
                    if current_depth < depth:
                        queue.append((str(linked_id), current_depth + 1))

        return KnowledgeGraph(nodes=nodes, edges=edges)

    def list_recent(self, group_id: str, limit: int) -> List[Memory]:
        """List recent memories using list_memories."""
        project_id = self._group_to_project_id(group_id)

        # Future implementation:
        # result = mcp__forgetful__execute_forgetful_tool("list_memories", {
        #     "project_ids": [project_id] if project_id else None,
        #     "limit": limit,
        #     "sort_by": "created_at",
        #     "sort_order": "desc"
        # })
        # return self._parse_forgetful_memories(result)

        return []

    # Dynamic discovery

    def get_capabilities(self) -> List[OperationInfo]:
        """Discover capabilities using Forgetful's meta-tools."""
        # Future implementation:
        # tools = mcp__forgetful__discover_forgetful_tools()
        # return self._map_forgetful_tools_to_operations(tools)

        # Static fallback
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
        ]

    def get_schema(self, operation: str) -> dict:
        """Get schema using how_to_use_forgetful_tool."""
        # Future implementation:
        # tool_name = self._operation_to_tool_name(operation)
        # return mcp__forgetful__how_to_use_forgetful_tool(tool_name)

        return {"description": f"Schema for {operation}", "params": {}}

    def get_examples(self, operation: str) -> List[str]:
        """Get usage examples from tool documentation."""
        # Future: extract from how_to_use_forgetful_tool response
        return [f'memory.{operation}(...)']

    # Helper methods

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

        # Future implementation:
        # projects = mcp__forgetful__execute_forgetful_tool("list_projects", {})
        #
        # for project in projects.get("projects", []):
        #     if project.get("name") == group_id:
        #         project_id = project.get("id")
        #         self._project_cache[group_id] = project_id
        #         return project_id
        #
        # # Create new project
        # result = mcp__forgetful__execute_forgetful_tool("create_project", {
        #     "name": group_id,
        #     "description": f"Auto-created from group_id: {group_id}"
        # })
        # project_id = result.get("project_id")
        # self._project_cache[group_id] = project_id
        # return project_id

        # Stub for now
        return 1

    def _parse_forgetful_memories(self, result: dict) -> List[Memory]:
        """Parse Forgetful memory format to Memory objects."""
        memories = []

        for mem in result.get("memories", []):
            memories.append(Memory(
                id=str(mem.get("id", "")),
                content=mem.get("content", ""),
                created_at=datetime.fromisoformat(mem.get("created_at", datetime.now().isoformat())),
                importance=mem.get("importance"),
                metadata={
                    "title": mem.get("title", ""),
                    "keywords": mem.get("keywords", []),
                    "tags": mem.get("tags", []),
                    "linked_memory_ids": mem.get("linked_memory_ids", [])
                }
            ))

        return memories
```

**Step 2: Update backends/__init__.py**

File: `lib/backends/__init__.py`

```python
"""Memory backend implementations."""
from .base import Backend
from .graphiti import GraphitiBackend
from .forgetful import ForgetfulBackend

__all__ = ['Backend', 'GraphitiBackend', 'ForgetfulBackend']
```

**Step 3: Test ForgetfulBackend**

Create test: `lib/test_forgetful.py` (temporary)

```python
"""Quick test of ForgetfulBackend."""
from backends.forgetful import ForgetfulBackend

backend = ForgetfulBackend()

# Test capabilities
caps = backend.get_capabilities()
print(f"Found {len(caps)} operations")

# Test project mapping
project_id = backend._group_to_project_id("test-project")
print(f"Project ID for 'test-project': {project_id}")
```

Run: `cd lib && python test_forgetful.py`
Expected: Shows operations count and project ID mapping

**Step 4: Clean up and commit**

```bash
rm lib/test_forgetful.py
git add lib/backends/forgetful.py lib/backends/__init__.py
git commit -m "feat: add Forgetful backend implementation

- Implement all Backend interface methods
- Project ID mapping with caching
- Manual graph exploration via linked_memory_ids
- Stub MCP calls (to be connected later)"
```

---

## Task 6: Memory Adapter

**Files:**
- Create: `lib/memory_adapter.py`
- Modify: `lib/__init__.py`

**Step 1: Implement MemoryAdapter**

File: `lib/memory_adapter.py`

```python
"""Main memory adapter that routes to backends."""
from typing import List

from .backends import Backend, GraphitiBackend, ForgetfulBackend
from .config import Config, load_config, detect_group_id
from .models import Memory, Relationship, KnowledgeGraph, OperationInfo


class MemoryAdapter:
    """
    Unified interface for memory operations.

    Automatically detects backend from config and routes operations
    to appropriate implementation (Graphiti or Forgetful).
    """

    def __init__(self, config: Config = None):
        """
        Initialize adapter with config.

        Args:
            config: Configuration (loads from file if None)
        """
        self.config = config or load_config()
        self.group_id = detect_group_id(self.config)
        self.backend = self._create_backend()

    def _create_backend(self) -> Backend:
        """Create backend instance based on config."""
        backend_name = self.config.memory.backend.lower()

        if backend_name == "graphiti":
            return GraphitiBackend()
        elif backend_name == "forgetful":
            return ForgetfulBackend()
        else:
            raise ValueError(f"Unknown backend: {backend_name}")

    # Core operations (delegate to backend)

    def query(self, query: str, limit: int = 10) -> List[Memory]:
        """
        Search for memories by semantic similarity.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching memories
        """
        return self.backend.query(query, self.group_id, limit)

    def search_facts(self, query: str, limit: int = 10) -> List[Relationship]:
        """
        Search for relationships between entities.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of relationships
        """
        return self.backend.search_facts(query, self.group_id, limit)

    def save(self, content: str, **metadata) -> str:
        """
        Save new memory/episode.

        Args:
            content: Memory content
            **metadata: Backend-specific metadata (title, importance, etc.)

        Returns:
            Memory/episode ID
        """
        return self.backend.save(content, self.group_id, **metadata)

    def explore(self, starting_point: str, depth: int = 2) -> KnowledgeGraph:
        """
        Deep traversal from a starting memory.

        Args:
            starting_point: Query to find starting memories
            depth: How many levels to traverse

        Returns:
            Knowledge graph of connected memories
        """
        return self.backend.explore(starting_point, self.group_id, depth)

    def list_recent(self, limit: int = 20) -> List[Memory]:
        """
        List recent memories.

        Args:
            limit: Maximum results

        Returns:
            List of recent memories
        """
        return self.backend.list_recent(self.group_id, limit)

    # Dynamic discovery

    def list_operations(self) -> List[OperationInfo]:
        """
        Discover available operations for current backend.

        Returns:
            List of operation info
        """
        return self.backend.get_capabilities()

    def get_operation_schema(self, operation: str) -> dict:
        """
        Get parameter schema for an operation.

        Args:
            operation: Operation name

        Returns:
            Schema dictionary
        """
        return self.backend.get_schema(operation)

    def get_operation_examples(self, operation: str) -> List[str]:
        """
        Get usage examples for an operation.

        Args:
            operation: Operation name

        Returns:
            List of example code strings
        """
        return self.backend.get_examples(operation)
```

**Step 2: Update lib/__init__.py**

File: `lib/__init__.py`

```python
"""Context Hub memory adapter library."""
from .config import Config, MemoryConfig, load_config, detect_group_id
from .models import Memory, Relationship, KnowledgeGraph, OperationInfo
from .memory_adapter import MemoryAdapter

__all__ = [
    'Config',
    'MemoryConfig',
    'load_config',
    'detect_group_id',
    'Memory',
    'Relationship',
    'KnowledgeGraph',
    'OperationInfo',
    'MemoryAdapter',
]
```

**Step 3: Test MemoryAdapter end-to-end**

Create test: `lib/test_adapter.py` (temporary)

```python
"""End-to-end test of MemoryAdapter."""
from memory_adapter import MemoryAdapter

# Test with default config (will use graphiti)
adapter = MemoryAdapter()
print(f"Using backend: {adapter.config.memory.backend}")
print(f"Detected group_id: {adapter.group_id}")

# Test operations
print("\nAvailable operations:")
for op in adapter.list_operations():
    print(f"  - {op.name}: {op.description}")

# Test query (stub for now)
print("\nQuerying memories...")
memories = adapter.query("test", limit=5)
print(f"Found {len(memories)} memories")

# Test save (stub for now)
print("\nSaving memory...")
memory_id = adapter.save("Test memory content", title="Test")
print(f"Saved with ID: {memory_id}")
```

Run: `cd lib && python test_adapter.py`
Expected: Shows backend, group_id, operations, and stub results

**Step 4: Clean up and commit**

```bash
rm lib/test_adapter.py
git add lib/memory_adapter.py lib/__init__.py
git commit -m "feat: add MemoryAdapter main interface

- Single entry point for all memory operations
- Auto-detects backend and group_id from config
- Delegates to backend implementations
- Provides clean API for commands/agents"
```

---

## Task 7: Create Example Usage Script

**Files:**
- Create: `examples/basic_usage.py`

**Step 1: Create example script**

```bash
mkdir -p examples
```

File: `examples/basic_usage.py`

```python
#!/usr/bin/env python3
"""
Example usage of the memory adapter.

This demonstrates basic operations without MCP integration.
"""
import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from memory_adapter import MemoryAdapter


def main():
    """Run example usage."""
    print("=== Memory Adapter Example ===\n")

    # 1. Initialize adapter (auto-detects config and group_id)
    adapter = MemoryAdapter()
    print(f"Backend: {adapter.config.memory.backend}")
    print(f"Group ID: {adapter.group_id}\n")

    # 2. Discover operations
    print("Available operations:")
    for op in adapter.list_operations():
        print(f"  {op.name}: {op.description}")
        print(f"    Example: {op.example}\n")

    # 3. Query memories
    print("Querying for 'authentication'...")
    memories = adapter.query("authentication", limit=5)
    print(f"Found {len(memories)} memories\n")

    # 4. Save a memory
    print("Saving new memory...")
    memory_id = adapter.save(
        "Decision: Use JWT for authentication",
        title="Auth Decision",
        importance=9
    )
    print(f"Saved with ID: {memory_id}\n")

    # 5. List recent
    print("Listing recent memories...")
    recent = adapter.list_recent(limit=10)
    print(f"Found {len(recent)} recent memories\n")

    # 6. Explore knowledge graph
    print("Exploring knowledge graph from 'authentication'...")
    graph = adapter.explore("authentication", depth=2)
    print(f"Graph has {len(graph.nodes)} nodes and {len(graph.edges)} edges")


if __name__ == "__main__":
    main()
```

**Step 2: Make executable and test**

```bash
chmod +x examples/basic_usage.py
python examples/basic_usage.py
```

Expected: Prints backend info, operations, and stub results

**Step 3: Commit example**

```bash
git add examples/basic_usage.py
git commit -m "feat: add basic usage example

- Demonstrates MemoryAdapter initialization
- Shows operation discovery
- Example of core operations (query, save, explore)
- Useful for testing without MCP integration"
```

---

## Task 8: Add Dependencies

**Files:**
- Create: `requirements.txt`
- Create: `README-lib.md`

**Step 1: Document dependencies**

File: `requirements.txt`

```txt
# Core dependencies for memory adapter library
pyyaml>=6.0
```

**Step 2: Create library README**

File: `README-lib.md`

```markdown
# Context Hub Memory Adapter Library

Python library for pluggable memory backend support.

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from lib import MemoryAdapter

# Initialize (auto-detects config and group_id)
adapter = MemoryAdapter()

# Query memories
memories = adapter.query("authentication patterns", limit=10)

# Save a memory
memory_id = adapter.save(
    "Decision: Using JWT for auth",
    title="Auth Decision"
)

# Explore knowledge graph
graph = adapter.explore("authentication", depth=2)
```

## Configuration

Create `.context-hub.yaml` in project root:

```yaml
memory:
  backend: "graphiti"  # or "forgetful"
  group_id: "auto"     # auto-detect from git or set explicitly
```

## Backend Support

- **Graphiti**: Knowledge graph with automatic entity extraction
- **Forgetful**: Atomic memories with manual linking

## Architecture

```
MemoryAdapter
  ├── ConfigManager (hierarchical config discovery)
  ├── GraphitiBackend (mcp__graphiti__* tools)
  └── ForgetfulBackend (mcp__forgetful__* tools)
```

See `examples/basic_usage.py` for detailed examples.
```

**Step 3: Commit documentation**

```bash
git add requirements.txt README-lib.md
git commit -m "docs: add library documentation and dependencies

- Add requirements.txt with pyyaml
- Add README-lib.md with quick start and architecture
- Document configuration and backend support"
```

---

## Summary

**Phase 1 Complete: Core Adapter Implementation** ✅

**What's Been Built:**
1. ✅ Project structure (`lib/`, `lib/backends/`)
2. ✅ Data models (Memory, Relationship, KnowledgeGraph, OperationInfo)
3. ✅ Config manager (hierarchical discovery, group_id detection)
4. ✅ Backend interface (abstract base class)
5. ✅ Graphiti backend (with stub MCP calls)
6. ✅ Forgetful backend (with stub MCP calls)
7. ✅ Memory adapter (unified API)
8. ✅ Example usage script
9. ✅ Documentation

**Next Steps:**

The adapter is ready to be integrated with actual commands. The remaining tasks are:

**Phase 2: Command Integration**
- Update `/memory-save` command to use adapter
- Update `/memory-search` command
- Update `/context_gather` command
- Update other commands

**Phase 3: MCP Integration**
- Replace stub calls with actual MCP tool invocations
- Test with live Graphiti server
- Test with Forgetful server (if available)

**Phase 4: Agent & Skills Updates**
- Update context-retrieval agent
- Rename skills
- Update documentation

Would you like to continue with **Phase 2: Command Integration**, or would you prefer to test the adapter with live MCP calls first?
