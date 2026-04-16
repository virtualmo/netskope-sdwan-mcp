"""NTP-config MCP tool implementations backed by the SDK."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error


def list_ntp_configs(filter: str | None = None) -> list[dict[str, Any]] | dict[str, Any]:
    """List NTP configs through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        ntp_configs = client.ntp_configs.list(filter=filter)
        return [serialize_ntp_config(item) for item in ntp_configs]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_ntp_config(id: str) -> dict[str, Any]:
    """Fetch one NTP config by ID through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        ntp_config = client.ntp_configs.get(id)
        return serialize_ntp_config(ntp_config)
    except Exception as exc:
        return _serialize_sdk_error(exc)


def serialize_ntp_config(ntp_config: Any) -> dict[str, Any]:
    """Serialize an SDK NTP-config resource into a plain dictionary."""
    if is_dataclass(ntp_config):
        serialized = asdict(ntp_config)
        raw = serialized.get("raw")
        if isinstance(raw, dict):
            return raw
        return serialized

    if isinstance(ntp_config, dict):
        return dict(ntp_config)

    raw = getattr(ntp_config, "raw", None)
    if isinstance(raw, dict):
        return dict(raw)

    return {
        "id": getattr(ntp_config, "id", None),
        "name": getattr(ntp_config, "name", None),
    }


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    return serialize_tool_error(exc)
