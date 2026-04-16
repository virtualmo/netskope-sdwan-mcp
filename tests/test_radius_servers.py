"""Focused tests for radius-server MCP tool behavior."""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Optional
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.tools.radius_servers import (
    get_radius_server,
    list_radius_servers,
    serialize_radius_server,
)


@dataclass
class FakeRadiusServer:
    id: str
    name: Optional[str] = None
    raw: Optional[dict] = None


class NotFoundError(Exception):
    """SDK-shaped not found error used in tests."""


class APIResponseError(Exception):
    """SDK-shaped generic API error used in tests."""


class RadiusServerToolsTest(unittest.TestCase):
    def test_list_radius_servers_success(self) -> None:
        client = Mock()
        client.radius_servers.list.return_value = [
            FakeRadiusServer(
                id="radius-001",
                name="Primary RADIUS",
                raw={"id": "radius-001", "name": "Primary RADIUS", "host": "10.0.0.5"},
            ),
            FakeRadiusServer(
                id="radius-002",
                name="Backup RADIUS",
                raw={"id": "radius-002", "name": "Backup RADIUS"},
            ),
        ]

        with patch(
            "netskope_sdwan_mcp.tools.radius_servers.build_sdk_client",
            return_value=client,
        ):
            result = list_radius_servers(filter="name: Primary")

        client.radius_servers.list.assert_called_once_with(filter="name: Primary")
        self.assertEqual(
            result,
            [
                {"id": "radius-001", "name": "Primary RADIUS", "host": "10.0.0.5"},
                {"id": "radius-002", "name": "Backup RADIUS"},
            ],
        )

    def test_get_radius_server_success(self) -> None:
        client = Mock()
        client.radius_servers.get.return_value = FakeRadiusServer(
            id="radius-001",
            name="Primary RADIUS",
            raw={"id": "radius-001", "name": "Primary RADIUS", "port": 1812},
        )

        with patch(
            "netskope_sdwan_mcp.tools.radius_servers.build_sdk_client",
            return_value=client,
        ):
            result = get_radius_server("radius-001")

        client.radius_servers.get.assert_called_once_with("radius-001")
        self.assertEqual(result["id"], "radius-001")
        self.assertEqual(result["name"], "Primary RADIUS")
        self.assertEqual(result["port"], 1812)

    def test_get_radius_server_not_found_path(self) -> None:
        client = Mock()
        client.radius_servers.get.side_effect = NotFoundError("radius server not found")

        with patch(
            "netskope_sdwan_mcp.tools.radius_servers.build_sdk_client",
            return_value=client,
        ):
            result = get_radius_server("missing-id")

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["error"]["type"], "NotFoundError")
        self.assertEqual(result["error"]["message"], "radius server not found")

    def test_list_radius_servers_sdk_error_path(self) -> None:
        client = Mock()
        client.radius_servers.list.side_effect = APIResponseError("upstream failure")

        with patch(
            "netskope_sdwan_mcp.tools.radius_servers.build_sdk_client",
            return_value=client,
        ):
            result = list_radius_servers()

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_serialize_radius_server_supports_sdk_objects(self) -> None:
        radius_server = FakeRadiusServer(
            id="radius-123",
            name="Corp RADIUS",
            raw={"id": "radius-123", "name": "Corp RADIUS", "tenant_id": "tenant-9"},
        )

        self.assertEqual(
            serialize_radius_server(radius_server),
            {"id": "radius-123", "name": "Corp RADIUS", "tenant_id": "tenant-9"},
        )


if __name__ == "__main__":
    unittest.main()
