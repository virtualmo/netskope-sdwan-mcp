"""Focused tests for segment MCP tool behavior."""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Optional
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.tools.segments import (
    get_segment,
    list_segments,
    serialize_segment,
)


@dataclass
class FakeSegment:
    id: str
    name: Optional[str] = None
    raw: Optional[dict] = None


class NotFoundError(Exception):
    """SDK-shaped not found error used in tests."""


class APIResponseError(Exception):
    """SDK-shaped generic API error used in tests."""


class SegmentToolsTest(unittest.TestCase):
    def test_list_segments_success(self) -> None:
        client = Mock()
        client.segments.list.return_value = [
            FakeSegment(
                id="seg-001",
                name="Corporate",
                raw={"id": "seg-001", "name": "Corporate", "priority": 1},
            ),
            FakeSegment(
                id="seg-002",
                name="Guest",
                raw={"id": "seg-002", "name": "Guest"},
            ),
        ]

        with patch(
            "netskope_sdwan_mcp.tools.segments.build_sdk_client",
            return_value=client,
        ):
            result = list_segments(filter="name: Corporate")

        client.segments.list.assert_called_once_with(filter="name: Corporate")
        self.assertEqual(
            result,
            [
                {"id": "seg-001", "name": "Corporate", "priority": 1},
                {"id": "seg-002", "name": "Guest"},
            ],
        )

    def test_get_segment_success(self) -> None:
        client = Mock()
        client.segments.get.return_value = FakeSegment(
            id="seg-001",
            name="Corporate",
            raw={"id": "seg-001", "name": "Corporate", "scope": "global"},
        )

        with patch(
            "netskope_sdwan_mcp.tools.segments.build_sdk_client",
            return_value=client,
        ):
            result = get_segment("seg-001")

        client.segments.get.assert_called_once_with("seg-001")
        self.assertEqual(result["id"], "seg-001")
        self.assertEqual(result["name"], "Corporate")
        self.assertEqual(result["scope"], "global")

    def test_get_segment_not_found_path(self) -> None:
        client = Mock()
        client.segments.get.side_effect = NotFoundError("segment not found")

        with patch(
            "netskope_sdwan_mcp.tools.segments.build_sdk_client",
            return_value=client,
        ):
            result = get_segment("missing-id")

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["error"]["type"], "NotFoundError")
        self.assertEqual(result["error"]["message"], "segment not found")

    def test_list_segments_sdk_error_path(self) -> None:
        client = Mock()
        client.segments.list.side_effect = APIResponseError("upstream failure")

        with patch(
            "netskope_sdwan_mcp.tools.segments.build_sdk_client",
            return_value=client,
        ):
            result = list_segments()

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_serialize_segment_supports_sdk_objects(self) -> None:
        segment = FakeSegment(
            id="seg-123",
            name="Readers",
            raw={"id": "seg-123", "name": "Readers", "account_id": "acct-9"},
        )

        self.assertEqual(
            serialize_segment(segment),
            {"id": "seg-123", "name": "Readers", "account_id": "acct-9"},
        )
