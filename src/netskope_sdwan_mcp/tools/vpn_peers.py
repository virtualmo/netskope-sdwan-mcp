"""VPN-peer MCP tool implementations backed by the SDK."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error
from ._pagination import build_list_kwargs


def list_vpn_peers(
    filter: str | None = None,
    after: str | None = None,
    first: int | None = None,
    sort: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """List VPN peers through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        vpn_peers = client.vpn_peers.list(
            **build_list_kwargs(
                filter=filter,
                after=after,
                first=first,
                sort=sort,
            ),
        )
        return [serialize_vpn_peer(item) for item in vpn_peers]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_vpn_peer(id: str) -> dict[str, Any]:
    """Fetch one VPN peer by ID through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        vpn_peer = client.vpn_peers.get(id)
        return serialize_vpn_peer(vpn_peer)
    except Exception as exc:
        return _serialize_sdk_error(exc)


def serialize_vpn_peer(vpn_peer: Any) -> dict[str, Any]:
    """Serialize an SDK VPN-peer resource into a plain dictionary."""
    if is_dataclass(vpn_peer):
        serialized = asdict(vpn_peer)
        raw = serialized.get("raw")
        if isinstance(raw, dict):
            return raw
        return serialized

    if isinstance(vpn_peer, dict):
        return dict(vpn_peer)

    raw = getattr(vpn_peer, "raw", None)
    if isinstance(raw, dict):
        return dict(raw)

    return {
        "id": getattr(vpn_peer, "id", None),
        "name": getattr(vpn_peer, "name", None),
    }


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    return serialize_tool_error(exc)
