# Encode Repository (Serena-Enhanced)

Systematically populate the knowledge base using Serena's LSP-powered symbol analysis for accurate, comprehensive codebase understanding.

## Purpose

Transform an undocumented or lightly-documented codebase into a rich, searchable knowledge repository. Use this when:
- Starting to use the memory system for an existing project
- Onboarding a new project into the memory system
- Preparing a project for AI agent collaboration
- Creating institutional knowledge for team members
- You want **symbol-accurate architecture mapping** (not regex guessing)

## Why Serena?

Unlike heuristic-based encoding, Serena provides:
- **Accurate symbol extraction** via Language Server Protocol (LSP)
- **Relationship discovery** - find_referencing_symbols shows actual usage
- **Cross-file analysis** - understand how components connect
- **Language-aware parsing** - no regex guessing

## Prerequisites Check (EXECUTE FIRST)

Before proceeding, verify Serena plugin is available:

```bash
claude plugins list | grep -i serena
```

If Serena is not installed:
```
STOP! Serena plugin is required for this command.

Install it with:
  claude plugins install serena

Then re-run /encode-repo-serena
```

Also verify memory backend is connected by testing:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'lib'))

from bridge import memory_get_config

config = memory_get_config()
print(f"Backend: {config['backend']}, Group: {config['group_id']}")
```

If this errors, run `/context-hub-setup` first.

## Arguments

$ARGUMENTS

Parse for:
- **Project path**: Directory to encode (default: current working directory)
- **Project name**: Override auto-detected name (optional)
- **Phases**: Specific phases to run (optional, default: all)

---

## Memory Targets by Project Profile

| Profile | Phase 1 | Phase 1B | Phase 2 | Phase 2B | Phase 3 | Phase 4 | Phase 5 | Phase 6 | Phase 6B | Phase 7B | Total |
|---------|---------|----------|---------|----------|---------|---------|---------|---------|----------|----------|-------|
| Small Simple | 3-5 | 1-2 | 3-5 | 3-5 entities | 3-5 | 2-4 | 0-2 | 3-5 artifacts | 1 doc + 1 mem | 1 doc + 1 mem | 17-31 memories + 2 docs + 3-5 artifacts + entities |
| Small Complex | 5-7 | 1-2 | 5-8 | 5-10 entities | 5-8 | 4-6 | 0-3 | 5-8 artifacts | 1 doc + 1 mem | 1 doc + 1 mem | 28-46 memories + 2 docs + 5-8 artifacts + entities |
| Medium Standard | 5-10 | 1-2 | 10-15 | 10-20 entities | 8-12 | 5-10 | 0-5 | 5-10 artifacts | 1-2 docs + 1-2 mems | 1 doc + 1 mem | 38-66 memories + 2-3 docs + 5-10 artifacts + entities |
| Large | 8-12 | 2-3 | 15-20 | 20-40 entities | 12-18 | 10-15 | 0-8 | 8-15 artifacts | 2-4 docs + 2-4 mems | 1-2 docs + 1-2 mems | 66-112 memories + 3-6 docs + 8-15 artifacts + entities |

**Notes**:
- Phase 1 now includes project.notes update (instant context primer)
- Phase 1B creates 1-3 dependency memories per project
- **Phase 2B is MANDATORY** - creates entities for components and their relationships
- Phase 5 is CONDITIONAL - only if explicit documentation exists (see Phase 5 guidelines)
- **Phase 6 is MANDATORY** - minimum 3 code artifacts for any project
- Phase 6B creates Symbol Index document(s) with entry memory - split by layer for large projects
- Phase 7B creates Architecture Reference document with entry memory

---

## Phase Completion Gates

**CRITICAL**: Do not proceed to the next phase until the current phase meets its minimum targets.

After each phase, report:
```
Phase [N] Complete:
- Created: [X] memories, [Y] entities, [Z] artifacts
- Minimum required: [targets from table above]
- Status: ✅ Met / ❌ Not met (explain gaps)
```

**Mandatory phases** (cannot skip):
- Phase 0: Discovery
- Phase 1: Foundation
- Phase 2: Architecture
- **Phase 2B: Entity Graph** (minimum 3 entities for any project)
- Phase 3: Patterns (minimum 3 pattern memories)
- Phase 6: Code Artifacts (minimum 3 artifacts)
- Phase 6B: Symbol Index
- Phase 7B: Architecture Document

**Conditional phases** (skip only if criteria not met):
- Phase 1B: Dependencies (skip if single-file script with no deps)
- Phase 4: Features (skip if <3 distinct features)
- Phase 5: Decisions (skip if NO explicit documentation found - see guidelines)
- Phase 7: Additional Documents (skip if no long-form content needed)

---

## Phase 0: Discovery & Assessment (ALWAYS START HERE)

### Step 1: Activate Project in Serena

**CRITICAL**: Serena requires an active project before any operations. Activate it first:

```
mcp__plugin_serena_serena__activate_project({
  "project": "<project_path_or_name>"
})
```

Use the current working directory path, or if the project is registered, use its name from the known projects list.

If activation fails with "No active project", Serena will show available registered projects - pick the matching one or provide the full path.

### Step 2: Explore Project Structure

```
mcp__plugin_serena_serena__list_dir({
  "relative_path": ".",
  "recursive": true,
  "skip_ignored_files": true
})
```

### Step 3: Check Existing Memory Coverage

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'lib'))

from bridge import memory_query, memory_get_config

config = memory_get_config()
print(f"Backend: {config['backend']}, Group: {config['group_id']}\n")

# Query existing memories
results = memory_query("architecture patterns", limit=10)
print(f"Found {len(results)} existing memories")
for r in results:
    print(f"  - {r['metadata'].get('title', 'Untitled')}")
```

