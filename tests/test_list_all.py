"""Focused tests for the generic auto-paginating list_all MCP tool."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.tools.list_all import (
    DEFAULT_LIMIT,
    list_all,
)


class ListAllToolsTest(unittest.TestCase):
    def test_list_all_dispatches_supported_resource(self) -> None:
        client = Mock()
        client.address_groups.last_page_info = {"has_next": False, "end_cursor": "cursor-1"}
        client.address_groups.last_cursors = None
        client.address_groups.list.return_value = [{"id": "ag-001", "name": "HQ"}]

        with patch(
            "netskope_sdwan_mcp.tools.list_all.build_sdk_client",
            return_value=client,
        ):
            result = list_all("address_groups", filter="name: HQ", first=50, sort="name", limit=50)

        client.address_groups.list.assert_called_once_with(
            after=None,
            first=50,
            sort="name",
            filter="name: HQ",
        )
        self.assertEqual(result["resource"], "address_groups")
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["items"], [{"id": "ag-001", "name": "HQ"}])
        self.assertFalse(result["has_more"])
        self.assertIsNone(result["next_after"])

    def test_list_all_paginates_using_after_cursor(self) -> None:
        client = Mock()
        manager = client.address_groups

        def list_side_effect(*, after=None, first=None, sort=None, filter=None):
            self.assertEqual(first, 2)
            if after is None:
                manager.last_page_info = {"has_next": True, "end_cursor": "cursor-1"}
                manager.last_cursors = {"after": "cursor-1"}
                return [{"id": "ag-001"}, {"id": "ag-002"}]

            self.assertEqual(after, "cursor-1")
            manager.last_page_info = {"has_next": False, "end_cursor": "cursor-2"}
            manager.last_cursors = {"after": "cursor-2"}
            return [{"id": "ag-003"}]

        manager.list.side_effect = list_side_effect

        with patch(
            "netskope_sdwan_mcp.tools.list_all.build_sdk_client",
            return_value=client,
        ):
            result = list_all("address_groups", first=2, limit=5)

        self.assertEqual(manager.list.call_count, 2)
        self.assertEqual(result["count"], 3)
        self.assertEqual(
            [item["id"] for item in result["items"]],
            ["ag-001", "ag-002", "ag-003"],
        )
        self.assertEqual(result["pages_fetched"], 2)
        self.assertFalse(result["has_more"])
        self.assertIsNone(result["next_after"])

    def test_list_all_stops_when_limit_is_reached(self) -> None:
        client = Mock()
        manager = client.address_groups

        def list_side_effect(*, after=None, first=None, sort=None, filter=None):
            if after is None:
                self.assertEqual(first, 2)
                manager.last_page_info = {"has_next": True, "end_cursor": "cursor-1"}
                manager.last_cursors = {"after": "cursor-1"}
                return [{"id": "ag-001"}, {"id": "ag-002"}]

            self.assertEqual(after, "cursor-1")
            self.assertEqual(first, 1)
            manager.last_page_info = {"has_next": True, "end_cursor": "cursor-2"}
            manager.last_cursors = {"after": "cursor-2"}
            return [{"id": "ag-003"}]

        manager.list.side_effect = list_side_effect

        with patch(
            "netskope_sdwan_mcp.tools.list_all.build_sdk_client",
            return_value=client,
        ):
            result = list_all("address_groups", first=2, limit=3)

        self.assertEqual(result["count"], 3)
        self.assertEqual(result["pages_fetched"], 2)
        self.assertTrue(result["has_more"])
        self.assertEqual(result["next_after"], "cursor-2")

    def test_list_all_requires_group_id_for_address_group_objects(self) -> None:
        result = list_all("address_group_objects")

        self.assertEqual(result["status"], "invalid_request")
        self.assertEqual(result["error"]["message"], "group_id is required for resource 'address_group_objects'")

    def test_list_all_rejects_unsupported_resource(self) -> None:
        result = list_all("not_a_resource")

        self.assertEqual(result["status"], "invalid_request")
        self.assertEqual(result["error"]["type"], "ValueError")
        self.assertIn("Unsupported resource", result["error"]["message"])

    def test_list_all_supports_audit_events_with_required_dates(self) -> None:
        client = Mock()
        manager = client.audit_events
        manager.last_page_info = {"has_next": False, "end_cursor": "cursor-1"}
        manager.last_cursors = None
        manager.list.return_value = [{"id": "evt-001", "activity": "login"}]

        with patch(
            "netskope_sdwan_mcp.tools.list_all.build_sdk_client",
            return_value=client,
        ):
            result = list_all(
                "audit_events",
                created_at_from="2026-04-16T00:00:00Z",
                created_at_to="2026-04-16T23:59:59Z",
                type="auth",
                subtype="sso",
                activity="login",
                first=25,
                limit=25,
            )

        manager.list.assert_called_once_with(
            created_at_from="2026-04-16T00:00:00Z",
            created_at_to="2026-04-16T23:59:59Z",
            type="auth",
            subtype="sso",
            activity="login",
            after=None,
            first=25,
            sort=None,
            filter=None,
        )
        self.assertEqual(result["items"], [{"id": "evt-001", "activity": "login"}])

    def test_list_all_requires_audit_event_dates(self) -> None:
        result = list_all("audit_events", created_at_from="2026-04-16T00:00:00Z")

        self.assertEqual(result["status"], "invalid_request")
        self.assertEqual(
            result["error"]["message"],
            "created_at_to is required for resource 'audit_events'",
        )

    def test_list_all_enforces_safe_default_limit(self) -> None:
        client = Mock()
        manager = client.address_groups

        def list_side_effect(*, after=None, first=None, sort=None, filter=None):
            self.assertEqual(first, 100)
            self.assertIsNone(after)
            manager.last_page_info = {"has_next": False, "end_cursor": "cursor-1"}
            manager.last_cursors = None
            return [{"id": "ag-001"}]

        manager.list.side_effect = list_side_effect

        with patch(
            "netskope_sdwan_mcp.tools.list_all.build_sdk_client",
            return_value=client,
        ):
            result = list_all("address_groups")

        self.assertEqual(result["limit"], DEFAULT_LIMIT)
        self.assertEqual(result["count"], 1)


if __name__ == "__main__":
    unittest.main()
