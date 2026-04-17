"""Focused tests for gateway MCP tool behavior."""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Optional
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.errors import ConfigurationError
from netskope_sdwan_mcp.tools.gateways import (
    get_gateway,
    get_gateway_status,
    get_gateway_telemetry_overview,
    get_gateway_operational_snapshot,
    list_gateways,
    list_gateways_with_status,
    serialize_gateway,
)


@dataclass
class FakeGateway:
    id: str
    name: Optional[str] = None
    managed: Optional[bool] = None
    is_activated: Optional[bool] = None
    overlay_id: Optional[str] = None
    created_at: Optional[str] = None
    modified_at: Optional[str] = None
    device_config_raw: Optional[dict] = None


class NotFoundError(Exception):
    """SDK-shaped not found error used in tests."""


class APIResponseError(Exception):
    """SDK-shaped generic API error used in tests."""


class UnauthorizedError(Exception):
    """SDK-shaped auth error used in tests."""


class GatewayToolsTest(unittest.TestCase):
    def test_list_gateways_success(self) -> None:
        client = Mock()
        client.gateways.list.return_value = [
            FakeGateway(id="gw-001", name="Branch Gateway 1", managed=True),
            FakeGateway(id="gw-002", name="Branch Gateway 2", managed=False),
        ]

        with patch("netskope_sdwan_mcp.tools.gateways.build_sdk_client", return_value=client):
            result = list_gateways(filter="status:up")

        client.gateways.list.assert_called_once_with(filter="status:up")
        self.assertEqual(
            result,
            [
                {
                    "id": "gw-001",
                    "name": "Branch Gateway 1",
                    "managed": True,
                    "is_activated": None,
                    "overlay_id": None,
                    "created_at": None,
                    "modified_at": None,
                    "device_config_raw": None,
                },
                {
                    "id": "gw-002",
                    "name": "Branch Gateway 2",
                    "managed": False,
                    "is_activated": None,
                    "overlay_id": None,
                    "created_at": None,
                    "modified_at": None,
                    "device_config_raw": None,
                },
            ],
        )

    def test_get_gateway_success(self) -> None:
        client = Mock()
        client.gateways.get.return_value = FakeGateway(
            id="gw-001",
            name="Branch Gateway 1",
            managed=True,
            overlay_id="overlay-1",
        )

        with patch("netskope_sdwan_mcp.tools.gateways.build_sdk_client", return_value=client):
            result = get_gateway("gw-001")

        client.gateways.get.assert_called_once_with("gw-001")
        self.assertEqual(result["id"], "gw-001")
        self.assertEqual(result["name"], "Branch Gateway 1")
        self.assertEqual(result["overlay_id"], "overlay-1")

    def test_list_gateways_with_status_success(self) -> None:
        client = Mock()
        client.gateways.list.return_value = [
            {
                "id": "gw-001",
                "name": "Branch Gateway 1",
                "is_activated": True,
                "city": "London",
                "country": "GB",
                "role": "hub",
            },
            {
                "id": "gw-002",
                "name": "Branch Gateway 2",
                "is_activated": False,
            },
        ]
        client.gateways.get_telemetry_overview.side_effect = [
            {
                "status_v2": {
                    "status": "online",
                    "conditions": [{"type": "wan", "status": "healthy"}],
                },
                "software_version": "10.2.1",
                "software_upgraded_at": "2026-04-17T09:30:00Z",
                "links_avg_score": 98.7,
            },
            {
                "status_v2": {
                    "status": "offline",
                    "conditions": [{"type": "reachability", "status": "down"}],
                },
                "software_version": "10.1.0",
                "software_upgraded_at": None,
                "links_avg_score": 12.0,
            },
        ]

        with patch("netskope_sdwan_mcp.tools.gateways.build_sdk_client", return_value=client):
            result = list_gateways_with_status()

        client.gateways.list.assert_called_once_with()
        self.assertEqual(client.gateways.get_telemetry_overview.call_count, 2)
        self.assertEqual(
            result,
            [
                {
                    "gateway_id": "gw-001",
                    "name": "Branch Gateway 1",
                    "is_activated": True,
                    "status": "online",
                    "conditions": [{"type": "wan", "status": "healthy"}],
                    "software_version": "10.2.1",
                    "software_upgraded_at": "2026-04-17T09:30:00Z",
                    "links_avg_score": 98.7,
                    "city": "London",
                    "country": "GB",
                    "role": "hub",
                },
                {
                    "gateway_id": "gw-002",
                    "name": "Branch Gateway 2",
                    "is_activated": False,
                    "status": "offline",
                    "conditions": [{"type": "reachability", "status": "down"}],
                    "software_version": "10.1.0",
                    "software_upgraded_at": None,
                    "links_avg_score": 12.0,
                    "city": None,
                    "country": None,
                    "role": None,
                },
            ],
        )

    def test_list_gateways_with_status_partial_telemetry_failure_keeps_item(self) -> None:
        client = Mock()
        client.gateways.list.return_value = [
            {
                "id": "gw-001",
                "name": "Branch Gateway 1",
                "is_activated": True,
            },
            {
                "id": "gw-002",
                "name": "Branch Gateway 2",
                "is_activated": False,
                "city": "Paris",
            },
        ]
        client.gateways.get_telemetry_overview.side_effect = [
            APIResponseError("upstream failure"),
            {
                "status_v2": {"status": "online", "conditions": []},
                "software_version": "10.2.2",
                "software_upgraded_at": "2026-04-18T09:30:00Z",
                "links_avg_score": 87.5,
            },
        ]

        with patch("netskope_sdwan_mcp.tools.gateways.build_sdk_client", return_value=client):
            result = list_gateways_with_status()

        self.assertEqual(
            result,
            [
                {
                    "gateway_id": "gw-001",
                    "name": "Branch Gateway 1",
                    "is_activated": True,
                    "status": None,
                    "conditions": None,
                    "software_version": None,
                    "software_upgraded_at": None,
                    "links_avg_score": None,
                    "city": None,
                    "country": None,
                    "role": None,
                },
                {
                    "gateway_id": "gw-002",
                    "name": "Branch Gateway 2",
                    "is_activated": False,
                    "status": "online",
                    "conditions": [],
                    "software_version": "10.2.2",
                    "software_upgraded_at": "2026-04-18T09:30:00Z",
                    "links_avg_score": 87.5,
                    "city": "Paris",
                    "country": None,
                    "role": None,
                },
            ],
        )

    def test_get_gateway_telemetry_overview_success(self) -> None:
        client = Mock()
        client.gateways.get_telemetry_overview.return_value = {
            "cpu": {"current": 17.5},
            "memory": {"current": 62.0},
        }

        with patch("netskope_sdwan_mcp.tools.gateways.build_sdk_client", return_value=client):
            result = get_gateway_telemetry_overview("gw-001")

        client.gateways.get_telemetry_overview.assert_called_once_with("gw-001")
        self.assertEqual(
            result,
            {
                "cpu": {"current": 17.5},
                "memory": {"current": 62.0},
            },
        )

    def test_get_gateway_status_success(self) -> None:
        client = Mock()
        client.gateways.get.return_value = FakeGateway(
            id="gw-001",
            name="Branch Gateway 1",
            is_activated=True,
        )
        client.gateways.get_telemetry_overview.return_value = {
            "status_v2": {
                "status": "online",
                "conditions": [{"type": "wan", "status": "healthy"}],
            },
            "software_version": "10.2.1",
            "software_upgraded_at": "2026-04-17T09:30:00Z",
            "links_avg_score": 98.7,
        }

        with patch("netskope_sdwan_mcp.tools.gateways.build_sdk_client", return_value=client):
            result = get_gateway_status("gw-001")

        client.gateways.get.assert_called_once_with("gw-001")
        client.gateways.get_telemetry_overview.assert_called_once_with("gw-001")
        self.assertEqual(
            result,
            {
                "gateway_id": "gw-001",
                "name": "Branch Gateway 1",
                "is_activated": True,
                "status": "online",
                "conditions": [{"type": "wan", "status": "healthy"}],
                "software_version": "10.2.1",
                "software_upgraded_at": "2026-04-17T09:30:00Z",
                "links_avg_score": 98.7,
            },
        )

    def test_get_gateway_status_missing_telemetry_fields_return_null(self) -> None:
        client = Mock()
        client.gateways.get.return_value = FakeGateway(
            id="gw-001",
            name="Branch Gateway 1",
            is_activated=False,
        )
        client.gateways.get_telemetry_overview.return_value = {"cpu": {"current": 17.5}}

        with patch("netskope_sdwan_mcp.tools.gateways.build_sdk_client", return_value=client):
            result = get_gateway_status("gw-001")

        self.assertEqual(
            result,
            {
                "gateway_id": "gw-001",
                "name": "Branch Gateway 1",
                "is_activated": False,
                "status": None,
                "conditions": None,
                "software_version": None,
                "software_upgraded_at": None,
                "links_avg_score": None,
            },
        )

    def test_get_gateway_operational_snapshot_success(self) -> None:
        client = Mock()
        client.gateways.get.return_value = FakeGateway(
            id="gw-001",
            name="Branch Gateway 1",
            managed=True,
            overlay_id="overlay-1",
        )
        client.v1.monitoring.get_interfaces_latest.return_value = [
            {"name": "wan0", "status": "up"}
        ]
        client.v1.monitoring.get_paths_latest.return_value = [
            {"path_id": "path-1", "state": "healthy"}
        ]
        client.v1.monitoring.get_routes_latest.return_value = {
            "routes": [{"prefix": "10.0.0.0/24", "nextHop": "192.0.2.1"}]
        }

        with patch("netskope_sdwan_mcp.tools.gateways.build_sdk_client", return_value=client):
            result = get_gateway_operational_snapshot(
                "gw-001",
                child_tenant_id="tenant-child-1",
            )

        client.gateways.get.assert_called_once_with("gw-001")
        client.v1.monitoring.get_interfaces_latest.assert_called_once_with(
            "gw-001",
            child_tenant_id="tenant-child-1",
        )
        client.v1.monitoring.get_paths_latest.assert_called_once_with(
            "gw-001",
            child_tenant_id="tenant-child-1",
        )
        client.v1.monitoring.get_routes_latest.assert_called_once_with(
            "gw-001",
            child_tenant_id="tenant-child-1",
        )
        self.assertEqual(
            result,
            {
                "gateway": {
                    "id": "gw-001",
                    "name": "Branch Gateway 1",
                    "managed": True,
                    "is_activated": None,
                    "overlay_id": "overlay-1",
                    "created_at": None,
                    "modified_at": None,
                    "device_config_raw": None,
                },
                "interfaces_latest": [{"name": "wan0", "status": "up"}],
                "paths_latest": [{"path_id": "path-1", "state": "healthy"}],
                "routes_latest": {
                    "routes": [{"prefix": "10.0.0.0/24", "nextHop": "192.0.2.1"}]
                },
            },
        )

    def test_get_gateway_not_found_path(self) -> None:
        client = Mock()
        client.gateways.get.side_effect = NotFoundError("gateway not found")

        with patch("netskope_sdwan_mcp.tools.gateways.build_sdk_client", return_value=client):
            result = get_gateway("missing-id")

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["error"]["type"], "NotFoundError")
        self.assertEqual(result["error"]["message"], "gateway not found")

    def test_list_gateways_sdk_error_path(self) -> None:
        client = Mock()
        client.gateways.list.side_effect = APIResponseError("upstream failure")

        with patch("netskope_sdwan_mcp.tools.gateways.build_sdk_client", return_value=client):
            result = list_gateways()

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_list_gateways_with_status_list_error_path(self) -> None:
        client = Mock()
        client.gateways.list.side_effect = APIResponseError("upstream failure")

        with patch("netskope_sdwan_mcp.tools.gateways.build_sdk_client", return_value=client):
            result = list_gateways_with_status()

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_list_gateways_configuration_error_path(self) -> None:
        with patch(
            "netskope_sdwan_mcp.tools.gateways.build_sdk_client",
            side_effect=ConfigurationError("Missing required environment variable: NETSKOPESDWAN_API_TOKEN"),
        ):
            result = list_gateways()

        self.assertEqual(result["status"], "configuration_error")
        self.assertEqual(result["error"]["type"], "ConfigurationError")
        self.assertEqual(
            result["error"]["message"],
            "Missing required environment variable: NETSKOPESDWAN_API_TOKEN",
        )

    def test_get_gateway_authentication_error_path(self) -> None:
        client = Mock()
        client.gateways.get.side_effect = UnauthorizedError(
            "401 unauthorized authorization: Bearer secret-token"
        )

        with patch("netskope_sdwan_mcp.tools.gateways.build_sdk_client", return_value=client):
            result = get_gateway("gw-001")

        self.assertEqual(result["status"], "unauthorized")
        self.assertEqual(result["error"]["type"], "AuthenticationError")
        self.assertEqual(
            result["error"]["message"],
            "Authentication failed for the Netskope SD-WAN API.",
        )

    def test_get_gateway_telemetry_overview_sdk_error_path(self) -> None:
        client = Mock()
        client.gateways.get_telemetry_overview.side_effect = APIResponseError("upstream failure")

        with patch("netskope_sdwan_mcp.tools.gateways.build_sdk_client", return_value=client):
            result = get_gateway_telemetry_overview("gw-001")

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_get_gateway_status_error_path(self) -> None:
        client = Mock()
        client.gateways.get.return_value = FakeGateway(
            id="gw-001",
            name="Branch Gateway 1",
        )
        client.gateways.get_telemetry_overview.side_effect = APIResponseError("upstream failure")

        with patch("netskope_sdwan_mcp.tools.gateways.build_sdk_client", return_value=client):
            result = get_gateway_status("gw-001")

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_get_gateway_operational_snapshot_error_path(self) -> None:
        client = Mock()
        client.gateways.get.return_value = FakeGateway(
            id="gw-001",
            name="Branch Gateway 1",
        )
        client.v1.monitoring.get_interfaces_latest.side_effect = APIResponseError(
            "upstream failure"
        )

        with patch("netskope_sdwan_mcp.tools.gateways.build_sdk_client", return_value=client):
            result = get_gateway_operational_snapshot("gw-001")

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_serialize_gateway_supports_sdk_objects(self) -> None:
        gateway = FakeGateway(
            id="gw-123",
            name="HQ Gateway",
            managed=True,
            is_activated=True,
            overlay_id="overlay-9",
            created_at="2024-01-01T00:00:00Z",
            modified_at="2024-01-02T00:00:00Z",
            device_config_raw={"hostname": "hq-1"},
        )

        self.assertEqual(
            serialize_gateway(gateway),
            {
                "id": "gw-123",
                "name": "HQ Gateway",
                "managed": True,
                "is_activated": True,
                "overlay_id": "overlay-9",
                "created_at": "2024-01-01T00:00:00Z",
                "modified_at": "2024-01-02T00:00:00Z",
                "device_config_raw": {"hostname": "hq-1"},
            },
        )
