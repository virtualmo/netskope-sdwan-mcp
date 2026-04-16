"""Radius-server MCP tool implementations backed by the SDK."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error


def list_radius_servers(filter: str | None = None) -> list[dict[str, Any]] | dict[str, Any]:
    """List radius servers through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        radius_servers = client.radius_servers.list(filter=filter)
        return [serialize_radius_server(item) for item in radius_servers]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_radius_server(id: str) -> dict[str, Any]:
    """Fetch one radius server by ID through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        radius_server = client.radius_servers.get(id)
        return serialize_radius_server(radius_server)
    except Exception as exc:
        return _serialize_sdk_error(exc)


def serialize_radius_server(radius_server: Any) -> dict[str, Any]:
    """Serialize an SDK radius-server resource into a plain dictionary."""
    if is_dataclass(radius_server):
        serialized = asdict(radius_server)
        raw = serialized.get("raw")
        if isinstance(raw, dict):
            return raw
        return serialized

    if isinstance(radius_server, dict):
        return dict(radius_server)

    raw = getattr(radius_server, "raw", None)
    if isinstance(raw, dict):
        return dict(raw)

    return {
        "id": getattr(radius_server, "id", None),
        "name": getattr(radius_server, "name", None),
    }


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    return serialize_tool_error(exc)
