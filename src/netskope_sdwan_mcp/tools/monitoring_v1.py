"""V1 monitoring MCP tool implementations backed by the SDK."""

from __future__ import annotations

from typing import Any

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error


def get_interfaces_latest(
    gateway_id: str,
    child_tenant_id: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Fetch the latest interface snapshot for one gateway."""
    try:
        client = build_sdk_client()
        return _serialize_monitoring_payload(
            client.v1.monitoring.get_interfaces_latest(
                gateway_id,
                child_tenant_id=child_tenant_id,
            )
        )
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_paths_latest(
    gateway_id: str,
    child_tenant_id: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Fetch the latest path snapshot for one gateway."""
    try:
        client = build_sdk_client()
        return _serialize_monitoring_payload(
            client.v1.monitoring.get_paths_latest(
                gateway_id,
                child_tenant_id=child_tenant_id,
            )
        )
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_routes_latest(
    gateway_id: str,
    child_tenant_id: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Fetch the latest route snapshot for one gateway."""
    try:
        client = build_sdk_client()
        return _serialize_monitoring_payload(
            client.v1.monitoring.get_routes_latest(
                gateway_id,
                child_tenant_id=child_tenant_id,
            )
        )
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_device_flows_totals(
    gateway_id: str,
    ip: str,
    start_datetime: str,
    end_datetime: str,
    child_tenant_id: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Fetch device flow totals for one gateway."""
    try:
        client = build_sdk_client()
        return _serialize_monitoring_payload(
            client.v1.monitoring.get_device_flows_totals(
                gateway_id,
                child_tenant_id=child_tenant_id,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                ip=ip,
            )
        )
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_devices_totals(
    gateway_id: str,
    start_datetime: str,
    end_datetime: str,
    child_tenant_id: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Fetch device totals for one gateway."""
    try:
        client = build_sdk_client()
        return _serialize_monitoring_payload(
            client.v1.monitoring.get_devices_totals(
                gateway_id,
                child_tenant_id=child_tenant_id,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
            )
        )
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_system_load(
    gateway_id: str,
    child_tenant_id: str | None = None,
    start_datetime: str | None = None,
    end_datetime: str | None = None,
    time_slots: int | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Fetch system load history for one gateway."""
    try:
        client = build_sdk_client()
        return _serialize_monitoring_payload(
            client.v1.monitoring.get_system_load(
                gateway_id,
                child_tenant_id=child_tenant_id,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                time_slots=time_slots,
            )
        )
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_system_lte(
    gateway_id: str,
    start_datetime: str,
    end_datetime: str,
    child_tenant_id: str | None = None,
    time_slots: int | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Fetch system LTE history for one gateway."""
    try:
        client = build_sdk_client()
        return _serialize_monitoring_payload(
            client.v1.monitoring.get_system_lte(
                gateway_id,
                child_tenant_id=child_tenant_id,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                time_slots=time_slots,
            )
        )
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_system_memory(
    gateway_id: str,
    start_datetime: str,
    end_datetime: str,
    child_tenant_id: str | None = None,
    time_slots: int | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Fetch system memory history for one gateway."""
    try:
        client = build_sdk_client()
        return _serialize_monitoring_payload(
            client.v1.monitoring.get_system_memory(
                gateway_id,
                child_tenant_id=child_tenant_id,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                time_slots=time_slots,
            )
        )
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_system_uptime(
    gateway_id: str,
    start_datetime: str,
    end_datetime: str,
    child_tenant_id: str | None = None,
    time_slots: int | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Fetch system uptime history for one gateway."""
    try:
        client = build_sdk_client()
        return _serialize_monitoring_payload(
            client.v1.monitoring.get_system_uptime(
                gateway_id,
                child_tenant_id=child_tenant_id,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                time_slots=time_slots,
            )
        )
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_system_wifi(
    gateway_id: str,
    start_datetime: str,
    end_datetime: str,
    child_tenant_id: str | None = None,
    time_slots: int | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Fetch system Wi-Fi history for one gateway."""
    try:
        client = build_sdk_client()
        return _serialize_monitoring_payload(
            client.v1.monitoring.get_system_wifi(
                gateway_id,
                child_tenant_id=child_tenant_id,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                time_slots=time_slots,
            )
        )
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_paths_links_totals(
    gateway_id: str,
    child_tenant_id: str | None = None,
    start_datetime: str | None = None,
    end_datetime: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Fetch WAN path/link totals for one gateway."""
    try:
        client = build_sdk_client()
        return _serialize_monitoring_payload(
            client.v1.monitoring.get_paths_links_totals(
                gateway_id,
                child_tenant_id=child_tenant_id,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
            )
        )
    except Exception as exc:
        return _serialize_sdk_error(exc)


def _serialize_monitoring_payload(
    payload: list[dict[str, Any]] | dict[str, Any],
) -> list[dict[str, Any]] | dict[str, Any]:
    if isinstance(payload, dict):
        return dict(payload)
    if isinstance(payload, list):
        return [dict(item) for item in payload]
    return {
        "status": "error",
        "error": {
            "type": "TypeError",
            "message": "Monitoring payload must be a JSON object or array of objects.",
        },
    }


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    return serialize_tool_error(exc)
