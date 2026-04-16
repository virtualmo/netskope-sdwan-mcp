"""Client-template MCP tool implementations backed by the SDK."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error


def list_client_templates(filter: str | None = None) -> list[dict[str, Any]] | dict[str, Any]:
    """List client templates through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        client_templates = client.client_templates.list(filter=filter)
        return [serialize_client_template(item) for item in client_templates]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_client_template(id: str) -> dict[str, Any]:
    """Fetch one client template by ID through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        client_template = client.client_templates.get(id)
        return serialize_client_template(client_template)
    except Exception as exc:
        return _serialize_sdk_error(exc)


def serialize_client_template(client_template: Any) -> dict[str, Any]:
    """Serialize an SDK client-template resource into a plain dictionary."""
    if is_dataclass(client_template):
        serialized = asdict(client_template)
        raw = serialized.get("raw")
        if isinstance(raw, dict):
            return raw
        return serialized

    if isinstance(client_template, dict):
        return dict(client_template)

    raw = getattr(client_template, "raw", None)
    if isinstance(raw, dict):
        return dict(raw)

    return {
        "id": getattr(client_template, "id", None),
        "name": getattr(client_template, "name", None),
    }


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    return serialize_tool_error(exc)
