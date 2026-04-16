"""Focused tests for device-group MCP tool behavior."""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Optional
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.tools.device_groups import (
    get_device_group,
    list_device_groups,
    serialize_device_group,
)


@dataclass
class FakeDeviceGroup:
    id: str
    name: Optional[str] = None
    raw: Optional[dict] = None


class NotFoundError(Exception):
    """SDK-shaped not found error used in tests."""


class APIResponseError(Exception):
    """SDK-shaped generic API error used in tests."""


class DeviceGroupToolsTest(unittest.TestCase):
    def test_list_device_groups_success(self) -> None:
        client = Mock()
        client.device_groups.list.return_value = [
            FakeDeviceGroup(
                id="dg-001",
                name="Branches",
                raw={"id": "dg-001", "name": "Branches", "scope": "global"},
            ),
            FakeDeviceGroup(
                id="dg-002",
                name="HQ",
                raw={"id": "dg-002", "name": "HQ"},
            ),
        ]

        with patch(
            "netskope_sdwan_mcp.tools.device_groups.build_sdk_client",
            return_value=client,
        ):
            result = list_device_groups(filter="name: Branches")

        client.device_groups.list.assert_called_once_with(filter="name: Branches")
        self.assertEqual(
            result,
            [
                {"id": "dg-001", "name": "Branches", "scope": "global"},
                {"id": "dg-002", "name": "HQ"},
            ],
        )

    def test_get_device_group_success(self) -> None:
        client = Mock()
        client.device_groups.get.return_value = FakeDeviceGroup(
            id="dg-001",
            name="Branches",
            raw={"id": "dg-001", "name": "Branches", "type": "static"},
        )

        with patch(
            "netskope_sdwan_mcp.tools.device_groups.build_sdk_client",
            return_value=client,
        ):
            result = get_device_group("dg-001")

        client.device_groups.get.assert_called_once_with("dg-001")
        self.assertEqual(result["id"], "dg-001")
        self.assertEqual(result["name"], "Branches")
        self.assertEqual(result["type"], "static")

    def test_get_device_group_not_found_path(self) -> None:
        client = Mock()
        client.device_groups.get.side_effect = NotFoundError("device group not found")

        with patch(
            "netskope_sdwan_mcp.tools.device_groups.build_sdk_client",
            return_value=client,
        ):
            result = get_device_group("missing-id")

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["error"]["type"], "NotFoundError")
        self.assertEqual(result["error"]["message"], "device group not found")

    def test_list_device_groups_sdk_error_path(self) -> None:
        client = Mock()
        client.device_groups.list.side_effect = APIResponseError("upstream failure")

        with patch(
            "netskope_sdwan_mcp.tools.device_groups.build_sdk_client",
            return_value=client,
        ):
            result = list_device_groups()

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_serialize_device_group_supports_sdk_objects(self) -> None:
        device_group = FakeDeviceGroup(
            id="dg-123",
            name="Field Devices",
            raw={"id": "dg-123", "name": "Field Devices", "account_id": "acct-9"},
        )

        self.assertEqual(
            serialize_device_group(device_group),
            {"id": "dg-123", "name": "Field Devices", "account_id": "acct-9"},
        )


if __name__ == "__main__":
    unittest.main()
