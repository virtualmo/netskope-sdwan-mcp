"""Overlay-tag MCP tool implementations backed by the SDK."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error
from ._pagination import build_list_kwargs


def list_overlay_tags(
    filter: str | None = None,
    after: str | None = None,
    first: int | None = None,
    sort: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """List overlay tags through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        overlay_tags = client.overlay_tags.list(
            **build_list_kwargs(
                filter=filter,
                after=after,
                first=first,
                sort=sort,
            ),
        )
        return [serialize_overlay_tag(item) for item in overlay_tags]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_overlay_tag(id: str) -> dict[str, Any]:
    """Fetch one overlay tag by ID through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        overlay_tag = client.overlay_tags.get(id)
        return serialize_overlay_tag(overlay_tag)
    except Exception as exc:
        return _serialize_sdk_error(exc)


def serialize_overlay_tag(overlay_tag: Any) -> dict[str, Any]:
    """Serialize an SDK overlay-tag resource into a plain dictionary."""
    if is_dataclass(overlay_tag):
        serialized = asdict(overlay_tag)
        raw = serialized.get("raw")
        if isinstance(raw, dict):
            return raw
        return serialized

    if isinstance(overlay_tag, dict):
        return dict(overlay_tag)

    raw = getattr(overlay_tag, "raw", None)
    if isinstance(raw, dict):
        return dict(raw)

    return {
        "id": getattr(overlay_tag, "id", None),
        "name": getattr(overlay_tag, "name", None),
    }


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    return serialize_tool_error(exc)
