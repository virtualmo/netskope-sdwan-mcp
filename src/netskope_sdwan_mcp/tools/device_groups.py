"""Device-group MCP tool implementations backed by the SDK."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error
from ._pagination import build_list_kwargs


def list_device_groups(
    filter: str | None = None,
    after: str | None = None,
    first: int | None = None,
    sort: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """List device groups through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        device_groups = client.device_groups.list(
            **build_list_kwargs(
                filter=filter,
                after=after,
                first=first,
                sort=sort,
            ),
        )
        return [serialize_device_group(item) for item in device_groups]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_device_group(id: str) -> dict[str, Any]:
    """Fetch one device group by ID through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        device_group = client.device_groups.get(id)
        return serialize_device_group(device_group)
    except Exception as exc:
        return _serialize_sdk_error(exc)


def serialize_device_group(device_group: Any) -> dict[str, Any]:
    """Serialize an SDK device-group resource into a plain dictionary."""
    if is_dataclass(device_group):
        serialized = asdict(device_group)
        raw = serialized.get("raw")
        if isinstance(raw, dict):
            return raw
        return serialized

    if isinstance(device_group, dict):
        return dict(device_group)

    raw = getattr(device_group, "raw", None)
    if isinstance(raw, dict):
        return dict(raw)

    return {
        "id": getattr(device_group, "id", None),
        "name": getattr(device_group, "name", None),
    }


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    return serialize_tool_error(exc)
