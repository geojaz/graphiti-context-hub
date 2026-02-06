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

        result = mcp__forgetful__execute_forgetful_tool("query_memory", {
            "query": query,
            "project_ids": [project_id] if project_id else None,
            "k": limit,
            "include_links": True
        })

        return self._parse_forgetful_memories(result)

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

        result = mcp__forgetful__execute_forgetful_tool("create_memory", {
            "title": metadata.get("title", "Untitled"),
            "content": content,
            "importance": metadata.get("importance", 5),
            "project_ids": [project_id] if project_id else [],
            "keywords": metadata.get("keywords", []),
            "tags": metadata.get("tags", []),
            "context": metadata.get("context", "")
        })

        return str(result.get("memory_id", result.get("id", "unknown")))

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

        result = mcp__forgetful__execute_forgetful_tool("list_memories", {
            "project_ids": [project_id] if project_id else None,
            "limit": limit,
            "sort_by": "created_at",
            "sort_order": "desc"
        })

        return self._parse_forgetful_memories(result)

    # Dynamic discovery

    def get_capabilities(self) -> List[OperationInfo]:
        """Discover capabilities using Forgetful's meta-tools."""
        tools = mcp__forgetful__discover_forgetful_tools()

        # Map Forgetful tools to our operations
        # For now, return static list (full mapping can be done later)
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
            OperationInfo(
                name="list_recent",
                description="List recent memories",
                params={"limit": "int"},
                example='memory.list_recent(limit=20)'
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

        # List and find
        result = mcp__forgetful__execute_forgetful_tool("list_projects", {})

        for project in result.get("projects", []):
            if project.get("name") == group_id:
                project_id = project.get("id")
                self._project_cache[group_id] = project_id
                return project_id

        # Create new project
        create_result = mcp__forgetful__execute_forgetful_tool("create_project", {
            "name": group_id,
            "description": f"Auto-created from group_id: {group_id}"
        })

        project_id = create_result.get("project_id", create_result.get("id"))
        self._project_cache[group_id] = project_id
        return project_id

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
