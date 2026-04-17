"""Client MCP tool implementations backed by the SDK."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error
from ._pagination import build_list_kwargs


def list_clients(
    filter: str | None = None,
    after: str | None = None,
    first: int | None = None,
    sort: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """List clients through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        clients = client.clients.list(
            **build_list_kwargs(
                filter=filter,
                after=after,
                first=first,
                sort=sort,
            ),
        )
        return [serialize_client(item) for item in clients]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_client(id: str) -> dict[str, Any]:
    """Fetch one client by ID through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        client_record = client.clients.get(id)
        return serialize_client(client_record)
    except Exception as exc:
        return _serialize_sdk_error(exc)


def serialize_client(client_record: Any) -> dict[str, Any]:
    """Serialize an SDK client resource into a plain dictionary."""
    if is_dataclass(client_record):
        serialized = asdict(client_record)
        raw = serialized.get("raw")
        if isinstance(raw, dict):
            return raw
        return serialized

    if isinstance(client_record, dict):
        return dict(client_record)

    raw = getattr(client_record, "raw", None)
    if isinstance(raw, dict):
        return dict(raw)

    return {
        "id": getattr(client_record, "id", None),
        "name": getattr(client_record, "name", None),
    }


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    return serialize_tool_error(exc)
