"""Shared error types and tool-facing error mapping for the MCP server."""

from __future__ import annotations

import re
from typing import Any


class NetskopeSdwanMcpError(Exception):
    """Base exception for the project."""


class ConfigurationError(NetskopeSdwanMcpError):
    """Raised when required configuration is missing or invalid."""


def serialize_tool_error(exc: Exception) -> dict[str, Any]:
    """Map internal exceptions to small, safe tool-facing error payloads."""
    if isinstance(exc, ConfigurationError):
        return _build_error(
            status="configuration_error",
            error_type="ConfigurationError",
            message=_sanitize_message(str(exc)),
        )

    if isinstance(exc, ValueError):
        return _build_error(
            status="invalid_request",
            error_type="ValueError",
            message=_sanitize_message(str(exc)),
        )

    if _is_not_found_error(exc):
        return _build_error(
            status="not_found",
            error_type="NotFoundError",
            message=_sanitize_message(str(exc)),
        )

    if _is_forbidden_error(exc):
        return _build_error(
            status="forbidden",
            error_type="AuthorizationError",
            message="Request is not authorized for this resource.",
        )

    if _is_unauthorized_error(exc):
        return _build_error(
            status="unauthorized",
            error_type="AuthenticationError",
            message="Authentication failed for the Netskope SD-WAN API.",
        )

    return _build_error(
        status="error",
        error_type="InternalError",
        message="Unexpected error while processing request.",
    )


def _build_error(*, status: str, error_type: str, message: str) -> dict[str, Any]:
    return {
        "status": status,
        "error": {
            "type": error_type,
            "message": message,
        },
    }


def _is_not_found_error(exc: Exception) -> bool:
    name = exc.__class__.__name__.lower()
    message = str(exc).lower()
    return name == "notfounderror" or " not found" in f" {message}"


def _is_unauthorized_error(exc: Exception) -> bool:
    name = exc.__class__.__name__.lower()
    message = str(exc).lower()
    return (
        "unauthorized" in name
        or "authentication" in name
        or "unauthorized" in message
        or "authentication failed" in message
        or "401" in message
    )


def _is_forbidden_error(exc: Exception) -> bool:
    name = exc.__class__.__name__.lower()
    message = str(exc).lower()
    return (
        "forbidden" in name
        or "authorization" in name
        or "forbidden" in message
        or "not authorized" in message
        or "403" in message
    )


def _sanitize_message(message: str) -> str:
    sanitized = re.sub(r"(?i)(bearer\s+)[^\s,;]+", r"\1[REDACTED]", message)
    sanitized = re.sub(r"(?i)(authorization:\s*)[^\s,;]+", r"\1[REDACTED]", sanitized)
    sanitized = re.sub(
        r"(?i)((?:api[_ -]?token|token|api[_ -]?key)\s*[=:]\s*)[^\s,;]+",
        r"\1[REDACTED]",
        sanitized,
    )
    return sanitized
