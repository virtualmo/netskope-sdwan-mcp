# netskope-sdwan-mcp

Read-only MCP server for Netskope SD-WAN.

This repository is separate from the SDK and is intended to use the existing
`netskope-sdwan-py-sdk` project as its API client layer rather than making HTTP
requests directly.

Implemented as a thin MCP wrapper around `netskope-sdwan-py-sdk`. Only read
operations are exposed.

## Local development

Requirements:

- Python 3.11+

Create a virtual environment and install the package in editable mode:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

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

Run the smoke test placeholder:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Run the MCP server entrypoint after installing dependencies:

```bash
python -m netskope_sdwan_mcp.server
```

## Implemented tools

### Gateways

- `list_gateways`
- `get_gateway`

### Gateway groups

- `list_gateway_groups`
- `get_gateway_group`

### Segments

- `list_segments`
- `get_segment`

### Applications

- `list_applications`
- `get_application`

### Tenants

- `list_tenants`
- `get_tenant`

### Users

- `list_users`
- `get_user`

### User groups

- `list_user_groups`
- `get_user_group`

## Example usage

Ask the MCP server for gateways with a backend filter such as `status:up` using
`list_gateways(filter="status:up")`, then inspect one result in detail with
`get_gateway(id="...")`.

## Project layout

```text
src/netskope_sdwan_mcp/
tests/
```
