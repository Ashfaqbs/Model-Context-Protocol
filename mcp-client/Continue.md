# Model Context Protocol (MCP) Integration with Continue.dev

## Overview

Model Context Protocol (MCP) is an open communication protocol that enables seamless interaction between AI models and external tools or data sources. Within the Continue.dev environment, MCP provides a standard interface to inject dynamic and structured context from multiple tools into AI workflows.

This guide outlines how to integrate MCP into Continue.dev, configure MCP servers, and use them effectively.

## Installing Continue

1. Install the Continue extension for your preferred IDE (VS Code or JetBrains).
2. Complete initial setup by following the installation guide at [https://docs.continue.dev](https://docs.continue.dev).

## Creating MCP Server Configuration

To register an MCP server:

1. At the root of your workspace, create a folder named `.continue/mcpServers`.
2. Inside that folder, create a YAML configuration file (e.g., `playwright-mcp.yaml`).
3. Use the following template as a base configuration:

```yaml
name: Playwright MCP Server
version: 0.0.1
schema: v1
mcpServers:
  - name: Browser Search
    command: npx
    args:
      - "@playwright/mcp@latest"
```

This sets up an MCP server using Playwright to perform browser-based tasks.

## Testing the MCP Server

Once configured, you can test it using a command like:

```
Open the browser and navigate to Hacker News. Save the top 10 headlines in a hn.txt file.
```

If set up correctly, the MCP server will produce a file `hn.txt` containing the headlines.

## Alternative Configuration via `config.yaml`

MCP servers can also be defined directly in the Continue configuration file:

```yaml
mcpServers:
  - name: SQLite MCP
    command: npx
    args:
      - "-y"
      - "mcp-sqlite"
      - "/path/to/your/database.db"
```

This defines a server for interacting with a SQLite database.

## Transport Types Supported

MCP supports multiple transport mechanisms:

### stdio

```yaml
mcpServers:
  - name: Local SQLite Server
    type: stdio
    command: npx
    args:
      - "mcp-sqlite"
      - "/path/to/your/database.db"
```

### sse (Server-Sent Events)

```yaml
mcpServers:
  - name: Remote SSE Server
    type: sse
    url: https://your-sse-server.com
```

### streamable-http

```yaml
mcpServers:
  - name: Remote HTTP Server
    type: streamable-http
    url: https://your-http-server.com
```

## Managing Environment Variables and Secrets

To inject sensitive information securely:

```yaml
mcpServers:
  - name: Secure MCP Server
    command: npx
    args:
      - "mcp-secure"
    env:
      API_KEY: ${{ secrets.API_KEY }}
```

Ensure secrets are securely stored and referenced correctly.

## Available MCP Servers

Common MCP server types include:

* Playwright MCP: for browser automation.
* SQLite MCP: for querying SQLite databases.

More servers are available at: [https://hub.continue.dev/explore/mcp](https://hub.continue.dev/explore/mcp)

## Additional Resources

* MCP documentation: [https://docs.continue.dev/customize/deep-dives/mcp](https://docs.continue.dev/customize/deep-dives/mcp)
* Model Context Protocol Specification: [https://modelcontextprotocol.io](https://modelcontextprotocol.io)
* Continue Configuration Reference: [https://docs.continue.dev/reference](https://docs.continue.dev/reference)

## Summary

Model Context Protocol (MCP) allows the Continue.dev environment to enhance its LLM capabilities by incorporating real-time, dynamic context from external sources. This documentation serves as a complete reference for setting up and using MCP in Continue-based development environments.
