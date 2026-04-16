# netskope-sdwan-mcp

Read-only MCP server scaffold for Netskope SD-WAN.

This repository is separate from the SDK and is intended to use the existing
`netskope-sdwan-py-sdk` project as its API client layer rather than making HTTP
requests directly.

## Status

This is an initial project scaffold only. No MCP tool logic is implemented yet,
and no write operations are included.

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

## Project layout

```text
src/netskope_sdwan_mcp/
tests/
```
