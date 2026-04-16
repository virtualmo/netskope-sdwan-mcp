# netskope-sdwan-mcp

Read-only Netskope SD-WAN MCP server backed by the Python SDK
`netskope-sdwan-py-sdk`.

This repository is a thin MCP wrapper over the SDK. It exposes read-only tools
and does not make direct HTTP requests itself.

## Implemented tools

### Gateway tools

- `list_gateways`
- `get_gateway`

### Resource tools

- `list_gateway_groups`
- `get_gateway_group`
- `list_segments`
- `get_segment`
- `list_applications`
- `get_application`
- `list_tenants`
- `get_tenant`
- `list_users`
- `get_user`
- `list_user_groups`
- `get_user_group`

### Audit tools

- `list_audit_events`

### Monitoring tools

- `get_interfaces_latest`
- `get_paths_latest`
- `get_routes_latest`
- `get_system_load`
- `get_paths_links_totals`

## Environment

Python 3.11+ is required.

Required environment variables:

```bash
export NETSKOPESDWAN_BASE_URL="https://your-sdwan-tenant.api.eu.infiot.net"
export NETSKOPESDWAN_API_TOKEN="your-api-token"
```

Optional environment variables:

```bash
export NETSKOPESDWAN_TIMEOUT="30"
export NETSKOPESDWAN_INSECURE="false"
```

## Local run

Create a virtual environment and install the package in editable mode:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

Minimal local run:

```bash
source .venv/bin/activate
export NETSKOPESDWAN_BASE_URL="https://your-sdwan-tenant.api.eu.infiot.net"
export NETSKOPESDWAN_API_TOKEN="your-api-token"
python -m netskope_sdwan_mcp.server
```
