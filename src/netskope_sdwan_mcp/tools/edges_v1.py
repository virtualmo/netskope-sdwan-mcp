"""V1 edge MCP tool implementations backed by the SDK."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error


def list_edges() -> list[dict[str, Any]] | dict[str, Any]:
    """List v1 edges through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        edges = client.v1.edges.list()
        return [serialize_edge(edge) for edge in edges]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_edge(edge_id: str) -> dict[str, Any]:
    """Fetch one v1 edge by ID through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        edge = client.v1.edges.get(edge_id)
        return serialize_edge(edge)
    except Exception as exc:
        return _serialize_sdk_error(exc)


def list_edge_interfaces(edge_id: str) -> list[dict[str, Any]] | dict[str, Any]:
    """List interfaces for one v1 edge through the SDK."""
    try:
        client = build_sdk_client()
        return _serialize_v1_edge_payload(client.v1.edges.list_interfaces(edge_id))
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_edge_interface(edge_id: str, interface_id: str) -> dict[str, Any]:
    """Fetch one v1 edge interface through the SDK."""
    try:
        client = build_sdk_client()
        return _serialize_v1_edge_payload(
            client.v1.edges.get_interface(edge_id, interface_id)
        )
    except Exception as exc:
        return _serialize_sdk_error(exc)


def list_gateway_interfaces(gateway_id: str) -> list[dict[str, Any]] | dict[str, Any]:
    """List interfaces for one v1 gateway through the SDK."""
    try:
        client = build_sdk_client()
        return _serialize_v1_edge_payload(client.v1.edges.list_gateway_interfaces(gateway_id))
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_gateway_interface(gateway_id: str, interface_id: str) -> dict[str, Any]:
    """Fetch one v1 gateway interface through the SDK."""
    try:
        client = build_sdk_client()
        return _serialize_v1_edge_payload(
            client.v1.edges.get_gateway_interface(gateway_id, interface_id)
        )
    except Exception as exc:
        return _serialize_sdk_error(exc)


def serialize_edge(edge: Any) -> dict[str, Any]:
    """Serialize an SDK v1 edge resource into a plain dictionary."""
    if is_dataclass(edge):
        serialized = asdict(edge)
        raw = serialized.get("raw")
        if isinstance(raw, dict):
            return raw
        return serialized

    if isinstance(edge, dict):
        return dict(edge)

    raw = getattr(edge, "raw", None)
    if isinstance(raw, dict):
        return dict(raw)

    return {
        "id": getattr(edge, "id", None),
        "name": getattr(edge, "name", None),
    }


def _serialize_v1_edge_payload(
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
            "message": "V1 edge payload must be a JSON object or array of objects.",
        },
    }


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    return serialize_tool_error(exc)