### Step 4: Analyze Entry Points

Read key files to understand project:
```
mcp__plugin_serena_serena__read_file({"relative_path": "README.md"})
mcp__plugin_serena_serena__read_file({"relative_path": "pyproject.toml"})
# or package.json, Cargo.toml, etc.
```

### Step 5: Gap Analysis

Compare:
- What's in Forgetful KB?
- What exists in codebase?
- What's missing?

Report findings before proceeding.

---

## Phase 1: Project Foundation (5-10 memories)

### Memory Adapter Setup

The memory adapter auto-detects the group_id from the git repo. For advanced Forgetful features (projects, entities, documents), you'll need the project_id:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'lib'))

from bridge import memory_get_config

config = memory_get_config()
group_id = config['group_id']
print(f"Group ID: {group_id}")

# For Forgetful backend only: Get or create project
if config['backend'] == 'forgetful':
    result = execute_forgetful_tool("list_projects", {})

    # Find or create project
    project_id = None
    for project in result.get("projects", []):
        if project.get("name") == group_id:
            project_id = project.get("id")
            break

    if not project_id:
        create_result = execute_forgetful_tool("create_project", {
            "name": group_id,
            "description": "<problem solved, features, tech stack>",
            "project_type": "development",
            "repo_name": group_id
        })
        project_id = create_result.get("project_id", create_result.get("id"))

    # Update project notes (Forgetful-specific feature)
    execute_forgetful_tool("update_project", {
        "project_id": project_id,
        "notes": "Entry: python3 -m ProjectName.main <mode>
Tech: Python 3.12, ClickHouse, XGBoost, FastAPI, Streamlit
Architecture: 6-layer (Data→Domain→Processing→ML→Strategy→Presentation)
Key patterns: Repository, Async generators, Batch writes, Factory
Core components: ConnectionPool, Fetchers, Writers, ML Pipeline"
    })

    print(f"Project ID: {project_id}")
else:
    print("Graphiti backend - using group_id directly")
```

**Notes format guidance** (500-1000 chars max, Forgetful only):
- Entry point command
- Tech stack summary (language, major frameworks, database)
- Architecture pattern (layer count, pattern name)
- Key patterns used
- Core components (top 5 by importance)

This provides instant context without querying memories.

### Create Foundation Memories

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'lib'))

from bridge import memory_save

# 1. Project Overview
memory_save(
    content="[Project purpose, what problems it solves, main features]",
    title="Project Overview",
    importance=10,
    keywords=["overview", "purpose"],
    tags=["foundation"]
)

# 2. Technology Stack
memory_save(
    content="Language: Python 3.12. Frameworks: FastAPI, Streamlit. Database: ClickHouse. ML: XGBoost.",
    title="Technology Stack",
    importance=9,
    keywords=["tech-stack", "dependencies"],
    tags=["foundation", "technology"]
)

# 3. Architecture Pattern
memory_save(
    content="6-layer architecture: Data→Domain→Processing→ML→Strategy→Presentation",
    title="Architecture Pattern",
    importance=10,
    keywords=["architecture", "layers"],
    tags=["foundation", "architecture"]
)

# 4. Development Setup
memory_save(
    content="[Setup instructions, environment requirements, how to run]",
    title="Development Setup",
    importance=8,
    keywords=["setup", "development"],
    tags=["foundation"]
)

# 5. Testing Strategy
memory_save(
    content="[Testing approach, frameworks used, how to run tests]",
    title="Testing Strategy",
    importance=8,
    keywords=["testing", "qa"],
    tags=["foundation"]
)

print("✅ Created 5 foundation memories")
```

---

## Phase 1B: Dependency Analysis

**Purpose**: Extract and document project dependencies systematically, validating assumptions with Context7.

### Step 1: Detect Manifest Files

Look for dependency manifests:
```
mcp__plugin_serena_serena__find_file({
  "file_mask": "package.json",
  "relative_path": "."
})
```

Common manifests to check:
- `package.json` (Node.js)
- `pyproject.toml`, `requirements.txt`, `Pipfile` (Python)
- `Cargo.toml` (Rust)
- `go.mod` (Go)
- `Gemfile` (Ruby)
- `pom.xml`, `build.gradle` (Java)

### Step 2: Parse Dependencies

Read manifest and extract:
- Direct dependencies (name, version)
- Dev dependencies
- Categorize by role: framework, library, database, tool

### Step 3: Validate with Context7 (Major Frameworks Only)

For core frameworks (FastAPI, React, PostgreSQL, etc.), validate usage assumptions:
```
mcp__plugin_context7_context7__resolve-library-id({
  "libraryName": "fastapi",
  "query": "How does FastAPI handle dependency injection?"
})
```

Then query specific patterns observed in the repo:
```
mcp__plugin_context7_context7__query-docs({
  "libraryId": "/tiangolo/fastapi",
  "query": "Depends pattern for request validation"
})
```

Use Context7 to confirm:
- Observed usage patterns are correct
- No deprecated APIs being used
- Best practices being followed

### Step 4: Create Dependency Memory

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'lib'))

from bridge import memory_save

