"""Focused tests for application MCP tool behavior."""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Optional
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.tools.applications import (
    get_application,
    list_applications,
    serialize_application,
)


@dataclass
class FakeApplication:
    id: str
    name: Optional[str] = None
    raw: Optional[dict] = None


class NotFoundError(Exception):
    """SDK-shaped not found error used in tests."""


class APIResponseError(Exception):
    """SDK-shaped generic API error used in tests."""


class ApplicationToolsTest(unittest.TestCase):
    def test_list_applications_success(self) -> None:
        client = Mock()
        client.applications.list_custom_apps.return_value = [
            FakeApplication(
                id="app-001",
                name="CRM",
                raw={"id": "app-001", "name": "CRM", "category": "business"},
            ),
            FakeApplication(
                id="app-002",
                name="Docs",
                raw={"id": "app-002", "name": "Docs"},
            ),
        ]

        with patch(
            "netskope_sdwan_mcp.tools.applications.build_sdk_client",
            return_value=client,
        ):
            result = list_applications(filter="name: CRM")

        client.applications.list_custom_apps.assert_called_once_with(filter="name: CRM")
        self.assertEqual(
            result,
            [
                {"id": "app-001", "name": "CRM", "category": "business"},
                {"id": "app-002", "name": "Docs"},
            ],
        )

    def test_get_application_success(self) -> None:
        client = Mock()
        client.applications.get_custom_app.return_value = FakeApplication(
            id="app-001",
            name="CRM",
            raw={"id": "app-001", "name": "CRM", "scope": "tenant"},
        )

        with patch(
            "netskope_sdwan_mcp.tools.applications.build_sdk_client",
            return_value=client,
        ):
            result = get_application("app-001")

        client.applications.get_custom_app.assert_called_once_with("app-001")
        self.assertEqual(result["id"], "app-001")
        self.assertEqual(result["name"], "CRM")
        self.assertEqual(result["scope"], "tenant")

    def test_get_application_not_found_path(self) -> None:
        client = Mock()
        client.applications.get_custom_app.side_effect = NotFoundError("application not found")

        with patch(
            "netskope_sdwan_mcp.tools.applications.build_sdk_client",
            return_value=client,
        ):
            result = get_application("missing-id")

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["error"]["type"], "NotFoundError")
        self.assertEqual(result["error"]["message"], "application not found")

    def test_list_applications_sdk_error_path(self) -> None:
        client = Mock()
        client.applications.list_custom_apps.side_effect = APIResponseError("upstream failure")

        with patch(
            "netskope_sdwan_mcp.tools.applications.build_sdk_client",
            return_value=client,
        ):
            result = list_applications()

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_serialize_application_supports_sdk_objects(self) -> None:
        application = FakeApplication(
            id="app-123",
            name="Readers",
            raw={"id": "app-123", "name": "Readers", "account_id": "acct-9"},
        )

        self.assertEqual(
            serialize_application(application),
            {"id": "app-123", "name": "Readers", "account_id": "acct-9"},
        )
