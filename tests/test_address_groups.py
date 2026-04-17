"""Focused tests for address-group MCP tool behavior."""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Optional
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.tools.address_groups import (
    get_address_group,
    list_address_group_objects,
    list_address_groups,
    serialize_address_group,
)


@dataclass
class FakeAddressGroup:
    id: str
    name: Optional[str] = None
    raw: Optional[dict] = None


class NotFoundError(Exception):
    """SDK-shaped not found error used in tests."""


class APIResponseError(Exception):
    """SDK-shaped generic API error used in tests."""


class AddressGroupToolsTest(unittest.TestCase):
    def test_list_address_groups_success(self) -> None:
        client = Mock()
        client.address_groups.list.return_value = [
            FakeAddressGroup(
                id="ag-001",
                name="HQ Addresses",
                raw={"id": "ag-001", "name": "HQ Addresses", "type": "static"},
            ),
            FakeAddressGroup(
                id="ag-002",
                name="Branch Addresses",
                raw={"id": "ag-002", "name": "Branch Addresses"},
            ),
        ]

        with patch(
            "netskope_sdwan_mcp.tools.address_groups.build_sdk_client",
            return_value=client,
        ):
            result = list_address_groups(filter="name: HQ")

        client.address_groups.list.assert_called_once_with(filter="name: HQ")
        self.assertEqual(
            result,
            [
                {"id": "ag-001", "name": "HQ Addresses", "type": "static"},
                {"id": "ag-002", "name": "Branch Addresses"},
            ],
        )

    def test_get_address_group_success(self) -> None:
        client = Mock()
        client.address_groups.get.return_value = FakeAddressGroup(
            id="ag-001",
            name="HQ Addresses",
            raw={"id": "ag-001", "name": "HQ Addresses", "scope": "global"},
        )

        with patch(
            "netskope_sdwan_mcp.tools.address_groups.build_sdk_client",
            return_value=client,
        ):
            result = get_address_group("ag-001")

        client.address_groups.get.assert_called_once_with("ag-001")
        self.assertEqual(result["id"], "ag-001")
        self.assertEqual(result["name"], "HQ Addresses")
        self.assertEqual(result["scope"], "global")

    def test_list_address_group_objects_success(self) -> None:
        client = Mock()
        client.address_groups.list_address_objects.return_value = [
            FakeAddressGroup(
                id="obj-001",
                name="HQ Object",
                raw={"id": "obj-001", "name": "HQ Object", "value": "10.0.0.0/24"},
            ),
            FakeAddressGroup(
                id="obj-002",
                name="Branch Object",
                raw={"id": "obj-002", "name": "Branch Object"},
            ),
        ]

        with patch(
            "netskope_sdwan_mcp.tools.address_groups.build_sdk_client",
            return_value=client,
        ):
            result = list_address_group_objects("ag-001", filter="name: HQ")

        client.address_groups.list_address_objects.assert_called_once_with(
            "ag-001",
            filter="name: HQ",
        )
        self.assertEqual(
            result,
            [
                {"id": "obj-001", "name": "HQ Object", "value": "10.0.0.0/24"},
                {"id": "obj-002", "name": "Branch Object"},
            ],
        )

    def test_get_address_group_not_found_path(self) -> None:
        client = Mock()
        client.address_groups.get.side_effect = NotFoundError("address group not found")

        with patch(
            "netskope_sdwan_mcp.tools.address_groups.build_sdk_client",
            return_value=client,
        ):
            result = get_address_group("missing-id")

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["error"]["type"], "NotFoundError")
        self.assertEqual(result["error"]["message"], "address group not found")

    def test_list_address_groups_sdk_error_path(self) -> None:
        client = Mock()
        client.address_groups.list.side_effect = APIResponseError("upstream failure")

        with patch(
            "netskope_sdwan_mcp.tools.address_groups.build_sdk_client",
            return_value=client,
        ):
            result = list_address_groups()

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_list_address_group_objects_sdk_error_path(self) -> None:
        client = Mock()
        client.address_groups.list_address_objects.side_effect = APIResponseError(
            "upstream failure"
        )

        with patch(
            "netskope_sdwan_mcp.tools.address_groups.build_sdk_client",
            return_value=client,
        ):
            result = list_address_group_objects("ag-001")

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_serialize_address_group_supports_sdk_objects(self) -> None:
        address_group = FakeAddressGroup(
            id="ag-123",
            name="Shared Addresses",
            raw={"id": "ag-123", "name": "Shared Addresses", "account_id": "acct-9"},
        )

        self.assertEqual(
            serialize_address_group(address_group),
            {"id": "ag-123", "name": "Shared Addresses", "account_id": "acct-9"},
        )


if __name__ == "__main__":
    unittest.main()
