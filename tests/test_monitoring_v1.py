"""Focused tests for v1 monitoring MCP tool behavior."""

from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.tools.monitoring_v1 import (
    get_interfaces_latest,
    get_paths_latest,
    get_routes_latest,
)


class APIResponseError(Exception):
    """SDK-shaped generic API error used in tests."""


class MonitoringV1ToolsTest(unittest.TestCase):
    def test_get_interfaces_latest_success(self) -> None:
        client = Mock()
        client.v1.monitoring.get_interfaces_latest.return_value = [
            {"name": "wan0", "status": "up"},
            {"name": "lan0", "status": "up"},
        ]

        with patch(
            "netskope_sdwan_mcp.tools.monitoring_v1.build_sdk_client",
            return_value=client,
        ):
            result = get_interfaces_latest("gw-123")

        client.v1.monitoring.get_interfaces_latest.assert_called_once_with(
            "gw-123",
            child_tenant_id=None,
        )
        self.assertEqual(
            result,
            [
                {"name": "wan0", "status": "up"},
                {"name": "lan0", "status": "up"},
            ],
        )

    def test_get_paths_latest_success_with_child_tenant_id(self) -> None:
        client = Mock()
        client.v1.monitoring.get_paths_latest.return_value = [
            {"path_id": "path-1", "state": "healthy"},
        ]

        with patch(
            "netskope_sdwan_mcp.tools.monitoring_v1.build_sdk_client",
            return_value=client,
        ):
            result = get_paths_latest("gw-123", child_tenant_id="tenant-child-1")

        client.v1.monitoring.get_paths_latest.assert_called_once_with(
            "gw-123",
            child_tenant_id="tenant-child-1",
        )
        self.assertEqual(result, [{"path_id": "path-1", "state": "healthy"}])

    def test_get_routes_latest_success(self) -> None:
        client = Mock()
        client.v1.monitoring.get_routes_latest.return_value = {
            "routes": [{"prefix": "10.0.0.0/24", "nextHop": "192.0.2.1"}]
        }

        with patch(
            "netskope_sdwan_mcp.tools.monitoring_v1.build_sdk_client",
            return_value=client,
        ):
            result = get_routes_latest("gw-123")

        client.v1.monitoring.get_routes_latest.assert_called_once_with(
            "gw-123",
            child_tenant_id=None,
        )
        self.assertEqual(
            result,
            {"routes": [{"prefix": "10.0.0.0/24", "nextHop": "192.0.2.1"}]},
        )

    def test_get_interfaces_latest_sdk_error_path(self) -> None:
        client = Mock()
        client.v1.monitoring.get_interfaces_latest.side_effect = APIResponseError(
            "upstream failure"
        )

        with patch(
            "netskope_sdwan_mcp.tools.monitoring_v1.build_sdk_client",
            return_value=client,
        ):
            result = get_interfaces_latest("gw-123")

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "APIResponseError")
        self.assertEqual(result["error"]["message"], "upstream failure")

    def test_get_paths_latest_sdk_error_path(self) -> None:
        client = Mock()
        client.v1.monitoring.get_paths_latest.side_effect = APIResponseError(
            "paths unavailable"
        )

        with patch(
            "netskope_sdwan_mcp.tools.monitoring_v1.build_sdk_client",
            return_value=client,
        ):
            result = get_paths_latest("gw-123")

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "APIResponseError")
        self.assertEqual(result["error"]["message"], "paths unavailable")

    def test_get_routes_latest_sdk_error_path(self) -> None:
        client = Mock()
        client.v1.monitoring.get_routes_latest.side_effect = APIResponseError(
            "routes unavailable"
        )

        with patch(
            "netskope_sdwan_mcp.tools.monitoring_v1.build_sdk_client",
            return_value=client,
        ):
            result = get_routes_latest("gw-123")

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "APIResponseError")
        self.assertEqual(result["error"]["message"], "routes unavailable")


if __name__ == "__main__":
    unittest.main()
