"""Focused tests for inventory-device MCP tool behavior."""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Optional
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.tools.inventory_devices import (
    list_inventory_devices,
    serialize_inventory_device,
)


@dataclass
class FakeInventoryDevice:
    id: str
    name: Optional[str] = None
    raw: Optional[dict] = None


class APIResponseError(Exception):
    """SDK-shaped generic API error used in tests."""


class InventoryDeviceToolsTest(unittest.TestCase):
    def test_list_inventory_devices_success(self) -> None:
        client = Mock()
        client.inventory_devices.list.return_value = [
            FakeInventoryDevice(
                id="inv-001",
                name="Router 1",
                raw={"id": "inv-001", "name": "Router 1", "serial": "ABC123"},
            ),
            FakeInventoryDevice(
                id="inv-002",
                name="Router 2",
                raw={"id": "inv-002", "name": "Router 2"},
            ),
        ]

        with patch(
            "netskope_sdwan_mcp.tools.inventory_devices.build_sdk_client",
            return_value=client,
        ):
            result = list_inventory_devices(filter="name: Router")

        client.inventory_devices.list.assert_called_once_with(filter="name: Router")
        self.assertEqual(
            result,
            [
                {"id": "inv-001", "name": "Router 1", "serial": "ABC123"},
                {"id": "inv-002", "name": "Router 2"},
            ],
        )

    def test_list_inventory_devices_sdk_error_path(self) -> None:
        client = Mock()
        client.inventory_devices.list.side_effect = APIResponseError("upstream failure")

        with patch(
            "netskope_sdwan_mcp.tools.inventory_devices.build_sdk_client",
            return_value=client,
        ):
            result = list_inventory_devices()

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_serialize_inventory_device_supports_sdk_objects(self) -> None:
        inventory_device = FakeInventoryDevice(
            id="inv-123",
            name="Gateway Appliance",
            raw={"id": "inv-123", "name": "Gateway Appliance", "tenant_id": "tenant-9"},
        )

        self.assertEqual(
            serialize_inventory_device(inventory_device),
            {"id": "inv-123", "name": "Gateway Appliance", "tenant_id": "tenant-9"},
        )


if __name__ == "__main__":
    unittest.main()
