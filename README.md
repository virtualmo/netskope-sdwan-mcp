![Python](https://img.shields.io/badge/python-3.11%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/github/license/virtualmo/netskope-sdwan-py-sdk)
![CI](https://github.com/virtualmo/netskope-sdwan-py-sdk/actions/workflows/ci.yml/badge.svg)
![Status](https://img.shields.io/badge/status-alpha-orange)
![MCP](https://img.shields.io/badge/MCP-compatible-blue)
[![Docs](https://img.shields.io/badge/docs-tools-blue)](./docs/tools.md)

# netskope-sdwan-mcp

Read-only Netskope SD-WAN MCP server backed by the Python SDK
[`netskope-sdwan-py-sdk`](https://github.com/virtualmo/netskope-sdwan-py-sdk).

This repository is a thin MCP wrapper over the public SDK. It exposes
read-only Netskope SD-WAN tools plus a few small composite tools for agent and
GUI workflows. It does not make direct HTTP requests itself.

> ⚠️ **Disclaimer:** This project is not an official Netskope product.

## Demo

See how to use natural language to query SD-WAN gateways, status, and link health via MCP:

https://github.com/user-attachments/assets/8961501c-8903-4478-a32b-c39c2b21c443


## Installation

Clone the repository and install it in a virtual environment:

```bash
git clone https://github.com/virtualmo/netskope-sdwan-mcp.git
cd netskope-sdwan-mcp
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
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

## Transport

- Local: ✅ stdio (Claude Desktop, Gemini CLI)
- Remote: ✅ experimental Streamable HTTP

## Running locally

Local stdio mode remains the default. Existing local setups do not need to change.

Run the MCP server over stdio:

```bash
source .venv/bin/activate
python -m netskope_sdwan_mcp.server
```

## Running remotely

Minimal remote MCP hosting is now available through FastMCP's Streamable HTTP
transport.

```bash
source .venv/bin/activate
export MCP_TRANSPORT="http"
export MCP_HOST="127.0.0.1"
export MCP_PORT="8000"
python -m netskope_sdwan_mcp.server
```

Environment variables:

- `MCP_TRANSPORT`: `stdio` (default) or `http`
- `MCP_HOST`: bind host for remote HTTP mode, default `127.0.0.1`
- `MCP_PORT`: bind port for remote HTTP mode, default `8000`

Notes:

- `MCP_TRANSPORT=http` maps to FastMCP's current `streamable-http` transport
- SSE is intentionally not enabled in this project
- for real hosted deployment, put the server behind HTTPS, authentication, and
  a reverse proxy or equivalent edge controls

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
server under `mcpServers` and use absolute paths. Keep the default stdio mode
for these local desktop clients.

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
        "NETSKOPESDWAN_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

Restart Claude Desktop after saving the file.

> [!NOTE]
> To avoid being prompted for each tool call during a session:  
> **Customize → Connectors → `netskope-sdwan` → Tool Permissions → “Always Allow”**  
>  
> This disables per-call approval prompts for MCP tools.


## Gemini CLI setup

Gemini CLI supports MCP servers through `mcpServers` in `settings.json`, or via
`gemini mcp add`. Keep the default stdio mode for local CLI usage.

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
        "NETSKOPESDWAN_API_TOKEN": "$NETSKOPESDWAN_API_TOKEN"
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
- `List recent audit events from last 24 hours`
- `Show the latest interfaces, paths, and routes for gateway gw-001.`

## Supported Capabilities

This MCP server provides access to Netskope SD-WAN resources, including:

- [Gateways](./docs/tools.md#gateways)
- [Policies](./docs/tools.md#policies)
- [Segments](./docs/tools.md#segments)
- [Device Groups](./docs/tools.md#device-groups)
- [Inventory](./docs/tools.md#inventory)
- [Monitoring (v1 legacy)](./docs/tools.md#monitoring-v1-legacy)

> 📄 Full tool reference: [View all MCP tools](./docs/tools.md)


## Safety notes

This MCP server is intentionally read-only.

It does not expose write, create, update, or delete operations.

Sensitive gateway credential endpoints are intentionally not exposed:

- local UI password retrieval
- SSH password retrieval

The compact gateway summary tools are also intentionally designed to avoid
returning large raw gateway configuration payloads unless you call the lower
level gateway detail tools directly.

## Example token permissions

Example SDWAN Tenant token permissions used for SDK validation:

```json
[
  {
    "rap_resource": "",
    "rap_privs": [
      "privGoskopeRead",
      "privPolicyRead",
      "privTaskRead",
      "privSegmentObjectRead",
      "privOverlayTagRead",
      "privNotificationChannelRead",
      "privSiteGroupRead",
      "privManagedDeviceProfileRead",
      "privTenantRead",
      "privTenantView",
      "privTenantSettingsRead",
      "privAlertSettingsRead",
      "privMonitorRead",
      "privMonitorAlertRead",
      "privInventoryDeviceRead",
      "privSASERead",
      "privManagedDevicePolicyRead",
      "privUserGroupRead",
      "privLoggedIn",
      "privOpsProbe",
      "privIpInfo",
      "privSiteRead",
      "privSiteWrite",
      "privSiteToken",
      "privSiteName",
      "privManagedDeviceDestinationRead",
      "privCaCertificateRead",
      "privTokenRead",
      "privCustomAppRead",
      "privIdpRead",
      "privIaasAccountRead",
      "privAuditRecordRead",
      "privAppAccessPolicyRead",
      "privRoleRead",
      "privUserRead",
      "privAddressGroupRead",
      "privAddressObjectRead",
      "privManagedDeviceRead",
      "privManagedDeviceServiceRead",
      "privAppRead",
      "privVPNPeerRead",
      "privAppContainerRead",
      "privRadiusRead"
    ]
  }
]
```

### Pagination & Sorting

All `list_*` tools support the following parameters (when supported by the underlying API):

- `filter`: API filter string
- `after`: cursor for pagination
- `first`: number of results to return
- `sort`: sort expression

Example:

```json
{
  "first": 50,
  "after": "cursor_token",
  "sort": "-created_at"
}
```

`list_all` Fetches multiple pages automatically for supported paginated resources. It supports the same paginated resource families already exposed by the MCP where the SDK provides cursor-based `.list(...)` behavior.


## Disclaimer

This project is unofficial and is not affiliated with, endorsed by, or supported by Netskope.

The SDK is provided on an "as-is" basis without warranties of any kind. Users are responsible for validating functionality and suitability for their own use cases.
