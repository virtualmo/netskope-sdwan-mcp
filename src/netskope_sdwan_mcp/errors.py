"""Shared error types for the MCP server."""


class NetskopeSdwanMcpError(Exception):
    """Base exception for the project."""


class ConfigurationError(NetskopeSdwanMcpError):
    """Raised when required configuration is missing or invalid."""

