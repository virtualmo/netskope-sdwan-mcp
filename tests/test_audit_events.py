"""Focused tests for audit-event MCP tool behavior."""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Optional
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.tools.audit_events import (
    list_audit_events,
    serialize_audit_event,
)


@dataclass
class FakeAuditEvent:
    id: str
    name: Optional[str] = None
    raw: Optional[dict] = None


class APIResponseError(Exception):
    """SDK-shaped generic API error used in tests."""


class AuditEventToolsTest(unittest.TestCase):
    def test_list_audit_events_success(self) -> None:
        client = Mock()
        client.audit_events.list.return_value = [
            FakeAuditEvent(
                id="evt-001",
                raw={"id": "evt-001", "activity": "login", "type": "auth"},
            ),
            FakeAuditEvent(
                id="evt-002",
                raw={"id": "evt-002", "activity": "logout", "type": "auth"},
            ),
        ]

        with patch(
            "netskope_sdwan_mcp.tools.audit_events.build_sdk_client",
            return_value=client,
        ):
            result = list_audit_events(
                created_at_from="2026-04-16T00:00:00Z",
                created_at_to="2026-04-16T23:59:59Z",
                type="auth",
            )

        client.audit_events.list.assert_called_once_with(
            created_at_from="2026-04-16T00:00:00Z",
            created_at_to="2026-04-16T23:59:59Z",
            type="auth",
            subtype=None,
            activity=None,
            after=None,
            first=None,
            sort=None,
            filter=None,
        )
        self.assertEqual(
            result,
            [
                {"id": "evt-001", "activity": "login", "type": "auth"},
                {"id": "evt-002", "activity": "logout", "type": "auth"},
            ],
        )

    def test_list_audit_events_missing_required_argument_path(self) -> None:
        result = list_audit_events(
            created_at_from="",
            created_at_to="2026-04-16T23:59:59Z",
        )

        self.assertEqual(result["status"], "invalid_request")
        self.assertEqual(result["error"]["type"], "ValueError")
        self.assertEqual(result["error"]["message"], "created_at_from is required")

    def test_list_audit_events_sdk_error_path(self) -> None:
        client = Mock()
        client.audit_events.list.side_effect = APIResponseError("upstream failure")

        with patch(
            "netskope_sdwan_mcp.tools.audit_events.build_sdk_client",
            return_value=client,
        ):
            result = list_audit_events(
                created_at_from="2026-04-16T00:00:00Z",
                created_at_to="2026-04-16T23:59:59Z",
            )

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_serialize_audit_event_supports_sdk_objects(self) -> None:
        audit_event = FakeAuditEvent(
            id="evt-123",
            raw={"id": "evt-123", "activity": "login", "request_id": "req-9"},
        )

        self.assertEqual(
            serialize_audit_event(audit_event),
            {"id": "evt-123", "activity": "login", "request_id": "req-9"},
        )
