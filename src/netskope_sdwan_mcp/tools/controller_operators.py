"""Controller-operator MCP tool implementations backed by the SDK."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error


def list_controller_operators(filter: str | None = None) -> list[dict[str, Any]] | dict[str, Any]:
    """List controller operators through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        controller_operators = client.controller_operators.list(filter=filter)
        return [serialize_controller_operator(item) for item in controller_operators]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_controller_operator(id: str) -> dict[str, Any]:
    """Fetch one controller operator by ID through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        controller_operator = client.controller_operators.get(id)
        return serialize_controller_operator(controller_operator)
    except Exception as exc:
        return _serialize_sdk_error(exc)


def serialize_controller_operator(controller_operator: Any) -> dict[str, Any]:
    """Serialize an SDK controller-operator resource into a plain dictionary."""
    if is_dataclass(controller_operator):
        serialized = asdict(controller_operator)
        raw = serialized.get("raw")
        if isinstance(raw, dict):
            return raw
        return serialized

    if isinstance(controller_operator, dict):
        return dict(controller_operator)

    raw = getattr(controller_operator, "raw", None)
    if isinstance(raw, dict):
        return dict(raw)

    return {
        "id": getattr(controller_operator, "id", None),
        "name": getattr(controller_operator, "name", None),
    }


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    return serialize_tool_error(exc)
