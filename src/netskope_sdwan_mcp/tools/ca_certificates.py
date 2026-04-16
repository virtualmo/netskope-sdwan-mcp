"""CA-certificate MCP tool implementations backed by the SDK."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error


def list_ca_certificates(filter: str | None = None) -> list[dict[str, Any]] | dict[str, Any]:
    """List CA certificates through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        ca_certificates = client.ca_certificates.list(filter=filter)
        return [serialize_ca_certificate(item) for item in ca_certificates]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_ca_certificate(id: str) -> dict[str, Any]:
    """Fetch one CA certificate by ID through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        ca_certificate = client.ca_certificates.get(id)
        return serialize_ca_certificate(ca_certificate)
    except Exception as exc:
        return _serialize_sdk_error(exc)


def serialize_ca_certificate(ca_certificate: Any) -> dict[str, Any]:
    """Serialize an SDK CA-certificate resource into a plain dictionary."""
    if is_dataclass(ca_certificate):
        serialized = asdict(ca_certificate)
        raw = serialized.get("raw")
        if isinstance(raw, dict):
            return raw
        return serialized

    if isinstance(ca_certificate, dict):
        return dict(ca_certificate)

    raw = getattr(ca_certificate, "raw", None)
    if isinstance(raw, dict):
        return dict(raw)

    return {
        "id": getattr(ca_certificate, "id", None),
        "name": getattr(ca_certificate, "name", None),
    }


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    return serialize_tool_error(exc)
