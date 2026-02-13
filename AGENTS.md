# Agents

## context-retrieval

Context retrieval specialist for gathering relevant context before planning or implementation.

**Sources:**
1. **Graphiti Knowledge Graph** - Semantic search across entities and relationships
2. **File System** - Read actual code referenced in memories
3. **Context7** - Framework-specific documentation
4. **WebSearch** - Fallback for recent information

**Usage:**
- Launched by `/context_gather` command
- Uses Graphiti MCP tools directly
- Auto-detects group_id from config
- Returns synthesized context summary

**Tools:**
- Graphiti MCP: `search_nodes`, `search_memory_facts`, `get_episodes`
- Context7: `resolve-library-id`, `get-library-docs`
- Core: Read, Glob, Grep, WebSearch, WebFetch
