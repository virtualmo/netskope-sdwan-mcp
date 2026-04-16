"""Focused tests for user MCP tool behavior."""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Optional
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.tools.users import get_user, list_users, serialize_user


@dataclass
class FakeUser:
    id: str
    name: Optional[str] = None
    raw: Optional[dict] = None


class NotFoundError(Exception):
    """SDK-shaped not found error used in tests."""


class APIResponseError(Exception):
    """SDK-shaped generic API error used in tests."""


class UserToolsTest(unittest.TestCase):
    def test_list_users_success(self) -> None:
        client = Mock()
        client.users.list.return_value = [
            FakeUser(id="user-001", name="Alice", raw={"id": "user-001", "name": "Alice", "email": "alice@example.com"}),
            FakeUser(id="user-002", name="Bob", raw={"id": "user-002", "name": "Bob"}),
        ]

        with patch("netskope_sdwan_mcp.tools.users.build_sdk_client", return_value=client):
            result = list_users(filter="name: Alice")

        client.users.list.assert_called_once_with(filter="name: Alice")
        self.assertEqual(
            result,
            [
                {"id": "user-001", "name": "Alice", "email": "alice@example.com"},
                {"id": "user-002", "name": "Bob"},
            ],
        )

    def test_get_user_success(self) -> None:
        client = Mock()
        client.users.get.return_value = FakeUser(
            id="user-001",
            name="Alice",
            raw={"id": "user-001", "name": "Alice", "role": "admin"},
        )

        with patch("netskope_sdwan_mcp.tools.users.build_sdk_client", return_value=client):
            result = get_user("user-001")

        client.users.get.assert_called_once_with("user-001")
        self.assertEqual(result["id"], "user-001")
        self.assertEqual(result["name"], "Alice")
        self.assertEqual(result["role"], "admin")

    def test_get_user_not_found_path(self) -> None:
        client = Mock()
        client.users.get.side_effect = NotFoundError("user not found")

        with patch("netskope_sdwan_mcp.tools.users.build_sdk_client", return_value=client):
            result = get_user("missing-id")

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["error"]["type"], "NotFoundError")
        self.assertEqual(result["error"]["message"], "user not found")

    def test_list_users_sdk_error_path(self) -> None:
        client = Mock()
        client.users.list.side_effect = APIResponseError("upstream failure")

        with patch("netskope_sdwan_mcp.tools.users.build_sdk_client", return_value=client):
            result = list_users()

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_serialize_user_supports_sdk_objects(self) -> None:
        user = FakeUser(
            id="user-123",
            name="Charlie",
            raw={"id": "user-123", "name": "Charlie", "account_id": "acct-9"},
        )

        self.assertEqual(
            serialize_user(user),
            {"id": "user-123", "name": "Charlie", "account_id": "acct-9"},
        )
