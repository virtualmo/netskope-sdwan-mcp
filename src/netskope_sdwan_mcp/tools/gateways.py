"""Gateway MCP tool implementations backed by the SDK."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error
from ._pagination import build_list_kwargs


def list_gateways(
    filter: str | None = None,
    after: str | None = None,
    first: int | None = None,
    sort: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """List gateways through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        gateways = client.gateways.list(
            **build_list_kwargs(
                filter=filter,
                after=after,
                first=first,
                sort=sort,
            ),
        )
        return [serialize_gateway(item) for item in gateways]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def list_gateways_with_status() -> list[dict[str, Any]] | dict[str, Any]:
    """List gateways with a compact composite status-oriented summary."""
    try:
        client = build_sdk_client()
        gateways = client.gateways.list()
        return [_build_gateway_status_summary(client, gateway) for gateway in gateways]
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


def get_gateway_telemetry_overview(gateway_id: str) -> dict[str, Any]:
    """Fetch gateway telemetry overview through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        return _serialize_gateway_telemetry_overview(
            client.gateways.get_telemetry_overview(gateway_id)
        )
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_gateway_status(gateway_id: str) -> dict[str, Any]:
    """Fetch a small composite gateway status view from gateway and telemetry data."""
    try:
        client = build_sdk_client()
        gateway = client.gateways.get(gateway_id)
        telemetry = _serialize_gateway_telemetry_overview(
            client.gateways.get_telemetry_overview(gateway_id)
        )
        return _build_gateway_status(gateway, telemetry)
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


def _build_gateway_status(gateway: Any, telemetry: dict[str, Any]) -> dict[str, Any]:
    status_v2 = telemetry.get("status_v2")
    if not isinstance(status_v2, dict):
        status_v2 = {}

    serialized_gateway = serialize_gateway(gateway)
    return {
        "gateway_id": serialized_gateway.get("id"),
        "name": serialized_gateway.get("name"),
        "is_activated": serialized_gateway.get("is_activated"),
        "status": status_v2.get("status"),
        "conditions": status_v2.get("conditions"),
        "software_version": telemetry.get("software_version"),
        "software_upgraded_at": telemetry.get("software_upgraded_at"),
        "links_avg_score": telemetry.get("links_avg_score"),
    }


def _build_gateway_status_summary(client: Any, gateway: Any) -> dict[str, Any]:
    telemetry = _load_gateway_telemetry_overview_or_empty(client, gateway)
    status_v2 = telemetry.get("status_v2")
    if not isinstance(status_v2, dict):
        status_v2 = {}

    gateway_id = _get_gateway_field(gateway, "id")
    return {
        "gateway_id": gateway_id,
        "name": _get_gateway_field(gateway, "name"),
        "is_activated": _get_gateway_field(gateway, "is_activated"),
        "status": status_v2.get("status"),
        "conditions": status_v2.get("conditions"),
        "software_version": telemetry.get("software_version"),
        "software_upgraded_at": telemetry.get("software_upgraded_at"),
        "links_avg_score": telemetry.get("links_avg_score"),
        "city": _get_gateway_field(gateway, "city"),
        "country": _get_gateway_field(gateway, "country"),
        "role": _get_gateway_field(gateway, "role"),
    }


def _load_gateway_telemetry_overview_or_empty(client: Any, gateway: Any) -> dict[str, Any]:
    gateway_id = _get_gateway_field(gateway, "id")
    if gateway_id is None:
        return {}

    try:
        return _serialize_gateway_telemetry_overview(
            client.gateways.get_telemetry_overview(gateway_id)
        )
    except Exception:
        return {}


def _get_gateway_field(gateway: Any, field_name: str) -> Any:
    if isinstance(gateway, dict):
        return gateway.get(field_name)
    return getattr(gateway, field_name, None)


def _serialize_gateway_telemetry_overview(payload: dict[str, Any]) -> dict[str, Any]:
    if isinstance(payload, dict):
        return dict(payload)
    return {
        "status": "error",
        "error": {
            "type": "TypeError",
            "message": "Gateway telemetry overview payload must be a JSON object.",
        },
    }


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    return serialize_tool_error(exc)
