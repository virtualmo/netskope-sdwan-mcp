"""Minimal MCP server entrypoint for Netskope SD-WAN."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from .tools.address_groups import (
    get_address_group,
    list_address_group_objects,
    list_address_groups,
)
from .tools.applications import (
    get_application,
    list_application_categories,
    list_applications,
    list_qosmos_apps,
    list_webroot_categories,
)
from .tools.audit_events import list_audit_events
from .tools.ca_certificates import get_ca_certificate, list_ca_certificates
from .tools.clients import get_client, list_clients
from .tools.client_templates import get_client_template, list_client_templates
from .tools.cloud_accounts import get_cloud_account, list_cloud_accounts
from .tools.controller_operators import (
    get_controller_operator,
    list_controller_operators,
)
from .tools.controllers import (
    get_controller,
    get_controller_operator_status,
    list_controllers,
)
from .tools.device_groups import get_device_group, list_device_groups
from .tools.edges_v1 import (
    get_edge,
    get_edge_interface,
    get_gateway_interface,
    list_edge_interfaces,
    list_edges,
    list_gateway_interfaces,
)
from .tools.gateways import (
    get_gateway,
    get_gateway_status,
    get_gateway_telemetry_overview,
    get_gateway_operational_snapshot,
    list_gateways,
    list_gateways_with_status,
)
from .tools.gateway_groups import get_gateway_group, list_gateway_groups
from .tools.gateway_templates import get_gateway_template, list_gateway_templates
from .tools.inventory_devices import list_inventory_devices
from .tools.jwks import get_jwks
from .tools.monitoring_v1 import (
    get_device_flows_totals,
    get_devices_totals,
    get_interfaces_latest,
    get_paths_latest,
    get_paths_links,
    get_paths_links_totals,
    get_routes_latest,
    get_system_lte,
    get_system_load,
    get_system_memory,
    get_system_uptime,
    get_system_wifi,
)
from .tools.ntp_configs import get_ntp_config, list_ntp_configs
from .tools.overlay_tags import get_overlay_tag, list_overlay_tags
from .tools.policies import get_policy, list_policies
from .tools.radius_servers import get_radius_server, list_radius_servers
from .tools.segments import get_segment, list_segments
from .tools.site_commands import (
    get_site_command,
    get_site_command_output,
    list_site_commands,
)
from .tools.software import list_software_downloads, list_software_versions
from .tools.tenants import get_tenant, list_tenants
from .tools.user_groups import get_user_group, list_user_groups
from .tools.users import get_user, list_users
from .tools.users_v1 import get_v1_user_groups
from .tools.vpn_peers import get_vpn_peer, list_vpn_peers

SERVER_NAME = "netskope-sdwan-mcp"
PLACEHOLDER_TOOL_NAMES = ("list_sites", "list_alerts")
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000


@dataclass(frozen=True)
class RuntimeConfig:
    """Transport settings for local or remote MCP startup."""

    transport: str = "stdio"
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT


def load_runtime_config(environ: dict[str, str] | None = None) -> RuntimeConfig:
    """Load env-driven runtime settings for stdio or remote HTTP startup."""
    env = environ if environ is not None else os.environ
    raw_transport = env.get("MCP_TRANSPORT", "stdio").strip().lower()

    if raw_transport == "stdio":
        transport = "stdio"
    elif raw_transport in {"http", "streamable-http"}:
        transport = "streamable-http"
    else:
        raise ValueError(
            "Unsupported MCP_TRANSPORT value. Expected one of: stdio, http."
        )

    host = env.get("MCP_HOST", DEFAULT_HOST).strip() or DEFAULT_HOST
    raw_port = env.get("MCP_PORT", str(DEFAULT_PORT)).strip()

    try:
        port = int(raw_port)
    except ValueError as exc:
        raise ValueError("MCP_PORT must be an integer.") from exc

    if not 1 <= port <= 65535:
        raise ValueError("MCP_PORT must be between 1 and 65535.")

    return RuntimeConfig(transport=transport, host=host, port=port)


def create_server(config: RuntimeConfig | None = None) -> Any:
    """Create the MCP server and register placeholder read-only tools."""
    try:
        from mcp.server.fastmcp import FastMCP
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "The MCP Python SDK is required. Install project dependencies to run the server."
        ) from exc

    runtime_config = config or load_runtime_config()
    server = FastMCP(
        SERVER_NAME,
        host=runtime_config.host,
        port=runtime_config.port,
        json_response=True,
    )
    register_tools(server)
    return server


def register_tools(server: Any) -> Any:
    """Register real and placeholder read-only tool handlers on an MCP server."""

    @server.tool(name="list_gateways")
    def _list_gateways(filter: str = None) -> list[dict[str, Any]] | dict[str, Any]:
        return list_gateways(filter=filter)

    @server.tool(name="list_gateways_with_status")
    def _list_gateways_with_status() -> list[dict[str, Any]] | dict[str, Any]:
        return list_gateways_with_status()

    @server.tool(name="list_address_groups")
    def _list_address_groups(filter: str = None) -> list[dict[str, Any]] | dict[str, Any]:
        return list_address_groups(filter=filter)

    @server.tool(name="get_address_group")
    def _get_address_group(id: str) -> dict[str, Any]:
        return get_address_group(id)

    @server.tool(name="list_address_group_objects")
    def _list_address_group_objects(
        group_id: str,
        filter: str = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        return list_address_group_objects(group_id, filter=filter)

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

    @server.tool(name="list_cloud_accounts")
    def _list_cloud_accounts(filter: str = None) -> list[dict[str, Any]] | dict[str, Any]:
        return list_cloud_accounts(filter=filter)

    @server.tool(name="get_cloud_account")
    def _get_cloud_account(id: str) -> dict[str, Any]:
        return get_cloud_account(id)

    @server.tool(name="list_ca_certificates")
    def _list_ca_certificates(filter: str = None) -> list[dict[str, Any]] | dict[str, Any]:
        return list_ca_certificates(filter=filter)

    @server.tool(name="get_ca_certificate")
    def _get_ca_certificate(id: str) -> dict[str, Any]:
        return get_ca_certificate(id)

    @server.tool(name="list_clients")
    def _list_clients(filter: str = None) -> list[dict[str, Any]] | dict[str, Any]:
        return list_clients(filter=filter)

    @server.tool(name="get_client")
    def _get_client(id: str) -> dict[str, Any]:
        return get_client(id)

    @server.tool(name="list_controller_operators")
    def _list_controller_operators(filter: str = None) -> list[dict[str, Any]] | dict[str, Any]:
        return list_controller_operators(filter=filter)

    @server.tool(name="get_controller_operator")
    def _get_controller_operator(id: str) -> dict[str, Any]:
        return get_controller_operator(id)

    @server.tool(name="list_controllers")
    def _list_controllers(filter: str = None) -> list[dict[str, Any]] | dict[str, Any]:
        return list_controllers(filter=filter)

    @server.tool(name="get_controller")
    def _get_controller(id: str) -> dict[str, Any]:
        return get_controller(id)

    @server.tool(name="get_controller_operator_status")
    def _get_controller_operator_status(controller_id: str) -> dict[str, Any]:
        return get_controller_operator_status(controller_id)

    @server.tool(name="list_gateway_templates")
    def _list_gateway_templates(filter: str = None) -> list[dict[str, Any]] | dict[str, Any]:
        return list_gateway_templates(filter=filter)

    @server.tool(name="get_gateway_template")
    def _get_gateway_template(id: str) -> dict[str, Any]:
        return get_gateway_template(id)

    @server.tool(name="list_inventory_devices")
    def _list_inventory_devices(filter: str = None) -> list[dict[str, Any]] | dict[str, Any]:
        return list_inventory_devices(filter=filter)

    @server.tool(name="get_jwks")
    def _get_jwks() -> dict[str, Any]:
        return get_jwks()

    @server.tool(name="list_software_versions")
    def _list_software_versions(filter: str = None) -> list[dict[str, Any]] | dict[str, Any]:
        return list_software_versions(filter=filter)

    @server.tool(name="list_software_downloads")
    def _list_software_downloads(filter: str = None) -> list[dict[str, Any]] | dict[str, Any]:
        return list_software_downloads(filter=filter)

    @server.tool(name="list_ntp_configs")
    def _list_ntp_configs(filter: str = None) -> list[dict[str, Any]] | dict[str, Any]:
        return list_ntp_configs(filter=filter)

    @server.tool(name="get_ntp_config")
    def _get_ntp_config(id: str) -> dict[str, Any]:
        return get_ntp_config(id)

    @server.tool(name="list_overlay_tags")
    def _list_overlay_tags(filter: str = None) -> list[dict[str, Any]] | dict[str, Any]:
        return list_overlay_tags(filter=filter)

    @server.tool(name="get_overlay_tag")
    def _get_overlay_tag(id: str) -> dict[str, Any]:
        return get_overlay_tag(id)

    @server.tool(name="list_policies")
    def _list_policies(filter: str = None) -> list[dict[str, Any]] | dict[str, Any]:
        return list_policies(filter=filter)

    @server.tool(name="get_policy")
    def _get_policy(id: str) -> dict[str, Any]:
        return get_policy(id)

    @server.tool(name="list_radius_servers")
    def _list_radius_servers(filter: str = None) -> list[dict[str, Any]] | dict[str, Any]:
        return list_radius_servers(filter=filter)

    @server.tool(name="get_radius_server")
    def _get_radius_server(id: str) -> dict[str, Any]:
        return get_radius_server(id)

    @server.tool(name="list_vpn_peers")
    def _list_vpn_peers(filter: str = None) -> list[dict[str, Any]] | dict[str, Any]:
        return list_vpn_peers(filter=filter)

    @server.tool(name="get_vpn_peer")
    def _get_vpn_peer(id: str) -> dict[str, Any]:
        return get_vpn_peer(id)

    @server.tool(name="get_gateway")
    def _get_gateway(id: str) -> dict[str, Any]:
        return get_gateway(id)

    @server.tool(name="get_gateway_telemetry_overview")
    def _get_gateway_telemetry_overview(gateway_id: str) -> dict[str, Any]:
        return get_gateway_telemetry_overview(gateway_id)

    @server.tool(name="get_gateway_status")
    def _get_gateway_status(gateway_id: str) -> dict[str, Any]:
        return get_gateway_status(gateway_id)

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

    @server.tool(name="list_site_commands")
    def _list_site_commands(filter: str = None) -> list[dict[str, Any]] | dict[str, Any]:
        return list_site_commands(filter=filter)

    @server.tool(name="get_site_command")
    def _get_site_command(command_id: str) -> dict[str, Any]:
        return get_site_command(command_id)

    @server.tool(name="get_site_command_output")
    def _get_site_command_output(command_id: str, name: str) -> dict[str, Any]:
        return get_site_command_output(command_id, name)

    @server.tool(name="list_applications")
    def _list_applications(filter: str = None) -> list[dict[str, Any]] | dict[str, Any]:
        return list_applications(filter=filter)

    @server.tool(name="list_application_categories")
    def _list_application_categories() -> list[dict[str, Any]] | dict[str, Any]:
        return list_application_categories()

    @server.tool(name="list_qosmos_apps")
    def _list_qosmos_apps(filter: str = None) -> list[dict[str, Any]] | dict[str, Any]:
        return list_qosmos_apps(filter=filter)

    @server.tool(name="list_webroot_categories")
    def _list_webroot_categories() -> list[dict[str, Any]] | dict[str, Any]:
        return list_webroot_categories()

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

    @server.tool(name="list_edges")
    def _list_edges() -> list[dict[str, Any]] | dict[str, Any]:
        return list_edges()

    @server.tool(name="get_edge")
    def _get_edge(edge_id: str) -> dict[str, Any]:
        return get_edge(edge_id)

    @server.tool(name="list_edge_interfaces")
    def _list_edge_interfaces(edge_id: str) -> list[dict[str, Any]] | dict[str, Any]:
        return list_edge_interfaces(edge_id)

    @server.tool(name="get_edge_interface")
    def _get_edge_interface(edge_id: str, interface_id: str) -> dict[str, Any]:
        return get_edge_interface(edge_id, interface_id)

    @server.tool(name="list_gateway_interfaces")
    def _list_gateway_interfaces(gateway_id: str) -> list[dict[str, Any]] | dict[str, Any]:
        return list_gateway_interfaces(gateway_id)

    @server.tool(name="get_gateway_interface")
    def _get_gateway_interface(gateway_id: str, interface_id: str) -> dict[str, Any]:
        return get_gateway_interface(gateway_id, interface_id)

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

    @server.tool(name="get_device_flows_totals")
    def _get_device_flows_totals(
        gateway_id: str,
        ip: str,
        start_datetime: str,
        end_datetime: str,
        child_tenant_id: str = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        return get_device_flows_totals(
            gateway_id,
            ip=ip,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            child_tenant_id=child_tenant_id,
        )

    @server.tool(name="get_devices_totals")
    def _get_devices_totals(
        gateway_id: str,
        start_datetime: str,
        end_datetime: str,
        child_tenant_id: str = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        return get_devices_totals(
            gateway_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
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

    @server.tool(name="get_system_lte")
    def _get_system_lte(
        gateway_id: str,
        start_datetime: str,
        end_datetime: str,
        child_tenant_id: str = None,
        time_slots: int = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        return get_system_lte(
            gateway_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            child_tenant_id=child_tenant_id,
            time_slots=time_slots,
        )

    @server.tool(name="get_system_memory")
    def _get_system_memory(
        gateway_id: str,
        start_datetime: str,
        end_datetime: str,
        child_tenant_id: str = None,
        time_slots: int = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        return get_system_memory(
            gateway_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            child_tenant_id=child_tenant_id,
            time_slots=time_slots,
        )

    @server.tool(name="get_system_uptime")
    def _get_system_uptime(
        gateway_id: str,
        start_datetime: str,
        end_datetime: str,
        child_tenant_id: str = None,
        time_slots: int = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        return get_system_uptime(
            gateway_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            child_tenant_id=child_tenant_id,
            time_slots=time_slots,
        )

    @server.tool(name="get_system_wifi")
    def _get_system_wifi(
        gateway_id: str,
        start_datetime: str,
        end_datetime: str,
        child_tenant_id: str = None,
        time_slots: int = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        return get_system_wifi(
            gateway_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            child_tenant_id=child_tenant_id,
            time_slots=time_slots,
        )

    @server.tool(name="get_paths_links")
    def _get_paths_links(
        gateway_id: str,
        child_tenant_id: str = None,
        start_datetime: str = None,
        end_datetime: str = None,
        metric: str = None,
        time_slots: int = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        return get_paths_links(
            gateway_id,
            child_tenant_id=child_tenant_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            metric=metric,
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

    @server.tool(name="get_v1_user_groups")
    def _get_v1_user_groups(user_id: str) -> list[dict[str, Any]] | dict[str, Any]:
        return get_v1_user_groups(user_id)

    for tool_name in PLACEHOLDER_TOOL_NAMES:

        @server.tool(name=tool_name)
        def _placeholder_tool(tool_name: str = tool_name) -> dict[str, str]:
            return {"status": "not_implemented", "tool": tool_name}

    return server


def main() -> None:
    """Run the MCP server in local stdio mode or optional remote HTTP mode."""
    config = load_runtime_config()
    create_server(config).run(transport=config.transport)


if __name__ == "__main__":
    main()
