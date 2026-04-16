"""Focused tests for v1 monitoring MCP tool behavior."""

from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.tools.monitoring_v1 import (
    get_interfaces_latest,
    get_paths_latest,
    get_paths_links_totals,
    get_routes_latest,
    get_system_load,
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
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

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
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

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
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_get_system_load_success(self) -> None:
        client = Mock()
        client.v1.monitoring.get_system_load.return_value = {
            "series": [{"timestamp": "2026-04-16T10:00:00Z", "cpu": 17.5}]
        }

        with patch(
            "netskope_sdwan_mcp.tools.monitoring_v1.build_sdk_client",
            return_value=client,
        ):
            result = get_system_load("gw-123")

        client.v1.monitoring.get_system_load.assert_called_once_with(
            "gw-123",
            child_tenant_id=None,
            start_datetime=None,
            end_datetime=None,
            time_slots=None,
        )
        self.assertEqual(
            result,
            {"series": [{"timestamp": "2026-04-16T10:00:00Z", "cpu": 17.5}]},
        )

    def test_get_system_load_argument_pass_through(self) -> None:
        client = Mock()
        client.v1.monitoring.get_system_load.return_value = {"series": []}

        with patch(
            "netskope_sdwan_mcp.tools.monitoring_v1.build_sdk_client",
            return_value=client,
        ):
            result = get_system_load(
                "gw-123",
                child_tenant_id="tenant-child-1",
                start_datetime="2026-04-16T00:00:00Z",
                end_datetime="2026-04-16T23:59:59Z",
                time_slots=24,
            )

        client.v1.monitoring.get_system_load.assert_called_once_with(
            "gw-123",
            child_tenant_id="tenant-child-1",
            start_datetime="2026-04-16T00:00:00Z",
            end_datetime="2026-04-16T23:59:59Z",
            time_slots=24,
        )
        self.assertEqual(result, {"series": []})

    def test_get_system_load_sdk_error_path(self) -> None:
        client = Mock()
        client.v1.monitoring.get_system_load.side_effect = APIResponseError(
            "system load unavailable"
        )

        with patch(
            "netskope_sdwan_mcp.tools.monitoring_v1.build_sdk_client",
            return_value=client,
        ):
            result = get_system_load("gw-123")

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_get_paths_links_totals_success(self) -> None:
        client = Mock()
        client.v1.monitoring.get_paths_links_totals.return_value = {
            "totals": {"healthy": 8, "degraded": 1}
        }

        with patch(
            "netskope_sdwan_mcp.tools.monitoring_v1.build_sdk_client",
            return_value=client,
        ):
            result = get_paths_links_totals("gw-123")

        client.v1.monitoring.get_paths_links_totals.assert_called_once_with(
            "gw-123",
            child_tenant_id=None,
            start_datetime=None,
            end_datetime=None,
        )
        self.assertEqual(result, {"totals": {"healthy": 8, "degraded": 1}})

    def test_get_paths_links_totals_argument_pass_through(self) -> None:
        client = Mock()
        client.v1.monitoring.get_paths_links_totals.return_value = {"totals": {}}

        with patch(
            "netskope_sdwan_mcp.tools.monitoring_v1.build_sdk_client",
            return_value=client,
        ):
            result = get_paths_links_totals(
                "gw-123",
                child_tenant_id="tenant-child-1",
                start_datetime="2026-04-16T00:00:00Z",
                end_datetime="2026-04-16T23:59:59Z",
            )

        client.v1.monitoring.get_paths_links_totals.assert_called_once_with(
            "gw-123",
            child_tenant_id="tenant-child-1",
            start_datetime="2026-04-16T00:00:00Z",
            end_datetime="2026-04-16T23:59:59Z",
        )
        self.assertEqual(result, {"totals": {}})

    def test_get_paths_links_totals_sdk_error_path(self) -> None:
        client = Mock()
        client.v1.monitoring.get_paths_links_totals.side_effect = APIResponseError(
            "path totals unavailable"
        )

        with patch(
            "netskope_sdwan_mcp.tools.monitoring_v1.build_sdk_client",
            return_value=client,
        ):
            result = get_paths_links_totals("gw-123")

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")


if __name__ == "__main__":
    unittest.main()
