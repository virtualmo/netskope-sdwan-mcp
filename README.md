# netskope-sdwan-mcp

Read-only Netskope SD-WAN MCP server backed by the Python SDK
`netskope-sdwan-py-sdk`.

This repository is a thin MCP wrapper over the public SDK. It exposes
read-only Netskope SD-WAN tools plus a few small composite tools for agent and
GUI workflows. It does not make direct HTTP requests itself.

## Demo

See how to use natural language to query SD-WAN gateways, status, and link health via MCP:

https://github.com/user-attachments/assets/20ff406c-3931-42a1-83a6-01ebc8321d4f

## Quick start

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .

export NETSKOPESDWAN_BASE_URL="https://your-sdwan-tenant.api.eu.infiot.net"
export NETSKOPESDWAN_API_TOKEN="your-api-token"

python -m netskope_sdwan_mcp.server
```

Python 3.11+ is required.

## Installation

Clone the repository and install it in a virtual environment:

```bash
git clone <YOUR_REPO_URL>
cd netskope-sdwan-mcp
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

## Environment variables

Required:

```bash
export NETSKOPESDWAN_BASE_URL="https://your-sdwan-tenant.api.eu.infiot.net"
export NETSKOPESDWAN_API_TOKEN="your-api-token"
```

Optional:

```bash
export NETSKOPESDWAN_TIMEOUT="30"
export NETSKOPESDWAN_INSECURE="false"
```

Meaning:

- `NETSKOPESDWAN_BASE_URL`: Netskope SD-WAN API base URL
- `NETSKOPESDWAN_API_TOKEN`: API bearer token
- `NETSKOPESDWAN_TIMEOUT`: request timeout in seconds, default `30`
- `NETSKOPESDWAN_INSECURE`: set to `true` to disable TLS verification, default `false`

## Running locally

Run the MCP server over stdio:

```bash
source .venv/bin/activate
python -m netskope_sdwan_mcp.server
```

The current MCP surface includes:

- gateway tools
- compact gateway status tools
- read-only resource lookup tools
- audit events
- software and inventory tools
- site commands
- applications metadata
- v1 edges
- v1 monitoring
- v1 user groups

Composite tools currently implemented:

- `get_gateway_status(gateway_id)`
- `list_gateways_with_status()`
- `get_gateway_operational_snapshot(id, child_tenant_id=None)`

## Claude Desktop setup

Claude Desktop runs local MCP servers through a JSON config file. Add this
server under `mcpServers` and use absolute paths.

Config file locations:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\\Claude\\claude_desktop_config.json`

Example:

```json
{
  "mcpServers": {
    "netskope-sdwan": {
      "command": "/ABSOLUTE/PATH/TO/netskope-sdwan-mcp/.venv/bin/python",
      "args": ["-m", "netskope_sdwan_mcp.server"],
      "env": {
        "NETSKOPESDWAN_BASE_URL": "https://your-sdwan-tenant.api.eu.infiot.net",
        "NETSKOPESDWAN_API_TOKEN": "your-api-token",
        "NETSKOPESDWAN_TIMEOUT": "30",
        "NETSKOPESDWAN_INSECURE": "false"
      }
    }
  }
}
```

Restart Claude Desktop after saving the file.

## Gemini CLI setup

Gemini CLI supports MCP servers through `mcpServers` in `settings.json`, or via
`gemini mcp add`.

User-scoped config file:

- `~/.gemini/settings.json`

Project-scoped config file:

- `.gemini/settings.json`

Example `settings.json` entry:

```json
{
  "mcpServers": {
    "netskope-sdwan": {
      "command": "/ABSOLUTE/PATH/TO/netskope-sdwan-mcp/.venv/bin/python",
      "args": ["-m", "netskope_sdwan_mcp.server"],
      "env": {
        "NETSKOPESDWAN_BASE_URL": "$NETSKOPESDWAN_BASE_URL",
        "NETSKOPESDWAN_API_TOKEN": "$NETSKOPESDWAN_API_TOKEN",
        "NETSKOPESDWAN_TIMEOUT": "$NETSKOPESDWAN_TIMEOUT",
        "NETSKOPESDWAN_INSECURE": "$NETSKOPESDWAN_INSECURE"
      },
      "cwd": "/ABSOLUTE/PATH/TO/netskope-sdwan-mcp"
    }
  }
}
```

Or add it from the CLI:

```bash
gemini mcp add -s user \
  -e NETSKOPESDWAN_BASE_URL="$NETSKOPESDWAN_BASE_URL" \
  -e NETSKOPESDWAN_API_TOKEN="$NETSKOPESDWAN_API_TOKEN" \
  -e NETSKOPESDWAN_TIMEOUT="${NETSKOPESDWAN_TIMEOUT:-30}" \
  -e NETSKOPESDWAN_INSECURE="${NETSKOPESDWAN_INSECURE:-false}" \
  netskope-sdwan \
  /ABSOLUTE/PATH/TO/netskope-sdwan-mcp/.venv/bin/python \
  -m netskope_sdwan_mcp.server
```

## Example prompts

- `List gateways with status and highlight anything offline or degraded.`
- `Get gateway status for gateway gw-001.`
- `Get a gateway operational snapshot for gw-001.`
- `List recent audit events from 2026-04-16T00:00:00Z to 2026-04-16T23:59:59Z.`
- `Show the latest interfaces, paths, and routes for gateway gw-001.`
- `List site commands and fetch the output for command cmd-001 and file output.txt.`

## Safety notes

This MCP server is intentionally read-only.

It does not expose write, create, update, or delete operations.

Sensitive gateway credential endpoints are intentionally not exposed:

- local UI password retrieval
- SSH password retrieval

The compact gateway summary tools are also intentionally designed to avoid
returning large raw gateway configuration payloads unless you call the lower
level gateway detail tools directly.
