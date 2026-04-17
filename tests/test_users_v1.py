"""Focused tests for v1 user MCP tool behavior."""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Optional
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.tools.users_v1 import (
    get_v1_user_groups,
    serialize_v1_user_group,
)


@dataclass
class FakeV1UserGroup:
    id: str
    name: Optional[str] = None
    raw: Optional[dict] = None


class APIResponseError(Exception):
    """SDK-shaped generic API error used in tests."""


class V1UserToolsTest(unittest.TestCase):
    def test_get_v1_user_groups_success(self) -> None:
        client = Mock()
        client.v1.users.get_groups.return_value = [
            FakeV1UserGroup(
                id="group-001",
                name="Ops",
                raw={"id": "group-001", "name": "Ops", "type": "static"},
            ),
            FakeV1UserGroup(
                id="group-002",
                name="Sales",
                raw={"id": "group-002", "name": "Sales"},
            ),
        ]

        with patch(
            "netskope_sdwan_mcp.tools.users_v1.build_sdk_client",
            return_value=client,
        ):
            result = get_v1_user_groups("user-001")

        client.v1.users.get_groups.assert_called_once_with("user-001")
        self.assertEqual(
            result,
            [
                {"id": "group-001", "name": "Ops", "type": "static"},
                {"id": "group-002", "name": "Sales"},
            ],
        )

    def test_get_v1_user_groups_sdk_error_path(self) -> None:
        client = Mock()
        client.v1.users.get_groups.side_effect = APIResponseError("upstream failure")

        with patch(
            "netskope_sdwan_mcp.tools.users_v1.build_sdk_client",
            return_value=client,
        ):
            result = get_v1_user_groups("user-001")

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_serialize_v1_user_group_supports_sdk_objects(self) -> None:
        group = FakeV1UserGroup(
            id="group-123",
            name="Engineering",
            raw={"id": "group-123", "name": "Engineering", "tenant_id": "tenant-9"},
        )

        self.assertEqual(
            serialize_v1_user_group(group),
            {"id": "group-123", "name": "Engineering", "tenant_id": "tenant-9"},
        )


if __name__ == "__main__":
    unittest.main()
