"""Minimal MCP server entrypoint for Netskope SD-WAN."""

from __future__ import annotations

from typing import Any

from .tools.address_groups import get_address_group, list_address_groups
from .tools.applications import get_application, list_applications
from .tools.audit_events import list_audit_events
from .tools.client_templates import get_client_template, list_client_templates
from .tools.device_groups import get_device_group, list_device_groups
from .tools.gateways import (
    get_gateway,
    get_gateway_operational_snapshot,
    list_gateways,
)
from .tools.gateway_groups import get_gateway_group, list_gateway_groups
from .tools.monitoring_v1 import (
    get_interfaces_latest,
    get_paths_latest,
    get_paths_links_totals,
    get_routes_latest,
    get_system_load,
)
from .tools.segments import get_segment, list_segments
from .tools.tenants import get_tenant, list_tenants
from .tools.user_groups import get_user_group, list_user_groups
from .tools.users import get_user, list_users

SERVER_NAME = "netskope-sdwan-mcp"
PLACEHOLDER_TOOL_NAMES = ("list_sites", "list_alerts")


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

    @server.tool(name="list_address_groups")
    def _list_address_groups(filter: str = None) -> list[dict[str, Any]] | dict[str, Any]:
        return list_address_groups(filter=filter)

    @server.tool(name="get_address_group")
    def _get_address_group(id: str) -> dict[str, Any]:
        return get_address_group(id)

    @server.tool(name="list_device_groups")
    def _list_device_groups(filter: str = None) -> list[dict[str, Any]] | dict[str, Any]:
        return list_device_groups(filter=filter)

    @server.tool(name="get_device_group")
    def _get_device_group(id: str) -> dict[str, Any]:
        return get_device_group(id)

    @server.tool(name="list_client_templates")
    def _list_client_templates(filter: str = None) -> list[dict[str, Any]] | dict[str, Any]:
        return list_client_templates(filter=filter)

    @server.tool(name="get_client_template")
    def _get_client_template(id: str) -> dict[str, Any]:
        return get_client_template(id)

    @server.tool(name="get_gateway")
    def _get_gateway(id: str) -> dict[str, Any]:
        return get_gateway(id)

    @server.tool(name="get_gateway_operational_snapshot")
    def _get_gateway_operational_snapshot(
        id: str,
        child_tenant_id: str = None,
    ) -> dict[str, Any]:
        return get_gateway_operational_snapshot(
            id,
            child_tenant_id=child_tenant_id,
        )

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

    @server.tool(name="list_applications")
    def _list_applications(filter: str = None) -> list[dict[str, Any]] | dict[str, Any]:
        return list_applications(filter=filter)

    @server.tool(name="get_application")
    def _get_application(id: str) -> dict[str, Any]:
        return get_application(id)

    @server.tool(name="list_audit_events")
    def _list_audit_events(
        created_at_from: str,
        created_at_to: str,
        type: str = None,
        subtype: str = None,
        activity: str = None,
        after: str = None,
        first: int = None,
        sort: str = None,
        filter: str = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        return list_audit_events(
            created_at_from=created_at_from,
            created_at_to=created_at_to,
            type=type,
            subtype=subtype,
            activity=activity,
            after=after,
            first=first,
            sort=sort,
            filter=filter,
        )

    @server.tool(name="get_interfaces_latest")
    def _get_interfaces_latest(
        gateway_id: str,
        child_tenant_id: str = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        return get_interfaces_latest(
            gateway_id,
            child_tenant_id=child_tenant_id,
        )

    @server.tool(name="get_paths_latest")
    def _get_paths_latest(
        gateway_id: str,
        child_tenant_id: str = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        return get_paths_latest(
            gateway_id,
            child_tenant_id=child_tenant_id,
        )

    @server.tool(name="get_routes_latest")
    def _get_routes_latest(
        gateway_id: str,
        child_tenant_id: str = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        return get_routes_latest(
            gateway_id,
            child_tenant_id=child_tenant_id,
        )

    @server.tool(name="get_system_load")
    def _get_system_load(
        gateway_id: str,
        child_tenant_id: str = None,
        start_datetime: str = None,
        end_datetime: str = None,
        time_slots: int = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        return get_system_load(
            gateway_id,
            child_tenant_id=child_tenant_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            time_slots=time_slots,
        )

    @server.tool(name="get_paths_links_totals")
    def _get_paths_links_totals(
        gateway_id: str,
        child_tenant_id: str = None,
        start_datetime: str = None,
        end_datetime: str = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        return get_paths_links_totals(
            gateway_id,
            child_tenant_id=child_tenant_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        )

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
