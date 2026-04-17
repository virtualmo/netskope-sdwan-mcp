"""Site-command MCP tool implementations backed by the SDK."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from ..client_factory import build_sdk_client
from ..errors import serialize_tool_error


def list_site_commands(filter: str | None = None) -> list[dict[str, Any]] | dict[str, Any]:
    """List site commands through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        site_commands = client.site_commands.list(filter=filter)
        return [serialize_site_command(item) for item in site_commands]
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_site_command(command_id: str) -> dict[str, Any]:
    """Fetch one site command by ID through the SDK and return JSON-serializable data."""
    try:
        client = build_sdk_client()
        site_command = client.site_commands.get(command_id)
        return serialize_site_command(site_command)
    except Exception as exc:
        return _serialize_sdk_error(exc)


def get_site_command_output(command_id: str, name: str) -> dict[str, Any]:
    """Fetch one site command output download through the SDK."""
    try:
        client = build_sdk_client()
        return _serialize_site_command_output(
            client.site_commands.get_output(command_id, name)
        )
    except Exception as exc:
        return _serialize_sdk_error(exc)


def serialize_site_command(site_command: Any) -> dict[str, Any]:
    """Serialize an SDK site-command resource into a plain dictionary."""
    if is_dataclass(site_command):
        serialized = asdict(site_command)
        raw = serialized.get("raw")
        if isinstance(raw, dict):
            return raw
        return serialized

    if isinstance(site_command, dict):
        return dict(site_command)

    raw = getattr(site_command, "raw", None)
    if isinstance(raw, dict):
        return dict(raw)

    return {
        "id": getattr(site_command, "id", None),
        "name": getattr(site_command, "name", None),
    }


def _serialize_site_command_output(download_result: Any) -> dict[str, Any]:
    if is_dataclass(download_result):
        serialized = asdict(download_result)
        content = serialized.get("content")
        if isinstance(content, bytes):
            serialized["content"] = content.decode("utf-8", errors="replace")
        return serialized

    return {
        "status": "error",
        "error": {
            "type": "TypeError",
            "message": "Site command output payload must be a download result object.",
        },
    }


def _serialize_sdk_error(exc: Exception) -> dict[str, Any]:
    return serialize_tool_error(exc)
