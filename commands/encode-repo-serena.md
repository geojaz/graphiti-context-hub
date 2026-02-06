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
| Small Simple | 3-5 | 1 | 3-5 | 3-5 | 3-5 | 2-4 | 0-2 | 3-5 | 1 | 1 | 20-33 memories |
| Small Complex | 5-7 | 1 | 5-8 | 5-10 | 5-8 | 4-6 | 0-3 | 5-8 | 1 | 1 | 32-52 memories |
| Medium Standard | 5-10 | 1 | 10-15 | 10-20 | 8-12 | 5-10 | 0-5 | 5-10 | 1-2 | 1 | 46-86 memories |
| Large | 8-12 | 2 | 15-20 | 20-40 | 12-18 | 10-15 | 0-8 | 8-15 | 2-4 | 1-2 | 78-136 memories |

**Notes**:
- All content stored as memories using bridge
- Phase 1B creates 1-2 dependency memories per project
- **Phase 2B is MANDATORY** - creates component memories documenting relationships
- Phase 5 is CONDITIONAL - only if explicit documentation exists (see Phase 5 guidelines)
- **Phase 6 is MANDATORY** - minimum 3 code example memories for any project
- Phase 6B creates Symbol Index memory - split by layer for large projects
- Phase 7B creates Architecture Reference memory - split by layer for very large projects

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
- **Phase 2B: Components** (minimum 3 component memories)
- Phase 3: Patterns (minimum 3 pattern memories)
- Phase 6: Code Examples (minimum 3 code example memories)
- Phase 6B: Symbol Index (1 memory)
- Phase 7B: Architecture Reference (1 memory)

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

The memory adapter auto-detects the group_id from the git repo:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'lib'))

from bridge import memory_get_config

config = memory_get_config()
print(f"Backend: {config['backend']}")
print(f"Group ID: {config['group_id']}")
```

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

## Phase 2B: Component Relationships (via Memories)

**Purpose**: Document project components and their relationships using the bridge.

Components are captured through memories. Entity extraction is automatic:
- **Graphiti**: Extracts entities automatically from memory content
- **Forgetful**: Requires manual entity creation (see Advanced Features section)

### Minimum Requirements

| Project Size | Component Memories |
|--------------|-------------------|
| Small | 3-5 |
| Medium | 10-20 |
| Large | 20-40 |

### Create Component Memories

Document major components discovered via Serena:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'lib'))

from bridge import memory_save

# Component memory example
memory_save(
    content="""AuthenticationService handles token validation and user context injection.
Location: src/services/auth.py
Dependencies: FastAPI, JWT library
Used by: All API endpoints requiring auth
Reference count: 42 (high usage across codebase)
Key methods: validate_token(), get_user_context()""",
    title="[Project] - AuthenticationService Component",
    context="Core service for authentication",
    keywords=["component", "auth", "service", "authentication"],
    tags=["component", "auth"],
    importance=8
)

# Framework/library memory example
memory_save(
    content="""FastAPI is the core HTTP framework.
Version: 0.104.1
Used for: REST API endpoints, WebSocket connections
Integration: Dependency injection via Depends()
Major components using it: All service endpoints""",
    title="[Project] - FastAPI Framework Integration",
    context="Core framework for HTTP layer",
    keywords=["framework", "fastapi", "api", "http"],
    tags=["framework", "dependency"],
    importance=8
)
```

### Document Relationships

Use content to capture relationships:

```python
memory_save(
    content="""Component dependencies in [Project]:

AuthenticationService → FastAPI (uses for routing)
DataService → PostgreSQL (connects for storage)
APIHandler → AuthenticationService (depends on for auth)
MLPipeline → XGBoost (uses for predictions)

Relationship strengths based on Serena reference counts:
- High usage (30+ refs): AuthenticationService→FastAPI
- Medium usage (10-30 refs): DataService→PostgreSQL
- Low usage (<10 refs): MLPipeline→XGBoost""",
    title="[Project] - Component Dependency Graph",
    context="How components connect and depend on each other",
    keywords=["dependencies", "relationships", "components", "architecture"],
    tags=["architecture", "relationships"],
    importance=9
)
```

### Phase 2B Completion Checkpoint

