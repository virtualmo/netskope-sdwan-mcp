"""Factory helpers for constructing the Netskope SD-WAN SDK client."""

from __future__ import annotations

from importlib import import_module
from typing import Any

from .config import Settings, load_settings


def build_sdk_client(settings: Settings | None = None) -> Any:
    """Construct and return the SDK client from validated configuration."""
    resolved_settings = settings or load_settings()
    sdk_module = import_module("netskopesdwan")
    client_class = getattr(sdk_module, "SDWANClient")
    return client_class(
        base_url=resolved_settings.base_url,
        api_token=resolved_settings.api_token,
        timeout=resolved_settings.timeout,
        verify_ssl=resolved_settings.verify_ssl,
    )
