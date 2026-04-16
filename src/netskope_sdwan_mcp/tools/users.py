"""User MCP tool implementations backed by the SDK."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error


def list_users(filter: str | None = None) -> list[dict[str, Any]] | dict[str, Any]:
    """List users through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        users = client.users.list(filter=filter)
        return [serialize_user(item) for item in users]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_user(id: str) -> dict[str, Any]:
    """Fetch one user by ID through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        user = client.users.get(id)
        return serialize_user(user)
    except Exception as exc:
        return _serialize_sdk_error(exc)


def serialize_user(user: Any) -> dict[str, Any]:
    """Serialize an SDK user resource into a plain dictionary."""
    if is_dataclass(user):
        serialized = asdict(user)
        raw = serialized.get("raw")
        if isinstance(raw, dict):
            return raw
        return serialized

    if isinstance(user, dict):
        return dict(user)

    raw = getattr(user, "raw", None)
    if isinstance(raw, dict):
        return dict(raw)

    return {
        "id": getattr(user, "id", None),
        "name": getattr(user, "name", None),
    }


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    return serialize_tool_error(exc)