memory_save(
    content="""Language: [lang] [version]. Core frameworks: [list with roles].
Data/storage: [databases]. HTTP/API: [frameworks].
Dev tools: [testing, linting, build].
Rationale: [why chosen, if documented].""",
    title="[Project] - Dependencies and External Libraries",
    context="Understanding technology choices and integration patterns",
    keywords=["tech-stack", "dependencies", "frameworks", "libraries"],
    tags=["technology", "foundation", "dependencies"],
    importance=9
)
```

---

## Phase 2: Symbol-Level Architecture (10-15 memories)

**This is where Serena shines.**

### Step 1: Get Symbol Overview for Key Files

For each major source file:
```
mcp__plugin_serena_serena__get_symbols_overview({
  "relative_path": "src/main.py",
  "depth": 1
})
```

This returns classes, functions, methods with their locations.

### Step 2: Analyze Key Classes/Modules

For important symbols discovered:
```
mcp__plugin_serena_serena__find_symbol({
  "name_path_pattern": "ClassName",
  "include_body": false,
  "depth": 1
})
```

### Step 3: Discover Relationships

For core classes/functions:
```
mcp__plugin_serena_serena__find_referencing_symbols({
  "name_path": "ClassName/method_name",
  "relative_path": "src/module.py"
})
```

This reveals:
- Who calls this method?
- Where is this class used?
- What depends on what?

### Step 4: Create Architecture Memories

For each architectural layer discovered:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'lib'))

from bridge import memory_save

memory_save(
    content="Key symbols: [list]. Relationships: [discovered references]. Pattern: [identified pattern].",
    title="[Project] - [Layer] Architecture",
    context="Discovered via Serena symbol analysis",
    importance=8,
    keywords=["architecture", "layer-name"],
    tags=["architecture"]
)
```

---

## Phase 2B: Entity Graph Creation (MANDATORY)

**Purpose**: Build a knowledge graph of project components and their relationships in Forgetful.

**THIS PHASE IS MANDATORY** - Minimum 3 entities for any project.

### Why Entities Matter

Entities enable:
- Cross-project discovery ("What projects use FastAPI?")
- Relationship mapping ("What depends on this component?")
- Knowledge graph navigation beyond text search
- Grounding abstract concepts in concrete components

Without entities, the encoding is incomplete. An agent querying "what components exist" will get nothing.

### Minimum Entity Requirements

| Project Size | Component Entities | Library/Framework Entities | Total Minimum |
|--------------|-------------------|---------------------------|---------------|
| Small | 2-3 core classes | 1-2 key deps | 3-5 |
| Medium | 5-10 services/modules | 3-5 frameworks | 10-20 |
| Large | 10-20 major components | 5-10 key deps | 20-40 |

### Entity Deduplication (ALWAYS CHECK FIRST)

Before creating any entity, check if it already exists:
```
execute_forgetful_tool("search_entities", {
  "query": "<entity-name>",
  "limit": 5
})
```

The search checks both `name` and `aka` (aliases) fields.

- **If found**: Use existing entity ID, optionally update notes/tags
- **If not found**: Create with comprehensive `aka` list for future matching

### Standard Entity Types

Use `entity_type: "other"` with these `custom_type` values (allow flexibility for non-standard cases):
- `Library` - external packages/dependencies (npm, pip, cargo packages)
- `Service` - backend services, APIs, microservices
- `Component` - major code components, modules
- `Tool` - build tools, CLI tools, parsers
- `Framework` - core frameworks (or use `entity_type: "organization"`)

### Entity Creation Criteria

Only create entities for **major components**:
- High reference count from Serena (agent judges "high" based on project size)
- Core architectural components (services, modules with many dependents)
- External dependencies central to the project
- Services/modules that other components depend on

### Tagging Strategy

- Use `project_ids` for scoping (no discovery-method tags)
- Tag by role: `library`, `service`, `component`, `database`, `framework`, `tool`
- Tag by domain if relevant: `auth`, `api`, `storage`, `ui`, `config`

**NOTE: Entity graph features are currently only available in Forgetful backend.**

### Step 1: Create Entities for Major Components (Forgetful Only)

For each major component discovered via Serena:
```python
# Only if using Forgetful backend
if config['backend'] == 'forgetful':
    execute_forgetful_tool("create_entity", {
        "name": "AuthenticationService",
        "entity_type": "other",
        "custom_type": "Service",
        "notes": "Centralized auth service. Location: src/services/auth.py. Handles token validation, user context injection.",
        "tags": ["service", "auth"],
        "aka": ["AuthService", "auth", "auth_service"],
        "project_ids": [project_id]
    })
```

### Step 2: Create Entities for Key Dependencies (Forgetful Only)

For external libraries central to the project:
```python
if config['backend'] == 'forgetful':
    execute_forgetful_tool("create_entity", {
        "name": "FastAPI",
        "entity_type": "other",
        "custom_type": "Framework",
        "notes": "Python async web framework. Used for REST API and WebSocket endpoints.",
        "tags": ["framework", "api"],
        "aka": ["fastapi", "fast-api", "fast_api"],
        "project_ids": [project_id]
    })
```

### Step 3: Create Relationships (Forgetful Only)

Map how components connect using reference counts from Serena:
```python
if config['backend'] == 'forgetful':
    execute_forgetful_tool("create_entity_relationship", {
        "source_entity_id": component_entity_id,
        "target_entity_id": library_id,
        "relationship_type": "uses",
        "strength": 1.0,
        "metadata": {
            "version": "0.104.1",
            "role": "HTTP framework and routing"
        }
    })
```

