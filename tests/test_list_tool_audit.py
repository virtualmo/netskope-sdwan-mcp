"""Audit coverage for MCP list-tool pagination passthrough and registration."""

from __future__ import annotations

from importlib import import_module
import inspect
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


COMMON_LIST_KWARGS = {
    "filter": "name: Example",
    "after": "cursor-001",
    "first": 25,
    "sort": "name",
}


LIST_TOOL_CASES = (
    ("netskope_sdwan_mcp.tools.address_groups", "list_address_groups", "address_groups", "list", ()),
    (
        "netskope_sdwan_mcp.tools.address_groups",
        "list_address_group_objects",
        "address_groups",
        "list_address_objects",
        ("ag-001",),
    ),
    ("netskope_sdwan_mcp.tools.applications", "list_applications", "applications", "list_custom_apps", ()),
    (
        "netskope_sdwan_mcp.tools.applications",
        "list_application_categories",
        "applications",
        "list_categories",
        (),
    ),
    ("netskope_sdwan_mcp.tools.applications", "list_qosmos_apps", "applications", "list_qosmos_apps", ()),
    (
        "netskope_sdwan_mcp.tools.applications",
        "list_webroot_categories",
        "applications",
        "list_webroot_categories",
        (),
    ),
    ("netskope_sdwan_mcp.tools.ca_certificates", "list_ca_certificates", "ca_certificates", "list", ()),
    ("netskope_sdwan_mcp.tools.client_templates", "list_client_templates", "client_templates", "list", ()),
    ("netskope_sdwan_mcp.tools.clients", "list_clients", "clients", "list", ()),
    ("netskope_sdwan_mcp.tools.cloud_accounts", "list_cloud_accounts", "cloud_accounts", "list", ()),
    (
        "netskope_sdwan_mcp.tools.controller_operators",
        "list_controller_operators",
        "controller_operators",
        "list",
        (),
    ),
    ("netskope_sdwan_mcp.tools.controllers", "list_controllers", "controllers", "list", ()),
    ("netskope_sdwan_mcp.tools.device_groups", "list_device_groups", "device_groups", "list", ()),
    ("netskope_sdwan_mcp.tools.gateway_groups", "list_gateway_groups", "gateway_groups", "list", ()),
    (
        "netskope_sdwan_mcp.tools.gateway_templates",
        "list_gateway_templates",
        "gateway_templates",
        "list",
        (),
    ),
    ("netskope_sdwan_mcp.tools.gateways", "list_gateways", "gateways", "list", ()),
    (
        "netskope_sdwan_mcp.tools.inventory_devices",
        "list_inventory_devices",
        "inventory_devices",
        "list",
        (),
    ),
    ("netskope_sdwan_mcp.tools.ntp_configs", "list_ntp_configs", "ntp_configs", "list", ()),
    ("netskope_sdwan_mcp.tools.overlay_tags", "list_overlay_tags", "overlay_tags", "list", ()),
    ("netskope_sdwan_mcp.tools.policies", "list_policies", "policies", "list", ()),
    ("netskope_sdwan_mcp.tools.radius_servers", "list_radius_servers", "radius_servers", "list", ()),
    ("netskope_sdwan_mcp.tools.segments", "list_segments", "segments", "list", ()),
    ("netskope_sdwan_mcp.tools.site_commands", "list_site_commands", "site_commands", "list", ()),
    ("netskope_sdwan_mcp.tools.software", "list_software_versions", "software", "list_versions", ()),
    ("netskope_sdwan_mcp.tools.software", "list_software_downloads", "software", "list_downloads", ()),
    ("netskope_sdwan_mcp.tools.tenants", "list_tenants", "tenants", "list", ()),
    ("netskope_sdwan_mcp.tools.user_groups", "list_user_groups", "user_groups", "list", ()),
    ("netskope_sdwan_mcp.tools.users", "list_users", "users", "list", ()),
    ("netskope_sdwan_mcp.tools.vpn_peers", "list_vpn_peers", "vpn_peers", "list", ()),
)


