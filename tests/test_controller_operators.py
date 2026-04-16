"""Focused tests for controller-operator MCP tool behavior."""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Optional
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.tools.controller_operators import (
    get_controller_operator,
    list_controller_operators,
    serialize_controller_operator,
)


@dataclass
class FakeControllerOperator:
    id: str
    name: Optional[str] = None
    raw: Optional[dict] = None


class NotFoundError(Exception):
    """SDK-shaped not found error used in tests."""


class APIResponseError(Exception):
    """SDK-shaped generic API error used in tests."""


class ControllerOperatorToolsTest(unittest.TestCase):
    def test_list_controller_operators_success(self) -> None:
        client = Mock()
        client.controller_operators.list.return_value = [
            FakeControllerOperator(
                id="op-001",
                name="Primary Operator",
                raw={"id": "op-001", "name": "Primary Operator", "role": "admin"},
            ),
            FakeControllerOperator(
                id="op-002",
                name="Backup Operator",
                raw={"id": "op-002", "name": "Backup Operator"},
            ),
        ]

        with patch(
            "netskope_sdwan_mcp.tools.controller_operators.build_sdk_client",
            return_value=client,
        ):
            result = list_controller_operators(filter="name: Primary")

        client.controller_operators.list.assert_called_once_with(filter="name: Primary")
        self.assertEqual(
            result,
            [
                {"id": "op-001", "name": "Primary Operator", "role": "admin"},
                {"id": "op-002", "name": "Backup Operator"},
            ],
        )

    def test_get_controller_operator_success(self) -> None:
        client = Mock()
        client.controller_operators.get.return_value = FakeControllerOperator(
            id="op-001",
            name="Primary Operator",
            raw={"id": "op-001", "name": "Primary Operator", "status": "active"},
        )

        with patch(
            "netskope_sdwan_mcp.tools.controller_operators.build_sdk_client",
            return_value=client,
        ):
            result = get_controller_operator("op-001")

        client.controller_operators.get.assert_called_once_with("op-001")
        self.assertEqual(result["id"], "op-001")
        self.assertEqual(result["name"], "Primary Operator")
        self.assertEqual(result["status"], "active")

    def test_get_controller_operator_not_found_path(self) -> None:
        client = Mock()
        client.controller_operators.get.side_effect = NotFoundError(
            "controller operator not found"
        )

        with patch(
            "netskope_sdwan_mcp.tools.controller_operators.build_sdk_client",
            return_value=client,
        ):
            result = get_controller_operator("missing-id")

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["error"]["type"], "NotFoundError")
        self.assertEqual(result["error"]["message"], "controller operator not found")

    def test_list_controller_operators_sdk_error_path(self) -> None:
        client = Mock()
        client.controller_operators.list.side_effect = APIResponseError("upstream failure")

        with patch(
            "netskope_sdwan_mcp.tools.controller_operators.build_sdk_client",
            return_value=client,
        ):
            result = list_controller_operators()

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_serialize_controller_operator_supports_sdk_objects(self) -> None:
        controller_operator = FakeControllerOperator(
            id="op-123",
            name="Regional Operator",
            raw={"id": "op-123", "name": "Regional Operator", "account_id": "acct-9"},
        )

        self.assertEqual(
            serialize_controller_operator(controller_operator),
            {"id": "op-123", "name": "Regional Operator", "account_id": "acct-9"},
        )


if __name__ == "__main__":
    unittest.main()