**Relationship types**:
- `uses` - project/component uses library
- `depends_on` - component depends on another
- `calls` - service calls another service
- `extends` - class extends base class
- `implements` - class implements interface
- `connects_to` - system connects to database/service

**Strength calculation**:
- Based on Serena reference count
- Normalize to 0.0-1.0 scale within project
- Higher reference count = higher strength

### Step 4: Link Entities to Memories (Forgetful Only)

Connect entities to their architecture memories:
```python
if config['backend'] == 'forgetful':
    execute_forgetful_tool("link_entity_to_memory", {
        "entity_id": component_entity_id,
        "memory_id": architecture_memory_id
    })
```

This enables bidirectional discovery:
- Find entity → get related memories
- Query memories → discover linked entities

**For Graphiti backend**: Entity extraction is automatic during memory save. No explicit entity creation needed.

### Phase 2B Completion Checkpoint

```
Phase 2B Complete:
- Component entities created: [count] (minimum 2-3)
- Library/framework entities created: [count] (minimum 1-2)
- Relationships created: [count]
- Entities linked to memories: [count]
- Status: ✅ Met minimum / ❌ Not met (create more before proceeding)
```

**DO NOT proceed to Phase 3 until minimum entity count is met.**

---

## Phase 3: Pattern Discovery (8-12 memories, minimum 3)

**Purpose**: Document recurring implementation patterns that define how the codebase works.

### Pattern Categories to Search

**1. Concurrency/Async Patterns**
```
mcp__plugin_serena_serena__search_for_pattern({
  "substring_pattern": "async def|await|asyncio|yield",
  "restrict_search_to_code_files": true,
  "context_lines_after": 5
})
```

**2. Error Handling Patterns**
```
mcp__plugin_serena_serena__search_for_pattern({
  "substring_pattern": "except.*:|catch\\s*\\(|raise|throw",
  "restrict_search_to_code_files": true
})
```

**3. Dependency Injection / IoC**
```
mcp__plugin_serena_serena__search_for_pattern({
  "substring_pattern": "Depends\\(|@inject|Container|def __init__\\(self,.*:",
  "restrict_search_to_code_files": true
})
```

**4. Decorator/Middleware Patterns**
```
mcp__plugin_serena_serena__search_for_pattern({
  "substring_pattern": "@app\\.|@router\\.|@middleware|@(before|after)",
  "restrict_search_to_code_files": true
})
```

**5. Database/Transaction Patterns**
```
mcp__plugin_serena_serena__search_for_pattern({
  "substring_pattern": "session|transaction|commit|rollback|with.*connection",
  "restrict_search_to_code_files": true
})
```

**6. Factory/Builder Patterns**
```
mcp__plugin_serena_serena__search_for_pattern({
  "substring_pattern": "Factory|Builder|create_|build_|make_",
  "restrict_search_to_code_files": true
})
```

**7. Repository/Data Access Patterns**
```
mcp__plugin_serena_serena__search_for_pattern({
  "substring_pattern": "Repository|DAO|DataAccess|load_|save_|find_",
  "restrict_search_to_code_files": true
})
```

**8. Event/Observer Patterns**
```
mcp__plugin_serena_serena__search_for_pattern({
  "substring_pattern": "emit|on_|subscribe|publish|EventHandler|Observer",
  "restrict_search_to_code_files": true
})
```

### Analyze Pattern Usage

For each pattern found with >3 occurrences:
```
mcp__plugin_serena_serena__find_symbol({
  "name_path_pattern": "pattern_name",
  "substring_matching": true,
  "include_body": true
})
```

Use `find_referencing_symbols` to understand how patterns are used:
```
mcp__plugin_serena_serena__find_referencing_symbols({
  "name_path": "PatternClass",
  "relative_path": "src/patterns/pattern.py"
})
```

### Create Pattern Memories

For each significant pattern (used 3+ times):
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'lib'))

from bridge import memory_save

memory_save(
    content="""Pattern: [name]. Used for: [purpose].
Locations: [list files/classes using it].
Implementation: [brief description of how it works].
Usage count: [X] occurrences across codebase.""",
    title="[Project] - [Pattern Name] Pattern",
    context="Recurring implementation pattern for [purpose]",
    keywords=["pattern", "<pattern-name>", "<domain>"],
    tags=["pattern", "implementation"],
    importance=7
)
```

### Phase 3 Completion Checkpoint

```
Phase 3 Complete:
- Patterns searched: [list categories checked]
- Patterns documented: [count] (minimum 3)
- Pattern memories created: [list titles]
- Status: ✅ Met minimum / ❌ Not met (continue searching)
```

**Minimum 3 pattern memories required.** If fewer than 3 patterns found, document whatever exists (even basic ones like "error handling approach").

---

## Phase 4: Critical Features (1-2 per feature, minimum 3 features)

**Purpose**: Document major user-facing features and their implementation flows.

### Identify Features via Symbol Analysis

**1. API Endpoints (REST/GraphQL)**
```
mcp__plugin_serena_serena__search_for_pattern({
  "substring_pattern": "@(app|router)\\.(get|post|put|delete|patch)|@(Query|Mutation)",
  "restrict_search_to_code_files": true
})
```

**2. CLI Commands**
```
mcp__plugin_serena_serena__search_for_pattern({
  "substring_pattern": "@click\\.|@command|argparse|subparser",
  "restrict_search_to_code_files": true
})
```

**3. Background Jobs/Tasks**
```
mcp__plugin_serena_serena__search_for_pattern({
  "substring_pattern": "@task|@job|celery|schedule|cron",
  "restrict_search_to_code_files": true
})
```

**4. UI Pages/Components (for frontend)**
```
mcp__plugin_serena_serena__search_for_pattern({
  "substring_pattern": "export.*function.*Page|def.*page|class.*View",
  "restrict_search_to_code_files": true
})
```

**5. Main Workflows**
```
mcp__plugin_serena_serena__search_for_pattern({
  "substring_pattern": "def main|def run|def process|def execute",
  "restrict_search_to_code_files": true
})
```

### Trace Feature Flow

For each feature:
1. Find the entry point symbol
2. Use `find_referencing_symbols` to trace downstream
3. Identify all components involved
4. Document the complete flow

```
mcp__plugin_serena_serena__find_referencing_symbols({
  "name_path": "endpoint_function",
  "relative_path": "src/routes/feature.py"
})
```

### Create Feature Memories

For each major feature:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'lib'))

from bridge import memory_save

memory_save(
    content="""Feature: [user-facing description].
Entry point: [file:function].
Flow: [step-by-step through components].
Key components: [list classes/functions involved].
Configuration: [relevant settings if any].""",
    title="[Project] - [Feature Name] Implementation",
    context="Implementation details for [feature purpose]",
    keywords=["feature", "<feature-name>", "implementation"],
    tags=["feature", "implementation"],
    importance=8
)
```

