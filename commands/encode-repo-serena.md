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

Also verify Graphiti MCP is connected:
```python
# Test Graphiti connection
try:
    result = mcp__graphiti__get_status()
    print("✅ Graphiti MCP server is connected")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("Run /context-hub-setup to configure Graphiti")
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
| Small Simple | 3-5 | 1 | 3-5 | 3-5 | 3-5 | 2-4 | 0-2 | 3-5 | 1 | 1 | 20-33 episodes |
| Small Complex | 5-7 | 1 | 5-8 | 5-10 | 5-8 | 4-6 | 0-3 | 5-8 | 1 | 1 | 32-52 episodes |
| Medium Standard | 5-10 | 1 | 10-15 | 10-20 | 8-12 | 5-10 | 0-5 | 5-10 | 1-2 | 1 | 46-86 episodes |
| Large | 8-12 | 2 | 15-20 | 20-40 | 12-18 | 10-15 | 0-8 | 8-15 | 2-4 | 1-2 | 78-136 episodes |

**Notes**:
- All content stored as episodes using Graphiti MCP
- Phase 1B creates 1-2 dependency episodes per project
- **Phase 2B is MANDATORY** - creates component episodes documenting relationships
- Phase 5 is CONDITIONAL - only if explicit documentation exists (see Phase 5 guidelines)
- **Phase 6 is MANDATORY** - minimum 3 code example episodes for any project
- Phase 6B creates Symbol Index episode - split by layer for large projects
- Phase 7B creates Architecture Reference episode - split by layer for very large projects

---

## Phase Completion Gates

**CRITICAL**: Do not proceed to the next phase until the current phase meets its minimum targets.

After each phase, report:
```
Phase [N] Complete:
- Created: [X] episodes (entities auto-extracted by Graphiti)
- Minimum required: [targets from table above]
- Status: ✅ Met / ❌ Not met (explain gaps)
```

**Mandatory phases** (cannot skip):
- Phase 0: Discovery
- Phase 1: Foundation
- Phase 2: Architecture
- **Phase 2B: Components** (minimum 3 component episodes)
- Phase 3: Patterns (minimum 3 pattern episodes)
- Phase 6: Code Examples (minimum 3 code example episodes)
- Phase 6B: Symbol Index (1 episode)
- Phase 7B: Architecture Reference (1 episode)

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
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))
from lib.config import get_git_repo_name

# Get group_id
group_id = get_git_repo_name() or Path.cwd().name
print(f"Group ID: {group_id}\n")

# Query existing episodes
results = mcp__graphiti__search_memory_facts({
    "query": "architecture patterns",
    "group_ids": [group_id],
    "max_facts": 10
})
print(f"Found {len(results)} existing facts")
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
- What's in Graphiti knowledge graph?
- What exists in codebase?
- What's missing?

Report findings before proceeding.

---

## Phase 1: Project Foundation (5-10 episodes)

### Get Group ID

Get the group_id from git repo:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))
from lib.config import get_git_repo_name

group_id = get_git_repo_name() or Path.cwd().name
print(f"Group ID: {group_id}")
```

### Create Foundation Episodes

