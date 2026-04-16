"""Focused tests for client-template MCP tool behavior."""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Optional
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.tools.client_templates import (
    get_client_template,
    list_client_templates,
    serialize_client_template,
)


@dataclass
class FakeClientTemplate:
    id: str
    name: Optional[str] = None
    raw: Optional[dict] = None


class NotFoundError(Exception):
    """SDK-shaped not found error used in tests."""


class APIResponseError(Exception):
    """SDK-shaped generic API error used in tests."""


class ClientTemplateToolsTest(unittest.TestCase):
    def test_list_client_templates_success(self) -> None:
        client = Mock()
        client.client_templates.list.return_value = [
            FakeClientTemplate(
                id="ct-001",
                name="Windows Client",
                raw={"id": "ct-001", "name": "Windows Client", "platform": "windows"},
            ),
            FakeClientTemplate(
                id="ct-002",
                name="macOS Client",
                raw={"id": "ct-002", "name": "macOS Client"},
            ),
        ]

        with patch(
            "netskope_sdwan_mcp.tools.client_templates.build_sdk_client",
            return_value=client,
        ):
            result = list_client_templates(filter="name: Windows")

        client.client_templates.list.assert_called_once_with(filter="name: Windows")
        self.assertEqual(
            result,
            [
                {"id": "ct-001", "name": "Windows Client", "platform": "windows"},
                {"id": "ct-002", "name": "macOS Client"},
            ],
        )

    def test_get_client_template_success(self) -> None:
        client = Mock()
        client.client_templates.get.return_value = FakeClientTemplate(
            id="ct-001",
            name="Windows Client",
            raw={"id": "ct-001", "name": "Windows Client", "version": "1.0"},
        )

        with patch(
            "netskope_sdwan_mcp.tools.client_templates.build_sdk_client",
            return_value=client,
        ):
            result = get_client_template("ct-001")

        client.client_templates.get.assert_called_once_with("ct-001")
        self.assertEqual(result["id"], "ct-001")
        self.assertEqual(result["name"], "Windows Client")
        self.assertEqual(result["version"], "1.0")

    def test_get_client_template_not_found_path(self) -> None:
        client = Mock()
        client.client_templates.get.side_effect = NotFoundError("client template not found")

        with patch(
            "netskope_sdwan_mcp.tools.client_templates.build_sdk_client",
            return_value=client,
        ):
            result = get_client_template("missing-id")

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["error"]["type"], "NotFoundError")
        self.assertEqual(result["error"]["message"], "client template not found")

    def test_list_client_templates_sdk_error_path(self) -> None:
        client = Mock()
        client.client_templates.list.side_effect = APIResponseError("upstream failure")

        with patch(
            "netskope_sdwan_mcp.tools.client_templates.build_sdk_client",
            return_value=client,
        ):
            result = list_client_templates()

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_serialize_client_template_supports_sdk_objects(self) -> None:
        client_template = FakeClientTemplate(
            id="ct-123",
            name="Linux Client",
            raw={"id": "ct-123", "name": "Linux Client", "account_id": "acct-9"},
        )

        self.assertEqual(
            serialize_client_template(client_template),
            {"id": "ct-123", "name": "Linux Client", "account_id": "acct-9"},
        )


if __name__ == "__main__":
    unittest.main()