### Phase 4 Completion Checkpoint

```
Phase 4 Complete:
- Features identified: [count]
- Feature memories created: [count] (minimum 3 for projects with 3+ features)
- Feature flows traced: [list]
- Status: ✅ Met / ⚠️ Fewer than 3 features exist (acceptable)
```

**Skip only if** project has fewer than 3 distinct features (e.g., single-purpose library).

---

## Phase 5: Design Decisions (DOCUMENTATION-ONLY)

**CRITICAL: This phase is CONDITIONAL. Only capture decisions that are EXPLICITLY documented.**

### What Counts as "Documented"

✅ **DO create decision memories for**:
- ADRs (Architecture Decision Records) in `docs/adr/` or similar
- README sections titled "Why X", "Rationale", "Design Decisions"
- Code comments explicitly stating "We chose X because Y"
- CONTRIBUTING.md or DESIGN.md files explaining choices
- Commit messages or PR descriptions linked from docs

❌ **DO NOT create decision memories for**:
- Inferred decisions (e.g., "They use PostgreSQL so they must value ACID")
- Technology choices without documented rationale
- Patterns you observe but aren't explained
- Your assumptions about why something was built a certain way
- Standard framework conventions (e.g., "FastAPI uses Pydantic")

### Search for Decision Documentation

```
mcp__plugin_serena_serena__search_for_pattern({
  "substring_pattern": "Decision:|Rationale:|## Why|ADR-|chose.*because|decided.*to|trade-?off",
  "paths_include_glob": "**/*.md"
})
```

Also check:
```
mcp__plugin_serena_serena__search_for_pattern({
  "substring_pattern": "# Why|## Rationale|Design Decision",
  "paths_include_glob": "**/*.md"
})
```

And code comments:
```
mcp__plugin_serena_serena__search_for_pattern({
  "substring_pattern": "# NOTE:.*chose|# DECISION:|# WHY:",
  "restrict_search_to_code_files": true
})
```

### Phase 5 Outcomes

**If documentation found**:
Create 1 memory per documented decision:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'lib'))

from bridge import memory_save

memory_save(
    content="""Decision: [what was decided].
Alternatives considered: [if documented].
Rationale: [QUOTE from documentation].
Source: [file path and line number].""",
    title="[Project] - Decision: [Topic]",
    context="Documented design decision from [source file]",
    keywords=["decision", "architecture", "rationale", "<topic>"],
    tags=["decision", "documented"],
    importance=8
)
```

**If NO documentation found**:
```
Phase 5 Complete:
- Searched: [X] markdown files, [Y] code files
- Documented decisions found: 0
- Status: ✅ SKIPPED (no explicit documentation)
```

**DO NOT** create decision memories based on inference. This pollutes the knowledge base with assumptions.

---

## Phase 6: Code Artifacts (MANDATORY, minimum 3)

**Purpose**: Store reusable code patterns that enable an agent to understand HOW the codebase works, not just WHAT exists.

**THIS PHASE IS MANDATORY** - Minimum 3 artifacts for any project.

### Why Code Artifacts Matter

Without artifacts, an agent knows components exist but cannot:
- Write code that integrates with existing patterns
- Understand implementation details
- See actual syntax and conventions used
- Learn project-specific idioms

### Artifact Selection Criteria

Create artifacts for:
1. **Core patterns** - Most-used patterns from Phase 3 (async generators, factories, etc.)
2. **Interface contracts** - Base classes/interfaces that define extensibility points
3. **Entry point examples** - Main handlers, API endpoints, CLI commands
4. **Utility functions** - Frequently-used helpers
5. **Configuration patterns** - How config is loaded/used

### Minimum Artifact Requirements

| Project Size | Minimum Artifacts | Recommended |
|--------------|-------------------|-------------|
| Small | 3 | 3-5 |
| Medium | 5 | 5-10 |
| Large | 8 | 8-15 |

### Extract Code Using Serena

```
mcp__plugin_serena_serena__find_symbol({
  "name_path_pattern": "PatternClass/key_method",
  "include_body": true
})
```

### Create Artifacts (Forgetful Only)

**NOTE: Code artifacts are a Forgetful-specific feature.**

For each key pattern/utility:
```python
if config['backend'] == 'forgetful':
    execute_forgetful_tool("create_code_artifact", {
        "title": "[Project] - [Pattern Name] ([Language])",
        "description": """What: [brief description of what it does].
When: [when to use this pattern].
Where: [file location in codebase].
Usage: [how other code uses this].""",
        "code": "<full implementation from find_symbol>",
        "language": "python",
        "tags": ["pattern", "<domain-tag>"],
        "project_id": project_id
    })