SERVER_SIGNATURES = {
    "list_address_groups": ("filter", "after", "first", "sort"),
    "list_address_group_objects": ("group_id", "filter", "after", "first", "sort"),
    "list_applications": ("filter", "after", "first", "sort"),
    "list_application_categories": ("filter", "after", "first", "sort"),
    "list_qosmos_apps": ("filter", "after", "first", "sort"),
    "list_webroot_categories": ("filter", "after", "first", "sort"),
    "list_ca_certificates": ("filter", "after", "first", "sort"),
    "list_client_templates": ("filter", "after", "first", "sort"),
    "list_clients": ("filter", "after", "first", "sort"),
    "list_cloud_accounts": ("filter", "after", "first", "sort"),
    "list_controller_operators": ("filter", "after", "first", "sort"),
    "list_controllers": ("filter", "after", "first", "sort"),
    "list_device_groups": ("filter", "after", "first", "sort"),
    "list_gateway_groups": ("filter", "after", "first", "sort"),
    "list_gateway_templates": ("filter", "after", "first", "sort"),
    "list_gateways": ("filter", "after", "first", "sort"),
    "list_inventory_devices": ("filter", "after", "first", "sort"),
    "list_ntp_configs": ("filter", "after", "first", "sort"),
    "list_overlay_tags": ("filter", "after", "first", "sort"),
    "list_policies": ("filter", "after", "first", "sort"),
    "list_radius_servers": ("filter", "after", "first", "sort"),
    "list_segments": ("filter", "after", "first", "sort"),
    "list_site_commands": ("filter", "after", "first", "sort"),
    "list_software_versions": ("filter", "after", "first", "sort"),
    "list_software_downloads": ("filter", "after", "first", "sort"),
    "list_tenants": ("filter", "after", "first", "sort"),
    "list_users": ("filter", "after", "first", "sort"),
    "list_user_groups": ("filter", "after", "first", "sort"),
    "list_vpn_peers": ("filter", "after", "first", "sort"),
    "list_audit_events": (
        "created_at_from",
        "created_at_to",
        "type",
        "subtype",
        "activity",
        "after",
        "first",
        "sort",
        "filter",
    ),
}


class FakeFastMCP:
    def __init__(
        self,
        name: str,
        json_response: bool = False,
        host: str = "127.0.0.1",
        port: int = 8000,
    ) -> None:
        self.name = name
        self.json_response = json_response
        self.host = host
        self.port = port
        self.registered_tools: dict[str, object] = {}

    def tool(self, name=None, description=None):
        _ = description

        def decorator(fn):
            self.registered_tools[name or fn.__name__] = fn
            return fn

        return decorator


class ListToolAuditTest(unittest.TestCase):
    def test_list_tools_forward_supported_pagination_arguments(self) -> None:
        for module_name, function_name, manager_name, method_name, args in LIST_TOOL_CASES:
            with self.subTest(function=function_name):
                module = import_module(module_name)
                tool_fn = getattr(module, function_name)
                client = Mock()
                manager = getattr(client, manager_name)
                getattr(manager, method_name).return_value = [{"id": function_name}]

                with patch(f"{module_name}.build_sdk_client", return_value=client):
                    result = tool_fn(*args, **COMMON_LIST_KWARGS)

                self.assertEqual(len(result), 1)
                self.assertEqual(result[0]["id"], function_name)
                getattr(manager, method_name).assert_called_once_with(*args, **COMMON_LIST_KWARGS)

    def test_audit_events_forward_required_and_optional_arguments(self) -> None:
        from netskope_sdwan_mcp.tools.audit_events import list_audit_events

        client = Mock()
        client.audit_events.list.return_value = [{"id": "evt-001"}]

        with patch(
            "netskope_sdwan_mcp.tools.audit_events.build_sdk_client",
            return_value=client,
        ):
            result = list_audit_events(
                created_at_from="2026-04-16T00:00:00Z",
                created_at_to="2026-04-16T23:59:59Z",
                type="auth",
                subtype="sso",
                activity="login",
                **COMMON_LIST_KWARGS,
            )

        self.assertEqual(result, [{"id": "evt-001"}])
        client.audit_events.list.assert_called_once_with(
            created_at_from="2026-04-16T00:00:00Z",
            created_at_to="2026-04-16T23:59:59Z",
            type="auth",
            subtype="sso",
            activity="login",
            **COMMON_LIST_KWARGS,
        )

    def test_server_registration_exposes_expected_list_parameters(self) -> None:
        fake_fastmcp_module = types.SimpleNamespace(FastMCP=FakeFastMCP)
        fake_mcp_module = types.ModuleType("mcp")
        fake_server_module = types.ModuleType("mcp.server")

        with patch.dict(
            sys.modules,
            {
                "mcp": fake_mcp_module,
                "mcp.server": fake_server_module,
                "mcp.server.fastmcp": fake_fastmcp_module,
            },
        ):
            sys.modules.pop("netskope_sdwan_mcp.server", None)
            server_module = import_module("netskope_sdwan_mcp.server")
            server = server_module.create_server()

        for tool_name, expected_params in SERVER_SIGNATURES.items():
            with self.subTest(tool=tool_name):
                self.assertIn(tool_name, server.registered_tools)
                signature = inspect.signature(server.registered_tools[tool_name])
                self.assertEqual(tuple(signature.parameters), expected_params)


if __name__ == "__main__":
    unittest.main()
