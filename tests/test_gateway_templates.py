"""Focused tests for gateway-template MCP tool behavior."""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Optional
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.tools.gateway_templates import (
    get_gateway_template,
    list_gateway_templates,
    serialize_gateway_template,
)


@dataclass
class FakeGatewayTemplate:
    id: str
    name: Optional[str] = None
    raw: Optional[dict] = None


class NotFoundError(Exception):
    """SDK-shaped not found error used in tests."""


class APIResponseError(Exception):
    """SDK-shaped generic API error used in tests."""


class GatewayTemplateToolsTest(unittest.TestCase):
    def test_list_gateway_templates_success(self) -> None:
        client = Mock()
        client.gateway_templates.list.return_value = [
            FakeGatewayTemplate(
                id="gt-001",
                name="Branch Template",
                raw={"id": "gt-001", "name": "Branch Template", "model": "edge"},
            ),
            FakeGatewayTemplate(
                id="gt-002",
                name="HQ Template",
                raw={"id": "gt-002", "name": "HQ Template"},
            ),
        ]

        with patch(
            "netskope_sdwan_mcp.tools.gateway_templates.build_sdk_client",
            return_value=client,
        ):
            result = list_gateway_templates(filter="name: Branch")

        client.gateway_templates.list.assert_called_once_with(filter="name: Branch")
        self.assertEqual(
            result,
            [
                {"id": "gt-001", "name": "Branch Template", "model": "edge"},
                {"id": "gt-002", "name": "HQ Template"},
            ],
        )

    def test_get_gateway_template_success(self) -> None:
        client = Mock()
        client.gateway_templates.get.return_value = FakeGatewayTemplate(
            id="gt-001",
            name="Branch Template",
            raw={"id": "gt-001", "name": "Branch Template", "version": "1.0"},
        )

        with patch(
            "netskope_sdwan_mcp.tools.gateway_templates.build_sdk_client",
            return_value=client,
        ):
            result = get_gateway_template("gt-001")

        client.gateway_templates.get.assert_called_once_with("gt-001")
        self.assertEqual(result["id"], "gt-001")
        self.assertEqual(result["name"], "Branch Template")
        self.assertEqual(result["version"], "1.0")

    def test_get_gateway_template_not_found_path(self) -> None:
        client = Mock()
        client.gateway_templates.get.side_effect = NotFoundError("gateway template not found")

        with patch(
            "netskope_sdwan_mcp.tools.gateway_templates.build_sdk_client",
            return_value=client,
        ):
            result = get_gateway_template("missing-id")

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["error"]["type"], "NotFoundError")
        self.assertEqual(result["error"]["message"], "gateway template not found")

    def test_list_gateway_templates_sdk_error_path(self) -> None:
        client = Mock()
        client.gateway_templates.list.side_effect = APIResponseError("upstream failure")

        with patch(
            "netskope_sdwan_mcp.tools.gateway_templates.build_sdk_client",
            return_value=client,
        ):
            result = list_gateway_templates()

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_serialize_gateway_template_supports_sdk_objects(self) -> None:
        gateway_template = FakeGatewayTemplate(
            id="gt-123",
            name="Regional Template",
            raw={"id": "gt-123", "name": "Regional Template", "account_id": "acct-9"},
        )

        self.assertEqual(
            serialize_gateway_template(gateway_template),
            {"id": "gt-123", "name": "Regional Template", "account_id": "acct-9"},
        )


if __name__ == "__main__":
    unittest.main()