```
Phase 2B Complete:
- Component memories created: [count] (minimum 3-5)
- Relationship memory created: 1
- Key components documented: [list]
- Status: ✅ Met minimum / ❌ Not met (create more before proceeding)
```

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

## Phase 6: Code Examples (MANDATORY, minimum 3)

**Purpose**: Store reusable code patterns that enable an agent to understand HOW the codebase works, not just WHAT exists.

**THIS PHASE IS MANDATORY** - Minimum 3 code example memories for any project.

### Why Code Examples Matter

Without code examples, an agent knows components exist but cannot:
- Write code that integrates with existing patterns
- Understand implementation details
- See actual syntax and conventions used
- Learn project-specific idioms

### Example Selection Criteria

Create examples for:
1. **Core patterns** - Most-used patterns from Phase 3 (async generators, factories, etc.)
2. **Interface contracts** - Base classes/interfaces that define extensibility points
3. **Entry point examples** - Main handlers, API endpoints, CLI commands
4. **Utility functions** - Frequently-used helpers
5. **Configuration patterns** - How config is loaded/used

### Minimum Requirements

| Project Size | Minimum Code Examples |
|--------------|----------------------|
| Small | 3 |
| Medium | 5 |
| Large | 8 |

### Extract Code Using Serena

```
mcp__plugin_serena_serena__find_symbol({
  "name_path_pattern": "PatternClass/key_method",
  "include_body": true
})
```

### Create Code Example Memories

For each key pattern/utility:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'lib'))

from bridge import memory_save

memory_save(
    content="""# Async Generator Pattern (Python)

What: Streams data chunks asynchronously without loading entire dataset in memory.
When: Processing large datasets that don't fit in RAM.
Where: src/data/fetchers.py - DataFetcher.stream_results()
Usage: Used by all batch processing pipelines (15 locations).

```python
async def stream_results(self, query: str) -> AsyncGenerator[Batch, None]:
    \"\"\"Stream query results in batches.\"\"\"
    async with self.pool.get_connection() as conn:
        cursor = await conn.cursor()
        await cursor.execute(query)

        while True:
            batch = await cursor.fetchmany(self.batch_size)
            if not batch:
                break
            yield Batch(data=batch)
```

Referenced by: MLPipeline, DataExporter, ReportGenerator (Serena ref count: 15)""",
    title="[Project] - Async Generator Pattern (Python)",
    context="Core pattern for memory-efficient data streaming",
    keywords=["code", "pattern", "async", "generator", "streaming"],
    tags=["pattern", "code", "example"],
    importance=8
)
```

### Recommended Examples by Project Type

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
- Code example memories created: [count] (minimum 3)
- Examples by category: [patterns: X, interfaces: Y, utilities: Z]
- Example titles: [list]
- Status: ✅ Met minimum / ❌ Not met (create more before proceeding)
```

**DO NOT proceed to Phase 6B until minimum count is met.**

---

## Phase 6B: Symbol Index Memory

**Purpose**: Compile Serena's LSP symbol analysis into a permanent, searchable memory.

This captures symbol locations, relationships, and reference counts that would otherwise be lost when Serena is not active.

### Step 1: Aggregate Symbol Data

Collect from all `get_symbols_overview` and `find_symbol` calls during Phase 2:
- Classes with file locations and line numbers
- Interfaces with their implementations
- Key functions with callers (from `find_referencing_symbols`)
- Reference counts for each symbol

### Step 2: Create Symbol Index Memory

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'lib'))

from bridge import memory_save

