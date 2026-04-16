"""Focused tests for client MCP tool behavior."""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Optional
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.tools.clients import (
    get_client,
    list_clients,
    serialize_client,
)


@dataclass
class FakeClient:
    id: str
    name: Optional[str] = None
    raw: Optional[dict] = None


class NotFoundError(Exception):
    """SDK-shaped not found error used in tests."""


class APIResponseError(Exception):
    """SDK-shaped generic API error used in tests."""


class ClientToolsTest(unittest.TestCase):
    def test_list_clients_success(self) -> None:
        client = Mock()
        client.clients.list.return_value = [
            FakeClient(
                id="client-001",
                name="Branch Laptop",
                raw={"id": "client-001", "name": "Branch Laptop", "os": "macOS"},
            ),
            FakeClient(
                id="client-002",
                name="HQ Desktop",
                raw={"id": "client-002", "name": "HQ Desktop"},
            ),
        ]

        with patch(
            "netskope_sdwan_mcp.tools.clients.build_sdk_client",
            return_value=client,
        ):
            result = list_clients(filter="name: Branch")

        client.clients.list.assert_called_once_with(filter="name: Branch")
        self.assertEqual(
            result,
            [
                {"id": "client-001", "name": "Branch Laptop", "os": "macOS"},
                {"id": "client-002", "name": "HQ Desktop"},
            ],
        )

    def test_get_client_success(self) -> None:
        client = Mock()
        client.clients.get.return_value = FakeClient(
            id="client-001",
            name="Branch Laptop",
            raw={"id": "client-001", "name": "Branch Laptop", "status": "online"},
        )

        with patch(
            "netskope_sdwan_mcp.tools.clients.build_sdk_client",
            return_value=client,
        ):
            result = get_client("client-001")

        client.clients.get.assert_called_once_with("client-001")
        self.assertEqual(result["id"], "client-001")
        self.assertEqual(result["name"], "Branch Laptop")
        self.assertEqual(result["status"], "online")

    def test_get_client_not_found_path(self) -> None:
        client = Mock()
        client.clients.get.side_effect = NotFoundError("client not found")

        with patch(
            "netskope_sdwan_mcp.tools.clients.build_sdk_client",
            return_value=client,
        ):
            result = get_client("missing-id")

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["error"]["type"], "NotFoundError")
        self.assertEqual(result["error"]["message"], "client not found")

    def test_list_clients_sdk_error_path(self) -> None:
        client = Mock()
        client.clients.list.side_effect = APIResponseError("upstream failure")

        with patch(
            "netskope_sdwan_mcp.tools.clients.build_sdk_client",
            return_value=client,
        ):
            result = list_clients()

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_serialize_client_supports_sdk_objects(self) -> None:
        client_record = FakeClient(
            id="client-123",
            name="Remote Tablet",
            raw={"id": "client-123", "name": "Remote Tablet", "tenant_id": "tenant-9"},
        )

        self.assertEqual(
            serialize_client(client_record),
            {"id": "client-123", "name": "Remote Tablet", "tenant_id": "tenant-9"},
        )


if __name__ == "__main__":
    unittest.main()
