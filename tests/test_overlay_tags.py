"""Focused tests for overlay-tag MCP tool behavior."""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Optional
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netskope_sdwan_mcp.tools.overlay_tags import (
    get_overlay_tag,
    list_overlay_tags,
    serialize_overlay_tag,
)


@dataclass
class FakeOverlayTag:
    id: str
    name: Optional[str] = None
    raw: Optional[dict] = None


class NotFoundError(Exception):
    """SDK-shaped not found error used in tests."""


class APIResponseError(Exception):
    """SDK-shaped generic API error used in tests."""


class OverlayTagToolsTest(unittest.TestCase):
    def test_list_overlay_tags_success(self) -> None:
        client = Mock()
        client.overlay_tags.list.return_value = [
            FakeOverlayTag(
                id="tag-001",
                name="Blue Overlay",
                raw={"id": "tag-001", "name": "Blue Overlay", "color": "blue"},
            ),
            FakeOverlayTag(
                id="tag-002",
                name="Green Overlay",
                raw={"id": "tag-002", "name": "Green Overlay"},
            ),
        ]

        with patch(
            "netskope_sdwan_mcp.tools.overlay_tags.build_sdk_client",
            return_value=client,
        ):
            result = list_overlay_tags(filter="name: Blue")

        client.overlay_tags.list.assert_called_once_with(filter="name: Blue")
        self.assertEqual(
            result,
            [
                {"id": "tag-001", "name": "Blue Overlay", "color": "blue"},
                {"id": "tag-002", "name": "Green Overlay"},
            ],
        )

    def test_get_overlay_tag_success(self) -> None:
        client = Mock()
        client.overlay_tags.get.return_value = FakeOverlayTag(
            id="tag-001",
            name="Blue Overlay",
            raw={"id": "tag-001", "name": "Blue Overlay", "priority": 10},
        )

        with patch(
            "netskope_sdwan_mcp.tools.overlay_tags.build_sdk_client",
            return_value=client,
        ):
            result = get_overlay_tag("tag-001")

        client.overlay_tags.get.assert_called_once_with("tag-001")
        self.assertEqual(result["id"], "tag-001")
        self.assertEqual(result["name"], "Blue Overlay")
        self.assertEqual(result["priority"], 10)

    def test_get_overlay_tag_not_found_path(self) -> None:
        client = Mock()
        client.overlay_tags.get.side_effect = NotFoundError("overlay tag not found")

        with patch(
            "netskope_sdwan_mcp.tools.overlay_tags.build_sdk_client",
            return_value=client,
        ):
            result = get_overlay_tag("missing-id")

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["error"]["type"], "NotFoundError")
        self.assertEqual(result["error"]["message"], "overlay tag not found")

    def test_list_overlay_tags_sdk_error_path(self) -> None:
        client = Mock()
        client.overlay_tags.list.side_effect = APIResponseError("upstream failure")

        with patch(
            "netskope_sdwan_mcp.tools.overlay_tags.build_sdk_client",
            return_value=client,
        ):
            result = list_overlay_tags()

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["type"], "InternalError")
        self.assertEqual(result["error"]["message"], "Unexpected error while processing request.")

    def test_serialize_overlay_tag_supports_sdk_objects(self) -> None:
        overlay_tag = FakeOverlayTag(
            id="tag-123",
            name="Red Overlay",
            raw={"id": "tag-123", "name": "Red Overlay", "account_id": "acct-9"},
        )

        self.assertEqual(
            serialize_overlay_tag(overlay_tag),
            {"id": "tag-123", "name": "Red Overlay", "account_id": "acct-9"},
        )


if __name__ == "__main__":
    unittest.main()
