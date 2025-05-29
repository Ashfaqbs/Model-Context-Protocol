#  Setting Up Postgres MCP Pro with Claude Desktop (Developer Mode Enabled)

##  Objective

To integrate [Postgres MCP Pro](https://github.com/crystaldba/postgres-mcp) into Claude Desktop using Docker. This setup enables Claude to analyze and interact with a live PostgreSQL database through its Model Context Protocol (MCP) layer.

---

##  Use Case

Postgres MCP Pro is designed to support developers and AI assistants in performing intelligent database operations such as:

* SQL query optimization
* Index analysis and recommendation
* Schema health monitoring
* Safer SQL execution with context awareness
* AI-assisted database debugging

This integration is ideal for backend developers, data engineers, or AI developers who want enhanced database reasoning capabilities in an IDE-like workflow.

---

## Environment Requirements

* Docker installed and running
* Claude Desktop installed
* PostgreSQL instance accessible locally
* Developer Mode enabled in Claude Desktop

---

## PostgreSQL Configuration

The following configuration was used for the PostgreSQL database:

```properties
datasource.url=jdbc:postgresql://localhost:9991/mainschema
username=postgres
password=admin
```

---

##  Claude Desktop Configuration

### File Location

Modify `claude_desktop_config.json`. Location varies by OS:

* macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
* Windows: `%APPDATA%\Claude\claude_desktop_config.json`

### Updated JSON Configuration

```json
{
  "mcpServers": {
    "postgres": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "DATABASE_URI",
        "crystaldba/postgres-mcp",
        "--access-mode=unrestricted"
      ],
      "env": {
        "DATABASE_URI": "postgresql://postgres:admin@host.docker.internal:9991/mainschema"
      }
    }
  },
  "git": {
    "command": "docker",
    "args": [
      "run",
      "--rm",
      "-i",
      "--mount", "type=bind,src=/Users/username/Desktop,dst=/projects/Desktop",
      "--mount", "type=bind,src=/path/to/other/allowed/dir,dst=/projects/other/allowed/dir,ro",
      "--mount", "type=bind,src=/path/to/file.txt,dst=/projects/path/to/file.txt",
      "mcp/git"
    ]
  }
}
```

**Note:** `host.docker.internal` is used for Docker to communicate with localhost in macOS and Windows. For Linux, this should be replaced with `localhost`.

---

## 🧪 Execution Steps

1. Pull the Docker image:

   ```bash
   docker pull crystaldba/postgres-mcp
   ```

2. Update `claude_desktop_config.json` as shown above.

3. Enable **Developer Mode** in Claude Desktop from settings.

4. Restart Claude Desktop. Upon restart, the **Tools** tab should appear automatically.

5. Manually handle any advanced CLAUDE UI interactions or internal configuration steps not documented here.

---

## 🔗 Reference

* Official Repository: [https://github.com/crystaldba/postgres-mcp](https://github.com/crystaldba/postgres-mcp)

---


