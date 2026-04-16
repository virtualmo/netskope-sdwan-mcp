"""Focused tests for user-group MCP tool behavior."""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Optional
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.tools.user_groups import (
    get_user_group,
    list_user_groups,
    serialize_user_group,
)


@dataclass
class FakeUserGroup:
    id: str
    name: Optional[str] = None
    raw: Optional[dict] = None


class NotFoundError(Exception):
    """SDK-shaped not found error used in tests."""


class APIResponseError(Exception):
    """SDK-shaped generic API error used in tests."""


class UserGroupToolsTest(unittest.TestCase):
    def test_list_user_groups_success(self) -> None:
        client = Mock()
        client.user_groups.list.return_value = [
            FakeUserGroup(
                id="group-001",
                name="Admins",
                raw={"id": "group-001", "name": "Admins", "member_count": 2},
            ),
            FakeUserGroup(
                id="group-002",
                name="Operators",
                raw={"id": "group-002", "name": "Operators"},
            ),
        ]

        with patch(
            "netskope_sdwan_mcp.tools.user_groups.build_sdk_client",
            return_value=client,
        ):
            result = list_user_groups(filter="name: Admins")

        client.user_groups.list.assert_called_once_with(filter="name: Admins")
        self.assertEqual(
            result,
            [
                {"id": "group-001", "name": "Admins", "member_count": 2},
                {"id": "group-002", "name": "Operators"},
            ],
        )

    def test_get_user_group_success(self) -> None:
        client = Mock()
        client.user_groups.get.return_value = FakeUserGroup(
            id="group-001",
            name="Admins",
            raw={"id": "group-001", "name": "Admins", "scope": "global"},
        )

        with patch(
            "netskope_sdwan_mcp.tools.user_groups.build_sdk_client",
            return_value=client,
        ):
            result = get_user_group("group-001")

        client.user_groups.get.assert_called_once_with("group-001")
        self.assertEqual(result["id"], "group-001")
        self.assertEqual(result["name"], "Admins")
        self.assertEqual(result["scope"], "global")

    def test_get_user_group_not_found_path(self) -> None:
        client = Mock()
        client.user_groups.get.side_effect = NotFoundError("user group not found")

        with patch(
            "netskope_sdwan_mcp.tools.user_groups.build_sdk_client",
            return_value=client,
        ):
            result = get_user_group("missing-id")

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["error"]["type"], "NotFoundError")
        self.assertEqual(result["error"]["message"], "user group not found")

    def test_list_user_groups_sdk_error_path(self) -> None:
        client = Mock()
        client.user_groups.list.side_effect = APIResponseError("upstream failure")

        with patch(
            "netskope_sdwan_mcp.tools.user_groups.build_sdk_client",
            return_value=client,
        ):
            result = list_user_groups()

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_serialize_user_group_supports_sdk_objects(self) -> None:
        user_group = FakeUserGroup(
            id="group-123",
            name="Readers",
            raw={"id": "group-123", "name": "Readers", "account_id": "acct-9"},
        )

        self.assertEqual(
            serialize_user_group(user_group),
            {"id": "group-123", "name": "Readers", "account_id": "acct-9"},
        )