memory_save(
    content="""# [Project] - Symbol Index

Generated: [date]
Total: X classes, Y interfaces, Z functions

## Classes

| Symbol | Location | Description | Refs |
|--------|----------|-------------|------|
| AuthenticationService | src/services/auth.py:15 | Centralized auth service | 42 |
| DataFetcher | src/data/fetchers.py:8 | Async data streaming | 15 |
| MLPipeline | src/ml/pipeline.py:22 | ML training pipeline | 8 |

## Interfaces

| Symbol | Location | Implementations |
|--------|----------|-----------------|
| BaseRepository | src/repositories/base.py:5 | UserRepo, DataRepo, ConfigRepo |
| Handler | src/handlers/base.py:3 | APIHandler, CLIHandler |

## Key Functions

| Symbol | Location | Called By |
|--------|----------|-----------|
| validate_token | src/services/auth.py:45 | All API endpoints (42 locations) |
| batch_process | src/data/processing.py:78 | MLPipeline, DataExporter |
| transform_data | src/data/transforms.py:12 | DataFetcher, MLPipeline |

## Top Referenced Symbols (by ref count)
1. AuthenticationService - 42 refs
2. DataFetcher - 15 refs
3. MLPipeline - 8 refs

## Key Interfaces (by implementation count)
1. BaseRepository - 3 implementations
2. Handler - 2 implementations""",
    title="[Project] - Symbol Index",
    context="LSP-accurate symbol listing with locations and relationships",
    keywords=["symbols", "classes", "functions", "navigation", "index"],
    tags=["reference", "navigation", "symbol-index"],
    importance=8
)
```

### Size Guidelines

| Project Size | Est. Symbols | Memory Size | Strategy |
|--------------|--------------|-------------|----------|
| Small | <50 | <2000 words | Single memory |
| Medium | 50-150 | 2000-5000 words | Single memory |
| Large | 150+ | >5000 words | Split by layer |

**If splitting** (large projects):
- Create separate memories per architectural layer
- Example: `[Project] - Symbol Index: Data Layer`, `[Project] - Symbol Index: API Layer`
- Each split gets separate memory with layer-specific symbols

---

## Phase 7: Additional Reference Memories (as needed)

For content >400 words (detailed guides, comprehensive analysis), save as long-form memories:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'lib'))

from bridge import memory_save

memory_save(
    content="<full documentation>",
    title="[Project] - [Topic] Reference",
    context="Comprehensive guide for [topic]",
    keywords=["documentation", "guide", "reference"],
    tags=["reference", "documentation"],
    importance=8
)
```

---

## Phase 7B: Architecture Reference Memory

**Purpose**: Consolidate architecture analysis into a comprehensive reference memory that persists Serena's insights.

This creates the definitive architecture reference, accessible even when Serena is not active.

### Step 1: Synthesize Architecture Content

Combine insights from:
- Phase 2 architecture memories (symbol-level analysis)
- Phase 2B component relationships
- Phase 3 pattern discoveries
- Serena's `find_referencing_symbols` relationship data

### Step 2: Create Architecture Reference Memory

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'lib'))

from bridge import memory_save

