"""Address-group MCP tool implementations backed by the SDK."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error
from ._pagination import build_list_kwargs


def list_address_groups(
    filter: str | None = None,
    after: str | None = None,
    first: int | None = None,
    sort: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """List address groups through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        address_groups = client.address_groups.list(
            **build_list_kwargs(
                filter=filter,
                after=after,
                first=first,
                sort=sort,
            ),
        )
        return [serialize_address_group(item) for item in address_groups]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_address_group(id: str) -> dict[str, Any]:
    """Fetch one address group by ID through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        address_group = client.address_groups.get(id)
        return serialize_address_group(address_group)
    except Exception as exc:
        return _serialize_sdk_error(exc)


def list_address_group_objects(
    group_id: str,
    filter: str | None = None,
    after: str | None = None,
    first: int | None = None,
    sort: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """List address objects for one address group through the SDK."""
    try:
        client = build_sdk_client()
        address_objects = client.address_groups.list_address_objects(
            group_id,
            **build_list_kwargs(
                filter=filter,
                after=after,
                first=first,
                sort=sort,
            ),
        )
        return [serialize_address_group(item) for item in address_objects]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def serialize_address_group(address_group: Any) -> dict[str, Any]:
    """Serialize an SDK address-group resource into a plain dictionary."""
    if is_dataclass(address_group):
        serialized = asdict(address_group)
        raw = serialized.get("raw")
        if isinstance(raw, dict):
            return raw
        return serialized

    if isinstance(address_group, dict):
        return dict(address_group)

    raw = getattr(address_group, "raw", None)
    if isinstance(raw, dict):
        return dict(raw)

    return {
        "id": getattr(address_group, "id", None),
        "name": getattr(address_group, "name", None),
    }


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    return serialize_tool_error(exc)
