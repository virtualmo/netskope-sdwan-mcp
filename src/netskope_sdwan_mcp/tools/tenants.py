"""Tenant MCP tool implementations backed by the SDK."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from ..client_factory import build_sdk_client


def list_tenants(filter: str | None = None) -> list[dict[str, Any]] | dict[str, Any]:
    """List tenants through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        tenants = client.tenants.list(filter=filter)
        return [serialize_tenant(item) for item in tenants]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_tenant(id: str) -> dict[str, Any]:
    """Fetch one tenant by ID through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        tenant = client.tenants.get(id)
        return serialize_tenant(tenant)
    except Exception as exc:
        return _serialize_sdk_error(exc)


def serialize_tenant(tenant: Any) -> dict[str, Any]:
    """Serialize an SDK tenant resource into a plain dictionary."""
    if is_dataclass(tenant):
        serialized = asdict(tenant)
        raw = serialized.get("raw")
        if isinstance(raw, dict):
            return raw
        return serialized

    if isinstance(tenant, dict):
        return dict(tenant)

    raw = getattr(tenant, "raw", None)
    if isinstance(raw, dict):
        return dict(raw)

    return {
        "id": getattr(tenant, "id", None),
        "name": getattr(tenant, "name", None),
    }


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    error_type = exc.__class__.__name__
    status = "error"
    if error_type == "NotFoundError":
        status = "not_found"

    return {
        "status": status,
        "error": {
            "type": error_type,
            "message": str(exc),
        },
    }
