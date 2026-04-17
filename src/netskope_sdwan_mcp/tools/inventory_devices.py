"""Inventory-device MCP tool implementations backed by the SDK."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error
from ._pagination import build_list_kwargs


def list_inventory_devices(
    filter: str | None = None,
    after: str | None = None,
    first: int | None = None,
    sort: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """List inventory devices through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        inventory_devices = client.inventory_devices.list(
            **build_list_kwargs(
                filter=filter,
                after=after,
                first=first,
                sort=sort,
            ),
        )
        return [serialize_inventory_device(item) for item in inventory_devices]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def serialize_inventory_device(inventory_device: Any) -> dict[str, Any]:
    """Serialize an SDK inventory-device resource into a plain dictionary."""
    if is_dataclass(inventory_device):
        serialized = asdict(inventory_device)
        raw = serialized.get("raw")
        if isinstance(raw, dict):
            return raw
        return serialized

    if isinstance(inventory_device, dict):
        return dict(inventory_device)

    raw = getattr(inventory_device, "raw", None)
    if isinstance(raw, dict):
        return dict(raw)

    return {
        "id": getattr(inventory_device, "id", None),
        "name": getattr(inventory_device, "name", None),
    }


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    return serialize_tool_error(exc)