else:
    # For Graphiti, save as regular memory with code
    memory_save(
        content=f"""# [Pattern Name] ([Language])

What: [brief description of what it does].
When: [when to use this pattern].
Where: [file location in codebase].
Usage: [how other code uses this].

```python
<full implementation from find_symbol>
```""",
        title="[Project] - [Pattern Name] Code Example",
        keywords=["code", "pattern", "example"],
        tags=["pattern", "code"],
        importance=7
    )
```

### Recommended Artifacts by Project Type

**Web API**:
1. Request handler pattern (endpoint example)
2. Middleware/interceptor pattern
3. Repository/data access pattern
4. Error handling pattern
5. Authentication pattern

**CLI Tool**:
1. Command handler pattern
2. Argument parsing pattern
3. Output formatting pattern

**Data Pipeline**:
1. Async generator/streaming pattern
2. Batch processing pattern
3. Transformation/mapping pattern
4. Error recovery pattern

**Library/SDK**:
1. Public API entry point
2. Factory/builder pattern
3. Configuration pattern
4. Extension point example

### Phase 6 Completion Checkpoint

```
Phase 6 Complete:
- Code artifacts created: [count] (minimum 3)
- Artifacts by category: [patterns: X, interfaces: Y, utilities: Z]
- Artifact titles: [list]
- Status: ✅ Met minimum / ❌ Not met (create more before proceeding)
```

**DO NOT proceed to Phase 6B until minimum artifact count is met.**

---

## Phase 6B: Symbol Index Document

**Purpose**: Compile Serena's LSP symbol analysis into a permanent, searchable Forgetful document.

This captures symbol locations, relationships, and reference counts that would otherwise be lost when Serena is not active.

### Step 1: Aggregate Symbol Data

Collect from all `get_symbols_overview` and `find_symbol` calls during Phase 2:
- Classes with file locations and line numbers
- Interfaces with their implementations
- Key functions with callers (from `find_referencing_symbols`)
- Reference counts for each symbol

### Step 2: Create Symbol Index Document (Forgetful Only)

**NOTE: Documents are a Forgetful-specific feature.**

```python
if config['backend'] == 'forgetful':
    execute_forgetful_tool("create_document", {
        "title": "[Project] - Symbol Index",
        "description": "LSP-accurate symbol listing with locations, relationships, and reference counts. Generated via Serena analysis.",
        "content": "<structured markdown table - see format below>",
        "document_type": "markdown",
        "project_id": project_id,
        "tags": ["symbol-index", "reference", "navigation"]
    })
else:
    # For Graphiti, save as long-form memory
    memory_save(
        content="<structured markdown table>",
        title="[Project] - Symbol Index",
        keywords=["symbols", "index", "navigation"],
        tags=["symbol-index", "reference"],
        importance=8
    )
```

**Document Format:**
```markdown
# [Project] - Symbol Index

Generated: [date]
Total: X classes, Y interfaces, Z functions

## Classes

| Symbol | Location | Description | Refs |
|--------|----------|-------------|------|
| ClassName | path/file.py:line | Brief description | count |
| ... | ... | ... | ... |

## Interfaces

| Symbol | Location | Implementations |
|--------|----------|-----------------|
| InterfaceName | path/file.py:line | Impl1, Impl2 |
| ... | ... | ... |

## Key Functions

| Symbol | Location | Called By |
|--------|----------|-----------|
| func_name | path/file.py:line | Caller1, Caller2 |
| ... | ... | ... |
```

### Step 3: Create Entry Memory

Create an atomic memory that summarizes the index:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'lib'))

from bridge import memory_save

if config['backend'] == 'forgetful':
    # Link to document
    execute_forgetful_tool("create_memory", {
        "title": "[Project] - Symbol Index Reference",
        "content": """Symbol index contains X classes, Y interfaces, Z functions.
Top referenced: [list top 5 by ref count].
Key interfaces: [list with implementation counts].
Full index in linked document.""",
        "context": "Entry point for symbol navigation - links to full index document",
        "keywords": ["symbols", "classes", "functions", "navigation", "index"],
        "tags": ["reference", "navigation", "symbol-index"],
        "importance": 8,
        "project_ids": [project_id],
        "document_ids": [symbol_index_doc_id]
    })
else:
    # For Graphiti, single memory with all info
    memory_save(
        content="""Symbol index contains X classes, Y interfaces, Z functions.
Top referenced: [list top 5 by ref count].
Key interfaces: [list with implementation counts].""",
        title="[Project] - Symbol Index Reference",
        context="Entry point for symbol navigation",
        keywords=["symbols", "classes", "functions", "navigation", "index"],
        tags=["reference", "navigation", "symbol-index"],
        importance=8
    )
```

### Size Guidelines

| Project Size | Est. Symbols | Doc Size | Split? |
|--------------|--------------|----------|--------|
| Small | <50 | <2000 words | No |
| Medium | 50-150 | 2000-5000 words | No |
| Large | 150+ | >5000 words | Yes, by layer |