memory_save(
    content="""# [Project] - Architecture Reference

Generated: [date]

## Overview

[2-3 paragraph summary of what the system does and how it's structured]

## Architecture Diagram

┌─────────────────────────────────────────────────────────────┐
│         Presentation Layer                                   │
│  (Streamlit Dashboard + FastAPI Prediction Server)           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Strategy Layer                                  │
│       (Decision Logic + Portfolio Management)                │
└─────────────────────────────────────────────────────────────┘
[Continue with remaining layers...]

## Layer Details

### Presentation Layer

**Purpose**: User interfaces and external API

**Key Components**:
- StreamlitApp (location: src/ui/app.py): Interactive dashboard
  - Key methods: render_dashboard(), handle_user_input()
  - Used by: End users
- PredictionAPI (location: src/api/server.py): REST API for predictions
  - Key methods: predict_endpoint(), health_check()
  - Used by: External systems (Serena ref count: 8)

**Patterns Used**: Dependency injection, async handlers

### [Next Layer...]

## Cross-Cutting Concerns

### Error Handling
All layers use centralized ErrorHandler. Exceptions bubble up with context.

### Configuration
Settings loaded via Pydantic from config.yaml. Environment overrides supported.

### Testing
Unit tests in tests/ directory. Integration tests use pytest fixtures.

## Component Relationships (from Serena analysis)

- AuthenticationService (42 refs) → FastAPI
- DataFetcher (15 refs) → PostgreSQL, Redis
- MLPipeline (8 refs) → XGBoost, DataFetcher

## Key Patterns

1. Async Generator Pattern - Memory-efficient streaming (15 uses)
2. Repository Pattern - Data access abstraction (8 implementations)
3. Dependency Injection - Via FastAPI Depends (42 uses)
4. Factory Pattern - Component creation (6 factories)

## Design Decisions

[Only if documented in repo - from Phase 5]""",
    title="[Project] - Architecture Reference",
    context="Comprehensive architecture documentation from Serena analysis",
    keywords=["architecture", "layers", "patterns", "design", "structure"],
    tags=["architecture", "reference", "foundation"],
    importance=9
)
```

### Size Guidelines

- **Target**: 3000-8000 words
- **If exceeding 8000 words**, split into multiple memories:
  - `[Project] - Architecture Reference: Data Layer`
  - `[Project] - Architecture Reference: ML Layer`
  - `[Project] - Architecture Reference: API Layer`
- Each split memory covers one architectural concern

---

## Execution Guidelines

### Phase Execution Order

Execute in order: 0 → 1 → 1B → 2 → **2B** → 3 → 4 → 5 → **6** → 6B → 7 → 7B

### Mandatory Phases (CANNOT SKIP)

| Phase | Minimum Output | Gate |
|-------|---------------|------|
| 0: Discovery | Gap analysis report | Report before proceeding |
| 1: Foundation | 5 memories | All 5 core memories |
| 2: Architecture | Layer memories | 1 per architectural layer |
| **2B: Components** | **3+ component memories** | **Component count met** |
| 3: Patterns | **3+ pattern memories** | Pattern count met |
| **6: Code Examples** | **3+ code example memories** | **Example count met** |
| 6B: Symbol Index | 1 memory | Memory created |
| 7B: Architecture Reference | 1 memory | Memory created |

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
6. **Use Context7** - Validate framework usage assumptions
7. **Update outdated memories** as discovered
8. **Mark obsolete** - Memories that reference removed code
9. **Phase 5 is documentation-only** - Never infer decisions from code
10. **Use only bridge methods** - memory_save(), memory_query(), memory_get_config()

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
for r in results:
    print(f"  - {r['metadata'].get('title', 'Untitled')}")

results = memory_query("What dependencies does this project use?", limit=5)
print(f"Found {len(results)} results for dependency query")
for r in results:
    print(f"  - {r['metadata'].get('title', 'Untitled')}")

results = memory_query("architecture patterns", limit=10)
print(f"Found {len(results)} architecture memories")
for r in results:
    print(f"  - {r['metadata'].get('title', 'Untitled')}")

results = memory_query("code examples async", limit=5)
print(f"Found {len(results)} code example memories")
for r in results:
    print(f"  - {r['metadata'].get('title', 'Untitled')}")
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

## Memories Created

| Type | Count | Minimum | Status |
|------|-------|---------|--------|
| Foundation memories | [X] | 5 | ✅/❌ |
| Architecture memories | [Y] | [per layer] | ✅/❌ |
| Component memories | [Z] | 3+ | ✅/❌ |
| Pattern memories | [W] | 3+ | ✅/❌ |
| Feature memories | [V] | 3+ | ✅/❌ |
| Code example memories | [U] | 3+ | ✅/❌ |
| Reference memories | [T] | 2+ | ✅/❌ |

## Phase Completion Status

| Phase | Status | Output |
|-------|--------|--------|
| 0: Discovery | ✅ | Gap analysis completed |
| 1: Foundation | ✅ | [X] memories |
| 1B: Dependencies | ✅/SKIP | [reason] |
| 2: Architecture | ✅ | [X] layer memories |
| 2B: Components | ✅ | [X] component memories |
| 3: Patterns | ✅ | [X] pattern memories |
| 4: Features | ✅/SKIP | [X] feature memories |
| 5: Decisions | ✅/SKIP | [X] decisions (or: no documentation found) |
| 6: Code Examples | ✅ | [X] code example memories |
| 6B: Symbol Index | ✅ | Symbol index memory |
| 7B: Architecture | ✅ | Architecture reference memory |

## Key Memories for Navigation

1. **Overview**: [title]
2. **Architecture Reference**: [title]
3. **Symbol Index**: [title]
4. **Component Dependency Graph**: [title]

## Component Summary

Components documented: [list]
Frameworks documented: [list]
Key relationships: [brief summary from dependency graph]

## Validation Queries Tested

- "How do I add a new endpoint?" → [result count + top result]
- "What patterns are used?" → [result count + top result]
- "What components exist?" → [result count + top result]
- "Show code examples for async" → [result count + top result]
```

