"""Focused tests for NTP-config MCP tool behavior."""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Optional
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.tools.ntp_configs import (
    get_ntp_config,
    list_ntp_configs,
    serialize_ntp_config,
)


@dataclass
class FakeNTPConfig:
    id: str
    name: Optional[str] = None
    raw: Optional[dict] = None


class NotFoundError(Exception):
    """SDK-shaped not found error used in tests."""


class APIResponseError(Exception):
    """SDK-shaped generic API error used in tests."""


class NTPConfigToolsTest(unittest.TestCase):
    def test_list_ntp_configs_success(self) -> None:
        client = Mock()
        client.ntp_configs.list.return_value = [
            FakeNTPConfig(
                id="ntp-001",
                name="Default NTP",
                raw={"id": "ntp-001", "name": "Default NTP", "timezone": "UTC"},
            ),
            FakeNTPConfig(
                id="ntp-002",
                name="Regional NTP",
                raw={"id": "ntp-002", "name": "Regional NTP"},
            ),
        ]

        with patch(
            "netskope_sdwan_mcp.tools.ntp_configs.build_sdk_client",
            return_value=client,
        ):
            result = list_ntp_configs(filter="name: Default")

        client.ntp_configs.list.assert_called_once_with(filter="name: Default")
        self.assertEqual(
            result,
            [
                {"id": "ntp-001", "name": "Default NTP", "timezone": "UTC"},
                {"id": "ntp-002", "name": "Regional NTP"},
            ],
        )

    def test_get_ntp_config_success(self) -> None:
        client = Mock()
        client.ntp_configs.get.return_value = FakeNTPConfig(
            id="ntp-001",
            name="Default NTP",
            raw={"id": "ntp-001", "name": "Default NTP", "servers": ["0.pool.ntp.org"]},
        )

        with patch(
            "netskope_sdwan_mcp.tools.ntp_configs.build_sdk_client",
            return_value=client,
        ):
            result = get_ntp_config("ntp-001")

        client.ntp_configs.get.assert_called_once_with("ntp-001")
        self.assertEqual(result["id"], "ntp-001")
        self.assertEqual(result["name"], "Default NTP")
        self.assertEqual(result["servers"], ["0.pool.ntp.org"])

    def test_get_ntp_config_not_found_path(self) -> None:
        client = Mock()
        client.ntp_configs.get.side_effect = NotFoundError("ntp config not found")

        with patch(
            "netskope_sdwan_mcp.tools.ntp_configs.build_sdk_client",
            return_value=client,
        ):
            result = get_ntp_config("missing-id")

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["error"]["type"], "NotFoundError")
        self.assertEqual(result["error"]["message"], "ntp config not found")

    def test_list_ntp_configs_sdk_error_path(self) -> None:
        client = Mock()
        client.ntp_configs.list.side_effect = APIResponseError("upstream failure")

        with patch(
            "netskope_sdwan_mcp.tools.ntp_configs.build_sdk_client",
            return_value=client,
        ):
            result = list_ntp_configs()

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_serialize_ntp_config_supports_sdk_objects(self) -> None:
        ntp_config = FakeNTPConfig(
            id="ntp-123",
            name="Edge NTP",
            raw={"id": "ntp-123", "name": "Edge NTP", "account_id": "acct-9"},
        )

        self.assertEqual(
            serialize_ntp_config(ntp_config),
            {"id": "ntp-123", "name": "Edge NTP", "account_id": "acct-9"},
        )


if __name__ == "__main__":
    unittest.main()
