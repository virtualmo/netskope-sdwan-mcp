"""Focused tests for software MCP tool behavior."""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Optional
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.tools.software import (
    list_software_downloads,
    list_software_versions,
    serialize_software_item,
)


@dataclass
class FakeSoftwareItem:
    id: str
    name: Optional[str] = None
    raw: Optional[dict] = None


class APIResponseError(Exception):
    """SDK-shaped generic API error used in tests."""


class SoftwareToolsTest(unittest.TestCase):
    def test_list_software_versions_success(self) -> None:
        client = Mock()
        client.software.list_versions.return_value = [
            FakeSoftwareItem(
                id="swv-001",
                name="Version 10.1.0",
                raw={"id": "swv-001", "name": "Version 10.1.0", "release": "stable"},
            ),
            FakeSoftwareItem(
                id="swv-002",
                name="Version 10.2.0",
                raw={"id": "swv-002", "name": "Version 10.2.0"},
            ),
        ]

        with patch(
            "netskope_sdwan_mcp.tools.software.build_sdk_client",
            return_value=client,
        ):
            result = list_software_versions(filter="name: 10.1")

        client.software.list_versions.assert_called_once_with(filter="name: 10.1")
        self.assertEqual(
            result,
            [
                {"id": "swv-001", "name": "Version 10.1.0", "release": "stable"},
                {"id": "swv-002", "name": "Version 10.2.0"},
            ],
        )

    def test_list_software_downloads_success(self) -> None:
        client = Mock()
        client.software.list_downloads.return_value = [
            FakeSoftwareItem(
                id="swd-001",
                name="Image A",
                raw={"id": "swd-001", "name": "Image A", "platform": "x86"},
            ),
            FakeSoftwareItem(
                id="swd-002",
                name="Image B",
                raw={"id": "swd-002", "name": "Image B"},
            ),
        ]

        with patch(
            "netskope_sdwan_mcp.tools.software.build_sdk_client",
            return_value=client,
        ):
            result = list_software_downloads(filter="name: Image")

        client.software.list_downloads.assert_called_once_with(filter="name: Image")
        self.assertEqual(
            result,
            [
                {"id": "swd-001", "name": "Image A", "platform": "x86"},
                {"id": "swd-002", "name": "Image B"},
            ],
        )

    def test_list_software_versions_sdk_error_path(self) -> None:
        client = Mock()
        client.software.list_versions.side_effect = APIResponseError("upstream failure")

        with patch(
            "netskope_sdwan_mcp.tools.software.build_sdk_client",
            return_value=client,
        ):
            result = list_software_versions()

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_list_software_downloads_sdk_error_path(self) -> None:
        client = Mock()
        client.software.list_downloads.side_effect = APIResponseError("upstream failure")

        with patch(
            "netskope_sdwan_mcp.tools.software.build_sdk_client",
            return_value=client,
        ):
            result = list_software_downloads()

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_serialize_software_item_supports_sdk_objects(self) -> None:
        software_item = FakeSoftwareItem(
            id="sw-123",
            name="Version 11.0.0",
            raw={"id": "sw-123", "name": "Version 11.0.0", "tenant_id": "tenant-9"},
        )

        self.assertEqual(
            serialize_software_item(software_item),
            {"id": "sw-123", "name": "Version 11.0.0", "tenant_id": "tenant-9"},
        )


if __name__ == "__main__":
    unittest.main()
