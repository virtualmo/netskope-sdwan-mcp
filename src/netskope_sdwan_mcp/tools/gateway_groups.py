"""Gateway-group MCP tool implementations backed by the SDK."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error
from ._pagination import build_list_kwargs


def list_gateway_groups(
    filter: str | None = None,
    after: str | None = None,
    first: int | None = None,
    sort: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """List gateway groups through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        gateway_groups = client.gateway_groups.list(
            **build_list_kwargs(
                filter=filter,
                after=after,
                first=first,
                sort=sort,
            ),
        )
        return [serialize_gateway_group(item) for item in gateway_groups]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_gateway_group(id: str) -> dict[str, Any]:
    """Fetch one gateway group by ID through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        gateway_group = client.gateway_groups.get(id)
        return serialize_gateway_group(gateway_group)
    except Exception as exc:
        return _serialize_sdk_error(exc)


def serialize_gateway_group(gateway_group: Any) -> dict[str, Any]:
    """Serialize an SDK gateway-group resource into a plain dictionary."""
    if is_dataclass(gateway_group):
        serialized = asdict(gateway_group)
        raw = serialized.get("raw")
        if isinstance(raw, dict):
            return raw
        return serialized

    if isinstance(gateway_group, dict):
        return dict(gateway_group)

    raw = getattr(gateway_group, "raw", None)
    if isinstance(raw, dict):
        return dict(raw)

    return {
        "id": getattr(gateway_group, "id", None),
        "name": getattr(gateway_group, "name", None),
    }


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    return serialize_tool_error(exc)
