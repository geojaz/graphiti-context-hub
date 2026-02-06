#!/usr/bin/env python3
"""
End-to-end test of adapter with both backends.

NOTE: This test will fail when run directly with python because MCP tools
are only available in Claude Code's execution context.
This file is kept for documentation and manual testing via Claude Code.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))

from bridge import (
    memory_query,
    memory_save,
    memory_list_recent,
    memory_explore,
    memory_get_config
)


def test_backend(backend_name: str):
    """Test a specific backend."""
    print(f"\n{'='*60}")
    print(f"Testing {backend_name.upper()} Backend")
    print(f"{'='*60}\n")

    # Get config
    config = memory_get_config()
    print(f"Config: {config}\n")

    # Test save
    print("1. Saving test memory...")
    try:
        memory_id = memory_save(
            f"Test memory for {backend_name}",
            title=f"{backend_name} Test",
            importance=7
        )
        print(f"   ✅ Saved: {memory_id}\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
        return False

    # Test query
    print("2. Querying memories...")
    try:
        results = memory_query("test", limit=5)
        print(f"   ✅ Found {len(results)} memories\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
        return False

    # Test list
    print("3. Listing recent...")
    try:
        recent = memory_list_recent(limit=5)
        print(f"   ✅ Listed {len(recent)} recent\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
        return False

    # Test explore
    print("4. Exploring graph...")
    try:
        graph = memory_explore("test", depth=1)
        print(f"   ✅ Graph: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
        return False

    return True


def main():
    """Run end-to-end tests."""
    print("=== End-to-End Adapter Test ===")

    # Test current backend
    config = memory_get_config()
    backend = config['backend']

    success = test_backend(backend)

    if success:
        print(f"\n✅ All tests passed for {backend} backend!")
    else:
        print(f"\n❌ Tests failed for {backend} backend")

    print("\nTo test other backend:")
    print("1. Update .context-hub.yaml")
    print("2. Restart Claude Code")
    print("3. Run this test again")


if __name__ == "__main__":
    main()
