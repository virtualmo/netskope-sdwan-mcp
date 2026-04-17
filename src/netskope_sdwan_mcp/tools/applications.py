"""Application MCP tool implementations backed by the SDK."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error
from ._pagination import build_list_kwargs


def list_applications(
    filter: str | None = None,
    after: str | None = None,
    first: int | None = None,
    sort: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """List applications through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        applications = client.applications.list_custom_apps(
            **build_list_kwargs(
                filter=filter,
                after=after,
                first=first,
                sort=sort,
            ),
        )
        return [serialize_application(item) for item in applications]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def list_application_categories(
    filter: str | None = None,
    after: str | None = None,
    first: int | None = None,
    sort: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """List application categories through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        categories = client.applications.list_categories(
            **build_list_kwargs(
                filter=filter,
                after=after,
                first=first,
                sort=sort,
            ),
        )
        return [serialize_application(item) for item in categories]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def list_qosmos_apps(
    filter: str | None = None,
    after: str | None = None,
    first: int | None = None,
    sort: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """List qosmos applications through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        qosmos_apps = client.applications.list_qosmos_apps(
            **build_list_kwargs(
                filter=filter,
                after=after,
                first=first,
                sort=sort,
            ),
        )
        return [serialize_application(item) for item in qosmos_apps]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def list_webroot_categories(
    filter: str | None = None,
    after: str | None = None,
    first: int | None = None,
    sort: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """List webroot categories through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        categories = client.applications.list_webroot_categories(
            **build_list_kwargs(
                filter=filter,
                after=after,
                first=first,
                sort=sort,
            ),
        )
        return [serialize_application(item) for item in categories]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_application(id: str) -> dict[str, Any]:
    """Fetch one application by ID through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        application = client.applications.get_custom_app(id)
        return serialize_application(application)
    except Exception as exc:
        return _serialize_sdk_error(exc)


def serialize_application(application: Any) -> dict[str, Any]:
    """Serialize an SDK application resource into a plain dictionary."""
    if is_dataclass(application):
        serialized = asdict(application)
        raw = serialized.get("raw")
        if isinstance(raw, dict):
            return raw
        return serialized

    if isinstance(application, dict):
        return dict(application)

    raw = getattr(application, "raw", None)
    if isinstance(raw, dict):
        return dict(raw)

    return {
        "id": getattr(application, "id", None),
        "name": getattr(application, "name", None),
    }


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    return serialize_tool_error(exc)
