"""Focused tests for gateway-group MCP tool behavior."""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Optional
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.tools.gateway_groups import (
    get_gateway_group,
    list_gateway_groups,
    serialize_gateway_group,
)


@dataclass
class FakeGatewayGroup:
    id: str
    name: Optional[str] = None
    raw: Optional[dict] = None


class NotFoundError(Exception):
    """SDK-shaped not found error used in tests."""


class APIResponseError(Exception):
    """SDK-shaped generic API error used in tests."""


class GatewayGroupToolsTest(unittest.TestCase):
    def test_list_gateway_groups_success(self) -> None:
        client = Mock()
        client.gateway_groups.list.return_value = [
            FakeGatewayGroup(
                id="gg-001",
                name="Branch Group",
                raw={"id": "gg-001", "name": "Branch Group", "gateway_count": 2},
            ),
            FakeGatewayGroup(
                id="gg-002",
                name="HQ Group",
                raw={"id": "gg-002", "name": "HQ Group"},
            ),
        ]

        with patch(
            "netskope_sdwan_mcp.tools.gateway_groups.build_sdk_client",
            return_value=client,
        ):
            result = list_gateway_groups(filter="name: Branch")

        client.gateway_groups.list.assert_called_once_with(filter="name: Branch")
        self.assertEqual(
            result,
            [
                {"id": "gg-001", "name": "Branch Group", "gateway_count": 2},
                {"id": "gg-002", "name": "HQ Group"},
            ],
        )

    def test_get_gateway_group_success(self) -> None:
        client = Mock()
        client.gateway_groups.get.return_value = FakeGatewayGroup(
            id="gg-001",
            name="Branch Group",
            raw={"id": "gg-001", "name": "Branch Group", "scope": "global"},
        )

        with patch(
            "netskope_sdwan_mcp.tools.gateway_groups.build_sdk_client",
            return_value=client,
        ):
            result = get_gateway_group("gg-001")

        client.gateway_groups.get.assert_called_once_with("gg-001")
        self.assertEqual(result["id"], "gg-001")
        self.assertEqual(result["name"], "Branch Group")
        self.assertEqual(result["scope"], "global")

    def test_get_gateway_group_not_found_path(self) -> None:
        client = Mock()
        client.gateway_groups.get.side_effect = NotFoundError("gateway group not found")

        with patch(
            "netskope_sdwan_mcp.tools.gateway_groups.build_sdk_client",
            return_value=client,
        ):
            result = get_gateway_group("missing-id")

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["error"]["type"], "NotFoundError")
        self.assertEqual(result["error"]["message"], "gateway group not found")

    def test_list_gateway_groups_sdk_error_path(self) -> None:
        client = Mock()
        client.gateway_groups.list.side_effect = APIResponseError("upstream failure")

        with patch(
            "netskope_sdwan_mcp.tools.gateway_groups.build_sdk_client",
            return_value=client,
        ):
            result = list_gateway_groups()

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "APIResponseError")
        self.assertEqual(result["error"]["message"], "upstream failure")

    def test_serialize_gateway_group_supports_sdk_objects(self) -> None:
        gateway_group = FakeGatewayGroup(
            id="gg-123",
            name="Readers",
            raw={"id": "gg-123", "name": "Readers", "account_id": "acct-9"},
        )

        self.assertEqual(
            serialize_gateway_group(gateway_group),
            {"id": "gg-123", "name": "Readers", "account_id": "acct-9"},
        )