```python
# 1. Project Overview
mcp__graphiti__add_memory({
    "name": "Project Overview",
    "episode_body": "[Project purpose, what problems it solves, main features]",
    "group_id": group_id,
    "source": "text",
    "source_description": "foundation"
})

# 2. Technology Stack
mcp__graphiti__add_memory({
    "name": "Technology Stack",
    "episode_body": "Language: Python 3.12. Frameworks: FastAPI, Streamlit. Database: ClickHouse. ML: XGBoost.",
    "group_id": group_id,
    "source": "text",
    "source_description": "foundation"
})

# 3. Architecture Pattern
mcp__graphiti__add_memory({
    "name": "Architecture Pattern",
    "episode_body": "6-layer architecture: Data→Domain→Processing→ML→Strategy→Presentation",
    "group_id": group_id,
    "source": "text",
    "source_description": "foundation"
})

# 4. Development Setup
mcp__graphiti__add_memory({
    "name": "Development Setup",
    "episode_body": "[Setup instructions, environment requirements, how to run]",
    "group_id": group_id,
    "source": "text",
    "source_description": "foundation"
})

# 5. Testing Strategy
mcp__graphiti__add_memory({
    "name": "Testing Strategy",
    "episode_body": "[Testing approach, frameworks used, how to run tests]",
    "group_id": group_id,
    "source": "text",
    "source_description": "foundation"
})

print("✅ Created 5 foundation episodes")
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

### Step 4: Create Dependency Episode

```python
mcp__graphiti__add_memory({
    "name": "[Project] - Dependencies and External Libraries",
    "episode_body": """Language: [lang] [version]. Core frameworks: [list with roles].
Data/storage: [databases]. HTTP/API: [frameworks].
Dev tools: [testing, linting, build].
Rationale: [why chosen, if documented].""",
    "group_id": group_id,
    "source": "text",
    "source_description": "dependency analysis"
})
```

---

## Phase 2: Symbol-Level Architecture (10-15 episodes)

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

### Step 4: Create Architecture Episodes

For each architectural layer discovered:
```python
mcp__graphiti__add_memory({
    "name": "[Project] - [Layer] Architecture",
    "episode_body": "Key symbols: [list]. Relationships: [discovered references]. Pattern: [identified pattern].",
    "group_id": group_id,
    "source": "text",
    "source_description": "Serena symbol analysis"
})
```

---

## Phase 2B: Component Relationships (via Episodes)

**Purpose**: Document project components and their relationships using Graphiti.

Components are captured through episodes. Graphiti automatically extracts entities and relationships from episode content.

### Minimum Requirements

| Project Size | Component Episodes |
|--------------|-------------------|
| Small | 3-5 |
| Medium | 10-20 |
| Large | 20-40 |

### Create Component Episodes

Document major components discovered via Serena:

```python
# Component episode example
mcp__graphiti__add_memory({
    "name": "[Project] - AuthenticationService Component",
    "episode_body": """AuthenticationService handles token validation and user context injection.
Location: src/services/auth.py
Dependencies: FastAPI, JWT library
Used by: All API endpoints requiring auth
Reference count: 42 (high usage across codebase)
Key methods: validate_token(), get_user_context()""",
    "group_id": group_id,
    "source": "text",
    "source_description": "component analysis"
})

