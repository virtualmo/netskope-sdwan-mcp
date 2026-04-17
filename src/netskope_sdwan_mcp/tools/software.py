"""Software MCP tool implementations backed by the SDK."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error
from ._pagination import build_list_kwargs


def list_software_versions(
    filter: str | None = None,
    after: str | None = None,
    first: int | None = None,
    sort: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """List software versions through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        software_versions = client.software.list_versions(
            **build_list_kwargs(
                filter=filter,
                after=after,
                first=first,
                sort=sort,
            ),
        )
        return [serialize_software_item(item) for item in software_versions]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def list_software_downloads(
    filter: str | None = None,
    after: str | None = None,
    first: int | None = None,
    sort: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """List software downloads through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        software_downloads = client.software.list_downloads(
            **build_list_kwargs(
                filter=filter,
                after=after,
                first=first,
                sort=sort,
            ),
        )
        return [serialize_software_item(item) for item in software_downloads]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def serialize_software_item(software_item: Any) -> dict[str, Any]:
    """Serialize an SDK software resource into a plain dictionary."""
    if is_dataclass(software_item):
        serialized = asdict(software_item)
        raw = serialized.get("raw")
        if isinstance(raw, dict):
            return raw
        return serialized

    if isinstance(software_item, dict):
        return dict(software_item)

    raw = getattr(software_item, "raw", None)
    if isinstance(raw, dict):
        return dict(raw)

    return {
        "id": getattr(software_item, "id", None),
        "name": getattr(software_item, "name", None),
    }


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    return serialize_tool_error(exc)
