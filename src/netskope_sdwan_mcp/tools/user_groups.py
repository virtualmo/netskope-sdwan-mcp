"""User-group MCP tool implementations backed by the SDK."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error
from ._pagination import build_list_kwargs


def list_user_groups(
    filter: str | None = None,
    after: str | None = None,
    first: int | None = None,
    sort: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """List user groups through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        user_groups = client.user_groups.list(
            **build_list_kwargs(
                filter=filter,
                after=after,
                first=first,
                sort=sort,
            ),
        )
        return [serialize_user_group(item) for item in user_groups]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_user_group(id: str) -> dict[str, Any]:
    """Fetch one user group by ID through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        user_group = client.user_groups.get(id)
        return serialize_user_group(user_group)
    except Exception as exc:
        return _serialize_sdk_error(exc)


def serialize_user_group(user_group: Any) -> dict[str, Any]:
    """Serialize an SDK user-group resource into a plain dictionary."""
    if is_dataclass(user_group):
        serialized = asdict(user_group)
        raw = serialized.get("raw")
        if isinstance(raw, dict):
            return raw
        return serialized

    if isinstance(user_group, dict):
        return dict(user_group)

    raw = getattr(user_group, "raw", None)
    if isinstance(raw, dict):
        return dict(raw)

    return {
        "id": getattr(user_group, "id", None),
        "name": getattr(user_group, "name", None),
    }


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    return serialize_tool_error(exc)