# Framework/library episode example
mcp__graphiti__add_memory({
    "name": "[Project] - FastAPI Framework Integration",
    "episode_body": """FastAPI is the core HTTP framework.
Version: 0.104.1
Used for: REST API endpoints, WebSocket connections
Integration: Dependency injection via Depends()
Major components using it: All service endpoints""",
    "group_id": group_id,
    "source": "text",
    "source_description": "framework integration"
})
```

### Document Relationships

Capture relationships in episode content (Graphiti extracts them automatically):

```python
mcp__graphiti__add_memory({
    "name": "[Project] - Component Dependency Graph",
    "episode_body": """Component dependencies in [Project]:

AuthenticationService → FastAPI (uses for routing)
DataService → PostgreSQL (connects for storage)
APIHandler → AuthenticationService (depends on for auth)
MLPipeline → XGBoost (uses for predictions)

Relationship strengths based on Serena reference counts:
- High usage (30+ refs): AuthenticationService→FastAPI
- Medium usage (10-30 refs): DataService→PostgreSQL
- Low usage (<10 refs): MLPipeline→XGBoost""",
    "group_id": group_id,
    "source": "text",
    "source_description": "relationship analysis"
})
```

### Phase 2B Completion Checkpoint

```
Phase 2B Complete:
- Component episodes created: [count] (minimum 3-5)
- Relationship episode created: 1
- Key components documented: [list]
- Entities auto-extracted by Graphiti
- Status: ✅ Met minimum / ❌ Not met (create more before proceeding)
```

---

## Phase 3: Pattern Discovery (8-12 episodes, minimum 3)

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

### Create Pattern Episodes

For each significant pattern (used 3+ times):
```python
mcp__graphiti__add_memory({
    "name": "[Project] - [Pattern Name] Pattern",
    "episode_body": """Pattern: [name]. Used for: [purpose].
Locations: [list files/classes using it].
Implementation: [brief description of how it works].
Usage count: [X] occurrences across codebase.""",
    "group_id": group_id,
    "source": "text",
    "source_description": "pattern analysis"
})
```

### Phase 3 Completion Checkpoint

```
Phase 3 Complete:
- Patterns searched: [list categories checked]
- Patterns documented: [count] (minimum 3)
- Pattern episodes created: [list titles]
- Status: ✅ Met minimum / ❌ Not met (continue searching)
```

**Minimum 3 pattern episodes required.** If fewer than 3 patterns found, document whatever exists (even basic ones like "error handling approach").

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

### Create Feature Episodes

For each major feature:
```python
mcp__graphiti__add_memory({
    "name": "[Project] - [Feature Name] Implementation",
    "episode_body": """Feature: [user-facing description].
Entry point: [file:function].
Flow: [step-by-step through components].
Key components: [list classes/functions involved].
Configuration: [relevant settings if any].""",
    "group_id": group_id,
    "source": "text",
    "source_description": "feature analysis"
})
```

### Phase 4 Completion Checkpoint

```
Phase 4 Complete:
- Features identified: [count]
- Feature episodes created: [count] (minimum 3 for projects with 3+ features)
- Feature flows traced: [list]
- Status: ✅ Met / ⚠️ Fewer than 3 features exist (acceptable)
```

**Skip only if** project has fewer than 3 distinct features (e.g., single-purpose library).

---

## Phase 5: Design Decisions (DOCUMENTATION-ONLY)

**CRITICAL: This phase is CONDITIONAL. Only capture decisions that are EXPLICITLY documented.**

### What Counts as "Documented"

✅ **DO create decision episodes for**:
- ADRs (Architecture Decision Records) in `docs/adr/` or similar
- README sections titled "Why X", "Rationale", "Design Decisions"
- Code comments explicitly stating "We chose X because Y"
- CONTRIBUTING.md or DESIGN.md files explaining choices
- Commit messages or PR descriptions linked from docs

❌ **DO NOT create decision episodes for**:
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
Create 1 episode per documented decision:
```python
mcp__graphiti__add_memory({
    "name": "[Project] - Decision: [Topic]",
    "episode_body": """Decision: [what was decided].
Alternatives considered: [if documented].
Rationale: [QUOTE from documentation].
Source: [file path and line number].""",
    "group_id": group_id,
    "source": "text",
    "source_description": "documented decision"
})
```

**If NO documentation found**:
```
Phase 5 Complete:
- Searched: [X] markdown files, [Y] code files
- Documented decisions found: 0
- Status: ✅ SKIPPED (no explicit documentation)
```

**DO NOT** create decision episodes based on inference. This pollutes the knowledge base with assumptions.

---

## Phase 6: Code Examples (MANDATORY, minimum 3)

**Purpose**: Store reusable code patterns that enable an agent to understand HOW the codebase works, not just WHAT exists.

**THIS PHASE IS MANDATORY** - Minimum 3 code example episodes for any project.

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

### Create Code Example Episodes

For each key pattern/utility:

```python
mcp__graphiti__add_memory({
    "name": "[Project] - Async Generator Pattern (Python)",
    "episode_body": """# Async Generator Pattern (Python)

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
    "group_id": group_id,
    "source": "text",
    "source_description": "code example"
})
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
- Code example episodes created: [count] (minimum 3)
- Examples by category: [patterns: X, interfaces: Y, utilities: Z]
- Example titles: [list]
- Status: ✅ Met minimum / ❌ Not met (create more before proceeding)
```

**DO NOT proceed to Phase 6B until minimum count is met.**

---

## Phase 6B: Symbol Index Episode

**Purpose**: Compile Serena's LSP symbol analysis into a permanent, searchable episode.

This captures symbol locations, relationships, and reference counts that would otherwise be lost when Serena is not active.

### Step 1: Aggregate Symbol Data

Collect from all `get_symbols_overview` and `find_symbol` calls during Phase 2:
- Classes with file locations and line numbers
- Interfaces with their implementations
- Key functions with callers (from `find_referencing_symbols`)
- Reference counts for each symbol

### Step 2: Create Symbol Index Episode

```python
mcp__graphiti__add_memory({
    "name": "[Project] - Symbol Index",
    "episode_body": """# [Project] - Symbol Index

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
    "group_id": group_id,
    "source": "text",
    "source_description": "symbol index"
})
```

### Size Guidelines

| Project Size | Est. Symbols | Episode Size | Strategy |
|--------------|--------------|-------------|----------|
| Small | <50 | <2000 words | Single episode |
| Medium | 50-150 | 2000-5000 words | Single episode |
| Large | 150+ | >5000 words | Split by layer |

**If splitting** (large projects):
- Create separate episodes per architectural layer
- Example: `[Project] - Symbol Index: Data Layer`, `[Project] - Symbol Index: API Layer`
- Each split gets separate episode with layer-specific symbols

---

## Phase 7: Additional Reference Episodes (as needed)

For content >400 words (detailed guides, comprehensive analysis), save as long-form episodes:

```python
mcp__graphiti__add_memory({
    "name": "[Project] - [Topic] Reference",
    "episode_body": "<full documentation>",
    "group_id": group_id,
    "source": "text",
    "source_description": "reference documentation"
})
```

---

## Phase 7B: Architecture Reference Episode

**Purpose**: Consolidate architecture analysis into a comprehensive reference episode that persists Serena's insights.

This creates the definitive architecture reference, accessible even when Serena is not active.

### Step 1: Synthesize Architecture Content

Combine insights from:
- Phase 2 architecture episodes (symbol-level analysis)
- Phase 2B component relationships
- Phase 3 pattern discoveries
- Serena's `find_referencing_symbols` relationship data

### Step 2: Create Architecture Reference Episode

```python
mcp__graphiti__add_memory({
    "name": "[Project] - Architecture Reference",
    "episode_body": """# [Project] - Architecture Reference

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
    "group_id": group_id,
    "source": "text",
    "source_description": "architecture reference"
})
```

### Size Guidelines

- **Target**: 3000-8000 words
- **If exceeding 8000 words**, split into multiple episodes:
  - `[Project] - Architecture Reference: Data Layer`
  - `[Project] - Architecture Reference: ML Layer`
  - `[Project] - Architecture Reference: API Layer`
- Each split episode covers one architectural concern

---

## Execution Guidelines

### Phase Execution Order

Execute in order: 0 → 1 → 1B → 2 → **2B** → 3 → 4 → 5 → **6** → 6B → 7 → 7B

### Mandatory Phases (CANNOT SKIP)

| Phase | Minimum Output | Gate |
|-------|---------------|------|
| 0: Discovery | Gap analysis report | Report before proceeding |
| 1: Foundation | 5 episodes | All 5 core episodes |
| 2: Architecture | Layer episodes | 1 per architectural layer |
| **2B: Components** | **3+ component episodes** | **Component count met** |
| 3: Patterns | **3+ pattern episodes** | Pattern count met |
| **6: Code Examples** | **3+ code example episodes** | **Example count met** |
| 6B: Symbol Index | 1 episode | Episode created |
| 7B: Architecture Reference | 1 episode | Episode created |

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
7. **Update outdated episodes** as discovered
8. **Delete obsolete episodes** - Episodes that reference removed code
9. **Phase 5 is documentation-only** - Never infer decisions from code
10. **Use Graphiti MCP directly** - mcp__graphiti__add_memory(), mcp__graphiti__search_memory_facts()

## Quality Principles

- **Symbol-accurate**: Use LSP data, not guesses
- **Relationship-aware**: Document how things connect
- **One concept per episode** (atomic)
- **200-400 words ideal** per episode
- **Use descriptive episode names**
- **Quality over quantity**
- **Only document what's explicitly in the repo** (especially for decisions)
- **Let Graphiti extract entities** - No manual entity creation needed

---

## Validation

After completion, verify coverage:

### Test Episodes

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))
from lib.config import get_git_repo_name

group_id = get_git_repo_name() or Path.cwd().name

# Test basic queries
results = mcp__graphiti__search_memory_facts({
    "query": "How do I add a new API endpoint?",
    "group_ids": [group_id],
    "max_facts": 5
})
print(f"Found {len(results)} facts for endpoint query")

results = mcp__graphiti__search_memory_facts({
    "query": "What dependencies does this project use?",
    "group_ids": [group_id],
    "max_facts": 5
})
print(f"Found {len(results)} facts for dependency query")

results = mcp__graphiti__search_memory_facts({
    "query": "architecture patterns",
    "group_ids": [group_id],
    "max_facts": 10
})
print(f"Found {len(results)} architecture facts")

results = mcp__graphiti__search_memory_facts({
    "query": "code examples async",
    "group_ids": [group_id],
    "max_facts": 5
})
print(f"Found {len(results)} code example facts")
```

Test with architecture questions - Serena-encoded repos should answer accurately.

---

## Report Progress

After each phase, report using the checkpoint format:
```
Phase [N] Complete:
- Created: [X] episodes (entities auto-extracted by Graphiti)
- Minimum required: [targets from table]
- Status: ✅ Met / ❌ Not met
```

**Proceed automatically** to the next phase once the checkpoint is met. Do not wait for user confirmation.

---

## Final Encoding Summary

When encoding is complete, provide a summary in this format:

```
# [Project] Encoding Complete

## Episodes Created

| Type | Count | Minimum | Status |
|------|-------|---------|--------|
| Foundation episodes | [X] | 5 | ✅/❌ |
| Architecture episodes | [Y] | [per layer] | ✅/❌ |
| Component episodes | [Z] | 3+ | ✅/❌ |
| Pattern episodes | [W] | 3+ | ✅/❌ |
| Feature episodes | [V] | 3+ | ✅/❌ |
| Code example episodes | [U] | 3+ | ✅/❌ |
| Reference episodes | [T] | 2+ | ✅/❌ |

## Phase Completion Status

| Phase | Status | Output |
|-------|--------|--------|
| 0: Discovery | ✅ | Gap analysis completed |
| 1: Foundation | ✅ | [X] episodes |
| 1B: Dependencies | ✅/SKIP | [reason] |
| 2: Architecture | ✅ | [X] layer episodes |
| 2B: Components | ✅ | [X] component episodes |
| 3: Patterns | ✅ | [X] pattern episodes |
| 4: Features | ✅/SKIP | [X] feature episodes |
| 5: Decisions | ✅/SKIP | [X] decisions (or: no documentation found) |
| 6: Code Examples | ✅ | [X] code example episodes |
| 6B: Symbol Index | ✅ | Symbol index episode |
| 7B: Architecture | ✅ | Architecture reference episode |

## Key Episodes for Navigation

1. **Overview**: [title]
2. **Architecture Reference**: [title]
3. **Symbol Index**: [title]
4. **Component Dependency Graph**: [title]

## Component Summary

Components documented: [list]
Frameworks documented: [list]
Key relationships: [brief summary from dependency graph]
Entities extracted by Graphiti: [estimated count]

## Validation Queries Tested

- "How do I add a new endpoint?" → [result count + top result]
- "What patterns are used?" → [result count + top result]
- "What components exist?" → [result count + top result]
- "Show code examples for async" → [result count + top result]
```

This summary confirms the encoding meets minimum requirements and provides quick navigation for future agents.

---

## Notes on Graphiti

- **Automatic entity extraction**: Graphiti automatically extracts entities and relationships from episode content
- **No manual linking required**: Just add descriptive episodes with clear relationships in the text
- **Group ID scoping**: All episodes are scoped to the project's group_id for isolation
- **Search capabilities**: Use search_memory_facts for semantic search across episodes
- **Knowledge graph**: Graphiti builds a knowledge graph automatically from episode content
