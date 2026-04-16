"""Audit-event MCP tool implementations backed by the SDK."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error


def list_audit_events(
    created_at_from: str,
    created_at_to: str,
    type: str | None = None,
    subtype: str | None = None,
    activity: str | None = None,
    after: str | None = None,
    first: int | None = None,
    sort: str | None = None,
    filter: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """List audit events through the SDK and return JSON-serializable data."""
    try:
        _validate_required_time_bounds(
            created_at_from=created_at_from,
            created_at_to=created_at_to,
        )
        client = build_sdk_client()
        audit_events = client.audit_events.list(
            created_at_from=created_at_from,
            created_at_to=created_at_to,
            type=type,
            subtype=subtype,
            activity=activity,
            after=after,
            first=first,
            sort=sort,
            filter=filter,
        )
        return [serialize_audit_event(item) for item in audit_events]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def serialize_audit_event(audit_event: Any) -> dict[str, Any]:
    """Serialize an SDK audit-event resource into a plain dictionary."""
    if is_dataclass(audit_event):
        serialized = asdict(audit_event)
        raw = serialized.get("raw")
        if isinstance(raw, dict):
            return raw
        return serialized

    if isinstance(audit_event, dict):
        return dict(audit_event)

    raw = getattr(audit_event, "raw", None)
    if isinstance(raw, dict):
        return dict(raw)

    return {
        "id": getattr(audit_event, "id", None),
        "name": getattr(audit_event, "name", None),
    }


def _validate_required_time_bounds(
    *,
    created_at_from: str,
    created_at_to: str,
) -> None:
    if not created_at_from:
        raise ValueError("created_at_from is required")
    if not created_at_to:
        raise ValueError("created_at_to is required")


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    return serialize_tool_error(exc)
