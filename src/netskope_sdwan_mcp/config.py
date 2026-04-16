"""Configuration loading for the MCP server."""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Mapping
from urllib.parse import urlparse

from .errors import ConfigurationError

ENV_BASE_URL = "NETSKOPESDWAN_BASE_URL"
ENV_API_TOKEN = "NETSKOPESDWAN_API_TOKEN"
ENV_TIMEOUT = "NETSKOPESDWAN_TIMEOUT"
ENV_INSECURE = "NETSKOPESDWAN_INSECURE"

_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off"}


@dataclass(frozen=True)
class Settings:
    """Validated SDK configuration loaded from environment variables."""

    base_url: str
    api_token: str
    timeout: int = 30
    insecure: bool = False

    @property
    def verify_ssl(self) -> bool:
        """Translate the MCP config flag into the SDK's expected SSL setting."""
        return not self.insecure


def load_settings(environ: Mapping[str, str] | None = None) -> Settings:
    """Load and validate runtime settings from environment variables."""
    env = os.environ if environ is None else environ

    base_url = _require_non_empty(env, ENV_BASE_URL)
    api_token = _require_non_empty(env, ENV_API_TOKEN)
    timeout = _parse_timeout(env.get(ENV_TIMEOUT))
    insecure = _parse_bool(env.get(ENV_INSECURE), env_name=ENV_INSECURE)

    _validate_base_url(base_url)

    return Settings(
        base_url=base_url.rstrip("/"),
        api_token=api_token,
        timeout=timeout,
        insecure=insecure,
    )


def _require_non_empty(environ: Mapping[str, str], env_name: str) -> str:
    value = environ.get(env_name)
    if value is None or not value.strip():
        raise ConfigurationError(f"Missing required environment variable: {env_name}")
    return value.strip()


def _parse_timeout(raw_value: str | None) -> int:
    if raw_value is None or not raw_value.strip():
        return 30

    try:
        timeout = int(raw_value.strip())
    except ValueError as exc:
        raise ConfigurationError(
            f"{ENV_TIMEOUT} must be a positive integer, got: {raw_value!r}"
        ) from exc

    if timeout <= 0:
        raise ConfigurationError(
            f"{ENV_TIMEOUT} must be a positive integer, got: {raw_value!r}"
        )

    return timeout


def _parse_bool(raw_value: str | None, *, env_name: str) -> bool:
    if raw_value is None or not raw_value.strip():
        return False

    normalized = raw_value.strip().lower()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False

    raise ConfigurationError(
        f"{env_name} must be one of: true, false, 1, 0, yes, no, on, off"
    )


def _validate_base_url(base_url: str) -> None:
    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ConfigurationError(
            f"{ENV_BASE_URL} must be a valid absolute http(s) URL, got: {base_url!r}"
        )
