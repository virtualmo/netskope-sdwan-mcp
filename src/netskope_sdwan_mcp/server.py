"""Minimal MCP server entrypoint for Netskope SD-WAN."""

from __future__ import annotations

from typing import Any

from .tools.gateways import get_gateway, list_gateways
from .tools.gateway_groups import get_gateway_group, list_gateway_groups
from .tools.segments import get_segment, list_segments
from .tools.tenants import get_tenant, list_tenants
from .tools.user_groups import get_user_group, list_user_groups
from .tools.users import get_user, list_users

SERVER_NAME = "netskope-sdwan-mcp"
PLACEHOLDER_TOOL_NAMES = ("list_sites", "list_alerts", "list_audit_events")


def create_server() -> Any:
    """Create the MCP server and register placeholder read-only tools."""
    try:
        from mcp.server.fastmcp import FastMCP
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "The MCP Python SDK is required. Install project dependencies to run the server."
        ) from exc

    server = FastMCP(SERVER_NAME, json_response=True)
    register_tools(server)
    return server


def register_tools(server: Any) -> Any:
    """Register real and placeholder read-only tool handlers on an MCP server."""

    @server.tool(name="list_gateways")
    def _list_gateways(filter: str = None) -> list[dict[str, Any]] | dict[str, Any]:
        return list_gateways(filter=filter)

    @server.tool(name="get_gateway")
    def _get_gateway(id: str) -> dict[str, Any]:
        return get_gateway(id)

    @server.tool(name="list_gateway_groups")
    def _list_gateway_groups(filter: str = None) -> list[dict[str, Any]] | dict[str, Any]:
        return list_gateway_groups(filter=filter)

    @server.tool(name="get_gateway_group")
    def _get_gateway_group(id: str) -> dict[str, Any]:
        return get_gateway_group(id)

    @server.tool(name="list_segments")
    def _list_segments(filter: str = None) -> list[dict[str, Any]] | dict[str, Any]:
        return list_segments(filter=filter)

    @server.tool(name="get_segment")
    def _get_segment(id: str) -> dict[str, Any]:
        return get_segment(id)

    @server.tool(name="list_tenants")
    def _list_tenants(filter: str = None) -> list[dict[str, Any]] | dict[str, Any]:
        return list_tenants(filter=filter)

    @server.tool(name="get_tenant")
    def _get_tenant(id: str) -> dict[str, Any]:
        return get_tenant(id)

    @server.tool(name="list_users")
    def _list_users(filter: str = None) -> list[dict[str, Any]] | dict[str, Any]:
        return list_users(filter=filter)

    @server.tool(name="get_user")
    def _get_user(id: str) -> dict[str, Any]:
        return get_user(id)

    @server.tool(name="list_user_groups")
    def _list_user_groups(filter: str = None) -> list[dict[str, Any]] | dict[str, Any]:
        return list_user_groups(filter=filter)

    @server.tool(name="get_user_group")
    def _get_user_group(id: str) -> dict[str, Any]:
        return get_user_group(id)

    for tool_name in PLACEHOLDER_TOOL_NAMES:

        @server.tool(name=tool_name)
        def _placeholder_tool(tool_name: str = tool_name) -> dict[str, str]:
            return {"status": "not_implemented", "tool": tool_name}

    return server


def main() -> None:
    """Run the MCP server with the SDK's default transport."""
    create_server().run()


if __name__ == "__main__":
    main()
