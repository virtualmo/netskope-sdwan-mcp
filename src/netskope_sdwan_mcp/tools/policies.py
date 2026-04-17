"""Policy MCP tool implementations backed by the SDK."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error
from ._pagination import build_list_kwargs


def list_policies(
    filter: str | None = None,
    after: str | None = None,
    first: int | None = None,
    sort: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """List policies through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        policies = client.policies.list(
            **build_list_kwargs(
                filter=filter,
                after=after,
                first=first,
                sort=sort,
            ),
        )
        return [serialize_policy(item) for item in policies]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_policy(id: str) -> dict[str, Any]:
    """Fetch one policy by ID through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        policy = client.policies.get(id)
        return serialize_policy(policy)
    except Exception as exc:
        return _serialize_sdk_error(exc)


def serialize_policy(policy: Any) -> dict[str, Any]:
    """Serialize an SDK policy resource into a plain dictionary."""
    if is_dataclass(policy):
        serialized = asdict(policy)
        raw = serialized.get("raw")
        if isinstance(raw, dict):
            return raw
        return serialized

    if isinstance(policy, dict):
        return dict(policy)

    raw = getattr(policy, "raw", None)
    if isinstance(raw, dict):
        return dict(raw)

    return {
        "id": getattr(policy, "id", None),
        "name": getattr(policy, "name", None),
    }


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    return serialize_tool_error(exc)