This summary confirms the encoding meets minimum requirements and provides quick navigation for future agents.

---

## Advanced: Forgetful-Only Features

**NOTE**: The following features are ONLY available when using the Forgetful backend. The main workflow above works with BOTH backends using only bridge methods.

If you need these advanced features, you must be using Forgetful backend AND call the MCP tools directly (outside the bridge).

### Project Notes (Forgetful Only)

Forgetful supports project-level metadata for instant context:

```python
# Get project_id first
from bridge import memory_get_config
config = memory_get_config()

if config['backend'] == 'forgetful':
    # Get or create project
    result = execute_forgetful_tool("list_projects", {})
    project_id = None
    for project in result.get("projects", []):
        if project.get("name") == config['group_id']:
            project_id = project.get("id")
            break

    if not project_id:
        create_result = execute_forgetful_tool("create_project", {
            "name": config['group_id'],
            "description": "Project description",
            "project_type": "development"
        })
        project_id = create_result.get("project_id")

    # Update project notes
    execute_forgetful_tool("update_project", {
        "project_id": project_id,
        "notes": """Entry: python3 -m ProjectName.main
Tech: Python 3.12, FastAPI, PostgreSQL
Architecture: 6-layer (Data→Domain→Processing→ML→Strategy→Presentation)
Key patterns: Repository, Async generators, Dependency injection"""
    })
```

### Entity Graph (Forgetful Only)

Forgetful supports explicit entity and relationship creation:

```python
if config['backend'] == 'forgetful':
    # Create entity
    entity_result = execute_forgetful_tool("create_entity", {
        "name": "AuthenticationService",
        "entity_type": "other",
        "custom_type": "Service",
        "notes": "Centralized auth service. Location: src/services/auth.py",
        "tags": ["service", "auth"],
        "aka": ["AuthService", "auth_service"],
        "project_ids": [project_id]
    })
    entity_id = entity_result.get("entity_id")

    # Create relationship
    execute_forgetful_tool("create_entity_relationship", {
        "source_entity_id": entity_id,
        "target_entity_id": library_id,
        "relationship_type": "uses",
        "strength": 1.0,
        "metadata": {"role": "HTTP framework"}
    })

    # Link entity to memory
    execute_forgetful_tool("link_entity_to_memory", {
        "entity_id": entity_id,
        "memory_id": memory_id
    })
```

**Note**: Graphiti extracts entities automatically from memory content. No explicit entity creation needed.

### Code Artifacts (Forgetful Only)

Forgetful supports dedicated code artifact storage:

```python
if config['backend'] == 'forgetful':
    execute_forgetful_tool("create_code_artifact", {
        "title": "[Project] - Async Generator Pattern (Python)",
        "description": "Memory-efficient data streaming pattern",
        "code": "<full code implementation>",
        "language": "python",
        "tags": ["pattern", "async"],
        "project_id": project_id
    })
```

**Note**: For cross-backend compatibility, the main workflow uses memory_save() with code in markdown blocks instead.

### Documents (Forgetful Only)

Forgetful supports long-form documents with linking:

```python
if config['backend'] == 'forgetful':
    # Create document
    doc_result = execute_forgetful_tool("create_document", {
        "title": "[Project] - Symbol Index",
        "description": "LSP-accurate symbol listing",
        "content": "<full markdown content>",
        "document_type": "markdown",
        "project_id": project_id,
        "tags": ["symbol-index", "reference"]
    })
    doc_id = doc_result.get("document_id")

    # Create entry memory linked to document
    execute_forgetful_tool("create_memory", {
        "title": "[Project] - Symbol Index Reference",
        "content": "Symbol index summary. Full index in linked document.",
        "keywords": ["symbols", "index"],
        "tags": ["reference"],
        "importance": 8,
        "project_ids": [project_id],
        "document_ids": [doc_id]
    })
```

**Note**: For cross-backend compatibility, the main workflow uses memory_save() for long-form content instead.