**If splitting** (large projects):
- Create separate docs per architectural layer: `[Project] - Symbol Index: Data Layer`
- Each doc gets its own entry memory
- Entry memories link to their respective documents

---

## Phase 7: Documents (as needed)

**NOTE: Documents are a Forgetful-specific feature.**

For content >400 words (detailed guides, comprehensive analysis):
```python
if config['backend'] == 'forgetful':
    execute_forgetful_tool("create_document", {
        "title": "Document name",
        "description": "Overview and purpose",
        "content": "<full documentation>",
        "document_type": "markdown",
        "project_id": project_id
    })

    # Create 3-5 atomic memories as entry points, linked via document_ids
else:
    # For Graphiti, save as long-form memory
    memory_save(
        content="<full documentation>",
        title="Document name",
        keywords=["documentation", "guide"],
        tags=["reference"],
        importance=8
    )
```

---

## Phase 7B: Architecture Document

**Purpose**: Consolidate architecture analysis into a comprehensive reference document that persists Serena's insights.

This creates the definitive architecture reference, accessible even when Serena is not active.

### Step 1: Synthesize Architecture Content

Combine insights from:
- Phase 2 architecture memories (symbol-level analysis)
- Phase 2B entity relationships (component graph)
- Phase 3 pattern discoveries
- Serena's `find_referencing_symbols` relationship data

### Step 2: Create Architecture Document

```python
if config['backend'] == 'forgetful':
    execute_forgetful_tool("create_document", {
        "title": "[Project] - Architecture Reference",
        "description": "Comprehensive architecture documentation with layer details, component relationships, and design patterns. Generated via Serena symbol analysis.",
        "content": "<structured architecture doc - see format below>",
        "document_type": "markdown",
        "project_id": project_id,
        "tags": ["architecture", "reference", "design"]
    })
else:
    # For Graphiti, save as memory
    memory_save(
        content="<structured architecture doc>",
        title="[Project] - Architecture Reference",
        keywords=["architecture", "reference", "design"],
        tags=["architecture", "reference"],
        importance=9
    )
```

**Document Format:**
```markdown
# [Project] - Architecture Reference

Generated: [date]

## Overview

[2-3 paragraph summary of what the system does and how it's structured]

## Architecture Diagram

┌─────────────────────────────────────────────────────────────┐
│         Presentation Layer                                   │
│  (Streamlit Dashboard + FastAPI Prediction Server)           │
└─────────────────────────────────────────────────────────────┘
                            ↓
[Continue with layer diagram...]

## Layer Details

### [Layer Name]

**Purpose**: [what this layer does]

**Key Components**:
- ComponentName (location: path/file.py): [brief description]
  - Key methods: method1(), method2()
  - Used by: [list consumers from find_referencing_symbols]

**Patterns Used**: [patterns in this layer]

### [Next Layer...]

## Cross-Cutting Concerns

### Error Handling
[how errors flow through the system]

### Configuration
[how config is managed]

### Testing
[testing approach and locations]

## Key Design Decisions

[Only if documented in repo - from Phase 5]
```

### Step 3: Create Entry Memory

Create an atomic memory that summarizes the architecture:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'lib'))

from bridge import memory_save

if config['backend'] == 'forgetful':
    # Link to document
    execute_forgetful_tool("create_memory", {
        "title": "[Project] - Architecture Reference",
        "content": """[Layer count]-layer architecture: [list layers].
Key patterns: [top 4-5 patterns].
Core components: [top 5 by reference count].
Full reference in linked document.""",
        "context": "Entry point for architecture deep-dives - links to comprehensive document",
        "keywords": ["architecture", "layers", "patterns", "design", "structure"],
        "tags": ["architecture", "reference", "foundation"],
        "importance": 9,
        "project_ids": [project_id],
        "document_ids": [arch_doc_id]
    })
else:
    # For Graphiti, single comprehensive memory
    memory_save(
        content="""[Layer count]-layer architecture: [list layers].
Key patterns: [top 4-5 patterns].
Core components: [top 5 by reference count].""",
        title="[Project] - Architecture Reference",
        context="Entry point for architecture deep-dives",
        keywords=["architecture", "layers", "patterns", "design", "structure"],
        tags=["architecture", "reference", "foundation"],
        importance=9
    )
