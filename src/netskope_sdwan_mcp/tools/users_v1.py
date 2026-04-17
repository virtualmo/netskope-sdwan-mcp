"""V1 user MCP tool implementations backed by the SDK."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error


def get_v1_user_groups(user_id: str) -> list[dict[str, Any]] | dict[str, Any]:
    """Fetch v1 groups for one user through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        groups = client.v1.users.get_groups(user_id)
        return [serialize_v1_user_group(group) for group in groups]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def serialize_v1_user_group(group: Any) -> dict[str, Any]:
    """Serialize an SDK v1 user-group resource into a plain dictionary."""
    if is_dataclass(group):
        serialized = asdict(group)
        raw = serialized.get("raw")
        if isinstance(raw, dict):
            return raw
        return serialized

    if isinstance(group, dict):
        return dict(group)

    raw = getattr(group, "raw", None)
    if isinstance(raw, dict):
        return dict(raw)

    return {
        "id": getattr(group, "id", None),
        "name": getattr(group, "name", None),
    }


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    return serialize_tool_error(exc)
