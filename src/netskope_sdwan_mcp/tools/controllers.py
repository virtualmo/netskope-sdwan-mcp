"""Controller MCP tool implementations backed by the SDK."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error
from ._pagination import build_list_kwargs


def list_controllers(
    filter: str | None = None,
    after: str | None = None,
    first: int | None = None,
    sort: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """List controllers through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        controllers = client.controllers.list(
            **build_list_kwargs(
                filter=filter,
                after=after,
                first=first,
                sort=sort,
            ),
        )
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


def get_controller_operator_status(controller_id: str) -> dict[str, Any]:
    """Fetch controller operator status through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        return _serialize_controller_operator_status(
            client.controllers.get_operator_status(controller_id)
        )
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


def _serialize_controller_operator_status(payload: dict[str, Any]) -> dict[str, Any]:
    if isinstance(payload, dict):
        return dict(payload)
    return {
        "status": "error",
        "error": {
            "type": "TypeError",
            "message": "Controller operator status payload must be a JSON object.",
        },
    }


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    return serialize_tool_error(exc)
