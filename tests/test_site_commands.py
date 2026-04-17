"""Focused tests for site-command MCP tool behavior."""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Optional
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.tools.site_commands import (
    get_site_command,
    get_site_command_output,
    list_site_commands,
    serialize_site_command,
)


@dataclass
class FakeSiteCommand:
    id: str
    name: Optional[str] = None
    raw: Optional[dict] = None


@dataclass
class FakeDownloadResult:
    content: bytes
    content_type: Optional[str] = None
    content_disposition: Optional[str] = None
    filename: Optional[str] = None


class NotFoundError(Exception):
    """SDK-shaped not found error used in tests."""


class APIResponseError(Exception):
    """SDK-shaped generic API error used in tests."""


class SiteCommandToolsTest(unittest.TestCase):
    def test_list_site_commands_success(self) -> None:
        client = Mock()
        client.site_commands.list.return_value = [
            FakeSiteCommand(
                id="cmd-001",
                name="Collect Logs",
                raw={"id": "cmd-001", "name": "Collect Logs", "status": "done"},
            ),
            FakeSiteCommand(
                id="cmd-002",
                name="Run Capture",
                raw={"id": "cmd-002", "name": "Run Capture"},
            ),
        ]

        with patch(
            "netskope_sdwan_mcp.tools.site_commands.build_sdk_client",
            return_value=client,
        ):
            result = list_site_commands(filter="name: Collect")

        client.site_commands.list.assert_called_once_with(filter="name: Collect")
        self.assertEqual(
            result,
            [
                {"id": "cmd-001", "name": "Collect Logs", "status": "done"},
                {"id": "cmd-002", "name": "Run Capture"},
            ],
        )

    def test_get_site_command_success(self) -> None:
        client = Mock()
        client.site_commands.get.return_value = FakeSiteCommand(
            id="cmd-001",
            name="Collect Logs",
            raw={"id": "cmd-001", "name": "Collect Logs", "scope": "tenant"},
        )

        with patch(
            "netskope_sdwan_mcp.tools.site_commands.build_sdk_client",
            return_value=client,
        ):
            result = get_site_command("cmd-001")

        client.site_commands.get.assert_called_once_with("cmd-001")
        self.assertEqual(result["id"], "cmd-001")
        self.assertEqual(result["name"], "Collect Logs")
        self.assertEqual(result["scope"], "tenant")

    def test_get_site_command_not_found_path(self) -> None:
        client = Mock()
        client.site_commands.get.side_effect = NotFoundError("site command not found")

        with patch(
            "netskope_sdwan_mcp.tools.site_commands.build_sdk_client",
            return_value=client,
        ):
            result = get_site_command("missing-id")

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["error"]["type"], "NotFoundError")
        self.assertEqual(result["error"]["message"], "site command not found")

    def test_get_site_command_output_success(self) -> None:
        client = Mock()
        client.site_commands.get_output.return_value = FakeDownloadResult(
            content=b"command output\n",
            content_type="text/plain",
            filename="output.txt",
        )

        with patch(
            "netskope_sdwan_mcp.tools.site_commands.build_sdk_client",
            return_value=client,
        ):
            result = get_site_command_output("cmd-001", "output.txt")

        client.site_commands.get_output.assert_called_once_with("cmd-001", "output.txt")
        self.assertEqual(
            result,
            {
                "content": "command output\n",
                "content_type": "text/plain",
                "content_disposition": None,
                "filename": "output.txt",
            },
        )

    def test_list_site_commands_sdk_error_path(self) -> None:
        client = Mock()
        client.site_commands.list.side_effect = APIResponseError("upstream failure")

        with patch(
            "netskope_sdwan_mcp.tools.site_commands.build_sdk_client",
            return_value=client,
        ):
            result = list_site_commands()

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_get_site_command_output_sdk_error_path(self) -> None:
        client = Mock()
        client.site_commands.get_output.side_effect = APIResponseError("upstream failure")

        with patch(
            "netskope_sdwan_mcp.tools.site_commands.build_sdk_client",
            return_value=client,
        ):
            result = get_site_command_output("cmd-001", "output.txt")

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_serialize_site_command_supports_sdk_objects(self) -> None:
        site_command = FakeSiteCommand(
            id="cmd-123",
            name="Health Check",
            raw={"id": "cmd-123", "name": "Health Check", "account_id": "acct-9"},
        )

        self.assertEqual(
            serialize_site_command(site_command),
            {"id": "cmd-123", "name": "Health Check", "account_id": "acct-9"},
        )


if __name__ == "__main__":
    unittest.main()
