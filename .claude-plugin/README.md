# Graphiti Context Hub Plugin Configuration

## MCP Server Setup

This plugin automatically configures Claude Code to connect to a Graphiti MCP server via HTTP.

### Server Configuration

The plugin adds an MCP server named `graphiti` that connects to:
- **URL**: `http://localhost:8000/mcp`
- **Transport**: HTTP

### Installing Graphiti Server

You need to install and run the Graphiti MCP server separately:

1. **Install Graphiti MCP server** (follow Graphiti documentation)
2. **Start the server** on port 8000:
   ```bash
   graphiti-server start --port 8000
   ```
3. **Verify connection** by running:
   ```bash
   /context-hub-setup
   ```

### Customizing the Endpoint

If you run Graphiti on a different host/port, update `.context-hub.yaml`:

```yaml
graphiti:
  group_id: "auto"
  endpoint: "http://your-host:your-port"
```

**Note:** The plugin will use the endpoint from `.context-hub.yaml` if specified, otherwise defaults to `http://localhost:8000`.
