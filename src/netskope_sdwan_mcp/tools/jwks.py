"""JWKS MCP tool implementations backed by the SDK."""

from __future__ import annotations

from typing import Any

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error


def get_jwks() -> dict[str, Any]:
    """Fetch the controller JWKS payload through the SDK."""
    try:
        client = build_sdk_client()
        return _serialize_jwks_payload(client.jwks.get())
    except Exception as exc:
        return _serialize_sdk_error(exc)


def _serialize_jwks_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if isinstance(payload, dict):
        return dict(payload)
    return {
        "status": "error",
        "error": {
            "type": "TypeError",
            "message": "JWKS payload must be a JSON object.",
        },
    }


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    return serialize_tool_error(exc)
