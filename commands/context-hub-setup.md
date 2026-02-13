---
description: Configure Graphiti MCP backend and plugin prerequisites
---

# Context Hub Setup

Configure Context Hub with Graphiti memory backend and verify prerequisites.

## Overview

This setup command will:
1. Check plugin prerequisites (Serena, Context7)
2. Verify Graphiti MCP configuration
3. Create `.context-hub.yaml` configuration file
4. Test Graphiti connectivity
5. Verify group_id auto-detection

## Step 1: Check Plugin Prerequisites

Check if required plugins are installed:

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

## Step 2: Verify Graphiti MCP Configuration

Check if Graphiti MCP is configured:

```bash
claude mcp list | grep -i graphiti
```

**If not configured, guide setup:**
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

## Step 3: Create Configuration File

Create `.context-hub.yaml` in your project root:

```python
import yaml
from pathlib import Path

config = {
    'memory': {
        'backend': 'graphiti',
        'group_id': 'auto'
    }
}

config_path = Path.cwd() / '.context-hub.yaml'
with open(config_path, 'w') as f:
    yaml.dump(config, f, default_flow_style=False)

print(f"✅ Created config at: {config_path}")
```

## Step 4: Test Graphiti Connection

Verify connectivity using MCP tools:

```python
# Test Graphiti connection
try:
    result = mcp__graphiti__get_status()
    print("✅ Graphiti MCP server is connected")
    print(f"Status: {result}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("Ensure Graphiti MCP server is running and configured correctly")
```

## Step 5: Verify Group ID Auto-Detection

Test that group_id is correctly detected:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))
from lib.config import get_git_repo_name

# Check git detection
git_name = get_git_repo_name()
if git_name:
    print(f"✅ Git repository detected: {git_name}")
    print(f"   This will be used as your group_id")
else:
    fallback = Path.cwd().name
    print(f"⚠️  No git repository found")
    print(f"   Using directory name as group_id: {fallback}")
```

## Step 6: Verify Complete Setup

Report comprehensive status:

```python
import subprocess
from pathlib import Path

print("=" * 50)
print("Context Hub Setup Status")
print("=" * 50)
print(f"Memory Backend: graphiti")
print(f"Config File:    {Path.cwd() / '.context-hub.yaml'}")
print()

# Check MCP status
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

mcp_status = "✅ Configured" if check_mcp("graphiti") else "❌ Not configured"
print(f"Graphiti MCP: {mcp_status}")

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

print(f"Serena Plugin:   {serena_status}")
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

## Step 7: Quick Test (Optional)

Test the setup:

```python
# Test Graphiti connection
result = mcp__graphiti__get_status()
print(f"✅ Graphiti status: {result}")

# List recent episodes
episodes = mcp__graphiti__get_episodes({"max_episodes": 5})
print(f"✅ Recent episodes: {len(episodes)} found")
```

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

### Graphiti Issues

**Connection failed:**
- Verify server is running: `curl http://localhost:8000/health`
- Check MCP config: `claude mcp list`
- Review Claude Code logs for MCP errors
- Verify Graphiti MCP server is properly configured

**MCP not found:**
```bash
claude mcp add graphiti --scope user -- npx @graphiti/mcp-server
```

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
- Ensure `.context-hub.yaml` is in current directory or project root
- Check file permissions

**Group ID not detected:**
- Verify git repository exists: `git remote -v`
- Override by setting `group_id: "your-project-name"` in config

## Configuration Reference

### Minimal Config
```yaml
memory:
  backend: "graphiti"
  group_id: "auto"
```

### Full Config Example
```yaml
memory:
  backend: "graphiti"
  group_id: "my-project"  # or "auto" for auto-detection
```

## Notes

- Configuration is searched in order: `./.context-hub.yaml`, `<project-root>/.context-hub.yaml`
- MCP server configs are stored in `~/.claude.json`
- Serena and Context7 are plugins, not MCPs - install via `claude plugins install`
- Group ID auto-detection uses: 1) git repo name, 2) directory name (fallback)
