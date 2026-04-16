"""Cloud-account MCP tool implementations backed by the SDK."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error


def list_cloud_accounts(filter: str | None = None) -> list[dict[str, Any]] | dict[str, Any]:
    """List cloud accounts through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        cloud_accounts = client.cloud_accounts.list(filter=filter)
        return [serialize_cloud_account(item) for item in cloud_accounts]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_cloud_account(id: str) -> dict[str, Any]:
    """Fetch one cloud account by ID through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        cloud_account = client.cloud_accounts.get(id)
        return serialize_cloud_account(cloud_account)
    except Exception as exc:
        return _serialize_sdk_error(exc)


def serialize_cloud_account(cloud_account: Any) -> dict[str, Any]:
    """Serialize an SDK cloud-account resource into a plain dictionary."""
    if is_dataclass(cloud_account):
        serialized = asdict(cloud_account)
        raw = serialized.get("raw")
        if isinstance(raw, dict):
            return raw
        return serialized

    if isinstance(cloud_account, dict):
        return dict(cloud_account)

    raw = getattr(cloud_account, "raw", None)
    if isinstance(raw, dict):
        return dict(raw)

    return {
        "id": getattr(cloud_account, "id", None),
        "name": getattr(cloud_account, "name", None),
    }


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    return serialize_tool_error(exc)
