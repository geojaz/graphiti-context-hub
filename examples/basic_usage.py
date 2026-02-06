#!/usr/bin/env python3
"""
Example usage of the memory adapter.

This demonstrates basic operations without MCP integration.
"""
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.memory_adapter import MemoryAdapter


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