```

### Size Guidelines

- **Target**: 3000-8000 words
- **If exceeding 8000 words**, consider splitting by:
  - Layer (Data Architecture, ML Architecture, API Architecture)
  - Concern (Core Architecture, Integration Points, Deployment)
- Each split doc gets its own entry memory

---

## Execution Guidelines

### Phase Execution Order

Execute in order: 0 → 1 → 1B → 2 → **2B** → 3 → 4 → 5 → **6** → 6B → 7 → 7B

### Mandatory Phases (CANNOT SKIP)

| Phase | Minimum Output | Gate |
|-------|---------------|------|
| 0: Discovery | Gap analysis report | Report before proceeding |
| 1: Foundation | 5 memories + project notes | All 5 core memories |
| 2: Architecture | Layer memories | 1 per architectural layer |
| **2B: Entities** | **3+ entities** | **Entity count met** |
| 3: Patterns | **3+ pattern memories** | Pattern count met |
| **6: Artifacts** | **3+ code artifacts** | **Artifact count met** |
| 6B: Symbol Index | 1 document + entry memory | Document created |
| 7B: Architecture Doc | 1 document + entry memory | Document created |

### Conditional Phases

| Phase | Skip Condition |
|-------|----------------|
| 1B: Dependencies | Single-file script with no deps |
| 4: Features | <3 distinct features |
| 5: Decisions | NO explicit documentation found |
| 7: Documents | No long-form content needed |

### Execution Rules

1. **Report after each phase** - Use the completion checkpoint format
2. **Meet minimums before proceeding** - DO NOT skip mandatory phases
3. **Leverage Serena's strengths** - Symbol analysis over text search
4. **Track relationships** - find_referencing_symbols is powerful
5. **Aggregate symbol data** - Collect during Phase 2 for Phase 6B
6. **Deduplicate entities** - Always search before creating
7. **Use Context7** - Validate framework usage assumptions
8. **Update outdated memories** as discovered
9. **Link entities to memories** - Enable bidirectional discovery
10. **Create entry memories** - Link documents via document_ids
11. **Mark obsolete** - Memories that reference removed code
12. **Phase 5 is documentation-only** - Never infer decisions from code

## Quality Principles

- **Symbol-accurate**: Use LSP data, not guesses
- **Relationship-aware**: Document how things connect
- **One concept per memory** (atomic)
- **200-400 words ideal** per memory
- **Include context field** explaining relevance
- **Honest importance scoring** (most should be 7-8)
- **Quality over quantity**
- **Only document what's explicitly in the repo** (especially for decisions)

---

## Validation

After completion, verify coverage:

### Test Memories
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'lib'))

from bridge import memory_query

# Test basic queries
results = memory_query("How do I add a new API endpoint?", limit=5)
print(f"Found {len(results)} results for endpoint query")

results = memory_query("What dependencies does this project use?", limit=5)
print(f"Found {len(results)} results for dependency query")

results = memory_query("architecture patterns", limit=10)
print(f"Found {len(results)} architecture memories")
```

### Test Entities (Forgetful Only)
```python
if config['backend'] == 'forgetful':
    # Test entity listing
    result = execute_forgetful_tool("list_entities", {
        "project_ids": [project_id]
    })
    print(f"Found {len(result.get('entities', []))} entities")

    # Test by role
    result = execute_forgetful_tool("list_entities", {
        "project_ids": [project_id],
        "tags": ["library"]
    })
    print(f"Found {len(result.get('entities', []))} library entities")

    # Test relationships
    result = execute_forgetful_tool("get_entity_relationships", {
        "entity_id": component_entity_id,
        "direction": "outgoing"
    })
    print(f"Found {len(result.get('relationships', []))} relationships")
```

### Test Documents (Forgetful Only)
```python
if config['backend'] == 'forgetful':
    result = execute_forgetful_tool("list_documents", {
        "project_id": project_id
    })
    print(f"Found {len(result.get('documents', []))} documents")

    # Should show Symbol Index and Architecture Reference
    for doc in result.get('documents', []):
        print(f"  - {doc.get('title')}")

    # Test document retrieval
    result = execute_forgetful_tool("get_document", {
        "document_id": symbol_index_doc_id
    })
    print("Symbol index document retrieved successfully")

    # Test project notes
    result = execute_forgetful_tool("get_project", {
        "project_id": project_id
    })
    print(f"Project notes: {result.get('notes', 'N/A')[:100]}...")
```

Test with architecture questions - Serena-encoded repos should answer accurately.

---

## Report Progress

After each phase, report using the checkpoint format:
```
Phase [N] Complete:
- Created: [X] memories, [Y] entities, [Z] artifacts
- Minimum required: [targets from table]
- Status: ✅ Met / ❌ Not met
```

**Proceed automatically** to the next phase once the checkpoint is met. Do not wait for user confirmation.

---

## Final Encoding Summary

When encoding is complete, provide a summary in this format:

```
# [Project] Encoding Complete

## Artifacts Created

| Type | Count | Minimum | Status |
|------|-------|---------|--------|
| Memories | [X] | [per profile] | ✅/❌ |
| Entities | [Y] | 3+ | ✅/❌ |
| Relationships | [Z] | - | - |
| Code Artifacts | [W] | 3+ | ✅/❌ |
| Documents | [V] | 2 | ✅/❌ |

## Phase Completion Status

| Phase | Status | Output |
|-------|--------|--------|
| 0: Discovery | ✅ | Gap analysis completed |
| 1: Foundation | ✅ | [X] memories |
| 1B: Dependencies | ✅/SKIP | [reason] |
| 2: Architecture | ✅ | [X] layer memories |
| 2B: Entities | ✅ | [X] entities, [Y] relationships |
| 3: Patterns | ✅ | [X] pattern memories |
| 4: Features | ✅/SKIP | [X] feature memories |
| 5: Decisions | ✅/SKIP | [X] decisions (or: no documentation found) |
| 6: Artifacts | ✅ | [X] code artifacts |
| 6B: Symbol Index | ✅ | Document + entry memory |
| 7B: Architecture | ✅ | Document + entry memory |

## Key Memories for Navigation

1. **Overview**: [title] (ID: X)
2. **Architecture**: [title] (ID: Y)
3. **Symbol Index**: [title] (ID: Z, links to doc)
4. **Architecture Doc**: [title] (ID: W, links to doc)

## Entity Graph Summary

Components: [list]
Frameworks: [list]
Key relationships: [list]

## Validation Queries Tested

- "How do I add a new endpoint?" → [result summary]
- "What patterns are used?" → [result summary]
- "What components exist?" → [entity count returned]
```

This summary confirms the encoding meets minimum requirements and provides quick navigation for future agents.
