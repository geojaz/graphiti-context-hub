---
description: Configure Context Hub backend (Graphiti/Forgetful) and plugin prerequisites
---

# Context Hub Setup

Configure Context Hub's memory backend and dependencies: Graphiti or Forgetful MCP server, plus prerequisite plugins.

## Overview

Context Hub supports two memory backends:
- **Graphiti** - Knowledge graph with automatic entity/relationship extraction (recommended)
- **Forgetful** - Atomic memories with explicit linking

This setup command will:
1. Check plugin prerequisites (Serena, Context7)
2. Help you choose and configure a memory backend
3. Create `.context-hub.yaml` configuration file
4. Test MCP connectivity
5. Verify group_id auto-detection

## Step 1: Check Plugin Prerequisites

First, check if the required plugins are installed:

```bash
claude plugins list
```

Look for:
- `serena` or similar (for code analysis)
- `context7` or similar (for framework docs)

**If Serena is not installed:**
```
To use /encode-repo-serena, install the Serena plugin:

  claude plugins install serena

Or search for it in the marketplace:

  claude plugins search serena
```

**If Context7 is not installed:**
```
For framework documentation in /context_gather, install Context7:

  claude plugins install context7 --marketplace pleaseai/claude-code-plugins

Or search for it:

  claude plugins search context7
```

## Step 2: Choose Memory Backend

Ask the user which backend they prefer:

**Question**: "Which memory backend would you like to use?"

**Options**:
1. **Graphiti (Recommended)** - Knowledge graph with automatic entity extraction
   - Best for: Complex projects, relationship discovery, semantic understanding
   - Requires: Graphiti MCP server running (typically localhost:8000)

2. **Forgetful** - Atomic memories with explicit linking
   - Best for: Simple notes, explicit memory management
   - Requires: Forgetful MCP server (uvx or custom setup)

### Option A: Graphiti Setup

If user chose Graphiti:

1. **Check if Graphiti MCP is configured:**
   ```bash
   claude mcp list | grep -i graphiti
   ```

2. **If not configured, guide setup:**
   ```
   To use Graphiti, you need the Graphiti MCP server running.

   Installation options:

   1. Local server (Docker):
      docker run -p 8000:8000 graphiti/mcp-server

   2. Remote server:
      Ensure server is accessible at configured endpoint

   3. Add to Claude MCP config:
      claude mcp add graphiti --scope user -- npx @graphiti/mcp-server

   For detailed setup: https://github.com/getzep/graphiti
   ```

3. **Create `.context-hub.yaml`:**
   ```python
   import yaml
   from pathlib import Path

   config = {
       'memory': {
           'backend': 'graphiti',
           'group_id': 'auto',
           'graphiti': {
               'endpoint': 'http://localhost:8000/mcp'
           }
       }
   }

   config_path = Path.cwd() / '.context-hub.yaml'
   with open(config_path, 'w') as f:
       yaml.dump(config, f, default_flow_style=False)

   print(f"Created config at: {config_path}")
   ```

4. **Test connectivity:**
   ```python
   # Test Graphiti connection using bridge
   import sys
   from pathlib import Path

   sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))
   from bridge import memory_get_config, memory_list_operations

   try:
       config = memory_get_config()
       print(f"✅ Backend: {config['backend']}")
       print(f"✅ Group ID: {config['group_id']}")

       # Test operation listing
       ops = memory_list_operations()
       print(f"✅ Connected to Graphiti - {len(ops)} operations available")

   except Exception as e:
       print(f"❌ Connection failed: {e}")
       print("Ensure Graphiti MCP server is running and configured correctly")
   ```

### Option B: Forgetful Setup

If user chose Forgetful:

1. **Check if Forgetful MCP is configured:**
   ```bash
   claude mcp list | grep -i forgetful
   ```

2. **If not configured, ask setup preference:**

   **Question**: "How would you like to configure Forgetful?"

   **Options**:
   - **Standard (Recommended)** - Zero config, uses uvx with SQLite storage
   - **Custom** - Remote HTTP server, PostgreSQL, custom embeddings

3. **Standard Setup:**
   ```bash
   claude mcp add forgetful --scope user -- uvx forgetful-ai
   ```

   Confirm:
   ```bash
   claude mcp list | grep -i forgetful
   ```

4. **Custom Setup:**

   Fetch configuration docs:
   ```
   WebFetch: https://github.com/ScottRBK/forgetful/blob/main/docs/configuration.md
   ```

   Guide through options:
   - **Remote HTTP server** - Connect to Forgetful running elsewhere
   - **PostgreSQL backend** - Use Postgres instead of SQLite
   - **Custom embeddings** - Different embedding model/provider

5. **Create `.context-hub.yaml`:**
   ```python
   import yaml
   from pathlib import Path

   config = {
       'memory': {
           'backend': 'forgetful',
           'group_id': 'auto',
           'forgetful': {}
       }
   }

   config_path = Path.cwd() / '.context-hub.yaml'
   with open(config_path, 'w') as f:
       yaml.dump(config, f, default_flow_style=False)

   print(f"Created config at: {config_path}")
   ```

