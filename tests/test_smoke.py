"""Smoke tests for package imports and MCP server registration."""

from importlib import import_module
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class FakeFastMCP:
    def __init__(self, name: str, json_response: bool = False) -> None:
        self.name = name
        self.json_response = json_response
        self.registered_tools: dict[str, object] = {}

    def tool(self, name=None, description=None):
        _ = description

        def decorator(fn):
            tool_name = name or fn.__name__
            self.registered_tools[tool_name] = fn
            return fn

        return decorator

    def run(self) -> None:
        return None


class SmokeTest(unittest.TestCase):
    def test_package_imports(self) -> None:
        package = import_module("netskope_sdwan_mcp")
        self.assertEqual(package.__version__, "0.1.0")

    def test_create_server_registers_placeholder_tools(self) -> None:
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

        self.assertEqual(server.name, "netskope-sdwan-mcp")
        self.assertTrue(server.json_response)
        self.assertEqual(
            tuple(server.registered_tools.keys()),
            (
                "list_gateways",
                "list_address_groups",
                "get_address_group",
                "list_device_groups",
                "get_device_group",
                "list_client_templates",
                "get_client_template",
                "get_gateway",
                "get_gateway_operational_snapshot",
                "list_gateway_groups",
                "get_gateway_group",
                "list_segments",
                "get_segment",
                "list_applications",
                "get_application",
                "list_audit_events",
                "get_interfaces_latest",
                "get_paths_latest",
                "get_routes_latest",
                "get_system_load",
                "get_paths_links_totals",
                "list_tenants",
                "get_tenant",
                "list_users",
                "get_user",
                "list_user_groups",
                "get_user_group",
                "list_sites",
                "list_alerts",
            ),
        )
        self.assertTrue(callable(server.registered_tools["list_address_groups"]))
        self.assertTrue(callable(server.registered_tools["get_address_group"]))
        self.assertTrue(callable(server.registered_tools["list_device_groups"]))
        self.assertTrue(callable(server.registered_tools["get_device_group"]))
        self.assertTrue(callable(server.registered_tools["list_client_templates"]))
        self.assertTrue(callable(server.registered_tools["get_client_template"]))
        self.assertTrue(callable(server.registered_tools["list_gateways"]))
        self.assertTrue(callable(server.registered_tools["get_gateway"]))
        self.assertTrue(callable(server.registered_tools["get_gateway_operational_snapshot"]))
        self.assertTrue(callable(server.registered_tools["list_gateway_groups"]))
        self.assertTrue(callable(server.registered_tools["get_gateway_group"]))
        self.assertTrue(callable(server.registered_tools["list_segments"]))
        self.assertTrue(callable(server.registered_tools["get_segment"]))
        self.assertTrue(callable(server.registered_tools["list_applications"]))
        self.assertTrue(callable(server.registered_tools["get_application"]))
        self.assertTrue(callable(server.registered_tools["list_audit_events"]))
        self.assertTrue(callable(server.registered_tools["get_interfaces_latest"]))
        self.assertTrue(callable(server.registered_tools["get_paths_latest"]))
        self.assertTrue(callable(server.registered_tools["get_routes_latest"]))
        self.assertTrue(callable(server.registered_tools["get_system_load"]))
        self.assertTrue(callable(server.registered_tools["get_paths_links_totals"]))
        self.assertTrue(callable(server.registered_tools["list_tenants"]))
        self.assertTrue(callable(server.registered_tools["get_tenant"]))
        self.assertTrue(callable(server.registered_tools["list_users"]))
        self.assertTrue(callable(server.registered_tools["get_user"]))
        self.assertTrue(callable(server.registered_tools["list_user_groups"]))
        self.assertTrue(callable(server.registered_tools["get_user_group"]))


if __name__ == "__main__":
    unittest.main()
