"""Focused tests for controller MCP tool behavior."""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Optional
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.tools.controllers import (
    get_controller,
    get_controller_operator_status,
    list_controllers,
    serialize_controller,
)


@dataclass
class FakeController:
    id: str
    name: Optional[str] = None
    raw: Optional[dict] = None


class NotFoundError(Exception):
    """SDK-shaped not found error used in tests."""


class APIResponseError(Exception):
    """SDK-shaped generic API error used in tests."""


class ControllerToolsTest(unittest.TestCase):
    def test_list_controllers_success(self) -> None:
        client = Mock()
        client.controllers.list.return_value = [
            FakeController(
                id="ctrl-001",
                name="Primary Controller",
                raw={"id": "ctrl-001", "name": "Primary Controller", "region": "eu"},
            ),
            FakeController(
                id="ctrl-002",
                name="Backup Controller",
                raw={"id": "ctrl-002", "name": "Backup Controller"},
            ),
        ]

        with patch(
            "netskope_sdwan_mcp.tools.controllers.build_sdk_client",
            return_value=client,
        ):
            result = list_controllers(filter="name: Primary")

        client.controllers.list.assert_called_once_with(filter="name: Primary")
        self.assertEqual(
            result,
            [
                {"id": "ctrl-001", "name": "Primary Controller", "region": "eu"},
                {"id": "ctrl-002", "name": "Backup Controller"},
            ],
        )

    def test_get_controller_success(self) -> None:
        client = Mock()
        client.controllers.get.return_value = FakeController(
            id="ctrl-001",
            name="Primary Controller",
            raw={"id": "ctrl-001", "name": "Primary Controller", "status": "active"},
        )

        with patch(
            "netskope_sdwan_mcp.tools.controllers.build_sdk_client",
            return_value=client,
        ):
            result = get_controller("ctrl-001")

        client.controllers.get.assert_called_once_with("ctrl-001")
        self.assertEqual(result["id"], "ctrl-001")
        self.assertEqual(result["name"], "Primary Controller")
        self.assertEqual(result["status"], "active")

    def test_get_controller_not_found_path(self) -> None:
        client = Mock()
        client.controllers.get.side_effect = NotFoundError("controller not found")

        with patch(
            "netskope_sdwan_mcp.tools.controllers.build_sdk_client",
            return_value=client,
        ):
            result = get_controller("missing-id")

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["error"]["type"], "NotFoundError")
        self.assertEqual(result["error"]["message"], "controller not found")

    def test_list_controllers_sdk_error_path(self) -> None:
        client = Mock()
        client.controllers.list.side_effect = APIResponseError("upstream failure")

        with patch(
            "netskope_sdwan_mcp.tools.controllers.build_sdk_client",
            return_value=client,
        ):
            result = list_controllers()

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_get_controller_operator_status_success(self) -> None:
        client = Mock()
        client.controllers.get_operator_status.return_value = {
            "controller_id": "ctrl-001",
            "status": "connected",
        }

        with patch(
            "netskope_sdwan_mcp.tools.controllers.build_sdk_client",
            return_value=client,
        ):
            result = get_controller_operator_status("ctrl-001")

        client.controllers.get_operator_status.assert_called_once_with("ctrl-001")
        self.assertEqual(
            result,
            {"controller_id": "ctrl-001", "status": "connected"},
        )

    def test_get_controller_operator_status_sdk_error_path(self) -> None:
        client = Mock()
        client.controllers.get_operator_status.side_effect = APIResponseError("upstream failure")

        with patch(
            "netskope_sdwan_mcp.tools.controllers.build_sdk_client",
            return_value=client,
        ):
            result = get_controller_operator_status("ctrl-001")

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_serialize_controller_supports_sdk_objects(self) -> None:
        controller = FakeController(
            id="ctrl-123",
            name="Regional Controller",
            raw={"id": "ctrl-123", "name": "Regional Controller", "account_id": "acct-9"},
        )

        self.assertEqual(
            serialize_controller(controller),
            {"id": "ctrl-123", "name": "Regional Controller", "account_id": "acct-9"},
        )


if __name__ == "__main__":
    unittest.main()
