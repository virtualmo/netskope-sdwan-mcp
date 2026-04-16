"""Gateway MCP tool implementations backed by the SDK."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error


def list_gateways(filter: str | None = None) -> list[dict[str, Any]] | dict[str, Any]:
    """List gateways through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        gateways = client.gateways.list(filter=filter)
        return [serialize_gateway(item) for item in gateways]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_gateway(id: str) -> dict[str, Any]:
    """Fetch one gateway by ID through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        gateway = client.gateways.get(id)
        return serialize_gateway(gateway)
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_gateway_operational_snapshot(
    id: str,
    child_tenant_id: str | None = None,
) -> dict[str, Any]:
    """Fetch gateway details and latest operational snapshots for one gateway."""
    try:
        client = build_sdk_client()
        gateway = client.gateways.get(id)
        interfaces_latest = client.v1.monitoring.get_interfaces_latest(
            id,
            child_tenant_id=child_tenant_id,
        )
        paths_latest = client.v1.monitoring.get_paths_latest(
            id,
            child_tenant_id=child_tenant_id,
        )
        routes_latest = client.v1.monitoring.get_routes_latest(
            id,
            child_tenant_id=child_tenant_id,
        )
        return {
            "gateway": serialize_gateway(gateway),
            "interfaces_latest": _serialize_monitoring_payload(interfaces_latest),
            "paths_latest": _serialize_monitoring_payload(paths_latest),
            "routes_latest": _serialize_monitoring_payload(routes_latest),
        }
    except Exception as exc:
        return _serialize_sdk_error(exc)


def serialize_gateway(gateway: Any) -> dict[str, Any]:
    """Serialize an SDK gateway model into a plain dictionary."""
    if is_dataclass(gateway):
        return asdict(gateway)

    if isinstance(gateway, dict):
        return {
            "id": gateway.get("id"),
            "name": gateway.get("name"),
            "managed": gateway.get("managed"),
            "is_activated": gateway.get("is_activated"),
            "overlay_id": gateway.get("overlay_id"),
            "created_at": gateway.get("created_at"),
            "modified_at": gateway.get("modified_at"),
            "device_config_raw": gateway.get("device_config_raw"),
        }

    return {
        "id": getattr(gateway, "id", None),
        "name": getattr(gateway, "name", None),
        "managed": getattr(gateway, "managed", None),
        "is_activated": getattr(gateway, "is_activated", None),
        "overlay_id": getattr(gateway, "overlay_id", None),
        "created_at": getattr(gateway, "created_at", None),
        "modified_at": getattr(gateway, "modified_at", None),
        "device_config_raw": getattr(gateway, "device_config_raw", None),
    }


def _serialize_monitoring_payload(
    payload: list[dict[str, Any]] | dict[str, Any],
) -> list[dict[str, Any]] | dict[str, Any]:
    if isinstance(payload, dict):
        return dict(payload)
    if isinstance(payload, list):
        return [dict(item) for item in payload]
    return payload


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    return serialize_tool_error(exc)
