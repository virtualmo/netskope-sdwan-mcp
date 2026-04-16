"""Controller MCP tool implementations backed by the SDK."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error


def list_controllers(filter: str | None = None) -> list[dict[str, Any]] | dict[str, Any]:
    """List controllers through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        controllers = client.controllers.list(filter=filter)
        return [serialize_controller(item) for item in controllers]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_controller(id: str) -> dict[str, Any]:
    """Fetch one controller by ID through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        controller = client.controllers.get(id)
        return serialize_controller(controller)
    except Exception as exc:
        return _serialize_sdk_error(exc)


def serialize_controller(controller: Any) -> dict[str, Any]:
    """Serialize an SDK controller resource into a plain dictionary."""
    if is_dataclass(controller):
        serialized = asdict(controller)
        raw = serialized.get("raw")
        if isinstance(raw, dict):
            return raw
        return serialized

    if isinstance(controller, dict):
        return dict(controller)

    raw = getattr(controller, "raw", None)
    if isinstance(raw, dict):
        return dict(raw)

    return {
        "id": getattr(controller, "id", None),
        "name": getattr(controller, "name", None),
    }


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    return serialize_tool_error(exc)
