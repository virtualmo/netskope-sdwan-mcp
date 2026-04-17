"""Focused tests for v1 edge MCP tool behavior."""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Optional
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.tools.edges_v1 import (
    get_edge,
    get_edge_interface,
    get_gateway_interface,
    list_edge_interfaces,
    list_edges,
    list_gateway_interfaces,
    serialize_edge,
)


@dataclass
class FakeEdge:
    id: str
    name: Optional[str] = None
    raw: Optional[dict] = None


class NotFoundError(Exception):
    """SDK-shaped not found error used in tests."""


class APIResponseError(Exception):
    """SDK-shaped generic API error used in tests."""


class V1EdgeToolsTest(unittest.TestCase):
    def test_list_edges_success(self) -> None:
        client = Mock()
        client.v1.edges.list.return_value = [
            FakeEdge(
                id="edge-001",
                name="Branch Edge 1",
                raw={"id": "edge-001", "name": "Branch Edge 1", "state": "ready"},
            ),
            FakeEdge(
                id="edge-002",
                name="Branch Edge 2",
                raw={"id": "edge-002", "name": "Branch Edge 2"},
            ),
        ]

        with patch(
            "netskope_sdwan_mcp.tools.edges_v1.build_sdk_client",
            return_value=client,
        ):
            result = list_edges()

        client.v1.edges.list.assert_called_once_with()
        self.assertEqual(
            result,
            [
                {"id": "edge-001", "name": "Branch Edge 1", "state": "ready"},
                {"id": "edge-002", "name": "Branch Edge 2"},
            ],
        )

    def test_get_edge_success(self) -> None:
        client = Mock()
        client.v1.edges.get.return_value = FakeEdge(
            id="edge-001",
            name="Branch Edge 1",
            raw={"id": "edge-001", "name": "Branch Edge 1", "tenant_id": "tenant-1"},
        )

        with patch(
            "netskope_sdwan_mcp.tools.edges_v1.build_sdk_client",
            return_value=client,
        ):
            result = get_edge("edge-001")

        client.v1.edges.get.assert_called_once_with("edge-001")
        self.assertEqual(
            result,
            {"id": "edge-001", "name": "Branch Edge 1", "tenant_id": "tenant-1"},
        )

    def test_get_edge_not_found_path(self) -> None:
        client = Mock()
        client.v1.edges.get.side_effect = NotFoundError("edge not found")

        with patch(
            "netskope_sdwan_mcp.tools.edges_v1.build_sdk_client",
            return_value=client,
        ):
            result = get_edge("missing-edge")

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["error"]["type"], "NotFoundError")
        self.assertEqual(result["error"]["message"], "edge not found")

    def test_list_edge_interfaces_success(self) -> None:
        client = Mock()
        client.v1.edges.list_interfaces.return_value = [
            {"name": "wan0", "state": "up"},
            {"name": "lan0", "state": "down"},
        ]

        with patch(
            "netskope_sdwan_mcp.tools.edges_v1.build_sdk_client",
            return_value=client,
        ):
            result = list_edge_interfaces("edge-001")

        client.v1.edges.list_interfaces.assert_called_once_with("edge-001")
        self.assertEqual(
            result,
            [
                {"name": "wan0", "state": "up"},
                {"name": "lan0", "state": "down"},
            ],
        )

    def test_get_edge_interface_success(self) -> None:
        client = Mock()
        client.v1.edges.get_interface.return_value = {"name": "wan0", "state": "up"}

        with patch(
            "netskope_sdwan_mcp.tools.edges_v1.build_sdk_client",
            return_value=client,
        ):
            result = get_edge_interface("edge-001", "wan0")

        client.v1.edges.get_interface.assert_called_once_with("edge-001", "wan0")
        self.assertEqual(result, {"name": "wan0", "state": "up"})

    def test_list_gateway_interfaces_success(self) -> None:
        client = Mock()
        client.v1.edges.list_gateway_interfaces.return_value = [
            {"name": "ge0", "adminUp": True},
        ]

        with patch(
            "netskope_sdwan_mcp.tools.edges_v1.build_sdk_client",
            return_value=client,
        ):
            result = list_gateway_interfaces("gw-001")

        client.v1.edges.list_gateway_interfaces.assert_called_once_with("gw-001")
        self.assertEqual(result, [{"name": "ge0", "adminUp": True}])

    def test_get_gateway_interface_success(self) -> None:
        client = Mock()
        client.v1.edges.get_gateway_interface.return_value = {
            "name": "ge0",
            "adminUp": True,
        }

        with patch(
            "netskope_sdwan_mcp.tools.edges_v1.build_sdk_client",
            return_value=client,
        ):
            result = get_gateway_interface("gw-001", "ge0")

        client.v1.edges.get_gateway_interface.assert_called_once_with("gw-001", "ge0")
        self.assertEqual(result, {"name": "ge0", "adminUp": True})

    def test_list_edge_interfaces_sdk_error_path(self) -> None:
        client = Mock()
        client.v1.edges.list_interfaces.side_effect = APIResponseError("upstream failure")

        with patch(
            "netskope_sdwan_mcp.tools.edges_v1.build_sdk_client",
            return_value=client,
        ):
            result = list_edge_interfaces("edge-001")

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_serialize_edge_supports_sdk_objects(self) -> None:
        edge = FakeEdge(
            id="edge-123",
            name="Remote Edge",
            raw={"id": "edge-123", "name": "Remote Edge", "account_id": "acct-9"},
        )

        self.assertEqual(
            serialize_edge(edge),
            {"id": "edge-123", "name": "Remote Edge", "account_id": "acct-9"},
        )


if __name__ == "__main__":
    unittest.main()
