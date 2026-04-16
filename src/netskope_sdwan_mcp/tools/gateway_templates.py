"""Gateway-template MCP tool implementations backed by the SDK."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error


def list_gateway_templates(filter: str | None = None) -> list[dict[str, Any]] | dict[str, Any]:
    """List gateway templates through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        gateway_templates = client.gateway_templates.list(filter=filter)
        return [serialize_gateway_template(item) for item in gateway_templates]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_gateway_template(id: str) -> dict[str, Any]:
    """Fetch one gateway template by ID through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        gateway_template = client.gateway_templates.get(id)
        return serialize_gateway_template(gateway_template)
    except Exception as exc:
        return _serialize_sdk_error(exc)


def serialize_gateway_template(gateway_template: Any) -> dict[str, Any]:
    """Serialize an SDK gateway-template resource into a plain dictionary."""
    if is_dataclass(gateway_template):
        serialized = asdict(gateway_template)
        raw = serialized.get("raw")
        if isinstance(raw, dict):
            return raw
        return serialized

    if isinstance(gateway_template, dict):
        return dict(gateway_template)

    raw = getattr(gateway_template, "raw", None)
    if isinstance(raw, dict):
        return dict(raw)

    return {
        "id": getattr(gateway_template, "id", None),
        "name": getattr(gateway_template, "name", None),
    }


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    return serialize_tool_error(exc)
