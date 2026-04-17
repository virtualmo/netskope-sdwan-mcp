"""Segment MCP tool implementations backed by the SDK."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error
from ._pagination import build_list_kwargs


def list_segments(
    filter: str | None = None,
    after: str | None = None,
    first: int | None = None,
    sort: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """List segments through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        segments = client.segments.list(
            **build_list_kwargs(
                filter=filter,
                after=after,
                first=first,
                sort=sort,
            ),
        )
        return [serialize_segment(item) for item in segments]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_segment(id: str) -> dict[str, Any]:
    """Fetch one segment by ID through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        segment = client.segments.get(id)
        return serialize_segment(segment)
    except Exception as exc:
        return _serialize_sdk_error(exc)


def serialize_segment(segment: Any) -> dict[str, Any]:
    """Serialize an SDK segment resource into a plain dictionary."""
    if is_dataclass(segment):
        serialized = asdict(segment)
        raw = serialized.get("raw")
        if isinstance(raw, dict):
            return raw
        return serialized

    if isinstance(segment, dict):
        return dict(segment)

    raw = getattr(segment, "raw", None)
    if isinstance(raw, dict):
        return dict(raw)

    return {
        "id": getattr(segment, "id", None),
        "name": getattr(segment, "name", None),
    }


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    return serialize_tool_error(exc)