6. **Test connectivity:**
   ```python
   # Test Forgetful connection using bridge
   import sys
   from pathlib import Path

   sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))
   from bridge import memory_get_config, memory_list_operations

   try:
       config = memory_get_config()
       print(f"✅ Backend: {config['backend']}")
       print(f"✅ Group ID: {config['group_id']}")

       # Test operation listing
       ops = memory_list_operations()
       print(f"✅ Connected to Forgetful - {len(ops)} operations available")

   except Exception as e:
       print(f"❌ Connection failed: {e}")
       print("Ensure Forgetful MCP server is configured and accessible")
   ```

## Step 3: Verify Group ID Auto-Detection

Test that group_id is correctly detected:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))
from lib.config import get_git_repo_name, find_project_root

# Check git detection
git_name = get_git_repo_name()
if git_name:
    print(f"✅ Git repository detected: {git_name}")
    print(f"   This will be used as your group_id")
else:
    fallback = Path.cwd().name
    print(f"⚠️  No git repository found")
    print(f"   Using directory name as group_id: {fallback}")

# Show project root
root = find_project_root()
if root:
    print(f"✅ Project root: {root}")
```

## Step 4: Verify Complete Setup

Report comprehensive status:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))
from bridge import memory_get_config

# Get config
config = memory_get_config()

print("=" * 50)
print("Context Hub Setup Status")
print("=" * 50)
print(f"Memory Backend: {config['backend']}")
print(f"Group ID:       {config['group_id']}")
print(f"Config File:    {Path.cwd() / '.context-hub.yaml'}")
print()

# Check MCP status
import subprocess

def check_mcp(name):
    try:
        result = subprocess.run(
            ['claude', 'mcp', 'list'],
            capture_output=True,
            text=True
        )
        return name.lower() in result.stdout.lower()
    except:
        return False

backend = config['backend']
mcp_status = "✅ Configured" if check_mcp(backend) else "❌ Not configured"
print(f"{backend.capitalize()} MCP: {mcp_status}")

# Check plugins
def check_plugin(name):
    try:
        result = subprocess.run(
            ['claude', 'plugins', 'list'],
            capture_output=True,
            text=True
        )
        return name.lower() in result.stdout.lower()
    except:
        return False

serena_status = "✅ Installed" if check_plugin("serena") else "❌ Not installed"
context7_status = "✅ Installed" if check_plugin("context7") else "⚠️  Not installed (optional)"

print(f"Serena Plugin:  {serena_status}")
print(f"Context7 Plugin: {context7_status}")
print()

print("Available Commands:")
print("  /context_gather <task>  - Multi-source context retrieval")
print("  /encode-repo-serena     - Repository encoding (requires Serena)")
print("  /memory-search <query>  - Search memories")
print("  /memory-list [count]    - List recent memories")
print("  /memory-save            - Save current context")
print("  /memory-explore <query> - Knowledge graph traversal")
print("=" * 50)
```

## Step 5: Quick Test (Optional)

Offer to test the setup:

**Test memory backend:**
```
/memory-list
```

If successful, you should see a list of recent memories (or empty if just set up).

**Test Serena (if installed):**
```python
# Quick Serena test
mcp__plugin_serena_serena__get_current_config()
```

**Test Context7 (if installed):**
```
Ask about a framework: "How does FastAPI dependency injection work?"
```

## Troubleshooting

### Backend Issues

**Graphiti connection failed:**
- Verify server is running: `curl http://localhost:8000/health`
- Check MCP config: `claude mcp list`
- Review Claude Code logs for MCP errors
- Verify endpoint in `.context-hub.yaml`

**Forgetful connection failed:**
- Check if `uvx` is installed: `which uvx`
- For HTTP: verify server is running
- Check MCP config: `claude mcp list`
- Review Claude Code logs

### Plugin Issues

**Serena not found:**
```bash
claude plugins install serena
```

**Context7 not found:**
```bash
claude plugins install context7 --marketplace pleaseai/claude-code-plugins
```

### Configuration Issues

**Config file not found:**
- Ensure `.context-hub.yaml` is in current directory, project root, or home directory
- Check file permissions

**Group ID not detected:**
- Verify git repository exists: `git remote -v`
- Override by setting `group_id: "your-project-name"` in config

## Configuration Reference

### Minimal Config (Graphiti)
```yaml
memory:
  backend: "graphiti"
  group_id: "auto"
```

### Minimal Config (Forgetful)
```yaml
memory:
  backend: "forgetful"
  group_id: "auto"
```

### Full Config Example
```yaml
memory:
  backend: "graphiti"
  group_id: "my-project"  # or "auto" for auto-detection

  graphiti:
    endpoint: "http://localhost:8000/mcp"

  forgetful:
    # Backend-specific settings (if using Forgetful)
```

## Notes

- Configuration is searched in order: `./.context-hub.yaml`, `<project-root>/.context-hub.yaml`, `~/.context-hub.yaml`
- MCP server configs are stored in `~/.claude.json` (persist across updates)
- Serena and Context7 are plugins, not MCPs - install via `claude plugins install`
- Group ID auto-detection uses: 1) git repo name, 2) directory name (fallback)
- Both backends can coexist - switch by changing `backend` in config
